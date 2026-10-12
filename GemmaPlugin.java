package com.neet.chemistry;

import android.app.Activity;
import android.content.Intent;
import android.database.Cursor;
import android.net.Uri;
import android.provider.OpenableColumns;

import androidx.activity.result.ActivityResult;

import com.getcapacitor.JSObject;
import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.ActivityCallback;
import com.getcapacitor.annotation.CapacitorPlugin;
import com.google.mediapipe.tasks.genai.llminference.LlmInference;

import java.io.File;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.io.OutputStream;

/** On-device Gemma (MediaPipe LLM Inference). The model file is copied once into app storage and reused. */
@CapacitorPlugin(name = "Gemma")
public class GemmaPlugin extends Plugin {

    private LlmInference llm;
    private final Object lock = new Object();

    private File modelFile() {
        return new File(getContext().getFilesDir(), "gemma.task");
    }

    @PluginMethod
    public void status(PluginCall call) {
        JSObject r = new JSObject();
        r.put("hasModel", modelFile().exists() && modelFile().length() > 1000000L);
        r.put("loaded", llm != null);
        call.resolve(r);
    }

    @PluginMethod
    public void pickModel(PluginCall call) {
        Intent i = new Intent(Intent.ACTION_OPEN_DOCUMENT);
        i.addCategory(Intent.CATEGORY_OPENABLE);
        i.setType("*/*");
        startActivityForResult(call, i, "pickResult");
    }

    @ActivityCallback
    private void pickResult(PluginCall call, ActivityResult result) {
        if (call == null) return;
        if (result.getResultCode() != Activity.RESULT_OK || result.getData() == null || result.getData().getData() == null) {
            call.reject("File select nahi hui.");
            return;
        }
        final Uri uri = result.getData().getData();
        new Thread(() -> copyModel(call, uri)).start();
    }

    private long sizeOf(Uri uri) {
        try (Cursor c = getContext().getContentResolver().query(uri, null, null, null, null)) {
            if (c != null && c.moveToFirst()) {
                int idx = c.getColumnIndex(OpenableColumns.SIZE);
                if (idx >= 0 && !c.isNull(idx)) return c.getLong(idx);
            }
        } catch (Exception ignored) {
        }
        return -1L;
    }

    private void copyModel(PluginCall call, Uri uri) {
        File tmp = new File(getContext().getFilesDir(), "gemma.tmp");
        try {
            long size = sizeOf(uri);
            long total = 0;
            int last = -1;
            try (InputStream in = getContext().getContentResolver().openInputStream(uri);
                 OutputStream out = new FileOutputStream(tmp)) {
                if (in == null) throw new Exception("File khul nahi payi.");
                byte[] buf = new byte[1 << 20];
                int n;
                while ((n = in.read(buf)) > 0) {
                    out.write(buf, 0, n);
                    total += n;
                    if (size > 0) {
                        int pct = (int) (total * 100L / size);
                        if (pct != last) {
                            last = pct;
                            JSObject p = new JSObject();
                            p.put("pct", pct);
                            notifyListeners("progress", p);
                        }
                    }
                }
            }
            synchronized (lock) {
                llm = null;
                File dst = modelFile();
                if (dst.exists()) dst.delete();
                if (!tmp.renameTo(dst)) throw new Exception("Model save nahi ho paya.");
            }
            call.resolve();
        } catch (Throwable t) {
            tmp.delete();
            call.reject("Copy fail: " + t.getMessage());
        }
    }

    @PluginMethod
    public void load(PluginCall call) {
        new Thread(() -> {
            try {
                synchronized (lock) {
                    if (llm == null) {
                        File f = modelFile();
                        if (!f.exists()) {
                            call.reject("Model file abhi nahi hai. Choose file se model chuno.");
                            return;
                        }
                        LlmInference.LlmInferenceOptions opts = LlmInference.LlmInferenceOptions.builder()
                                .setModelPath(f.getAbsolutePath())
                                .setMaxTokens(2048)
                                .build();
                        llm = LlmInference.createFromOptions(getContext(), opts);
                    }
                }
                call.resolve();
            } catch (Throwable t) {
                call.reject("Gemma load fail: " + t.getMessage());
            }
        }).start();
    }

    @PluginMethod
    public void generate(PluginCall call) {
        final String prompt = call.getString("prompt", "");
        new Thread(() -> {
            try {
                String text;
                synchronized (lock) {
                    if (llm == null) {
                        call.reject("Gemma load nahi hua.");
                        return;
                    }
                    text = llm.generateResponse(prompt);
                }
                JSObject r = new JSObject();
                r.put("text", text);
                call.resolve(r);
            } catch (Throwable t) {
                call.reject("Gemma error: " + t.getMessage());
            }
        }).start();
    }
}
