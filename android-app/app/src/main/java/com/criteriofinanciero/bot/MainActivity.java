package com.criteriofinanciero.bot;

import android.app.Activity;
import android.content.Intent;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.provider.Settings;
import android.view.View;
import android.webkit.CookieManager;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;
import java.util.Random;

public class MainActivity extends Activity {

    private static final String TARGET_BASE = "https://criteriofinanciero.onrender.com";

    private static final String[] PATHS = new String[]{
            "/",
            "/guias",
            "/comparativas",
            "/mercados",
            "/calculadoras",
            "/calculadoras/interes-compuesto",
            "/calculadoras/rendimiento-billeteras",
            "/calculadoras/conversor-dolar",
            "/articulo/como-invertir-en-cedears-argentina-guia-paso-a-paso",
            "/articulo/como-comprar-dolar-mep-home-banking-sin-limites",
            "/articulo/billeteras-virtuales-que-mas-pagan-argentina-comparativa",
            "/articulo/mejores-brokers-argentina-comparativa-comisiones",
            "/articulo/que-son-las-lecaps-y-como-invertir-tasa-fija",
            "/articulo/impuesto-bienes-personales-ganancias-inversiones-argentina",
            "/articulo/obligaciones-negociables-on-como-cobrar-renta-en-dolares",
            "/articulo/fondos-comunes-de-inversion-fci-money-market-vs-t1",
            "/articulo/lemon-cash-vs-belo-vs-buenbit-mejor-tarjeta-cripto",
            "/articulo/cauciones-bursatiles-el-plazo-fijo-de-la-bolsa",
            "/articulo/bonos-soberanos-al30-y-gd30-analisis-riesgo-pais",
            "/articulo/como-armar-cartera-de-retiro-dividendos-sp500"
    };

    private static final String[] USER_AGENTS = new String[]{
            "Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.6613.127 Mobile Safari/537.36",
            "Mozilla/5.0 (Linux; Android 13; SM-A546E) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.6533.103 Mobile Safari/537.36",
            "Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.6668.70 Mobile Safari/537.36",
            "Mozilla/5.0 (Linux; Android 13; motorola edge 40) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.6478.122 Mobile Safari/537.36",
            "Mozilla/5.0 (Linux; Android 14; Redmi Note 13 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.6613.88 Mobile Safari/537.36",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Mobile/15E148 Safari/604.1"
    };

    private TextView tvStatus;
    private TextView tvIp;
    private TextView tvVisitsCount;
    private TextView tvLog;
    private ScrollView scrollLog;
    private WebView webView;
    private Button btnToggleAuto;
    private Button btnAirplaneQuick;

    private boolean isRunning = false;
    private int visitCount = 0;
    private String lastIp = "Detectando...";
    private final Handler handler = new Handler(Looper.getMainLooper());
    private final Random random = new Random();

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        getWindow().addFlags(android.view.WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);

        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setBackgroundColor(Color.parseColor("#070d19"));
        root.setPadding(36, 48, 36, 36);

        // Header
        TextView title = new TextView(this);
        title.setText("Criterio Financiero — Bot Mobile");
        title.setTextColor(Color.WHITE);
        title.setTextSize(20f);
        title.setTypeface(null, Typeface.BOLD);
        root.addView(title);

        TextView subtitle = new TextView(this);
        subtitle.setText("Generador de Tráfico 4G Real & Rotación de IP");
        subtitle.setTextColor(Color.parseColor("#10b981"));
        subtitle.setTextSize(13f);
        subtitle.setPadding(0, 4, 0, 24);
        root.addView(subtitle);

        // Card de Métricas
        LinearLayout card = new LinearLayout(this);
        card.setOrientation(LinearLayout.VERTICAL);
        GradientDrawable cardBg = new GradientDrawable();
        cardBg.setColor(Color.parseColor("#0f1a2e"));
        cardBg.setCornerRadius(24f);
        cardBg.setStroke(2, Color.parseColor("#1f3358"));
        card.setBackground(cardBg);
        card.setPadding(32, 28, 32, 28);

        tvStatus = new TextView(this);
        tvStatus.setText("ESTADO: DETENIDO");
        tvStatus.setTextColor(Color.parseColor("#fde047"));
        tvStatus.setTextSize(14f);
        tvStatus.setTypeface(null, Typeface.BOLD);
        card.addView(tvStatus);

