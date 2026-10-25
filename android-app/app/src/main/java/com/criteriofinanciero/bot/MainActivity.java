package com.criteriofinanciero.bot;

import android.app.Activity;
import android.content.Intent;
import android.content.SharedPreferences;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.os.Message;
import android.webkit.WebChromeClient;
import android.provider.Settings;
import android.util.Log;
import android.view.View;
import android.view.WindowManager;
import android.webkit.CookieManager;
import android.webkit.WebStorage;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.HashMap;
import java.util.Locale;
import java.util.Map;
import java.util.Random;

public class MainActivity extends Activity {

    private static final String DEFAULT_TARGET_URL = "https://criteriofinanciero.onrender.com";
    private static final String PREFS_NAME = "CFBotPrefs";
    private static final String KEY_CUSTOM_URL = "custom_target_url";

        private static final String[] PATHS = new String[]{
            "/",
            "/",
            "/guias",
            "/comparativas",
            "/articulo/como-invertir-en-cedears-argentina-guia-paso-a-paso",
            "/articulo/que-billetera-virtual-paga-mas-tasa-argentina",
            "/articulo/como-comprar-dolar-mep-home-banking-sin-cepo",
            "/articulo/mejores-brokers-argentina-comparativa-comisiones"
    };

    private static final String[] USER_AGENTS = new String[]{
            "Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Mobile Safari/537.36",
            "Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Mobile Safari/537.36",
            "Mozilla/5.0 (Linux; Android 12; moto g52) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Mobile Safari/537.36",
            "Mozilla/5.0 (Linux; Android 13; motorola edge 40) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Mobile Safari/537.36",
            "Mozilla/5.0 (Linux; Android 14; SM-A546E) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Mobile Safari/537.36",
            "Mozilla/5.0 (Linux; Android 13; 2210132G) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Mobile Safari/537.36"
    };

    private final Handler handler = new Handler(Looper.getMainLooper());
    private final Random random = new Random();

    private TextView tvStatus;
    private TextView tvIp;
    private TextView tvVisitsCount;
    private TextView tvLog;
    private EditText etTargetUrl;
    private ScrollView scrollLog;
    private WebView webView;
    private Button btnToggleAuto;
    private Button btnAirplaneQuick;
    private Button btnPermisoSinPc;

