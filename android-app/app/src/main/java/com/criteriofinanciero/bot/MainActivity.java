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
import android.view.Gravity;
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
            "/calculadoras",
            "/mercados",
            "/calculadoras/interes-compuesto",
            "/calculadoras/rendimiento-billeteras",
            "/calculadoras/conversor-dolar",
            "/articulo/como-invertir-en-cedears-argentina-guia-paso-a-paso",
            "/articulo/mejores-brokers-argentina-comparativa-comisiones",
            "/articulo/que-billetera-virtual-paga-mas-tasa-argentina",
            "/articulo/como-comprar-dolar-mep-home-banking-sin-cepo",
            "/articulo/dolar-cripto-como-comprar-usdt-pesos-argentinos",
            "/articulo/fondos-comunes-inversion-fci-guia-completa",
            "/articulo/resena-completa-balanz-capital-opiniones-comisiones",
            "/articulo/invertironline-iol-analisis-cuenta-remunerada-costos",
            "/articulo/como-salir-de-deudas-tarjeta-credito-metodo-bola-nieve",
            "/articulo/staking-criptomonedas-rendimientos-en-dolares-pasivos",
            "/articulo/bienes-personales-inversiones-exentas-argentina-2026",
            "/articulo/lemon-cash-vs-belo-vs-buenbit-mejor-tarjeta-cripto",
            "/articulo/bonos-soberanos-al30-gd30-como-operar-calcular-tir",
            "/articulo/obligaciones-negociables-como-cobrar-renta-en-dolares",
            "/articulo/calculadora-inflacion-perdida-poder-adquisitivo",
            "/articulo/plazo-fijo-tradicional-vs-plazo-fijo-uva-cual-conviene-2026",
            "/articulo/como-enviar-dolares-exterior-argentina-metodos-legales",
            "/articulo/cuenta-bancaria-en-usa-desde-argentina-abrir-online",
            "/articulo/brecha-cambiaria-explicada-oficial-mep-ccl-blue",
            "/articulo/7-errores-mas-comunes-al-empezar-a-invertir-evitarlos"
    };

    private static final String[] USER_AGENTS = new String[]{
            "Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
            "Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Mobile Safari/537.36",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (Linux; Android 13; motorola edge 40) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Mobile Safari/537.36",
            "Mozilla/5.0 (Linux; Android 14; SM-A546E) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36"
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

        View spacer = new View(this);
        spacer.setMinimumHeight(18);
        btnRow.addView(spacer);

        btnAirplaneQuick = new Button(this);
        btnAirplaneQuick.setText("✈ CAMBIAR IP (MODO AVIÓN / AUTO)");
        btnAirplaneQuick.setBackgroundColor(Color.parseColor("#3b82f6"));
        btnAirplaneQuick.setTextColor(Color.WHITE);
        btnAirplaneQuick.setTypeface(null, Typeface.BOLD);
        btnAirplaneQuick.setPadding(20, 24, 20, 24);
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

        // Visor Web en Vivo (Muestra la navegación real y ejecuta el beacon JS)
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
        ws.setCacheMode(WebSettings.LOAD_NO_CACHE);

        webView.setWebViewClient(new WebViewClient() {
            @Override
            public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                return false;
            }

            @Override
            public void onPageFinished(WebView view, String url) {
                super.onPageFinished(view, url);
                log("✔ Página cargada: " + url.replace(TARGET_BASE, ""));
                // Simular scroll humano y enviar telemetría biométrica
                view.evaluateJavascript(
                        "window.scrollTo({top: Math.floor(Math.random()*900)+200, behavior: 'smooth'});",
                        null
                );
            }
        });

        root.addView(webView);
        setContentView(root);

        log("App iniciada. Destino: " + TARGET_BASE);
        checkPublicIp(false);
    }

    private void log(final String msg) {
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
        try {
            java.net.Socket socket = new java.net.Socket("127.0.0.1", 38291);
            socket.setSoTimeout(12000);
            BufferedReader reader = new BufferedReader(new InputStreamReader(socket.getInputStream()));
            String resp = reader.readLine();
            socket.close();
            return resp != null && resp.contains("OK");
        } catch (Exception e) {
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
        // Cada vez que vuelve del panel de Modo Avión, verifica la nueva IP 4G y lanza visita
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

        // Limpiar cookies y sesión para que cuente como visitante 100% nuevo
        CookieManager.getInstance().removeAllCookies(null);
        webView.clearCache(true);

        // Elegir User-Agent móvil aleatorio
        String ua = USER_AGENTS[random.nextInt(USER_AGENTS.length)];
        webView.getSettings().setUserAgentString(ua);

        // Elegir página inicial (Portada o Guía directa)
        String path = PATHS[random.nextInt(PATHS.length)];
        String fullUrl = TARGET_BASE + path;

        visitCount++;
        tvVisitsCount.setText("Visitas enviadas en esta sesión: " + visitCount);
        log("Visitas #" + visitCount + " (IP " + lastIp + ") -> " + path);

        webView.loadUrl(fullUrl);

        // Navegar a una segunda guía interna a los 12 segundos (simula usuario leyendo 2 páginas)
        handler.postDelayed(new Runnable() {
            @Override
            public void run() {
                if (!isRunning) return;
                String secondPath = PATHS[8 + random.nextInt(PATHS.length - 8)];
                log("↳ Leyendo guía interna: " + secondPath);
                webView.loadUrl(TARGET_BASE + secondPath);
            }
        }, 12000);

        // Programar rotación automática de IP y siguiente visita a los 26 segundos
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
                }
                handler.post(new Runnable() {
                    @Override
                    public void run() {
                        if (!isRunning) return;
                        runNextCycle();
                    }
                });
            }
        }).start();
    }
}
