package com.criteriofinanciero.botwifi;

import android.util.Base64;
import android.util.Log;

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

        boolean ok = sendHttpRequest(target, "POST", null, null, cb);
        if (!ok) {
            ok = sendHttpRequest(target, "GET", null, null, cb);
        }

        if (!ok && !target.contains("?") && target.split("/").length <= 4) {
            String cleanBase = target.endsWith("/") ? target.substring(0, target.length() - 1) : target;
            cb.onLog("Probando endpoint Shelly (/relay/0?turn=toggle)...");
            ok = sendHttpRequest(cleanBase + "/relay/0?turn=toggle", "GET", null, null, cb);
            if (!ok) {
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
            return rebootMovistarHgu(base, user, pass, cb);
        } else if (brand.contains("Huawei")) {
            success = sendHttpRequest(base + "/api/system/reboot", "POST", "<request><Control>1</Control></request>", basicAuth, cb);
            if (!success) {
                success = sendHttpRequest(base + "/index/reboot.cgi", "POST", "reboot=1", basicAuth, cb);
            }
            if (!success) {
                success = sendHttpRequest(base + "/api/system/device-reboot", "POST", null, basicAuth, cb);
            }
        } else if (brand.contains("ZTE")) {
            success = sendHttpRequest(base + "/getpage.gch?pid=1002&nextpage=diagnose_reboot.gch&reboot_type=1", "POST", null, basicAuth, cb);
            if (!success) {
                success = sendHttpRequest(base + "/getpage.gch?pid=1001", "POST", "Action=Reboot", basicAuth, cb);
            }
        } else if (brand.contains("Sagemcom")) {
            String sagemPayload = "{\"method\":\"reboot\",\"parameters\":{}}";
            success = sendHttpRequest(base + "/json-rpc", "POST", sagemPayload, basicAuth, cb);
            if (!success) {
                success = sendHttpRequest(base + "/gui/reboot", "POST", null, basicAuth, cb);
            }
        } else {
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

    private static boolean rebootMovistarHgu(String host, String user, String pass, LogCallback cb) {
        String cleanIp = host.replace("http://", "").replace("https://", "");
        if (cleanIp.contains("/")) cleanIp = cleanIp.split("/")[0];
        if (cleanIp.contains(":")) cleanIp = cleanIp.split(":")[0];
        if (cleanIp.trim().isEmpty()) cleanIp = "192.168.1.1";
        final String pw = pass != null ? pass.trim() : "";

        String[] bases = new String[]{
                "http://" + cleanIp + ":8000",
                "https://" + cleanIp + ":8000",
                "http://" + cleanIp,
                "https://" + cleanIp
        };

        String u1 = (user != null && !user.trim().isEmpty()) ? user.trim() : "1234";
        String[] users = u1.equals("1234") ? new String[]{"1234", "admin"} : new String[]{u1, "1234", "admin"};

        cb.onLog("📡 Autenticando en Módem Movistar GPT (" + cleanIp + ")...");

        // 1. Login formal con captura de Cookie
        for (String baseUrl : bases) {
            for (String u : users) {
                for (String loginPath : new String[]{"/cgi-bin/logIn_mhs.cgi", "/cgi-bin/login.cgi", "/login.cgi"}) {
                    try {
                        String payload = "Username=" + java.net.URLEncoder.encode(u, "UTF-8") + "&Password=" + java.net.URLEncoder.encode(pw, "UTF-8");
                        HttpURLConnection conn = openConnection(baseUrl + loginPath, "POST", payload, null, null);
                        int code = conn.getResponseCode();
                        String cookie = conn.getHeaderField("Set-Cookie");
                        conn.disconnect();

                        if (cookie != null && !cookie.isEmpty()) {
                            String cookieHeader = cookie.split(";")[0];
                            cb.onLog("✔ Sesión iniciada en " + baseUrl + " con usuario '" + u + "'");

                            // 2. Enviar orden de reboot con la cookie
                            for (String rPath : new String[]{"/cgi-bin/reboot.cgi", "/cgi-bin/te_reboot.cgi"}) {
                                try {
                                    HttpURLConnection rConn = openConnection(baseUrl + rPath, "POST", "reboot=1", null, cookieHeader);
                                    int rCode = rConn.getResponseCode();
                                    rConn.disconnect();
                                    if (rCode >= 200 && rCode < 400) {
                                        cb.onLog("✔ ¡Orden de reinicio aceptada por el módem Movistar GPT!");
                                        return true;
                                    }
                                } catch (Exception ignored) {}
                            }
                        }
                    } catch (Exception ignored) {}
                }
            }
        }

        // 3. Fallback directo a endpoints comunes
        cb.onLog("Probando rutas directas de reinicio Movistar...");
        for (String baseUrl : bases) {
            for (String rPath : new String[]{"/cgi-bin/te_reboot.cgi", "/cgi-bin/reboot.cgi", "/reboot.cgi"}) {
                boolean ok = sendHttpRequest(baseUrl + rPath, "POST", "reboot=1", null, cb);
                if (ok) {
                    cb.onLog("✔ Orden de reinicio enviada a " + baseUrl + rPath);
                    return true;
                }
            }
        }
        cb.onLog("⚡ Peticiones enviadas al módem Movistar. Iniciando ciclo de espera...");
        return true;
    }

    private static boolean sendHttpRequest(String urlStr, String method, String body, String authHeader, LogCallback cb) {
        HttpURLConnection conn = null;
        try {
            conn = openConnection(urlStr, method, body, authHeader, null);
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

    private static HttpURLConnection openConnection(String urlStr, String method, String body, String authHeader, String cookieHeader) throws Exception {
        URL url = new URL(urlStr);
        HttpURLConnection conn = (HttpURLConnection) url.openConnection();
        conn.setRequestMethod(method);
        conn.setConnectTimeout(4000);
        conn.setReadTimeout(4000);
        conn.setUseCaches(false);
        conn.setDoInput(true);

        if (conn instanceof javax.net.ssl.HttpsURLConnection) {
            javax.net.ssl.HttpsURLConnection httpsConn = (javax.net.ssl.HttpsURLConnection) conn;
            httpsConn.setHostnameVerifier(new javax.net.ssl.HostnameVerifier() {
                @Override
                public boolean verify(String hostname, javax.net.ssl.SSLSession session) {
                    return true;
                }
            });
            try {
                javax.net.ssl.SSLContext sc = javax.net.ssl.SSLContext.getInstance("TLS");
                sc.init(null, new javax.net.ssl.TrustManager[]{
                        new javax.net.ssl.X509TrustManager() {
                            public java.security.cert.X509Certificate[] getAcceptedIssuers() { return new java.security.cert.X509Certificate[0]; }
                            public void checkClientTrusted(java.security.cert.X509Certificate[] certs, String authType) {}
                            public void checkServerTrusted(java.security.cert.X509Certificate[] certs, String authType) {}
                        }
                }, new java.security.SecureRandom());
                httpsConn.setSSLSocketFactory(sc.getSocketFactory());
            } catch (Exception ignored) {}
        }

        if (authHeader != null) {
            conn.setRequestProperty("Authorization", authHeader);
        }
        if (cookieHeader != null) {
            conn.setRequestProperty("Cookie", cookieHeader);
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
        return conn;
    }
}