    private boolean isRunning = false;
    private boolean isVisiting = false;
    private int visitCount = 0;
    private String lastIp = "";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);

        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setBackgroundColor(Color.parseColor("#070d19"));
        root.setPadding(32, 36, 32, 24);

        // Header
        TextView title = new TextView(this);
        title.setText("CF Bot 4G — Tráfico & Rotación IP");
        title.setTextColor(Color.WHITE);
        title.setTextSize(18f);
        title.setTypeface(null, Typeface.BOLD);
        root.addView(title);

        // Selector de URL Destino Personalizable
        TextView urlLabel = new TextView(this);
        urlLabel.setText("URL de la Página Web Destino (Editable):");
        urlLabel.setTextColor(Color.parseColor("#34d399"));
        urlLabel.setTextSize(12f);
        urlLabel.setPadding(0, 10, 0, 4);
        root.addView(urlLabel);

        SharedPreferences prefs = getSharedPreferences(PREFS_NAME, MODE_PRIVATE);
        String savedUrl = prefs.getString(KEY_CUSTOM_URL, DEFAULT_TARGET_URL);

        etTargetUrl = new EditText(this);
        etTargetUrl.setText(savedUrl);
        etTargetUrl.setTextColor(Color.WHITE);
        etTargetUrl.setHintTextColor(Color.parseColor("#64748b"));
        etTargetUrl.setHint("https://tupaginaweb.com");
        etTargetUrl.setTextSize(13.5f);
        etTargetUrl.setSingleLine(true);
        GradientDrawable inputBg = new GradientDrawable();
        inputBg.setColor(Color.parseColor("#0f1a2e"));
        inputBg.setCornerRadius(14f);
        inputBg.setStroke(2, Color.parseColor("#10b981"));
        etTargetUrl.setBackground(inputBg);
        etTargetUrl.setPadding(24, 16, 24, 16);
        root.addView(etTargetUrl);

        // Card de Métricas
        LinearLayout card = new LinearLayout(this);
        card.setOrientation(LinearLayout.VERTICAL);
        GradientDrawable cardBg = new GradientDrawable();
        cardBg.setColor(Color.parseColor("#0f1a2e"));
        cardBg.setCornerRadius(20f);
        cardBg.setStroke(2, Color.parseColor("#1f3358"));
        card.setBackground(cardBg);
        card.setPadding(28, 20, 28, 20);
        LinearLayout.LayoutParams cardParams = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT);
        cardParams.topMargin = 14;
        card.setLayoutParams(cardParams);

        tvStatus = new TextView(this);
        tvStatus.setText("ESTADO: DETENIDO");
        tvStatus.setTextColor(Color.parseColor("#fde047"));
        tvStatus.setTextSize(13f);
        tvStatus.setTypeface(null, Typeface.BOLD);
        card.addView(tvStatus);

        tvIp = new TextView(this);
        tvIp.setText("IP Pública 4G actual: Consultando...");
        tvIp.setTextColor(Color.parseColor("#f1f5f9"));
        tvIp.setTextSize(14f);
        tvIp.setPadding(0, 6, 0, 4);
        card.addView(tvIp);

        tvVisitsCount = new TextView(this);
        tvVisitsCount.setText("Visitas enviadas en esta sesión: 0");
        tvVisitsCount.setTextColor(Color.parseColor("#34d399"));
        tvVisitsCount.setTextSize(14f);
        tvVisitsCount.setTypeface(null, Typeface.BOLD);
        card.addView(tvVisitsCount);

        root.addView(card);

        // Botones de Control
        LinearLayout btnRow = new LinearLayout(this);
        btnRow.setOrientation(LinearLayout.VERTICAL);
        btnRow.setPadding(0, 16, 0, 10);

        btnToggleAuto = new Button(this);
        btnToggleAuto.setText("▶ INICIAR BOT AUTOMÁTICO");
        btnToggleAuto.setBackgroundColor(Color.parseColor("#10b981"));
        btnToggleAuto.setTextColor(Color.WHITE);
        btnToggleAuto.setTypeface(null, Typeface.BOLD);
        btnToggleAuto.setPadding(16, 20, 16, 20);
        btnToggleAuto.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                saveCurrentTargetUrl();
                toggleBot();
            }
        });
        btnRow.addView(btnToggleAuto);

        btnAirplaneQuick = new Button(this);
        btnAirplaneQuick.setText("✈ CAMBIAR IP AHORA (MODO AVIÓN AUTO)");
        btnAirplaneQuick.setBackgroundColor(Color.parseColor("#3b82f6"));
        btnAirplaneQuick.setTextColor(Color.WHITE);
        btnAirplaneQuick.setTypeface(null, Typeface.BOLD);
        btnAirplaneQuick.setPadding(16, 18, 16, 18);
        LinearLayout.LayoutParams btnAirParams = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT);
        btnAirParams.topMargin = 12;
        btnAirplaneQuick.setLayoutParams(btnAirParams);
        btnAirplaneQuick.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                triggerIpRotation();
            }
        });
        btnRow.addView(btnAirplaneQuick);

        btnPermisoSinPc = new Button(this);
        btnPermisoSinPc.setText("⚙ PERMISO PERMANENTE SIN PC (ACCESIBILIDAD)");
        btnPermisoSinPc.setBackgroundColor(Color.parseColor("#475569"));
        btnPermisoSinPc.setTextColor(Color.WHITE);
        btnPermisoSinPc.setTextSize(11.5f);
        btnPermisoSinPc.setTypeface(null, Typeface.BOLD);
        btnPermisoSinPc.setPadding(14, 14, 14, 14);
        LinearLayout.LayoutParams btnPermParams = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT);
        btnPermParams.topMargin = 10;
        btnPermisoSinPc.setLayoutParams(btnPermParams);
        btnPermisoSinPc.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                log("Abriendo Accesibilidad: activá 'CF Bot 4G — Auto Modo Avión' para que funcione siempre sin PC.");
                try {
                    Intent intent = new Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS);
                    startActivity(intent);
                } catch (Exception ignored) {
                }
            }
        });
        btnRow.addView(btnPermisoSinPc);

        root.addView(btnRow);

        // Consola de Log
        TextView logHeader = new TextView(this);
        logHeader.setText("Registro de Actividad en Vivo:");
        logHeader.setTextColor(Color.parseColor("#cbd5e1"));
        logHeader.setTextSize(11.5f);
        logHeader.setPadding(0, 4, 0, 4);
        root.addView(logHeader);

        scrollLog = new ScrollView(this);
        LinearLayout.LayoutParams scrollParams = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, 260);
        scrollLog.setLayoutParams(scrollParams);
        scrollLog.setBackgroundColor(Color.parseColor("#030710"));
        scrollLog.setPadding(16, 12, 16, 12);

        tvLog = new TextView(this);
        tvLog.setTextColor(Color.parseColor("#e2e8f0"));
        tvLog.setTextSize(11f);
        tvLog.setTypeface(Typeface.MONOSPACE);
        scrollLog.addView(tvLog);
        root.addView(scrollLog);

        // Visor Web en Vivo
        TextView webHeader = new TextView(this);
        webHeader.setText("Visor de Navegación Orgánica:");
        webHeader.setTextColor(Color.parseColor("#cbd5e1"));
        webHeader.setTextSize(11.5f);
        webHeader.setPadding(0, 10, 0, 6);
        root.addView(webHeader);

        webView = new WebView(this);
        LinearLayout.LayoutParams webParams = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.MATCH_PARENT);
        webView.setLayoutParams(webParams);

        WebSettings ws = webView.getSettings();
        ws.setJavaScriptEnabled(true);
        ws.setDomStorageEnabled(true);
        ws.setJavaScriptCanOpenWindowsAutomatically(true);
        ws.setDatabaseEnabled(true);
        ws.setMediaPlaybackRequiresUserGesture(true); // Bloqueo estricto de autoplay de videos y audios pesados
        ws.setCacheMode(WebSettings.LOAD_DEFAULT); // Cache inteligente: no re-descarga CSS ni logos en cada visita

        ws.setSupportMultipleWindows(true);

        webView.setWebChromeClient(new WebChromeClient() {
            @Override
            public boolean onCreateWindow(WebView view, boolean isDialog, boolean isUserGesture, Message resultMsg) {
                final WebView tempView = new WebView(MainActivity.this);
                WebSettings ts = tempView.getSettings();
                ts.setJavaScriptEnabled(true);
                ts.setDomStorageEnabled(true);
                ts.setDatabaseEnabled(true);
                ts.setUserAgentString(ws.getUserAgentString());

                tempView.setWebViewClient(new WebViewClient() {
                    @Override
                    public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                        if (request != null && request.getUrl() != null) {
                            return handlePopunderUrl(view, request.getUrl().toString());
                        }
                        return false;
                    }

                    @SuppressWarnings("deprecation")
                    @Override
                    public boolean shouldOverrideUrlLoading(WebView view, String url) {
                        return handlePopunderUrl(view, url);
                    }

                    private boolean handlePopunderUrl(final WebView view, String url) {
                        if (url == null) return false;
                        String u = url.toLowerCase();
                        if (u.contains("unfolded-uncle.com") || u.contains("hilltop") || u.contains("criteriofinanciero")) {
                            return false;
                        }
                        log("💰 HilltopAds Popunder validado! Bloqueando landing externa: " + (url.length() > 42 ? url.substring(0, 42) + "..." : url));
                        handler.post(new Runnable() {
                            @Override
                            public void run() {
                                try {
                                    view.stopLoading();
                                    view.destroy();
                                } catch (Exception ignored) {}
                            }
                        });
                        return true;
                    }
                });

                handler.postDelayed(new Runnable() {
                    @Override
                    public void run() {
                        try {
                            tempView.stopLoading();
                            tempView.destroy();
                        } catch (Exception ignored) {}
                    }
                }, 6500);

                WebView.WebViewTransport transport = (WebView.WebViewTransport) resultMsg.obj;
                transport.setWebView(tempView);
                resultMsg.sendToTarget();
                return true;
            }
        });

        webView.setWebViewClient(new WebViewClient() {
            @Override
            public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                if (request != null && request.getUrl() != null) {
                    return blockExternalLanding(request.getUrl().toString());
                }
                return false;
            }

            @SuppressWarnings("deprecation")
            @Override
            public boolean shouldOverrideUrlLoading(WebView view, String url) {
                if (url != null) {
                    return blockExternalLanding(url);
                }
                return false;
            }

            private boolean blockExternalLanding(String url) {
                if (url == null) return false;
                String u = url.toLowerCase();
                String targetBase = getCurrentTargetBase().toLowerCase();

                // Permitir navegación legítima dentro del portal de Criterio Financiero
                if (u.contains("criteriofinanciero") || u.startsWith(targetBase)) {
                    return false;
                }

                // SI ES UNA REDIRECCIÓN DE ANUNCIANTE (casino, juego, app, descarga, temu):
                // Bloquear navegación externa de inmediato. Retornar true hace que Android descarte la carga.
                // Ahorro masivo de ~5 MB por clic. La red publicitaria ya registró la impresión/clic.
                log("🛡 Ahorro 4G: Landing externa bloqueada (" + (url.length() > 42 ? url.substring(0, 42) + "..." : url) + ")");
                return true;
            }

            @Override
            public WebResourceResponse shouldInterceptRequest(WebView view, WebResourceRequest request) {
                if (request != null && request.getUrl() != null) {
                    String u = request.getUrl().toString().toLowerCase();
                    // 1. Bloqueo de creatividades GIF pesadas (ahorro de ~200 KB por banner)
                    // Responde con un GIF transparente 1x1 (43 bytes) para mantener intacta la impresion y el iframe
                    if (u.contains(".gif")) {
                        byte[] transparent1x1Gif = new byte[]{
                            0x47, 0x49, 0x46, 0x38, 0x39, 0x61, 0x01, 0x00, 0x01, 0x00, (byte)0x80, 0x00, 0x00,
                            (byte)0xff, (byte)0xff, (byte)0xff, 0x00, 0x00, 0x00, 0x21, (byte)0xf9, 0x04, 0x01,
                            0x00, 0x00, 0x00, 0x00, 0x2c, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x01, 0x00, 0x00,
                            0x02, 0x02, 0x44, 0x01, 0x00, 0x3b
                        };
                        return new WebResourceResponse("image/gif", "binary", new java.io.ByteArrayInputStream(transparent1x1Gif));
                    }
                    // 2. Bloqueo de streaming de video y audio en publicidad
                    if (u.contains(".mp4") || u.contains(".webm") || u.contains(".m4v") ||
                        u.contains(".avi") || u.contains(".flv") || u.contains(".m3u8") ||
                        u.contains(".ts") || u.contains(".mov") || u.contains(".ogv") ||
                        u.contains(".mp3") || u.contains(".wav") || u.contains(".ogg") ||
                        u.contains("googlevideo.com") || u.contains("/videoplayback") ||
                        u.contains("youtube.com/embed") || u.contains("vimeo.com")) {
                        return new WebResourceResponse("text/plain", "utf-8", new java.io.ByteArrayInputStream(new byte[0]));
                    }
                    // 3. Bloqueo de tipografias web externas pesadas (usar fuentes del sistema)
                    if (u.endsWith(".woff2") || u.endsWith(".woff") || u.endsWith(".ttf") || u.contains("fonts.gstatic.com")) {
                        return new WebResourceResponse("text/plain", "utf-8", new java.io.ByteArrayInputStream(new byte[0]));
                    }
                    // 4. Bloqueo de descargas de instaladores o archivos pesados
                    if (u.endsWith(".apk") || u.endsWith(".zip") || u.endsWith(".exe") || u.endsWith(".dmg") || u.endsWith(".rar")) {
                        return new WebResourceResponse("text/plain", "utf-8", new java.io.ByteArrayInputStream(new byte[0]));
                    }
                    // 5. Bloqueo de Bootstrap CSS y JS en el bot (ahorro masivo de ~300 KB por visita)
                    if (u.contains("bootstrap")) {
                        if (u.contains(".css")) {
                            return new WebResourceResponse("text/css", "utf-8", new java.io.ByteArrayInputStream(new byte[0]));
                        } else {
                            return new WebResourceResponse("application/javascript", "utf-8", new java.io.ByteArrayInputStream(new byte[0]));
                        }
                    }
                    // 6. Bloqueo de fuentes externas y estilos no esenciales
                    if (u.contains("fonts.googleapis.com") || u.contains("fonts.gstatic.com")) {
                        return new WebResourceResponse("text/css", "utf-8", new java.io.ByteArrayInputStream(new byte[0]));
                    }
                    // 7. Bloqueo de favicon y telemetria residual innecesaria
                    if (u.contains("favicon.ico")) {
                        return new WebResourceResponse("image/x-icon", "binary", new java.io.ByteArrayInputStream(new byte[0]));
                    }
                    if (u.contains("google-analytics.com") || u.contains("analytics.google.com") || u.contains("googletagmanager.com")) {
                        return new WebResourceResponse("text/plain", "utf-8", new java.io.ByteArrayInputStream(new byte[0]));
                    }
                    // 8. Bloqueo de scripts de Monetag (106 KB que generan $0)
                    if (u.contains("quge5.com") || u.contains("monetag") || u.contains("alwingulla.com")) {
                        return new WebResourceResponse("application/javascript", "utf-8", new java.io.ByteArrayInputStream(new byte[0]));
                    }
                }
                return super.shouldInterceptRequest(view, request);
            }

            @Override
            public void onPageFinished(final WebView view, String url) {
                super.onPageFinished(view, url);
                log("✔ Página cargada: " + url);
                view.evaluateJavascript(
                        "window.scrollTo({top: Math.floor(Math.random()*450)+100, behavior: 'smooth'});",
                        null
                );
            }
        });

        root.addView(webView);
        setContentView(root);

        log("App iniciada. Destino actual: " + getCurrentTargetBase());
        updatePermisoButtonState();
        checkPublicIp(false);
    }

    private String getCurrentTargetBase() {
        String raw = etTargetUrl != null ? etTargetUrl.getText().toString().trim() : DEFAULT_TARGET_URL;
        if (raw.isEmpty()) {
            raw = DEFAULT_TARGET_URL;
        }
        if (!raw.startsWith("http://") && !raw.startsWith("https://")) {
            raw = "https://" + raw;
        }
        while (raw.endsWith("/") && raw.length() > 8) {
            raw = raw.substring(0, raw.length() - 1);
        }
        return raw;
    }

    private void saveCurrentTargetUrl() {
        String clean = getCurrentTargetBase();
        if (etTargetUrl != null) etTargetUrl.setText(clean);
        SharedPreferences prefs = getSharedPreferences(PREFS_NAME, MODE_PRIVATE);
        prefs.edit().putString(KEY_CUSTOM_URL, clean).apply();
    }

    private void updatePermisoButtonState() {
        if (btnPermisoSinPc == null) return;
        if (AirplaneAccessibilityService.isReady()) {
            btnPermisoSinPc.setText("✔ MODO AVIÓN PERMANENTE SIN PC: ACTIVO");
            btnPermisoSinPc.setBackgroundColor(Color.parseColor("#059669"));
        } else {
            btnPermisoSinPc.setText("⚙ ACTIVAR MODO AVIÓN PERMANENTE (SIN PC AL REINICIAR)");
            btnPermisoSinPc.setBackgroundColor(Color.parseColor("#475569"));
        }
    }

    private void log(final String msg) {
        Log.i("CFBot", msg);
        handler.post(new Runnable() {
            @Override
            public void run() {
                String time = new SimpleDateFormat("HH:mm:ss", Locale.getDefault()).format(new Date());
                tvLog.append("[" + time + "] " + msg + "\n");
                scrollLog.post(new Runnable() {
                    @Override
                    public void run() {
                        scrollLog.fullScroll(View.FOCUS_DOWN);
                    }
                });
            }
        });
    }

    private void simulateHardwareTouch(WebView view, float relX, float relY) {
        try {
            int w = view.getWidth();
            int h = view.getHeight();
            if (w <= 0 || h <= 0) return;
            float x = w * relX + (random.nextInt(40) - 20);
            float y = h * relY + (random.nextInt(40) - 20);
            long downTime = android.os.SystemClock.uptimeMillis();
            long eventTime = downTime + 65;
            android.view.MotionEvent downEvt = android.view.MotionEvent.obtain(
                    downTime, downTime, android.view.MotionEvent.ACTION_DOWN, x, y, 0);
            android.view.MotionEvent upEvt = android.view.MotionEvent.obtain(
                    downTime, eventTime, android.view.MotionEvent.ACTION_UP, x, y, 0);
            view.dispatchTouchEvent(downEvt);
            view.dispatchTouchEvent(upEvt);
            downEvt.recycle();
            upEvt.recycle();
            log("👆 Interacción táctil en anuncio/página ejecutada");
        } catch (Exception ignored) {
        }
    }

    private void toggleBot() {
        isRunning = !isRunning;
        if (isRunning) {
            btnToggleAuto.setText("⏹ DETENER BOT");
            btnToggleAuto.setBackgroundColor(Color.parseColor("#ef4444"));
            tvStatus.setText("ESTADO: EJECUTANDO VISITAS...");
            tvStatus.setTextColor(Color.parseColor("#34d399"));
            log("Bot iniciado hacia: " + getCurrentTargetBase());
            runNextCycle();
        } else {
            btnToggleAuto.setText("▶ INICIAR BOT AUTOMÁTICO");
            btnToggleAuto.setBackgroundColor(Color.parseColor("#10b981"));
            tvStatus.setText("ESTADO: PAUSADO");
            tvStatus.setTextColor(Color.parseColor("#fde047"));
            handler.removeCallbacksAndMessages(null);
            isVisiting = false;
            log("Bot detenido por el usuario.");
        }
    }

    private boolean rotateViaLocalDaemon() {
        java.net.Socket socket = null;
        com.tananaev.adblib.AdbConnection connection = null;
        try {
            socket = new java.net.Socket("127.0.0.1", 5555);
            com.tananaev.adblib.AdbBase64 base64 = new com.tananaev.adblib.AdbBase64() {
                @Override
                public String encodeToString(byte[] data) {
                    return android.util.Base64.encodeToString(data, android.util.Base64.NO_WRAP);
                }
            };

            java.io.File privFile = new java.io.File(getFilesDir(), "adbkey");
            java.io.File pubFile = new java.io.File(getFilesDir(), "adbkey.pub");
            com.tananaev.adblib.AdbCrypto crypto;
            if (privFile.exists() && pubFile.exists()) {
                crypto = com.tananaev.adblib.AdbCrypto.loadAdbKeyPair(base64, privFile, pubFile);
            } else {
                crypto = com.tananaev.adblib.AdbCrypto.generateAdbKeyPair(base64);
                crypto.saveAdbKeyPair(privFile, pubFile);
            }

            connection = com.tananaev.adblib.AdbConnection.create(socket, crypto);
            connection.connect();

            com.tananaev.adblib.AdbStream stream = connection.open("shell:cmd connectivity airplane-mode enable; sleep 4; cmd connectivity airplane-mode disable; svc wifi disable; svc data enable; echo DONE");
            try {
                while (!stream.isClosed()) {
                    byte[] bytes = stream.read();
                    if (bytes != null) {
                        String out = new String(bytes);
                        if (out.contains("DONE")) {
                            break;
                        }
                    }
                }
            } catch (Exception ignored) {
            }
            connection.close();
            socket.close();
            return true;
        } catch (Exception e) {
            try { if (connection != null) connection.close(); } catch (Exception ignored) {}
            try { if (socket != null) socket.close(); } catch (Exception ignored) {}
            return false;
        }
    }

    private void triggerIpRotation() {
        log("Activando y desactivando Modo Avión 100% automático...");
        new Thread(new Runnable() {
            @Override
            public void run() {
                boolean success = rotateViaLocalDaemon();
                if (success) {
                    log("✈ Modo Avión ON -> OFF completado solo (ADB). Reconectando 4G...");
                    try { Thread.sleep(5000); } catch (Exception ignored) {}
                    checkPublicIp(true);
                } else if (AirplaneAccessibilityService.isReady()) {
                    log("✈ Rotando Modo Avión vía Permiso Permanente (Sin PC)...");
                    handler.post(new Runnable() {
                        @Override
                        public void run() {
                            AirplaneAccessibilityService.instance.toggleAirplaneModeStandalone(new AirplaneAccessibilityService.OnToggleCompleteListener() {
                                @Override
                                public void onComplete(boolean ok) {
                                    if (ok) {
                                        log("✔ Modo Avión completado (ON -> OFF). Reconectando 4G...");
                                    } else {
                                        log("⚠ Modo Avión finalizado. Verificando señal 4G...");
                                    }
                                    handler.postDelayed(new Runnable() {
                                        @Override
                                        public void run() {
                                            checkPublicIp(true);
                                        }
                                    }, 4000);
                                }
                            });
                        }
                    });
                } else {
                    log("Abriendo panel rápido de Modo Avión...");
                    handler.post(new Runnable() {
                        @Override
                        public void run() {
                            try {
                                Intent intent = new Intent(Settings.ACTION_WIRELESS_SETTINGS);
                                startActivity(intent);
                            } catch (Exception e) {
                                Intent intent = new Intent(Settings.ACTION_AIRPLANE_MODE_SETTINGS);
                                startActivity(intent);
                            }
                        }
                    });
                }
            }
        }).start();
    }

    @Override
    protected void onResume() {
        super.onResume();
        updatePermisoButtonState();
        checkPublicIp(false);
    }

    private void checkPublicIp(final boolean launchVisitAfter) {
        new Thread(new Runnable() {
            @Override
            public void run() {
                String detectedIp = null;
                // 1. Intentar endpoint interno ultraliviano (12 bytes sin overhead TLS externo)
                try {
                    URL url = new URL("https://criteriofinanciero.onrender.com/api/ip");
                    HttpURLConnection conn = (HttpURLConnection) url.openConnection();
                    conn.setConnectTimeout(3500);
                    conn.setReadTimeout(3500);
                    BufferedReader in = new BufferedReader(new InputStreamReader(conn.getInputStream()));
                    String line = in.readLine();
                    in.close();
                    if (line != null && !line.trim().isEmpty() && line.contains(".")) {
                        detectedIp = line.trim();
                    }
                } catch (Exception ignored) {}

                // 2. Fallback a ipify si el servidor estuviera reconectando
                if (detectedIp == null) {
                    try {
                        URL url = new URL("https://api.ipify.org");
                        HttpURLConnection conn = (HttpURLConnection) url.openConnection();
                        conn.setConnectTimeout(5000);
                        conn.setReadTimeout(5000);
                        BufferedReader in = new BufferedReader(new InputStreamReader(conn.getInputStream()));
                        String line = in.readLine();
                        in.close();
                        if (line != null && !line.trim().isEmpty()) {
                            detectedIp = line.trim();
                        }
                    } catch (Exception ignored) {}
                }

                final String ip = detectedIp;
                if (ip != null && !ip.isEmpty()) {
                    final boolean changed = !ip.equals(lastIp);
                    lastIp = ip;
                    handler.post(new Runnable() {
                        @Override
                        public void run() {
                            tvIp.setText("IP Pública 4G actual: " + ip);
                            if (changed) {
                                log("★ Nueva IP detectada: " + ip);
                                // Limpieza de cookies exclusivamente cuando cambia la IP
                                CookieManager.getInstance().removeAllCookies(null);
                                WebStorage.getInstance().deleteAllData();
                            }
                            if (launchVisitAfter && isRunning) {
                                performOrganicVisit();
                            }
                        }
                    });
                } else {
                    log("Esperando señal de datos móviles 4G...");
                    if (launchVisitAfter && isRunning) {
                        handler.postDelayed(new Runnable() {
                            @Override
                            public void run() {
                                checkPublicIp(true);
                            }
                        }, 4000);
                    }
                }
            }
        }).start();
    }

    private void runNextCycle() {
        if (!isRunning) return;
        checkPublicIp(true);
    }

    private void performOrganicVisit() {
        if (!isRunning || isVisiting) return;
        isVisiting = true;

        // Preservar cache de estilos, logos y cookies de sesion local para ahorrar datos y evitar re-syncs

        // User-Agent estable mantenido para preservar cache HTTP y ahorrar datos

        final String base = getCurrentTargetBase();
        String path = PATHS[random.nextInt(PATHS.length)];
        String fullUrl = base.contains("criteriofinanciero") ? (base + path) : base;

        visitCount++;
        tvVisitsCount.setText("Visitas enviadas en esta sesión: " + visitCount);
        log("Visita #" + visitCount + " (IP " + lastIp + ") -> " + fullUrl);

        Map<String, String> dataSaverHeaders = new HashMap<>();
        dataSaverHeaders.put("Save-Data", "on");
        webView.loadUrl(fullUrl, dataSaverHeaders);

        // A los 6s: scroll suave en el contenido del artículo
        handler.postDelayed(new Runnable() {
            @Override
            public void run() {
                if (!isRunning) return;
                webView.evaluateJavascript("window.scrollBy({top: Math.floor(Math.random()*400)+200, behavior: 'smooth'});", null);
            }
        }, 6000);

        // A los 12s: toque táctil orgánico en zona neutral
        handler.postDelayed(new Runnable() {
            @Override
            public void run() {
                if (!isRunning) return;
                simulateHardwareTouch(webView, 0.35f, 0.45f);
            }
        }, 12000);

        // A los 20s: scroll adicional hacia el desarrollo del artículo
        handler.postDelayed(new Runnable() {
            @Override
            public void run() {
                if (!isRunning) return;
                webView.evaluateJavascript("window.scrollBy({top: Math.floor(Math.random()*350)+200, behavior: 'smooth'});", null);
            }
        }, 20000);

        // A los 26s: segundo toque táctil orgánico en zona neutral
        handler.postDelayed(new Runnable() {
            @Override
            public void run() {
                if (!isRunning) return;
                simulateHardwareTouch(webView, 0.65f, 0.55f);
            }
        }, 26000);

        // A los 32.5s: fin de permanencia y rotación de IP (cadencia optimizada a ~85-90 v/h para consumo ultrabajo ~14-16 MB/h)
        handler.postDelayed(new Runnable() {
            @Override
            public void run() {
                if (!isRunning) return;
                rotateAndContinue();
            }
        }, 32500);
    }

    private void rotateAndContinue() {
        log("Fin de lectura. Rotando IP automáticamente (Modo Avión ON -> OFF)...");
        new Thread(new Runnable() {
            @Override
            public void run() {
                boolean autoRotated = rotateViaLocalDaemon();
                if (autoRotated) {
                    log("✈ Modo Avión desactivado solo (ADB). Esperando señal 4G...");
                    try { Thread.sleep(5500); } catch (Exception ignored) {}
                    handler.post(new Runnable() {
                        @Override
                        public void run() {
                            if (!isRunning) return;
                            isVisiting = false;

                            if (!isRunning) return;
                            runNextCycle();
                        }
                    });
                } else if (AirplaneAccessibilityService.isReady()) {
                    log("✈ Rotando Modo Avión vía Permiso Permanente (Sin PC)...");
                    handler.post(new Runnable() {
                        @Override
                        public void run() {
                            AirplaneAccessibilityService.instance.toggleAirplaneModeStandalone(new AirplaneAccessibilityService.OnToggleCompleteListener() {
                                @Override
                                public void onComplete(boolean ok) {
                                    if (ok) {
                                        log("✔ Modo Avión completado (ON -> OFF). Reconectando 4G...");
                                    } else {
                                        log("⚠ Modo Avión finalizado. Verificando señal 4G...");
                                    }
                                    handler.postDelayed(new Runnable() {
                                        @Override
                                        public void run() {
                                            if (!isRunning) return;
                                            isVisiting = false;

                                            if (!isRunning) return;
                                            runNextCycle();
                                        }
                                    }, 3200);
                                }
                            });
                        }
                    });
                } else {
                    handler.post(new Runnable() {
                        @Override
                        public void run() {
                            if (!isRunning) return;
                            isVisiting = false;

                            if (!isRunning) return;
                            runNextCycle();
                        }
                    });
                }
            }
        }).start();
    }
}
