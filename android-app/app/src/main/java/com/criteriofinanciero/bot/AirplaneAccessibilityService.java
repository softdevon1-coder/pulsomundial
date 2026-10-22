package com.criteriofinanciero.bot;

import android.accessibilityservice.AccessibilityService;
import android.content.Intent;
import android.os.Handler;
import android.os.Looper;
import android.provider.Settings;
import android.util.Log;
import android.view.accessibility.AccessibilityEvent;
import android.view.accessibility.AccessibilityNodeInfo;

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
            // Abrir pantalla de Redes e Internet donde está el interruptor de Modo de Avión
            Intent intent;
            try {
                intent = new Intent(Settings.ACTION_WIRELESS_SETTINGS);
            } catch (Exception ignored) {
                intent = new Intent(Settings.ACTION_AIRPLANE_MODE_SETTINGS);
            }
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TOP);
            startActivity(intent);

            step = 1; // Paso 1: Encender Modo Avión
            stateTimestamp = System.currentTimeMillis();
            attemptsInStep = 0;

            startPolling();
        } catch (Exception e) {
            Log.e(TAG, "Error iniciando toggle: " + e.getMessage());
            if (listener != null) listener.onComplete(false);
        }
    }

    private void startPolling() {
        pollRunnable = new Runnable() {
            @Override
            public void run() {
                handleStateLoop();
            }
        };
        handler.postDelayed(pollRunnable, 350);
    }

    private void handleStateLoop() {
        boolean airOn = isAirplaneModeOn();
        long now = System.currentTimeMillis();
        attemptsInStep++;

        switch (step) {
            case 1: // Intentando encender Modo Avión
                if (airOn) {
                    Log.i(TAG, "Modo Avión encendido confirmado.");
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
                handler.postDelayed(pollRunnable, 400);
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
                handler.postDelayed(pollRunnable, 400);
                break;

            case 3: // Intentando apagar Modo Avión
                if (!airOn) {
                    Log.i(TAG, "Modo Avión apagado confirmado. Regresando a la app...");
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
                handler.postDelayed(pollRunnable, 400);
                break;

            case 4: // Regresar automáticamente a la app del Bot
                performGlobalAction(GLOBAL_ACTION_BACK);
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
            AccessibilityNodeInfo root = getRootInActiveWindow();
            if (root == null) return false;

            // Manejar si saltó un cartel de diálogo ("Aceptar", "Activar", "Entendido", etc.)
            String[] confirmLabels = new String[]{"Aceptar", "Activar", "OK", "Entendido", "Continuar"};
            for (String cLabel : confirmLabels) {
                List<AccessibilityNodeInfo> confirmNodes = root.findAccessibilityNodeInfosByText(cLabel);
                if (confirmNodes != null && !confirmNodes.isEmpty()) {
                    for (AccessibilityNodeInfo cn : confirmNodes) {
                        if (cn.isClickable()) {
                            cn.performAction(AccessibilityNodeInfo.ACTION_CLICK);
                            return true;
                        }
                    }
                }
            }

            // Buscar por texto exacto de etiqueta de Modo Avión (en Motorola es "Modo de avión")
            String[] labels = new String[]{
                    "Modo de avión", "Modo de avion",
                    "Modo avión", "Modo avion",
                    "Airplane mode"
            };
            for (String label : labels) {
                List<AccessibilityNodeInfo> nodes = root.findAccessibilityNodeInfosByText(label);
                if (nodes != null && !nodes.isEmpty()) {
                    for (AccessibilityNodeInfo node : nodes) {
                        // Descartar si es un banner que dice "El modo de avión está activado"
                        CharSequence txt = node.getText();
                        if (txt != null && txt.toString().toLowerCase().contains("está activado")) {
                            continue;
                        }
                        if (toggleSwitchNearNode(node, targetState)) {
                            return true;
                        }
                    }
                }
            }
        } catch (Exception ignored) {
        }
        return false;
    }

    private boolean toggleSwitchNearNode(AccessibilityNodeInfo node, boolean targetState) {
        AccessibilityNodeInfo current = node;
        for (int i = 0; i < 4 && current != null; i++) {
            AccessibilityNodeInfo checkable = findCheckable(current);
            if (checkable != null && checkable.isCheckable()) {
                if (checkable.isChecked() != targetState) {
                    // Clickear la fila cliqueable que contiene el switch
                    if (current.isClickable()) {
                        return current.performAction(AccessibilityNodeInfo.ACTION_CLICK);
                    }
                    if (checkable.isClickable()) {
                        return checkable.performAction(AccessibilityNodeInfo.ACTION_CLICK);
                    }
                } else {
                    return true; // Ya está en el estado deseado
                }
            }
            if (current.isClickable()) {
                // Si la fila es cliqueable y no encontramos el widget switch directamente
                return current.performAction(AccessibilityNodeInfo.ACTION_CLICK);
            }
            current = current.getParent();
        }
        return false;
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
