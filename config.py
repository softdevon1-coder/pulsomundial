# ============================================================
#  CONFIGURACIÓN — Editá esto antes de subir a GitHub
# ============================================================

# ── Tu sitio ──────────────────────────────────────────────
TARGET_URL = "https://pulsomundial.onrender.com"

# Nota: las secciones (/mundo, /economia, /tecnologia, etc.) y los artículos
# son manejados automáticamente por visitor.py — no hace falta configurarlos aquí.


# ── Comportamiento humano ──────────────────────────────────
# Tiempo total de lectura por visita (segundos)
READING_TIME_MIN = 20
READING_TIME_MAX = 50

# Pausa antes de navegar a una subpágina (segundos)
NAV_PAUSE_MIN = 2
NAV_PAUSE_MAX = 6

# Probabilidad de visitar una subpágina (0.0 a 1.0)
SUBPAGE_PROBABILITY = 0.65

# Máximo de subpáginas por visita
MAX_SUBPAGES = 2

# ── Rendimiento ────────────────────────────────────────────
# Workers async POR JOB de GitHub Actions
# (cada job de Actions tiene 2 cores / 7GB RAM)
WORKERS_PER_JOB = 25

# Workers en modo Navegador Real (Playwright Headless Chromium)
# 3 por job × 10 jobs paralelos = 30 navegadores reales simultáneos
BROWSER_WORKERS_PER_JOB = 3

# Usar motor de navegador real (Playwright) para validación de huella (Canvas, WebGL, Biometría)
USE_BROWSER_MODE = True

# Duración máxima de cada job en segundos (5.5 horas)
JOB_DURATION_SECONDS = 5.5 * 3600

# ── Assets del sitio ──────────────────────────────────────
# Descargar CSS/JS/imágenes (simula carga real del browser)
DOWNLOAD_ASSETS = True
MAX_ASSETS_PER_PAGE = 20   # máximo assets por página
MAX_IMAGES_PER_PAGE = 8    # máximo imágenes (más pesadas)

# ── Logging ───────────────────────────────────────────────
LOG_EVERY = 25    # loguear progreso cada N visitas

