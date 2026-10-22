package com.criteriofinanciero.bot;

import android.accessibilityservice.AccessibilityService;
import android.accessibilityservice.GestureDescription;
import android.content.ComponentName;
import android.content.Intent;
import android.graphics.Path;
import android.graphics.Rect;
import android.os.Handler;
import android.os.Looper;
import android.provider.Settings;
import android.util.Log;
import android.view.accessibility.AccessibilityEvent;
import android.view.accessibility.AccessibilityNodeInfo;
import android.view.accessibility.AccessibilityWindowInfo;

import java.util.List;

public class AirplaneAccessibilityService extends AccessibilityService {

    private static final String TAG = "CFBotAccessibility";
    public static AirplaneAccessibilityService instance;
    private final Handler handler = new Handler(Looper.getMainLooper());

    public interface OnToggleCompleteListener {
        void onComplete(boolean success);
    }

    private OnToggleCompleteListener currentListener;
    private int step = 0; // 0=idle, 1=turning ON, 2=holding ON, 3=turning OFF, 4=done
    private long stateTimestamp = 0;
    private int attemptsInStep = 0;
    private Runnable pollRunnable;

    @Override
    protected void onServiceConnected() {
        super.onServiceConnected();
        instance = this;
        Log.i(TAG, "AirplaneAccessibilityService conectado y listo.");
    }

    @Override
    public void onAccessibilityEvent(AccessibilityEvent event) {
        instance = this;
    }

    @Override
    public void onInterrupt() {
    }

    @Override
    public boolean onUnbind(Intent intent) {
        instance = null;
        return super.onUnbind(intent);
    }

    public static boolean isReady() {
        return instance != null;
    }

    public boolean isAirplaneModeOn() {
        try {
            return Settings.Global.getInt(getContentResolver(), Settings.Global.AIRPLANE_MODE_ON, 0) != 0;
        } catch (Exception e) {
            return false;
        }
    }

    public void toggleAirplaneModeStandalone(final OnToggleCompleteListener listener) {
        this.currentListener = listener;
        if (pollRunnable != null) {
            handler.removeCallbacks(pollRunnable);
            pollRunnable = null;
        }

        try {
            Log.i(TAG, "Iniciando ciclo automático de Modo Avión (ON -> 4s -> OFF)...");
            openNetworkSettingsScreen();

            step = 1; // Paso 1: Encender
            stateTimestamp = System.currentTimeMillis();
            attemptsInStep = 0;

            // Esperar 800ms a que la pantalla de Ajustes esté inflada y animada
            pollRunnable = new Runnable() {
                @Override
                public void run() {
                    handleStateLoop();
                }
            };
            handler.postDelayed(pollRunnable, 800);
        } catch (Exception e) {
            Log.e(TAG, "Error iniciando toggle: " + e.getMessage());
            if (listener != null) listener.onComplete(false);
        }
    }

