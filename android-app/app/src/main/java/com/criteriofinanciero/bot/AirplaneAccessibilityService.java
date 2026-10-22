package com.criteriofinanciero.bot;

import android.accessibilityservice.AccessibilityService;
import android.content.Intent;
import android.os.Handler;
import android.os.Looper;
import android.provider.Settings;
import android.view.accessibility.AccessibilityEvent;
import android.view.accessibility.AccessibilityNodeInfo;

import java.util.List;

public class AirplaneAccessibilityService extends AccessibilityService {

    public static AirplaneAccessibilityService instance;
    private final Handler handler = new Handler(Looper.getMainLooper());

    @Override
    protected void onServiceConnected() {
        super.onServiceConnected();
        instance = this;
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

    public boolean toggleAirplaneModeStandalone() {
        try {
            // Abrir pantalla directa de Modo Avión del sistema
            Intent intent = new Intent(Settings.ACTION_AIRPLANE_MODE_SETTINGS);
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TOP);
            startActivity(intent);

            // Paso 1: A los 1.5s tocar el interruptor de "Modo avión" (ON)
            handler.postDelayed(new Runnable() {
                @Override
                public void run() {
                    clickAirplaneSwitch();
                }
            }, 1500);

            // Paso 2: A los 5.5s volver a tocar el interruptor de "Modo avión" (OFF)
            handler.postDelayed(new Runnable() {
                @Override
                public void run() {
                    clickAirplaneSwitch();
                }
            }, 5500);

            // Paso 3: A los 7.0s regresar automáticamente a la App del Bot
            handler.postDelayed(new Runnable() {
                @Override
                public void run() {
                    performGlobalAction(GLOBAL_ACTION_BACK);
                }
            }, 7000);

            return true;
        } catch (Exception e) {
            return false;
        }
    }

    private void clickAirplaneSwitch() {
        try {
            AccessibilityNodeInfo root = getRootInActiveWindow();
            if (root == null) return;

            String[] labels = new String[]{"Modo avión", "Modo Avión", "Modo avion", "Airplane mode", "Avión"};
            for (String label : labels) {
                List<AccessibilityNodeInfo> nodes = root.findAccessibilityNodeInfosByText(label);
                if (nodes != null && !nodes.isEmpty()) {
                    for (AccessibilityNodeInfo node : nodes) {
                        if (clickNodeOrParent(node)) {
                            return;
                        }
                    }
                }
            }
        } catch (Exception ignored) {
        }
    }

    private boolean clickNodeOrParent(AccessibilityNodeInfo node) {
        AccessibilityNodeInfo current = node;
        for (int i = 0; i < 6 && current != null; i++) {
            if (current.isClickable()) {
                return current.performAction(AccessibilityNodeInfo.ACTION_CLICK);
            }
            current = current.getParent();
        }
        return false;
    }
}
