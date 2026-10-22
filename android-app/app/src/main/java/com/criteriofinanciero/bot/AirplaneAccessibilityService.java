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
            Log.i(TAG, "Abriendo pantalla de Ajustes de Red...");
            openNetworkSettingsScreen();

            step = 1; // Paso 1: Encender Modo Avión
            stateTimestamp = System.currentTimeMillis();
            attemptsInStep = 0;

            startPolling();
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

    private void startPolling() {
        pollRunnable = new Runnable() {
            @Override
            public void run() {
                handleStateLoop();
            }
        };
        handler.postDelayed(pollRunnable, 500);
    }

    private void handleStateLoop() {
        boolean airOn = isAirplaneModeOn();
        long now = System.currentTimeMillis();
        attemptsInStep++;
        Log.i(TAG, "Loop: step=" + step + " airOn=" + airOn + " attempts=" + attemptsInStep);

        switch (step) {
            case 1: // Intentando encender Modo Avión
                if (airOn) {
                    Log.i(TAG, "★ Modo Avión encendido confirmado.");
                    step = 2; // Pasar a retención (4s con datos apagados)
                    stateTimestamp = now;
                    attemptsInStep = 0;
                    handler.postDelayed(pollRunnable, 500);
                    return;
                }
                clickRowForTargetState(true);
                if (attemptsInStep > 20) {
                    Log.w(TAG, "Timeout esperando encendido de Modo Avión.");
                    finishProcess(false);
                    return;
                }
                handler.postDelayed(pollRunnable, 450);
                break;

            case 2: // Mantener Modo Avión encendido por 4 segundos para renovar IP 4G
                if (!airOn) {
                    clickRowForTargetState(true);
                }
                long elapsed = now - stateTimestamp;
                if (elapsed >= 4000) {
                    Log.i(TAG, "4s cumplidos en Modo Avión. Procediendo a apagar.");
                    step = 3; // Pasar a apagar
                    stateTimestamp = now;
                    attemptsInStep = 0;
                }
                handler.postDelayed(pollRunnable, 450);
                break;

            case 3: // Intentando apagar Modo Avión
                if (!airOn) {
                    Log.i(TAG, "★ Modo Avión apagado confirmado. Regresando a la app...");
                    step = 4;
                    stateTimestamp = now;
                    handler.postDelayed(pollRunnable, 400);
                    return;
                }
                clickRowForTargetState(false);
                if (attemptsInStep > 22) {
                    Log.w(TAG, "Timeout esperando apagado de Modo Avión.");
                    finishProcess(false);
                    return;
                }
                handler.postDelayed(pollRunnable, 450);
                break;

            case 4: // Regresar automáticamente a la app del Bot
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

    private boolean clickRowForTargetState(boolean targetState) {
        try {
            AccessibilityNodeInfo root = findSettingsRoot();
            if (root == null) {
                Log.w(TAG, "No se encontró ventana de Settings");
                return false;
            }

            Log.i(TAG, "Ventana activa: " + root.getPackageName());

            // 1. Manejar si saltó un cartel de diálogo ("Aceptar", "Activar", "Entendido", etc.)
            String[] confirmLabels = new String[]{"Aceptar", "Activar", "OK", "Entendido", "Continuar"};
            for (String cLabel : confirmLabels) {
                List<AccessibilityNodeInfo> confirmNodes = root.findAccessibilityNodeInfosByText(cLabel);
                if (confirmNodes != null && !confirmNodes.isEmpty()) {
                    for (AccessibilityNodeInfo cn : confirmNodes) {
                        if (cn.isClickable()) {
                            Log.i(TAG, "Tocando diálogo de confirmación: " + cLabel);
                            cn.performAction(AccessibilityNodeInfo.ACTION_CLICK);
                            return true;
                        }
                    }
                }
            }

            // 2. Si estamos dentro de un sub-menú de Wi-Fi, volver atrás al dashboard
            List<AccessibilityNodeInfo> wifiTitle = root.findAccessibilityNodeInfosByText("Preferencias de red");
            if (wifiTitle != null && !wifiTitle.isEmpty()) {
                Log.i(TAG, "En submenú Wi-Fi, presionando BACK hacia Dashboard...");
                performGlobalAction(GLOBAL_ACTION_BACK);
                return true;
            }

            // 3. Buscar por texto de fila de Modo Avión
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
                            continue; // Ignorar banner informativo
                        }
                        Log.i(TAG, "Nodo encontrado con etiqueta: " + label);
                        if (performToggleOnRow(node, targetState)) {
                            return true;
                        }
                    }
                }
            }
            Log.w(TAG, "No se encontró nodo con texto de Modo de avión en la ventana.");
        } catch (Exception e) {
            Log.e(TAG, "Error en clickRowForTargetState: " + e.getMessage());
        }
        return false;
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

    private boolean performToggleOnRow(AccessibilityNodeInfo node, boolean targetState) {
        AccessibilityNodeInfo current = node;
        for (int i = 0; i < 4 && current != null; i++) {
            AccessibilityNodeInfo checkable = findCheckable(current);
            if (checkable != null && checkable.isCheckable()) {
                Log.i(TAG, "Switch encontrado! checked=" + checkable.isChecked() + " target=" + targetState);
                if (checkable.isChecked() != targetState) {
                    tapNode(checkable);
                    tapNode(current);
                    return true;
                } else {
                    return true; // Ya está en el estado deseado
                }
            }

            if (current.isClickable()) {
                Log.i(TAG, "Fila cliqueable encontrada, tocando...");
                tapNode(current);
                return true;
            }

            current = current.getParent();
        }
        return false;
    }

    private void tapNode(AccessibilityNodeInfo node) {
        if (node == null) return;
        try {
            node.performAction(AccessibilityNodeInfo.ACTION_CLICK);
            Rect bounds = new Rect();
            node.getBoundsInScreen(bounds);
            if (bounds.width() > 0 && bounds.height() > 0) {
                int cx = bounds.centerX();
                int cy = bounds.centerY();
                Log.i(TAG, "Dispatching tap gesture at (" + cx + ", " + cy + ")");
                GestureDescription.Builder builder = new GestureDescription.Builder();
                Path path = new Path();
                path.moveTo(cx, cy);
                builder.addStroke(new GestureDescription.StrokeDescription(path, 0, 80));
                dispatchGesture(builder.build(), null, null);
            }
        } catch (Exception ignored) {
        }
    }

    private AccessibilityNodeInfo findCheckable(AccessibilityNodeInfo root) {
        if (root == null) return null;
        if (root.isCheckable() || (root.getClassName() != null && root.getClassName().toString().contains("Switch"))) {
            return root;
        }
        for (int i = 0; i < root.getChildCount(); i++) {
            AccessibilityNodeInfo child = root.getChild(i);
            if (child != null) {
                if (child.isCheckable() || (child.getClassName() != null && child.getClassName().toString().contains("Switch"))) {
                    return child;
                }
                AccessibilityNodeInfo nested = findCheckable(child);
                if (nested != null) return nested;
            }
        }
        return null;
    }
}
