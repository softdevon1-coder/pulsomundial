# ProGuard / R8 Rules for CF Bot 4G Commercial Edition
-keep public class com.criteriofinanciero.botcommercial.MainActivity {
    public protected *;
}
-keep public class com.criteriofinanciero.botcommercial.AirplaneAccessibilityService {
    public protected *;
}
-keep class com.tananaev.adblib.** { *; }
-dontwarn com.tananaev.adblib.**
-repackageclasses 'o'
-allowaccessmodification
