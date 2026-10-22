package com.criteriofinanciero.botwifi;

import android.util.Base64;
import android.util.Log;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;

public class ModemRebooter {

    private static final String TAG = "ModemRebooter";

    public interface LogCallback {
        void onLog(String message);
    }

    public static boolean reboot(boolean useSmartPlug, String smartPlugUrl,
                                 String host, String user, String pass, String brand,
                                 LogCallback callback) {
        if (useSmartPlug) {
            return triggerSmartPlug(smartPlugUrl, callback);
        } else {
            return triggerModem(host, user, pass, brand, callback);
        }
    }

    private static boolean triggerSmartPlug(String rawUrl, LogCallback cb) {
        if (rawUrl == null || rawUrl.trim().isEmpty()) {
            cb.onLog("⚠ Error: URL o IP del Enchufe Inteligente vacía.");
            return false;
        }

        String target = rawUrl.trim();
        if (!target.startsWith("http://") && !target.startsWith("https://")) {
            target = "http://" + target;
        }

        cb.onLog("🔌 Enviando orden de corte de energía al enchufe: " + target);

        // Intento directo al endpoint configurado
        boolean ok = sendHttpRequest(target, "POST", null, null, cb);
        if (!ok) {
            ok = sendHttpRequest(target, "GET", null, null, cb);
        }

        // Si solo se ingresó una IP (ej: http://192.168.1.150), probar endpoints comunes de enchufes
        if (!ok && !target.contains("?") && target.split("/").length <= 4) {
            String cleanBase = target.endsWith("/") ? target.substring(0, target.length() - 1) : target;
            // Shelly: /relay/0?turn=toggle
            cb.onLog("Probando endpoint Shelly (/relay/0?turn=toggle)...");
            ok = sendHttpRequest(cleanBase + "/relay/0?turn=toggle", "GET", null, null, cb);
            if (!ok) {
                // Tasmota: /cm?cmnd=Power%20TOGGLE
                cb.onLog("Probando endpoint Tasmota (/cm?cmnd=Power%20TOGGLE)...");
                ok = sendHttpRequest(cleanBase + "/cm?cmnd=Power%20TOGGLE", "GET", null, null, cb);
            }
        }

        if (ok) {
            cb.onLog("✔ Señal recibida por el Enchufe Inteligente.");
        } else {
            cb.onLog("⚠ Señal enviada (sin confirmación HTTP directa, esperando ciclo de reinicio).");
        }
        return true;
    }

    private static boolean triggerModem(String host, String user, String pass, String brand, LogCallback cb) {
        if (host == null || host.trim().isEmpty()) {
            host = "192.168.1.1";
        }
        String base = host.trim();
        if (!base.startsWith("http://") && !base.startsWith("https://")) {
            base = "http://" + base;
        }
        while (base.endsWith("/")) {
            base = base.substring(0, base.length() - 1);
        }

        cb.onLog("📡 Enviando orden de reinicio al módem (" + brand + ") en: " + base);

        String basicAuth = null;
        if (user != null && !user.isEmpty() && pass != null && !pass.isEmpty()) {
            String creds = user.trim() + ":" + pass.trim();
            basicAuth = "Basic " + Base64.encodeToString(creds.getBytes(StandardCharsets.UTF_8), Base64.NO_WRAP);
        }

        boolean success = false;

        if (brand.contains("Movistar")) {
            // Movistar HGU (Askey RTF8115VW / MitraStar GPT-2541GNAC)
            success = sendHttpRequest(base + "/cgi-bin/te_reboot.cgi", "POST", null, basicAuth, cb);
            if (!success) {
                success = sendHttpRequest(base + "/reboot.cgi", "POST", "reboot=1", basicAuth, cb);
            }
            if (!success) {
                success = sendHttpRequest(base + "/cgi-bin/reboot.cgi", "POST", null, basicAuth, cb);
            }
        } else if (brand.contains("Huawei")) {
            // Huawei ONT / HG8245 reboot endpoints
            success = sendHttpRequest(base + "/api/system/reboot", "POST", "<request><Control>1</Control></request>", basicAuth, cb);
            if (!success) {
                success = sendHttpRequest(base + "/index/reboot.cgi", "POST", "reboot=1", basicAuth, cb);
            }
            if (!success) {
                success = sendHttpRequest(base + "/api/system/device-reboot", "POST", null, basicAuth, cb);
            }
        } else if (brand.contains("ZTE")) {
            // ZTE F660 / F670 / F680
            success = sendHttpRequest(base + "/getpage.gch?pid=1002&nextpage=diagnose_reboot.gch&reboot_type=1", "POST", null, basicAuth, cb);
            if (!success) {
                success = sendHttpRequest(base + "/getpage.gch?pid=1001", "POST", "Action=Reboot", basicAuth, cb);
            }
        } else if (brand.contains("Sagemcom")) {
            // Sagemcom Fast
            String sagemPayload = "{\"method\":\"reboot\",\"parameters\":{}}";
            success = sendHttpRequest(base + "/json-rpc", "POST", sagemPayload, basicAuth, cb);
            if (!success) {
                success = sendHttpRequest(base + "/gui/reboot", "POST", null, basicAuth, cb);
            }
        } else {
            // TP-Link o Genérico / Desconocido
            success = sendHttpRequest(base + "/userRpm/SysRebootRpm.htm?Reboot=Reboot", "GET", null, basicAuth, cb);
            if (!success) {
                success = sendHttpRequest(base + "/cgi/reboot", "POST", null, basicAuth, cb);
            }
            if (!success) {
                success = sendHttpRequest(base + "/reboot.cgi", "POST", "reboot=1", basicAuth, cb);
            }
            if (!success) {
                success = sendHttpRequest(base + "/api/system/reboot", "POST", null, basicAuth, cb);
            }
        }

        if (success) {
            cb.onLog("✔ Petición de reinicio aceptada por el módem.");
        } else {
            cb.onLog("⚡ Peticiones enviadas al módem. Iniciando ciclo de reconexión...");
        }
        return true;
    }

    private static boolean sendHttpRequest(String urlStr, String method, String body, String authHeader, LogCallback cb) {
        HttpURLConnection conn = null;
        try {
            URL url = new URL(urlStr);
            conn = (HttpURLConnection) url.openConnection();
            conn.setRequestMethod(method);
            conn.setConnectTimeout(4500);
            conn.setReadTimeout(4500);
            conn.setUseCaches(false);
            conn.setDoInput(true);

            if (authHeader != null) {
                conn.setRequestProperty("Authorization", authHeader);
            }
            conn.setRequestProperty("User-Agent", "Mozilla/5.0 (Android; CFBotWiFi/1.0)");
            conn.setRequestProperty("Content-Type", "application/x-www-form-urlencoded");

            if (body != null && "POST".equalsIgnoreCase(method)) {
                conn.setDoOutput(true);
                byte[] bytes = body.getBytes(StandardCharsets.UTF_8);
                conn.setFixedLengthStreamingMode(bytes.length);
                try (OutputStream os = conn.getOutputStream()) {
                    os.write(bytes);
                    os.flush();
                }
            }

            int code = conn.getResponseCode();
            Log.d(TAG, "Response from " + urlStr + " -> HTTP " + code);
            return (code >= 200 && code < 400);
        } catch (Exception e) {
            Log.d(TAG, "Request to " + urlStr + " returned: " + e.getMessage());
            return false;
        } finally {
            if (conn != null) {
                try { conn.disconnect(); } catch (Exception ignored) {}
            }
        }
    }
}