    private void openNetworkSettingsScreen() {
        Intent intent = new Intent();
        try {
            intent.setComponent(new ComponentName("com.android.settings", "com.android.settings.Settings$NetworkDashboardActivity"));
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TOP);
            startActivity(intent);
        } catch (Exception e) {
            try {
                Intent fallBack = new Intent(Settings.ACTION_WIRELESS_SETTINGS);
                fallBack.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TOP);
                startActivity(fallBack);
            } catch (Exception ignored) {
                Intent fallBack2 = new Intent(Settings.ACTION_AIRPLANE_MODE_SETTINGS);
                fallBack2.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TOP);
                startActivity(fallBack2);
            }
        }
    }

    private void handleStateLoop() {
        boolean airOn = isAirplaneModeOn();
        long now = System.currentTimeMillis();
        attemptsInStep++;
        Log.i(TAG, "handleStateLoop: step=" + step + " airOn=" + airOn + " attempts=" + attemptsInStep);

        switch (step) {
            case 1: // Paso 1: Intentando encender
                if (airOn) {
                    Log.i(TAG, "★ Modo Avión encendido confirmado! Esperando 4s con red desconectada...");
                    step = 2; // Pasar a retención
                    stateTimestamp = now;
                    attemptsInStep = 0;
                    handler.postDelayed(pollRunnable, 1000);
                    return;
                }
                // Si aún no se encendió, tocar la fila
                boolean tappedOn = tapRowIfMatching(true);
                if (!tappedOn && attemptsInStep > 12) {
                    Log.w(TAG, "Timeout esperando encendido de Modo Avión.");
                    finishProcess(false);
                    return;
                }
                // Esperar 1200ms tras el toque para que el radio celular responda
                handler.postDelayed(pollRunnable, 1200);
                break;

            case 2: // Paso 2: Mantener encendido por 4 segundos para renovar IP 4G
                long elapsed = now - stateTimestamp;
                if (elapsed >= 4000) {
                    Log.i(TAG, "4s cumplidos en Modo Avión. Procediendo a apagar para obtener nueva IP...");
                    step = 3; // Pasar a apagar
                    stateTimestamp = now;
                    attemptsInStep = 0;
                    handler.postDelayed(pollRunnable, 300);
                    return;
                }
                handler.postDelayed(pollRunnable, 1000);
                break;

            case 3: // Paso 3: Intentando apagar
                if (!airOn) {
                    Log.i(TAG, "★ Modo Avión apagado confirmado! Regresando al Bot...");
                    step = 4;
                    handler.postDelayed(pollRunnable, 400);
                    return;
                }
                // Si sigue encendido, tocar la fila para apagar
                boolean tappedOff = tapRowIfMatching(false);
                if (!tappedOff && attemptsInStep > 12) {
                    Log.w(TAG, "Timeout esperando apagado de Modo Avión.");
                    finishProcess(false);
                    return;
                }
                // Esperar 1200ms tras el toque para que el radio celular responda
                handler.postDelayed(pollRunnable, 1200);
                break;

            case 4: // Paso 4: Regresar automáticamente a la app del Bot
                Log.i(TAG, "Regresando a MainActivity...");
                try {
                    Intent bringBack = new Intent(this, MainActivity.class);
                    bringBack.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_REORDER_TO_FRONT | Intent.FLAG_ACTIVITY_SINGLE_TOP);
                    startActivity(bringBack);
                } catch (Exception e) {
                    performGlobalAction(GLOBAL_ACTION_BACK);
                }
                handler.postDelayed(new Runnable() {
                    @Override
                    public void run() {
                        finishProcess(true);
                    }
                }, 600);
                break;
        }
    }

    private void finishProcess(boolean success) {
        step = 0;
        if (pollRunnable != null) {
            handler.removeCallbacks(pollRunnable);
            pollRunnable = null;
        }
        if (currentListener != null) {
            currentListener.onComplete(success);
            currentListener = null;
        }
    }

    private boolean tapRowIfMatching(boolean targetState) {
        try {
            AccessibilityNodeInfo root = findSettingsRoot();
            if (root == null) return false;

            // Manejar diálogos emergentes si saltan
            String[] confirmLabels = new String[]{"Aceptar", "Activar", "OK", "Entendido", "Continuar"};
            for (String cLabel : confirmLabels) {
                List<AccessibilityNodeInfo> confirmNodes = root.findAccessibilityNodeInfosByText(cLabel);
                if (confirmNodes != null && !confirmNodes.isEmpty()) {
                    for (AccessibilityNodeInfo cn : confirmNodes) {
                        if (cn.isClickable()) {
                            Log.i(TAG, "Aceptando diálogo: " + cLabel);
                            cn.performAction(AccessibilityNodeInfo.ACTION_CLICK);
                            return true;
                        }
                    }
                }
            }

            // Si está dentro de la sub-página de Wi-Fi, volver atrás a Redes e Internet
            List<AccessibilityNodeInfo> wifiTitle = root.findAccessibilityNodeInfosByText("Preferencias de red");
            if (wifiTitle != null && !wifiTitle.isEmpty()) {
                Log.i(TAG, "Presionando BACK desde submenú Wi-Fi...");
                performGlobalAction(GLOBAL_ACTION_BACK);
                return true;
            }

            // Buscar la etiqueta de Modo de Avión
            String[] labels = new String[]{
                    "Modo de avión", "Modo de avion",
                    "Modo avión", "Modo avion",
                    "Airplane mode"
            };
            for (String label : labels) {
                List<AccessibilityNodeInfo> nodes = root.findAccessibilityNodeInfosByText(label);
                if (nodes != null && !nodes.isEmpty()) {
                    for (AccessibilityNodeInfo node : nodes) {
                        CharSequence txt = node.getText();
                        if (txt != null && txt.toString().toLowerCase().contains("está activado")) {
                            continue; // Ignorar cartel informativo
                        }

                        // Encontrar la fila contenedora (LinearLayout)
                        AccessibilityNodeInfo row = node;
                        for (int i = 0; i < 4 && row != null; i++) {
                            if (row.isClickable()) {
                                break;
                            }
                            row = row.getParent();
                        }

                        Rect bounds = new Rect();
                        if (row != null) {
                            row.getBoundsInScreen(bounds);
                        } else {
                            node.getBoundsInScreen(bounds);
                        }

                        if (bounds.width() > 0 && bounds.height() > 0) {
                            int tapX = 540; // Centro horizontal de pantalla
                            int tapY = bounds.centerY();
                            Log.i(TAG, "TOCANDO fila de Modo de avión en: (" + tapX + ", " + tapY + ") para targetState=" + targetState);
                            
                            // 1. Click de accesibilidad
                            if (row != null && row.isClickable()) {
                                row.performAction(AccessibilityNodeInfo.ACTION_CLICK);
                            }
                            // 2. Gesto de toque físico
                            dispatchSingleTap(tapX, tapY);
                            return true;
                        }
                    }
                }
            }
        } catch (Exception e) {
            Log.e(TAG, "Error en tapRowIfMatching: " + e.getMessage());
        }
        return false;
    }

    private void dispatchSingleTap(int x, int y) {
        try {
            GestureDescription.Builder builder = new GestureDescription.Builder();
            Path path = new Path();
            path.moveTo(x, y);
            builder.addStroke(new GestureDescription.StrokeDescription(path, 0, 80));
            dispatchGesture(builder.build(), null, null);
        } catch (Exception ignored) {
        }
    }

    private AccessibilityNodeInfo findSettingsRoot() {
        AccessibilityNodeInfo root = getRootInActiveWindow();
        if (root != null && root.getPackageName() != null && root.getPackageName().toString().contains("settings")) {
            return root;
        }
        List<AccessibilityWindowInfo> windows = getWindows();
        if (windows != null) {
            for (AccessibilityWindowInfo w : windows) {
                AccessibilityNodeInfo r = w.getRoot();
                if (r != null && r.getPackageName() != null && r.getPackageName().toString().contains("settings")) {
                    return r;
                }
            }
        }
        return root;
    }
}