        tvIp = new TextView(this);
        tvIp.setText("IP Pública 4G actual: Consultando...");
        tvIp.setTextColor(Color.parseColor("#f1f5f9"));
        tvIp.setTextSize(15f);
        tvIp.setPadding(0, 12, 0, 6);
        card.addView(tvIp);

        tvVisitsCount = new TextView(this);
        tvVisitsCount.setText("Visitas enviadas en esta sesión: 0");
        tvVisitsCount.setTextColor(Color.parseColor("#34d399"));
        tvVisitsCount.setTextSize(15f);
        tvVisitsCount.setTypeface(null, Typeface.BOLD);
        card.addView(tvVisitsCount);

        root.addView(card);

        // Botones de Control
        LinearLayout btnRow = new LinearLayout(this);
        btnRow.setOrientation(LinearLayout.VERTICAL);
        btnRow.setPadding(0, 24, 0, 16);

        btnToggleAuto = new Button(this);
        btnToggleAuto.setText("▶ INICIAR BOT AUTOMÁTICO");
        btnToggleAuto.setBackgroundColor(Color.parseColor("#10b981"));
        btnToggleAuto.setTextColor(Color.WHITE);
        btnToggleAuto.setTypeface(null, Typeface.BOLD);
        btnToggleAuto.setPadding(20, 28, 20, 28);
        btnToggleAuto.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                toggleBot();
            }
        });
        btnRow.addView(btnToggleAuto);

        btnAirplaneQuick = new Button(this);
        btnAirplaneQuick.setText("✈ CAMBIAR IP AHORA (MODO AVIÓN AUTO)");
        btnAirplaneQuick.setBackgroundColor(Color.parseColor("#3b82f6"));
        btnAirplaneQuick.setTextColor(Color.WHITE);
        btnAirplaneQuick.setTypeface(null, Typeface.BOLD);
        btnAirplaneQuick.setPadding(20, 22, 20, 22);
        LinearLayout.LayoutParams btnAirParams = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT);
        btnAirParams.topMargin = 20;
        btnAirplaneQuick.setLayoutParams(btnAirParams);
        btnAirplaneQuick.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                triggerIpRotation();
            }
        });
        btnRow.addView(btnAirplaneQuick);

        root.addView(btnRow);

        // Consola de Log
        TextView logHeader = new TextView(this);
        logHeader.setText("Registro de Actividad en Vivo:");
        logHeader.setTextColor(Color.parseColor("#cbd5e1"));
        logHeader.setTextSize(12f);
        logHeader.setPadding(0, 8, 0, 8);
        root.addView(logHeader);

        scrollLog = new ScrollView(this);
        LinearLayout.LayoutParams scrollParams = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, 360);
        scrollLog.setLayoutParams(scrollParams);
        scrollLog.setBackgroundColor(Color.parseColor("#030710"));
        scrollLog.setPadding(20, 16, 20, 16);

        tvLog = new TextView(this);
        tvLog.setTextColor(Color.parseColor("#e2e8f0"));
        tvLog.setTextSize(11.5f);
        tvLog.setTypeface(Typeface.MONOSPACE);
        scrollLog.addView(tvLog);
        root.addView(scrollLog);

        // Visor Web en Vivo
        TextView webHeader = new TextView(this);
        webHeader.setText("Visor de Navegación Orgánica (Criterio Financiero):");
        webHeader.setTextColor(Color.parseColor("#cbd5e1"));
        webHeader.setTextSize(12f);
        webHeader.setPadding(0, 16, 0, 8);
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
        ws.setCacheMode(WebSettings.LOAD_NO_CACHE);

        webView.setWebViewClient(new WebViewClient() {
            @Override
            public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                return false;
            }

            @Override
            public void onPageFinished(final WebView view, String url) {
                super.onPageFinished(view, url);
                log("✔ Página cargada: " + url.replace(TARGET_BASE, ""));
                view.evaluateJavascript(
                        "window.scrollTo({top: Math.floor(Math.random()*500)+120, behavior: 'smooth'});",
                        null
                );
                handler.postDelayed(new Runnable() {
                    @Override
                    public void run() {
                        if (!isRunning) return;
                        simulateHardwareTouch(view, 0.5f, 0.35f);
                    }
                }, 3200);
                handler.postDelayed(new Runnable() {
                    @Override
                    public void run() {
                        if (!isRunning) return;
                        simulateHardwareTouch(view, 0.5f, 0.55f);
                    }
                }, 7000);
            }
        });

        root.addView(webView);
        setContentView(root);

        log("App iniciada. Destino: " + TARGET_BASE);
        checkPublicIp(false);
    }

    private void log(final String msg) {
        android.util.Log.i("CFBot", msg);
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
            log("Bot iniciado. Ejecutando ciclo de visitas...");
            runNextCycle();
        } else {
            btnToggleAuto.setText("▶ INICIAR BOT AUTOMÁTICO");
            btnToggleAuto.setBackgroundColor(Color.parseColor("#10b981"));
            tvStatus.setText("ESTADO: PAUSADO");
            tvStatus.setTextColor(Color.parseColor("#fde047"));
            handler.removeCallbacksAndMessages(null);
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
                    log("✈ Modo Avión ON -> OFF completado solo. Reconectando 4G...");
                    try { Thread.sleep(5000); } catch (Exception ignored) {}
                    checkPublicIp(true);
                } else if (AirplaneAccessibilityService.isReady()) {
                    log("✈ Rotando Modo Avión vía Permiso Permanente (Sin PC)...");
                    handler.post(new Runnable() {
                        @Override
                        public void run() {
                            AirplaneAccessibilityService.instance.toggleAirplaneModeStandalone(new AirplaneAccessibilityService.OnToggleCompleteListener() {
                                @Override
                                public void onComplete(boolean success) {
                                    if (success) {
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
                                Intent intent = new Intent(Settings.ACTION_AIRPLANE_MODE_SETTINGS);
                                startActivity(intent);
                            } catch (Exception e) {
                                Intent intent = new Intent(Settings.ACTION_WIRELESS_SETTINGS);
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
        checkPublicIp(isRunning);
    }

    private void checkPublicIp(final boolean launchVisitAfter) {
        new Thread(new Runnable() {
            @Override
            public void run() {
                try {
                    URL url = new URL("https://api.ipify.org");
                    HttpURLConnection conn = (HttpURLConnection) url.openConnection();
                    conn.setConnectTimeout(6000);
                    conn.setReadTimeout(6000);
                    BufferedReader in = new BufferedReader(new InputStreamReader(conn.getInputStream()));
                    final String ip = in.readLine();
                    in.close();
                    if (ip != null && !ip.isEmpty()) {
                        final boolean changed = !ip.equals(lastIp);
                        lastIp = ip;
                        handler.post(new Runnable() {
                            @Override
                            public void run() {
                                tvIp.setText("IP Pública 4G actual: " + ip);
                                if (changed) {
                                    log("★ Nueva IP detectada: " + ip);
                                }
                                if (launchVisitAfter && isRunning) {
                                    performOrganicVisit();
                                }
                            }
                        });
                    }
                } catch (Exception e) {
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
        if (!isRunning) return;

        CookieManager.getInstance().removeAllCookies(null);
        webView.clearCache(true);

        String ua = USER_AGENTS[random.nextInt(USER_AGENTS.length)];
        webView.getSettings().setUserAgentString(ua);

        String path = PATHS[random.nextInt(PATHS.length)];
        String fullUrl = TARGET_BASE + path;

        visitCount++;
        tvVisitsCount.setText("Visitas enviadas en esta sesión: " + visitCount);
        log("Visitas #" + visitCount + " (IP " + lastIp + ") -> " + path);

        webView.loadUrl(fullUrl);

        handler.postDelayed(new Runnable() {
            @Override
            public void run() {
                if (!isRunning) return;
                String secondPath = PATHS[8 + random.nextInt(PATHS.length - 8)];
                log("↳ Leyendo guía interna: " + secondPath);
                webView.loadUrl(TARGET_BASE + secondPath);
            }
        }, 12000);

        handler.postDelayed(new Runnable() {
            @Override
            public void run() {
                if (!isRunning) return;
                rotateAndContinue();
            }
        }, 26000);
    }

    private void rotateAndContinue() {
        log("Fin de lectura. Rotando IP automáticamente (Modo Avión ON -> OFF)...");
        new Thread(new Runnable() {
            @Override
            public void run() {
                boolean autoRotated = rotateViaLocalDaemon();
                if (autoRotated) {
                    log("✈ Modo Avión desactivado solo. Esperando señal 4G...");
                    try { Thread.sleep(5500); } catch (Exception ignored) {}
                    handler.post(new Runnable() {
                        @Override
                        public void run() {
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
                                public void onComplete(boolean success) {
                                    if (success) {
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
                    handler.post(new Runnable() {
                        @Override
                        public void run() {
                            if (!isRunning) return;
                            runNextCycle();
                        }
                    });
                }
            }
        }).start();
    }
}
