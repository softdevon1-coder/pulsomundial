package com.criteriofinanciero.botwifi;



import android.app.Activity;

import android.content.Context;

import android.content.SharedPreferences;

import android.graphics.Color;

import android.graphics.Typeface;

import android.graphics.drawable.GradientDrawable;

import android.net.ConnectivityManager;

import android.net.NetworkCapabilities;

import android.os.Bundle;

import android.os.Handler;

import android.os.Looper;
import android.os.Message;
import android.webkit.WebChromeClient;

import android.text.InputType;

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

import android.widget.ArrayAdapter;

import android.widget.Button;

import android.widget.CheckBox;

import android.widget.CompoundButton;

import android.widget.EditText;

import android.widget.LinearLayout;

import android.widget.ScrollView;

import android.widget.Spinner;

import android.widget.TextView;



import java.io.BufferedReader;

import java.io.ByteArrayInputStream;

import java.io.InputStreamReader;

import java.net.HttpURLConnection;

import java.net.URL;

import java.text.SimpleDateFormat;

import java.util.Date;

import java.util.Locale;

import java.util.Random;



public class MainActivity extends Activity {



    private static final String DEFAULT_TARGET_URL = "https://criteriofinanciero.onrender.com";

    private static final String PREFS_NAME = "CFBotWiFiPrefs";



    private static final String KEY_TARGET_URL = "target_url";

    private static final String KEY_MODEM_IP = "modem_ip";

    private static final String KEY_MODEM_USER = "modem_user";

    private static final String KEY_MODEM_PASS = "modem_pass";

    private static final String KEY_MODEM_BRAND_POS = "modem_brand_pos";

    private static final String KEY_USE_SMART_PLUG = "use_smart_plug";

    private static final String KEY_SMART_PLUG_URL = "smart_plug_url";



            private static final String[] SEGUROYCREDITO_PATHS = new String[]{
            "/",
            "/seguros-auto",
            "/prestamos-personales",
            "/seguros-hogar",
            "/creditos-hipotecarios",
            "/seguros-vida",
            "/prestamos-monotributo",
            "/calculadora"
    };
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

            "Mozilla/5.0 (Linux; Android 13; SM-S908B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.64 Mobile Safari/537.36",

            "Mozilla/5.0 (Linux; Android 12; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.6167.178 Mobile Safari/537.36",

            "Mozilla/5.0 (Linux; Android 14; SM-A546B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.6312.40 Mobile Safari/537.36",

            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",

            "Mozilla/5.0 (Linux; Android 13; Moto G52) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.144 Mobile Safari/537.36",

            "Mozilla/5.0 (Linux; Android 11; Redmi Note 10) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.6045.163 Mobile Safari/537.36"

    };



    private static final String[] MODEM_BRANDS = new String[]{

            "Movistar HGU (Smart WiFi / Askey / MitraStar)",

            "Huawei (HG8245 / ONT Fibra)",

            "ZTE (F660 / F670 / F680)",

            "Sagemcom (Fast 3890 / 5655)",

            "TP-Link / Genérico"

    };



    private EditText etTargetUrl;

    private EditText etModemIp;

    private EditText etModemUser;

    private EditText etModemPass;

    private Spinner spModemBrand;

    private CheckBox chkUseSmartPlug;

    private LinearLayout layoutModemFields;

    private LinearLayout layoutSmartPlugFields;

    private EditText etSmartPlugUrl;



    private TextView tvStatus;

    private TextView tvIp;

    private TextView tvVisitsCount;

    private Button btnToggleAuto;

    private Button btnRebootNow;

    private TextView tvLog;

    private ScrollView scrollLog;

    private WebView webView;



    private boolean isRunning = false;

    private boolean isVisiting = false;

    private int visitCount = 0;

    private String lastIp = "";

    private final Handler handler = new Handler(Looper.getMainLooper());

    private final Random random = new Random();



    @Override

    protected void onCreate(Bundle savedInstanceState) {

        super.onCreate(savedInstanceState);
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);



        // Contenedor Principal Scrollable

        ScrollView rootScroll = new ScrollView(this);

        rootScroll.setBackgroundColor(Color.parseColor("#070d19"));



        LinearLayout root = new LinearLayout(this);

        root.setOrientation(LinearLayout.VERTICAL);

        root.setPadding(28, 36, 28, 36);

        rootScroll.addView(root);



        // Encabezado

        TextView title = new TextView(this);

        title.setText("CF BOT — MÓDEM & FIBRA ÓPTICA");

        title.setTextColor(Color.parseColor("#38bdf8"));

        title.setTextSize(17f);

        title.setTypeface(null, Typeface.BOLD);

        root.addView(title);



        TextView subTitle = new TextView(this);

        subTitle.setText("Visitas Orgánicas con Rotación WiFi Residencial (Costo 4G = $0)");

        subTitle.setTextColor(Color.parseColor("#94a3b8"));

        subTitle.setTextSize(11.5f);

        subTitle.setPadding(0, 4, 0, 16);

        root.addView(subTitle);



        SharedPreferences prefs = getSharedPreferences(PREFS_NAME, MODE_PRIVATE);



        // 1. URL Destino

        TextView urlLabel = new TextView(this);

        urlLabel.setText("URL de la Página Web Destino:");

        urlLabel.setTextColor(Color.parseColor("#34d399"));

        urlLabel.setTextSize(12f);

        root.addView(urlLabel);



        etTargetUrl = new EditText(this);

        etTargetUrl.setText(prefs.getString(KEY_TARGET_URL, DEFAULT_TARGET_URL));

        etTargetUrl.setTextColor(Color.WHITE);

        etTargetUrl.setTextSize(13f);

        etTargetUrl.setSingleLine(true);

        styleInput(etTargetUrl, "#10b981");

        root.addView(etTargetUrl);



        // 2. Card de Configuración de Rotación (Módem o Enchufe)

        LinearLayout cardConfig = createCard();

        cardConfig.addView(createSectionHeader("CONFIGURACIÓN DE ROTACIÓN DE IP"));



        chkUseSmartPlug = new CheckBox(this);

        chkUseSmartPlug.setText("Usar Enchufe Inteligente WiFi (Smart Plug)");

        chkUseSmartPlug.setTextColor(Color.parseColor("#fde047"));

        chkUseSmartPlug.setTextSize(12.5f);

        chkUseSmartPlug.setChecked(prefs.getBoolean(KEY_USE_SMART_PLUG, false));

        cardConfig.addView(chkUseSmartPlug);



        // Campos Módem

        layoutModemFields = new LinearLayout(this);

        layoutModemFields.setOrientation(LinearLayout.VERTICAL);

        layoutModemFields.setPadding(0, 8, 0, 4);



        TextView lblModemIp = createFieldLabel("Dirección Interna del Módem:");

        layoutModemFields.addView(lblModemIp);

        etModemIp = new EditText(this);

        etModemIp.setText(prefs.getString(KEY_MODEM_IP, "192.168.1.1"));

        etModemIp.setHint("192.168.1.1 o 192.168.0.1");

        styleInput(etModemIp, "#3b82f6");

        layoutModemFields.addView(etModemIp);



        LinearLayout rowCreds = new LinearLayout(this);

        rowCreds.setOrientation(LinearLayout.HORIZONTAL);



        LinearLayout colUser = new LinearLayout(this);

        colUser.setOrientation(LinearLayout.VERTICAL);

        colUser.setLayoutParams(new LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f));

        colUser.addView(createFieldLabel("Usuario Admin:"));

        etModemUser = new EditText(this);

        etModemUser.setText(prefs.getString(KEY_MODEM_USER, "admin"));

        styleInput(etModemUser, "#3b82f6");

        colUser.addView(etModemUser);

        rowCreds.addView(colUser);



        View spacer = new View(this);

        spacer.setLayoutParams(new LinearLayout.LayoutParams(16, 1));

        rowCreds.addView(spacer);



        LinearLayout colPass = new LinearLayout(this);

        colPass.setOrientation(LinearLayout.VERTICAL);

        colPass.setLayoutParams(new LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1.2f));

        colPass.addView(createFieldLabel("Contraseña Admin:"));

        etModemPass = new EditText(this);

        etModemPass.setInputType(InputType.TYPE_CLASS_TEXT | InputType.TYPE_TEXT_VARIATION_PASSWORD);

        etModemPass.setText(prefs.getString(KEY_MODEM_PASS, ""));

        etModemPass.setHint("Clave de la etiqueta");

        styleInput(etModemPass, "#3b82f6");

        colPass.addView(etModemPass);

        rowCreds.addView(colPass);



        layoutModemFields.addView(rowCreds);



        TextView lblBrand = createFieldLabel("Marca o Modelo del Módem:");

        layoutModemFields.addView(lblBrand);

        spModemBrand = new Spinner(this);

        ArrayAdapter<String> brandAdapter = new ArrayAdapter<>(this, android.R.layout.simple_spinner_dropdown_item, MODEM_BRANDS);

        spModemBrand.setAdapter(brandAdapter);

        spModemBrand.setSelection(prefs.getInt(KEY_MODEM_BRAND_POS, 0));

        spModemBrand.setBackgroundColor(Color.parseColor("#0f1a2e"));

        layoutModemFields.addView(spModemBrand);



        cardConfig.addView(layoutModemFields);



        // Campos Enchufe Inteligente

        layoutSmartPlugFields = new LinearLayout(this);

        layoutSmartPlugFields.setOrientation(LinearLayout.VERTICAL);

        layoutSmartPlugFields.setPadding(0, 8, 0, 4);



        TextView lblPlug = createFieldLabel("URL / IP del Enchufe Inteligente:");

        layoutSmartPlugFields.addView(lblPlug);

        etSmartPlugUrl = new EditText(this);

        etSmartPlugUrl.setText(prefs.getString(KEY_SMART_PLUG_URL, "http://192.168.1.150/relay/0?turn=toggle"));

        etSmartPlugUrl.setHint("http://192.168.1.150/relay/0?turn=toggle");

        styleInput(etSmartPlugUrl, "#f59e0b");

        layoutSmartPlugFields.addView(etSmartPlugUrl);



        cardConfig.addView(layoutSmartPlugFields);



        chkUseSmartPlug.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {

            @Override

            public void onCheckedChanged(CompoundButton buttonView, boolean isChecked) {

                updateRotationFieldsVisibility(isChecked);

            }

        });

        updateRotationFieldsVisibility(chkUseSmartPlug.isChecked());



        root.addView(cardConfig);



        // 3. Card de Métricas en Vivo

        LinearLayout cardMetrics = createCard();

        tvStatus = new TextView(this);

        tvStatus.setText("ESTADO: DETENIDO");

        tvStatus.setTextColor(Color.parseColor("#fde047"));

        tvStatus.setTextSize(13f);

        tvStatus.setTypeface(null, Typeface.BOLD);

        cardMetrics.addView(tvStatus);



        tvIp = new TextView(this);

        tvIp.setText("IP Pública WiFi actual: Consultando...");

        tvIp.setTextColor(Color.parseColor("#f1f5f9"));

        tvIp.setTextSize(13.5f);

        tvIp.setPadding(0, 6, 0, 4);

        cardMetrics.addView(tvIp);



        tvVisitsCount = new TextView(this);

        tvVisitsCount.setText("Visitas enviadas en esta sesión: 0");

        tvVisitsCount.setTextColor(Color.parseColor("#34d399"));

        tvVisitsCount.setTextSize(13.5f);

        tvVisitsCount.setTypeface(null, Typeface.BOLD);

        cardMetrics.addView(tvVisitsCount);



        root.addView(cardMetrics);



        // 4. Botones de Control

        LinearLayout btnBox = new LinearLayout(this);

        btnBox.setOrientation(LinearLayout.VERTICAL);

        btnBox.setPadding(0, 14, 0, 10);



        btnToggleAuto = new Button(this);

        btnToggleAuto.setText("▶ INICIAR BOT WIFI");

        btnToggleAuto.setBackgroundColor(Color.parseColor("#10b981"));

        btnToggleAuto.setTextColor(Color.WHITE);

        btnToggleAuto.setTypeface(null, Typeface.BOLD);

        btnToggleAuto.setPadding(16, 20, 16, 20);

        btnToggleAuto.setOnClickListener(new View.OnClickListener() {

            @Override

            public void onClick(View v) {

                saveSettings();

                toggleBot();

            }

        });

        btnBox.addView(btnToggleAuto);



        btnRebootNow = new Button(this);

        btnRebootNow.setText("🔄 REINICIAR MÓDEM / ENCHUFE AHORA");

        btnRebootNow.setBackgroundColor(Color.parseColor("#0284c7"));

        btnRebootNow.setTextColor(Color.WHITE);

        btnRebootNow.setTypeface(null, Typeface.BOLD);

        btnRebootNow.setPadding(16, 16, 16, 16);

        LinearLayout.LayoutParams btnRebootParams = new LinearLayout.LayoutParams(

                LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT);

        btnRebootParams.topMargin = 10;

        btnRebootNow.setLayoutParams(btnRebootParams);

        btnRebootNow.setOnClickListener(new View.OnClickListener() {

            @Override

            public void onClick(View v) {

                saveSettings();

                triggerManualReboot();

            }

        });

        btnBox.addView(btnRebootNow);



        root.addView(btnBox);



        // 5. Consola de Logs

        TextView logHeader = new TextView(this);

        logHeader.setText("Registro de Actividad WiFi:");

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



        // 6. WebView Orgánico

        TextView webHeader = new TextView(this);

        webHeader.setText("Visor de Navegación Orgánica:");

        webHeader.setTextColor(Color.parseColor("#cbd5e1"));

        webHeader.setTextSize(11.5f);

        webHeader.setPadding(0, 10, 0, 6);

        root.addView(webHeader);



        webView = new WebView(this);

        LinearLayout.LayoutParams webParams = new LinearLayout.LayoutParams(

                LinearLayout.LayoutParams.MATCH_PARENT, 450);

        webView.setLayoutParams(webParams);



        WebSettings ws = webView.getSettings();

        ws.setJavaScriptEnabled(true);

        ws.setDomStorageEnabled(true);

        ws.setJavaScriptCanOpenWindowsAutomatically(true);

        ws.setCacheMode(WebSettings.LOAD_DEFAULT);

        ws.setSupportMultipleWindows(true);

        CookieManager.getInstance().setAcceptCookie(true);
        if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.LOLLIPOP) {
            CookieManager.getInstance().setAcceptThirdPartyCookies(webView, true);
        }

        webView.setWebChromeClient(new WebChromeClient() {
            @Override
            public boolean onCreateWindow(WebView view, boolean isDialog, boolean isUserGesture, Message resultMsg) {
                final WebView tempView = new WebView(MainActivity.this);
                WebSettings ts = tempView.getSettings();
                ts.setJavaScriptEnabled(true);
                ts.setDomStorageEnabled(true);
                ts.setDatabaseEnabled(true);
                ts.setUserAgentString(ws.getUserAgentString());
                if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.LOLLIPOP) {
                    CookieManager.getInstance().setAcceptThirdPartyCookies(tempView, true);
                }

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

                    @Override
                    public WebResourceResponse shouldInterceptRequest(WebView view, WebResourceRequest request) {
                        if (request != null && request.getUrl() != null) {
                            String u = request.getUrl().toString().toLowerCase();
                            if (u.contains("abscloud.org") || u.contains("araplhn.org") || u.contains("asiafilm.org") || u.contains("nresystems.com") || u.contains("unfolded-uncle.com") || u.contains("hilltop") || u.contains("surefootedpause.com") || u.contains("zzztrack.com") || u.contains("joviallength.com") || u.contains("criteriofinanciero") || u.contains("seguroycredito") || u.contains("quge5.com") || u.contains("al5sm.com") || u.contains("uplcm.com") || u.contains("rtmark.net") || u.contains("alwingulla.com") || u.contains("3nbf4.com") || u.contains("monetag")) {
                                return super.shouldInterceptRequest(view, request);
                            }
                            handlePopunderUrl(view, u);
                            byte[] emptyHtml = "<!DOCTYPE html><html><head><title>OK</title></head><body></body></html>".getBytes(java.nio.charset.StandardCharsets.UTF_8);
                            return new WebResourceResponse("text/html", "utf-8", 200, "OK", null, new java.io.ByteArrayInputStream(emptyHtml));
                        }
                        return super.shouldInterceptRequest(view, request);
                    }

                    private boolean handlePopunderUrl(final WebView view, String url) {
                        if (url == null) return false;
                        String u = url.toLowerCase();
                        if (u.contains("abscloud.org") || u.contains("araplhn.org") || u.contains("asiafilm.org") || u.contains("nresystems.com") || u.contains("unfolded-uncle.com") || u.contains("hilltop") || u.contains("surefootedpause.com") || u.contains("zzztrack.com") || u.contains("joviallength.com") || u.contains("criteriofinanciero") || u.contains("seguroycredito") || u.contains("quge5.com") || u.contains("al5sm.com") || u.contains("uplcm.com") || u.contains("rtmark.net") || u.contains("alwingulla.com") || u.contains("3nbf4.com") || u.contains("monetag")) {
                            return false;
                        }
                        if (view.getTag() == null) {
                            view.setTag("killed");
                            log("💰 Popunder validado! Manteniendo 2.5s de gracia (landing externa bloqueada a 0 bytes): " + (url.length() > 42 ? url.substring(0, 42) + "..." : url));
                            handler.postDelayed(new Runnable() {
                                @Override
                                public void run() {
                                    try {
                                        view.stopLoading();
                                        view.destroy();
                                    } catch (Exception ignored) {}
                                }
                            }, 2500);
                        }
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

        ws.setUserAgentString("Mozilla/5.0 (Linux; Android 12; moto g52) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Mobile Safari/537.36"); // Device UA estable para preservar cache



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



                if (u.contains("criteriofinanciero") || u.contains("seguroycredito") || u.startsWith(targetBase)) {

                    return false;

                }



                log("🛡 Ahorro WiFi: Landing externa bloqueada (" + (url.length() > 42 ? url.substring(0, 42) + "..." : url) + ")");

                return true;

            }



            @Override

            public WebResourceResponse shouldInterceptRequest(WebView view, WebResourceRequest request) {

                if (request != null && request.getUrl() != null) {

                    String u = request.getUrl().toString().toLowerCase();

                    if (u.contains(".mp4") || u.contains(".webm") || u.contains(".m4v") ||

                        u.contains(".avi") || u.contains(".flv") || u.contains(".m3u8") ||

                        u.contains(".ts") || u.contains(".mov") || u.contains(".ogv") ||

                        u.contains(".mp3") || u.contains(".wav") || u.contains(".ogg") ||

                        u.contains("googlevideo.com") || u.contains("/videoplayback")) {

                        return new WebResourceResponse("text/plain", "utf-8", new ByteArrayInputStream(new byte[0]));

                    }

                    if (u.endsWith(".woff2") || u.endsWith(".woff") || u.endsWith(".ttf") || u.contains("fonts.gstatic.com")) {

                        return new WebResourceResponse("text/plain", "utf-8", new ByteArrayInputStream(new byte[0]));

                    }

                    if (u.endsWith(".apk") || u.endsWith(".zip") || u.endsWith(".exe") || u.endsWith(".dmg") || u.endsWith(".rar")) {

                        return new WebResourceResponse("text/plain", "utf-8", new ByteArrayInputStream(new byte[0]));

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

        setContentView(rootScroll);



        log("CF Bot WiFi iniciado. Destino actual: " + getCurrentTargetBase());

        checkPublicIp(false);

    }



    private void updateRotationFieldsVisibility(boolean useSmartPlug) {

        if (useSmartPlug) {

            layoutModemFields.setVisibility(View.GONE);

            layoutSmartPlugFields.setVisibility(View.VISIBLE);

        } else {

            layoutModemFields.setVisibility(View.VISIBLE);

            layoutSmartPlugFields.setVisibility(View.GONE);

        }

    }



    private void saveSettings() {

        SharedPreferences prefs = getSharedPreferences(PREFS_NAME, MODE_PRIVATE);

        prefs.edit()

                .putString(KEY_TARGET_URL, getCurrentTargetBase())

                .putString(KEY_MODEM_IP, etModemIp != null ? etModemIp.getText().toString().trim() : "192.168.1.1")

                .putString(KEY_MODEM_USER, etModemUser != null ? etModemUser.getText().toString().trim() : "admin")

                .putString(KEY_MODEM_PASS, etModemPass != null ? etModemPass.getText().toString() : "")

                .putInt(KEY_MODEM_BRAND_POS, spModemBrand != null ? spModemBrand.getSelectedItemPosition() : 0)

                .putBoolean(KEY_USE_SMART_PLUG, chkUseSmartPlug != null && chkUseSmartPlug.isChecked())

                .putString(KEY_SMART_PLUG_URL, etSmartPlugUrl != null ? etSmartPlugUrl.getText().toString().trim() : "")

                .apply();

    }



    private String getCurrentTargetBase() {

        String raw = etTargetUrl != null ? etTargetUrl.getText().toString().trim() : DEFAULT_TARGET_URL;

        if (raw.isEmpty()) raw = DEFAULT_TARGET_URL;

        if (!raw.startsWith("http://") && !raw.startsWith("https://")) raw = "https://" + raw;

        while (raw.endsWith("/") && raw.length() > 8) raw = raw.substring(0, raw.length() - 1);

        return raw;

    }



    private void log(final String msg) {

        Log.i("CFBotWiFi", msg);

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

            log("👆 Interacción táctil ejecutada en página");

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

            log("Bot WiFi iniciado hacia: " + getCurrentTargetBase());

            checkPublicIp(true);

        } else {

            btnToggleAuto.setText("▶ INICIAR BOT WIFI");

            btnToggleAuto.setBackgroundColor(Color.parseColor("#10b981"));

            tvStatus.setText("ESTADO: PAUSADO");

            tvStatus.setTextColor(Color.parseColor("#fde047"));

            handler.removeCallbacksAndMessages(null);

            isVisiting = false;

            log("Bot detenido por el usuario.");

        }

    }



    private void triggerManualReboot() {

        log("Disparando reinicio manual de red...");

        executeModemRotation(false);

    }



    private void performOrganicVisit() {

        if (!isRunning || isVisiting) return;

        isVisiting = true;



        CookieManager.getInstance().removeAllCookies(null);
                                WebStorage.getInstance().deleteAllData();

        webView.clearCache(true);



        // User-Agent estable mantenido para preservar cache HTTP y ahorrar datos



        final String base = getCurrentTargetBase();

        String path = PATHS[random.nextInt(PATHS.length)];

        String fullUrl = base.contains("criteriofinanciero") ? (base + path) : base;



        visitCount++;

        tvVisitsCount.setText("Visitas enviadas en esta sesión: " + visitCount);

        log("Visita #" + visitCount + " (IP " + lastIp + ") -> " + fullUrl);



        webView.loadUrl(fullUrl);



        // A los 7s: toque táctil orgánico en zona neutral

        handler.postDelayed(new Runnable() {

            @Override

            public void run() {

                if (!isRunning) return;

                simulateHardwareTouch(webView, 0.25f, 0.45f);

            }

        }, 7000);



        // A los 14s: scroll intermedio adicional en la primera página

        handler.postDelayed(new Runnable() {

            @Override

            public void run() {

                if (!isRunning) return;

                webView.evaluateJavascript("window.scrollBy({top: Math.floor(Math.random()*400)+200, behavior: 'smooth'});", null);

            }

        }, 14000);



        // A los 24s: pasar al segundo artículo o seguir explorando

        handler.postDelayed(new Runnable() {

            @Override

            public void run() {

                if (!isRunning) return;

                if (base.contains("criteriofinanciero")) {

                    String secondPath = PATHS[8 + random.nextInt(PATHS.length - 8)];

                    log("↳ Leyendo artículo interno: " + secondPath + " (~26s más)");

                    webView.loadUrl(base + secondPath);

                } else {

                    log("↳ Leyendo contenido interno de la página (~26s más)...");

                    webView.evaluateJavascript("window.scrollBy({top: Math.floor(Math.random()*500)+300, behavior: 'smooth'});", null);

                }

            }

        }, 24000);



        // A los 32s: toque táctil orgánico en el segundo artículo

        handler.postDelayed(new Runnable() {

            @Override

            public void run() {

                if (!isRunning) return;

                simulateHardwareTouch(webView, 0.72f, 0.52f);

            }

        }, 32000);



        // A los 40s: scroll adicional en el segundo artículo

        handler.postDelayed(new Runnable() {

            @Override

            public void run() {

                if (!isRunning) return;

                webView.evaluateJavascript("window.scrollBy({top: Math.floor(Math.random()*350)+150, behavior: 'smooth'});", null);

            }

        }, 40000);



        // A los 50s: fin de permanencia completa -> enviar orden de reinicio al módem

        handler.postDelayed(new Runnable() {

            @Override

            public void run() {

                if (!isRunning) return;

                log("Fin de lectura (50s). Enviando orden de reinicio de IP al módem/enchufe...");

                executeModemRotation(true);

            }

        }, 50000);

    }



    private void executeModemRotation(final boolean continueBotAfter) {

        handler.post(new Runnable() {

            @Override

            public void run() {

                tvStatus.setText("ESTADO: ENVIANDO REINICIO...");

                tvStatus.setTextColor(Color.parseColor("#38bdf8"));

            }

        });



        final boolean usePlug = chkUseSmartPlug != null && chkUseSmartPlug.isChecked();

        final String plugUrl = etSmartPlugUrl != null ? etSmartPlugUrl.getText().toString().trim() : "";

        final String mIp = etModemIp != null ? etModemIp.getText().toString().trim() : "192.168.1.1";

        final String mUser = etModemUser != null ? etModemUser.getText().toString().trim() : "admin";

        final String mPass = etModemPass != null ? etModemPass.getText().toString() : "";

        final String mBrand = spModemBrand != null ? spModemBrand.getSelectedItem().toString() : "Huawei";



        new Thread(new Runnable() {

            @Override

            public void run() {

                ModemRebooter.reboot(usePlug, plugUrl, mIp, mUser, mPass, mBrand, new ModemRebooter.LogCallback() {

                    @Override

                    public void onLog(String message) {

                        log(message);

                    }

                });



                handler.post(new Runnable() {

                    @Override

                    public void run() {

                        tvStatus.setText("ESTADO: ESPERANDO RECONEXIÓN WIFI...");

                        tvStatus.setTextColor(Color.parseColor("#f97316"));

                    }

                });



                log("Esperando 15 segundos a que caiga el enlace de fibra...");

                try { Thread.sleep(15000); } catch (Exception ignored) {}



                waitForWifiAndResume(continueBotAfter);

            }

        }).start();

    }



    private void waitForWifiAndResume(final boolean continueBotAfter) {

        log("Comprobando reconexión de WiFi e internet...");



        new Thread(new Runnable() {

            @Override

            public void run() {

                int attempts = 0;

                boolean isConnected = false;



                while (attempts < 36) { // Hasta 3 minutos de espera máxima

                    attempts++;

                    try {

                        if (hasActiveInternetConnection()) {

                            isConnected = true;

                            break;

                        }

                    } catch (Exception ignored) {}



                    try { Thread.sleep(5000); } catch (Exception ignored) {}

                }



                if (isConnected) {

                    log("✔ Conexión a internet restablecida exitosamente.");

                    handler.post(new Runnable() {

                        @Override

                        public void run() {

                            tvStatus.setText("ESTADO: CONECTADO (NUEVA IP)");

                            tvStatus.setTextColor(Color.parseColor("#34d399"));

                            checkPublicIp(continueBotAfter && isRunning);

                        }

                    });

                } else {

                    log("⚠ Tiempo de espera agotado. Verificando conectividad...");

                    handler.post(new Runnable() {

                        @Override

                        public void run() {

                            tvStatus.setText("ESTADO: ESPERANDO SEÑAL...");

                            tvStatus.setTextColor(Color.parseColor("#ef4444"));

                            if (continueBotAfter && isRunning) {

                                handler.postDelayed(new Runnable() {

                                    @Override

                                    public void run() {

                                        waitForWifiAndResume(true);

                                    }

                                }, 8000);

                            }

                        }

                    });

                }

            }

        }).start();

    }



    private boolean hasActiveInternetConnection() {

        try {

            ConnectivityManager cm = (ConnectivityManager) getSystemService(Context.CONNECTIVITY_SERVICE);

            if (cm != null) {

                NetworkCapabilities nc = cm.getNetworkCapabilities(cm.getActiveNetwork());

                if (nc != null && nc.hasCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET)) {

                    URL url = new URL("https://api.ipify.org");

                    HttpURLConnection conn = (HttpURLConnection) url.openConnection();

                    conn.setConnectTimeout(4000);

                    conn.setReadTimeout(4000);

                    int code = conn.getResponseCode();

                    conn.disconnect();

                    return code == 200;

                }

            }

        } catch (Exception ignored) {

        }

        return false;

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

                                tvIp.setText("IP Pública WiFi actual: " + ip);

                                if (changed) {

                                    log("★ Nueva IP de Fibra detectada: " + ip);

                                }

                                if (launchVisitAfter && isRunning) {

                                    performOrganicVisit();

                                }

                            }

                        });

                    }

                } catch (Exception e) {

                    log("Consultando estado de red WiFi...");

                    if (launchVisitAfter && isRunning) {

                        handler.postDelayed(new Runnable() {

                            @Override

                            public void run() {

                                checkPublicIp(true);

                            }

                        }, 5000);

                    }

                }

            }

        }).start();

    }



    // Helpers UI

    private LinearLayout createCard() {

        LinearLayout card = new LinearLayout(this);

        card.setOrientation(LinearLayout.VERTICAL);

        GradientDrawable cardBg = new GradientDrawable();

        cardBg.setColor(Color.parseColor("#0f1a2e"));

        cardBg.setCornerRadius(16f);

        cardBg.setStroke(2, Color.parseColor("#1f3358"));

        card.setBackground(cardBg);

        card.setPadding(24, 20, 24, 20);

        LinearLayout.LayoutParams params = new LinearLayout.LayoutParams(

                LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT);

        params.topMargin = 14;

        card.setLayoutParams(params);

        return card;

    }



    private TextView createSectionHeader(String text) {

        TextView tv = new TextView(this);

        tv.setText(text);

        tv.setTextColor(Color.parseColor("#38bdf8"));

        tv.setTextSize(12.5f);

        tv.setTypeface(null, Typeface.BOLD);

        tv.setPadding(0, 0, 0, 8);

        return tv;

    }



    private TextView createFieldLabel(String text) {

        TextView tv = new TextView(this);

        tv.setText(text);

        tv.setTextColor(Color.parseColor("#94a3b8"));

        tv.setTextSize(11.5f);

        tv.setPadding(0, 6, 0, 3);

        return tv;

    }



    private void styleInput(EditText et, String strokeColor) {

        et.setTextColor(Color.WHITE);

        et.setHintTextColor(Color.parseColor("#64748b"));

        et.setTextSize(13f);

        et.setSingleLine(true);

        GradientDrawable bg = new GradientDrawable();

        bg.setColor(Color.parseColor("#070d19"));

        bg.setCornerRadius(12f);

        bg.setStroke(2, Color.parseColor(strokeColor));

        et.setBackground(bg);

        et.setPadding(20, 14, 20, 14);

        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(

                LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT);

        lp.topMargin = 4;

        lp.bottomMargin = 8;

        et.setLayoutParams(lp);

    }

}

