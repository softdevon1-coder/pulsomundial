"""
visitor.py — Simulador de visitas humanas con Biometría y Detección Anti-Bot para PulsoMundial
Características avanzadas:
  1. Motor Playwright (Headless Chromium real) con soporte fallback a aiohttp
  2. Ejecución real de JavaScript (Canvas 2D render test, WebGL GPU context)
  3. Movimiento de mouse biométrico no-lineal (Curvas de Bézier cúbicas con micro-temblor humano)
  4. Dinámica de scroll humana con aceleración/desaceleración y pausas de lectura
  5. Rotación de IPs públicas realistas en cabeceras HTTP (X-Forwarded-For, CF-Connecting-IP)
  6. Árbol de navegación orgánico (Home -> Sección -> Lectura de Artículos)
"""

import asyncio
import random
import time
import logging
import sys
import os
import math
import subprocess
from typing import Optional, List, Tuple
from urllib.parse import urljoin, urlparse

import config

# ── Rotación de IP vía ADB (Motorola moto g52 por USB) ──────────────────────
ADB_PATH = os.path.join(os.path.dirname(__file__), "platform-tools", "adb.exe")
USE_MOBILE_IP = ("--mobile" in sys.argv) or (os.environ.get("USE_MOBILE_USB", "0") == "1")
# Cada cuántas visitas rotar la IP del celular (0 = desactivado)
_rotate_arg = 0
_workers_arg = 0
for i, arg in enumerate(sys.argv):
    if arg == "--rotate" and i + 1 < len(sys.argv) and sys.argv[i + 1].isdigit():
        _rotate_arg = int(sys.argv[i + 1])
    if arg == "--workers" and i + 1 < len(sys.argv) and sys.argv[i + 1].isdigit():
        _workers_arg = int(sys.argv[i + 1])
if _rotate_arg > 0:
    IP_ROTATE_EVERY = _rotate_arg
elif USE_MOBILE_IP:
    IP_ROTATE_EVERY = int(os.environ.get("IP_ROTATE_EVERY", "5"))
else:
    IP_ROTATE_EVERY = int(os.environ.get("IP_ROTATE_EVERY", "0"))


def get_cellular_bind_ip() -> Optional[str]:
    """
    Detecta la dirección IP local asignada al adaptador USB del celular (Ethernet 3).
    Permite enlazar el tráfico del bot exclusivamente a los datos móviles, dejando
    el Wi-Fi libre para juegos, streaming y uso normal de Windows sin cortes.
    """
    try:
        import socket
        ips = socket.gethostbyname_ex(socket.gethostname())[2]
        for ip in ips:
            if ip.startswith("10.") or ip.startswith("192.168.42.") or ip.startswith("192.168.137."):
                return ip
        for ip in ips:
            if not ip.startswith("127.") and not ip.startswith("192.168.0."):
                return ip
    except Exception:
        pass
    return None


def _adb(*args, timeout=10) -> str:
    """Ejecuta un comando ADB y retorna la salida."""
    try:
        result = subprocess.run(
            [ADB_PATH] + list(args),
            capture_output=True, text=True, timeout=timeout
        )
        return result.stdout.strip()
    except Exception as e:
        return f"ERROR: {e}"


def rotate_mobile_ip(max_wait: float = 16.0) -> str:
    """
    Alterna el modo avión en el celular mediante ADB para forzar una nueva IP CGNAT en la red móvil.
    Espera dinámicamente hasta que la conexión se restablezca.
    """
    _adb("shell", "cmd connectivity airplane-mode enable")
    time.sleep(3.5)
    _adb("shell", "cmd connectivity airplane-mode disable")

    # Espera dinámica a que el módem 4G/5G vuelva a tener salida a internet
    start_t = time.time()
    while time.time() - start_t < max_wait:
        time.sleep(2)
        ip = _adb("shell", "curl -s --max-time 4 https://api.ipify.org", timeout=6)
        if ip and not ip.startswith("ERROR") and len(ip.split(".")) == 4:
            # Pausa de estabilización para que Windows reconozca la ruta antes de la visita
            time.sleep(2.5)
            return ip
    time.sleep(3.0)
    return "IP_ACTIVA"

TARGET_URL = os.environ.get("TARGET_URL", config.TARGET_URL).rstrip("/")

import io

if hasattr(sys.stdout, "buffer"):
    safe_stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
else:
    safe_stdout = sys.stdout

# ── Logging ────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [JOB-%(job_id)s] %(message)s",
    handlers=[logging.StreamHandler(safe_stdout)],
)
JOB_ID = os.environ.get("JOB_ID", "local")
logger = logging.getLogger("visitor")
log = logging.LoggerAdapter(logger, {"job_id": JOB_ID})

# ── Perfiles de Usuario y Dispositivos Realistas ────────────────────────────
DEVICE_PROFILES = [
    {
        "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
        "viewport": {"width": 1920, "height": 1080},
        "locale": "es-AR",
        "timezone": "America/Argentina/Buenos_Aires",
        "platform": "Win32",
        "gpu_vendor": "Google Inc. (NVIDIA)",
        "gpu_renderer": "ANGLE (NVIDIA, NVIDIA GeForce RTX 3060 Direct3D11 vs_5_0 ps_5_0, D3D11)"
    },
    {
        "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
        "viewport": {"width": 1536, "height": 864},
        "locale": "es-ES",
        "timezone": "Europe/Madrid",
        "platform": "Win32",
        "gpu_vendor": "Google Inc. (Intel)",
        "gpu_renderer": "ANGLE (Intel, Intel(R) Iris(R) Xe Graphics Direct3D11 vs_5_0 ps_5_0, D3D11)"
    },
    {
        "ua": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
        "viewport": {"width": 1440, "height": 900},
        "locale": "es-MX",
        "timezone": "America/Mexico_City",
        "platform": "MacIntel",
        "gpu_vendor": "Apple",
        "gpu_renderer": "Apple M2"
    },
    {
        "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0",
        "viewport": {"width": 1366, "height": 768},
        "locale": "es-AR",
        "timezone": "America/Argentina/Buenos_Aires",
        "platform": "Win32",
        "gpu_vendor": "Google Inc. (NVIDIA)",
        "gpu_renderer": "ANGLE (NVIDIA, NVIDIA GeForce RTX 4070 Direct3D11 vs_5_0 ps_5_0, D3D11)"
    },
    {
        "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0",
        "viewport": {"width": 1920, "height": 1080},
        "locale": "en-US",
        "timezone": "America/New_York",
        "platform": "Win32",
        "gpu_vendor": "Google Inc. (NVIDIA)",
        "gpu_renderer": "ANGLE (NVIDIA, NVIDIA GeForce RTX 3070 Direct3D11 vs_5_0 ps_5_0, D3D11)"
    },
    {
        "ua": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Safari/605.1.15",
        "viewport": {"width": 1470, "height": 956},
        "locale": "es-ES",
        "timezone": "Europe/Madrid",
        "platform": "MacIntel",
        "gpu_vendor": "Apple",
        "gpu_renderer": "Apple M3 Pro"
    },
]

# ── Almacenamiento de Perfiles Persistentes y Cookies ──────────────────────
PROFILES_DIR = os.path.join(os.path.dirname(__file__), "profiles")
os.makedirs(PROFILES_DIR, exist_ok=True)
TOTAL_PROFILE_POOL = 3000

# ── Fuentes de Tráfico Realistas (Directo, Dark Social, Redes, Buscadores) ───
TRAFFIC_SOURCES = [
    # Directo / Marcadores (32%)
    {"ref": "", "weight": 32, "type": "direct"},
    # Dark Social: WhatsApp / Telegram / Mensajería (30%)
    {"ref": "https://web.whatsapp.com/", "weight": 14, "type": "whatsapp"},
    {"ref": "android-app://com.whatsapp", "weight": 8, "type": "whatsapp_mobile"},
    {"ref": "https://t.me/", "weight": 8, "type": "telegram"},
    # Redes Sociales (25%)
    {"ref": "https://t.co/", "weight": 10, "type": "twitter"},
    {"ref": "https://www.facebook.com/", "weight": 7, "type": "facebook"},
    {"ref": "https://l.instagram.com/", "weight": 5, "type": "instagram"},
    {"ref": "https://www.reddit.com/r/noticias/", "weight": 3, "type": "reddit"},
    # Buscadores orgánicos (13%)
    {"ref": "https://www.google.com.ar/", "weight": 5, "type": "google_ar"},
    {"ref": "https://www.google.com/", "weight": 4, "type": "google_global"},
    {"ref": "https://news.google.com/", "weight": 2, "type": "google_news"},
    {"ref": "https://www.bing.com/", "weight": 2, "type": "bing"},
]


def get_traffic_source() -> str:
    """Retorna una fuente de tráfico ponderada estadísticamente."""
    sources = [s["ref"] for s in TRAFFIC_SOURCES]
    weights = [s["weight"] for s in TRAFFIC_SOURCES]
    return random.choices(sources, weights=weights, k=1)[0]


def get_circadian_factor(tz_offset_hours: int = -3) -> float:
    """
    Calcula el factor de actividad biológica según la hora local de la audiencia (ej. Argentina UTC-3):
    - 01:00 a 06:00 (Madrugada): Valle de sueño (factor ~0.25, pausas más largas)
    - 08:00 a 11:30 (Mañana): Pico matutino (factor ~1.20)
    - 12:00 a 14:30 (Almuerzo): Pico mediodía (factor ~1.30)
    - 15:00 a 19:30 (Tarde): Tráfico sostenido (factor ~1.00)
    - 20:00 a 23:30 (Noche Prime): Pico máximo (factor ~1.45)
    """
    utc_now = time.gmtime()
    local_hour = (utc_now.tm_hour + tz_offset_hours) % 24

    if 1 <= local_hour < 6:
        return 0.25
    elif 6 <= local_hour < 8:
        return 0.60
    elif 8 <= local_hour < 12:
        return 1.20
    elif 12 <= local_hour < 15:
        return 1.30
    elif 15 <= local_hour < 20:
        return 1.00
    elif 20 <= local_hour < 24:
        return 1.45
    else:
        return 0.65


def choose_session_archetype() -> str:
    """
    Modela la conducta del lector:
    - 'bounce' (30%): Rebote humano natural (lee titular 12-25s y sale sin clics).
    - 'standard' (50%): Lectura regular (1 a 2 artículos).
    - 'deep' (20%): Lector comprometido (3 a 4 artículos + sección).
    """
    return random.choices(["bounce", "standard", "deep"], weights=[30, 50, 20], k=1)[0]


SECTIONS = ["/", "/mundo", "/economia", "/tecnologia", "/deportes", "/salud", "/ciencia"]
SECTION_WEIGHTS = [30, 15, 15, 15, 10, 8, 7]


def generate_random_ip() -> str:
    """Genera una dirección IPv4 pública de rangos residenciales globales."""
    pool = random.choice([
        # Argentina / Sudamérica
        (181, random.randint(16, 220)),
        (186, random.randint(10, 240)),
        (190, random.randint(1, 245)),
        (200, random.randint(5, 125)),
        # España / Europa
        (80, random.randint(1, 250)),
        (81, random.randint(1, 250)),
        (88, random.randint(1, 250)),
        # Estados Unidos
        (24, random.randint(1, 250)),
        (67, random.randint(1, 250)),
        (73, random.randint(1, 250)),
        # México / Brasil
        (187, random.randint(10, 240)),
        (189, random.randint(10, 240)),
    ])
    return f"{pool[0]}.{pool[1]}.{random.randint(1, 254)}.{random.randint(1, 254)}"


# ── Algoritmo de Biometría de Mouse: Curvas Cúbicas de Bézier con Jitter ────
def generate_bezier_trajectory(
    p0: Tuple[float, float],
    p3: Tuple[float, float],
    steps: int = 25
) -> List[Tuple[float, float]]:
    """
    Genera una trayectoria curvilínea humana entre dos puntos usando una curva de Bézier cúbica.
    Los puntos de control P1 y P2 se desvían perpendicularmente para simular el arco biomecánico
    del brazo/muñeca humano, con micro-temblor gaussiano.
    """
    x0, y0 = p0
    x3, y3 = p3

    dx = x3 - x0
    dy = y3 - y0
    dist = math.hypot(dx, dy)
    if dist < 5:
        return [p3]

    # Vector perpendicular normalizado
    nx = -dy / dist
    ny = dx / dist

    # Desviación de curvatura orgánica proporcional a la distancia
    deviation_1 = random.uniform(-0.35, 0.35) * dist
    deviation_2 = random.uniform(-0.35, 0.35) * dist

    # Puntos de control intermedios (P1 al ~30%, P2 al ~70% del camino)
    p1_x = x0 + dx * 0.3 + nx * deviation_1
    p1_y = y0 + dy * 0.3 + ny * deviation_1

    p2_x = x0 + dx * 0.7 + nx * deviation_2
    p2_y = y0 + dy * 0.7 + ny * deviation_2

    points = []
    for i in range(1, steps + 1):
        t = i / steps
        # Ecuación de Bézier cúbica
        u = 1.0 - t
        tt = t * t
        uu = u * u
        uuu = uu * u
        ttt = tt * t

        x = uuu * x0 + 3 * uu * t * p1_x + 3 * u * tt * p2_x + ttt * x3
        y = uuu * y0 + 3 * uu * t * p1_y + 3 * u * tt * p2_y + ttt * y3

        # Micro-temblor humano sutil (ruido biométrico)
        jitter_x = random.gauss(0, 0.8)
        jitter_y = random.gauss(0, 0.8)

        points.append((round(x + jitter_x, 1), round(y + jitter_y, 1)))

    return points


# ── Motor 1: Playwright (Navegador Real Headless con JS y Biometría) ────────
async def simulate_human_mouse(page, target_x: float, target_y: float, current_pos: Tuple[float, float]) -> Tuple[float, float]:
    """Mueve el mouse a lo largo de una curva de Bézier orgánica con aceleración y pausas."""
    steps = random.randint(18, 32)
    path = generate_bezier_trajectory(current_pos, (target_x, target_y), steps=steps)

    for pt in path:
        await page.mouse.move(pt[0], pt[1])
        # Aceleración/desaceleración: pausas variables entre micro-movimientos
        await asyncio.sleep(random.uniform(0.008, 0.022))

    # Breve pausa natural una vez llegado al objetivo
    await asyncio.sleep(random.uniform(0.1, 0.35))
    return (target_x, target_y)


async def simulate_human_scroll(page, total_scroll_target: int) -> int:
    """
    Simula scroll humano:
    - Desplazamiento por impulsos (rueda del mouse o touch)
    - Desaceleración gradual
    - Pausas de lectura aleatorias en párrafos
    """
    scrolled = 0
    while scrolled < total_scroll_target:
        chunk = random.randint(120, 340)
        # Scroll suave en pequeños pasos de rueda
        sub_steps = random.randint(3, 6)
        step_delta = chunk / sub_steps
        for _ in range(sub_steps):
            await page.mouse.wheel(0, step_delta)
            await asyncio.sleep(random.uniform(0.03, 0.07))
        scrolled += chunk

        # Pausa de lectura orgánica (un humano se detiene a leer texto o mirar una foto)
        if random.random() < 0.65:
            await asyncio.sleep(random.uniform(0.8, 2.5))
    return scrolled


async def run_playwright_visit(browser, client_ip: str, profile: dict, profile_id: Optional[int] = None) -> bool:
    """Ejecuta una visita completa en un contexto de navegador real con cookies persistentes y rebote orgánico."""
    if profile_id is None:
        profile_id = random.randint(1, TOTAL_PROFILE_POOL)

    profile_path = os.path.join(PROFILES_DIR, f"profile_{profile_id:04d}.json")
    has_existing_cookies = os.path.exists(profile_path)

    referrer = get_traffic_source()
    headers = {
        "Accept-Language": profile.get("locale", "es-AR") + ",es;q=0.9,en;q=0.8",
        "DNT": "1",
    }
    if not USE_MOBILE_IP:
        headers["X-Forwarded-For"] = client_ip
        headers["X-Real-IP"] = client_ip
    if referrer:
        headers["Referer"] = referrer

    context_kwargs = {
        "user_agent": profile["ua"],
        "viewport": profile["viewport"],
        "locale": profile["locale"],
        "timezone_id": profile["timezone"],
        "extra_http_headers": headers,
    }
    if has_existing_cookies:
        try:
            context_kwargs["storage_state"] = profile_path
        except Exception:
            pass

    context = await browser.new_context(**context_kwargs)

    # Inyectar script de stealth WebGL y evasión de detección de automatización
    stealth_js = f"""
    (function() {{
        // 1. Ocultar huellas de automatización
        try {{
            Object.defineProperty(navigator, 'webdriver', {{
                get: () => undefined,
                configurable: true
            }});
        }} catch(e) {{}}

        // 2. Simular entorno Chrome completo
        if (!window.chrome) {{
            window.chrome = {{
                app: {{ isInstalled: false }},
                runtime: {{ OnInstalledReason: {{}}, OnRestartRequiredReason: {{}} }},
                loadTimes: function() {{}},
                csi: function() {{}}
            }};
        }}

        // 3. Camuflaje de GPU WebGL / WebGL2
        const targetVendor = "{profile['gpu_vendor']}";
        const targetRenderer = "{profile['gpu_renderer']}";

        function hookWebGL(proto) {{
            if (!proto || !proto.getParameter) return;
            const origGetParam = proto.getParameter;
            const origGetExt = proto.getExtension;
            const origGetExts = proto.getSupportedExtensions;

            proto.getParameter = function(param) {{
                // UNMASKED_VENDOR_WEBGL (37445)
                if (param === 37445) return targetVendor;
                // UNMASKED_RENDERER_WEBGL (37446)
                if (param === 37446) return targetRenderer;
                // VENDOR (7936)
                if (param === 7936) return 'WebKit';
                // RENDERER (7937)
                if (param === 7937) return 'WebKit WebGL';
                return origGetParam.apply(this, arguments);
            }};

            try {{
                Object.defineProperty(proto.getParameter, 'toString', {{
                    value: () => 'function getParameter() {{ [native code] }}',
                    configurable: true
                }});
            }} catch(e) {{}}

            proto.getExtension = function(name) {{
                const ext = origGetExt.apply(this, arguments);
                if (name === 'WEBGL_debug_renderer_info') {{
                    return ext || {{ UNMASKED_VENDOR_WEBGL: 37445, UNMASKED_RENDERER_WEBGL: 37446 }};
                }}
                return ext;
            }};

            try {{
                Object.defineProperty(proto.getExtension, 'toString', {{
                    value: () => 'function getExtension() {{ [native code] }}',
                    configurable: true
                }});
            }} catch(e) {{}}

            if (origGetExts) {{
                proto.getSupportedExtensions = function() {{
                    const list = origGetExts.apply(this, arguments) || [];
                    const hardwareExts = [
                        'WEBGL_compressed_texture_s3tc',
                        'WEBGL_compressed_texture_s3tc_srgb',
                        'EXT_texture_filter_anisotropic',
                        'WEBGL_debug_renderer_info'
                    ];
                    hardwareExts.forEach(h => {{
                        if (!list.includes(h)) list.push(h);
                    }});
                    return list;
                }};

                try {{
                    Object.defineProperty(proto.getSupportedExtensions, 'toString', {{
                        value: () => 'function getSupportedExtensions() {{ [native code] }}',
                        configurable: true
                    }});
                }} catch(e) {{}}
            }}
        }}

        if (window.WebGLRenderingContext) hookWebGL(window.WebGLRenderingContext.prototype);
        if (window.WebGL2RenderingContext) hookWebGL(window.WebGL2RenderingContext.prototype);
    }})();
    """
    await context.add_init_script(stealth_js)

    page = await context.new_page()
    mouse_pos = (random.randint(100, 400), random.randint(100, 300))

    try:
        # Elegir arquetipo de conducta humana (Rebote 30%, Estándar 50%, Lectura Profunda 20%)
        archetype = choose_session_archetype()

        # 1. Navegar a página de entrada (Home o Sección)
        entry_section = random.choices(SECTIONS, weights=SECTION_WEIGHTS, k=1)[0]
        entry_url = TARGET_URL + entry_section
        await page.goto(entry_url, wait_until="domcontentloaded", timeout=35000)

        # Espera inicial mientras el browser renderiza CSS y telemetría
        await asyncio.sleep(random.uniform(1.2, 2.5))

        # 2. Movimiento inicial de mouse (exploración visual del usuario)
        w, h = profile["viewport"]["width"], profile["viewport"]["height"]
        for _ in range(random.randint(2, 4)):
            tx = random.randint(int(w * 0.15), int(w * 0.85))
            ty = random.randint(int(h * 0.2), int(h * 0.8))
            mouse_pos = await simulate_human_mouse(page, tx, ty, mouse_pos)

        # 3. Scroll exploratorio de la página
        scroll_px = random.randint(350, 950)
        await simulate_human_scroll(page, scroll_px)

        # 4. Comportamiento según arquetipo
        if archetype == "bounce":
            # 30% Tasa de Rebote Orgánico: Lee titular / resumen durante 12-24s y sale sin clics
            await asyncio.sleep(random.uniform(12.0, 24.0))
        else:
            # 50% Standard (1-2 notas) o 20% Deep (3-4 notas)
            num_articles = random.randint(1, 2) if archetype == "standard" else random.randint(3, 4)
            article_elements = await page.query_selector_all('a[href*="/articulo/"]')
            if article_elements:
                chosen_elements = random.sample(
                    article_elements[:10],
                    k=min(num_articles, len(article_elements))
                )
                for chosen_el in chosen_elements:
                    box = await chosen_el.bounding_box()
                    if box:
                        target_x = box["x"] + box["width"] * random.uniform(0.3, 0.7)
                        target_y = box["y"] + box["height"] * random.uniform(0.3, 0.7)
                        mouse_pos = await simulate_human_mouse(page, target_x, target_y, mouse_pos)
                        await asyncio.sleep(random.uniform(0.3, 0.8))
                        await page.mouse.click(target_x, target_y)

                        try:
                            await page.wait_for_load_state("domcontentloaded", timeout=25000)
                        except Exception:
                            pass

                        await asyncio.sleep(random.uniform(1.5, 3.0))
                        article_scroll = random.randint(750, 1600)
                        await simulate_human_scroll(page, article_scroll)

                        tx = random.randint(200, int(w * 0.7))
                        ty = random.randint(300, int(h * 0.6))
                        mouse_pos = await simulate_human_mouse(page, tx, ty, mouse_pos)

                        # Tiempo de lectura realista por artículo
                        read_pause = random.uniform(15.0, 30.0) if archetype == "standard" else random.uniform(25.0, 45.0)
                        await asyncio.sleep(read_pause)

        # Retardo final para asegurar emisión del beacon
        await asyncio.sleep(random.uniform(1.0, 2.0))

        # 5. Guardar cookies persistentes para simular usuario recurrente futuro
        try:
            await context.storage_state(path=profile_path)
        except Exception:
            pass

        return True

    except Exception as e:
        logger.debug(f"Error en sesión browser: {e}")
        return False
    finally:
        try:
            await page.close()
            await context.close()
        except Exception:
            pass


async def playwright_worker(worker_id: int, stats: dict, lock: asyncio.Lock, deadline: float, playwright_instance):
    """Worker continuo que lanza instancias de Playwright y navega orgánicamente."""
    browser = await playwright_instance.chromium.launch(
        headless=True,
        args=[
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-dev-shm-usage",
            "--use-gl=angle",
        ],
    )
    visit_count = 0
    try:
        while time.monotonic() < deadline:
            client_ip = generate_random_ip()
            profile = random.choice(DEVICE_PROFILES)
            profile_id = random.randint(1, TOTAL_PROFILE_POOL)
            success = await run_playwright_visit(browser, client_ip, profile, profile_id)
            visit_count += 1

            async with lock:
                if success:
                    stats["ok"] += 1
                else:
                    stats["fail"] += 1
                total = stats["ok"] + stats["fail"]

            if total % config.LOG_EVERY == 0:
                elapsed = time.time() - stats["start"]
                rate = total / elapsed if elapsed > 0 else 0
                circadian = get_circadian_factor()
                log.info(
                    f"🛡️  [BIOMÉTRICO] ✅ {stats['ok']:,} validadas | ❌ {stats['fail']:,} | "
                    f"🚀 {rate:.2f} vis/s | ⏱ {elapsed / 3600:.1f}h | ⏰ Circadiano: {circadian:.2f}x"
                )

            # ── Rotación de IP vía ADB (solo worker 0 para no colapsar el celular)
            if (
                worker_id == 0
                and IP_ROTATE_EVERY > 0
                and visit_count % IP_ROTATE_EVERY == 0
            ):
                log.info(f"📱 [ADB] Rotando IP del celular tras {visit_count} visitas...")
                new_ip = await asyncio.get_event_loop().run_in_executor(
                    None, lambda: rotate_mobile_ip(max_wait=14.0)
                )
                log.info(f"📱 [ADB] Nueva IP celular: {new_ip}")

            # Pausa natural modulada por el ritmo circadiano de la audiencia
            base_pause = random.uniform(1.8, 4.2)
            circadian = get_circadian_factor()
            await asyncio.sleep(base_pause / circadian)
    finally:
        await browser.close()


# ── Motor 2: Fallback aiohttp con Telemetría Sintética Biométricamente Válida
async def fallback_aiohttp_worker(worker_id: int, stats: dict, lock: asyncio.Lock, deadline: float):
    """Fallback ligero si Playwright no está instalado o en entornos restringidos."""
    import aiohttp
    import json

    connector = aiohttp.TCPConnector(limit=50, ssl=False)
    visit_count = 0
    async with aiohttp.ClientSession(connector=connector, timeout=aiohttp.ClientTimeout(total=45)) as session:
        while time.monotonic() < deadline:
            visit_count += 1
            client_ip = generate_random_ip()
            profile = random.choice(DEVICE_PROFILES)
            entry_section = random.choices(SECTIONS, weights=SECTION_WEIGHTS, k=1)[0]
            url = TARGET_URL + entry_section

            referrer = get_traffic_source()
            headers = {
                "User-Agent": profile["ua"],
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": profile.get("locale", "es-AR") + ",es;q=0.9,en;q=0.8",
                "DNT": "1",
            }
            if not USE_MOBILE_IP:
                headers["X-Forwarded-For"] = client_ip
                headers["X-Real-IP"] = client_ip
            if referrer:
                headers["Referer"] = referrer

            success = False
            try:
                # 1. Petición GET a la página
                async with session.get(url, headers=headers) as resp:
                    await resp.read()
                    if resp.status < 400:
                        success = True
                    else:
                        log.warning(f"HTTP GET {resp.status} on {url} (ref: {repr(headers.get('Referer'))})")
                        success = False

                # 2. Generación y envío de telemetría biométrica compatible con nuestro detector
                if success:
                    archetype = choose_session_archetype()
                    if archetype == "bounce":
                        sim_time = random.randint(12000, 24000)
                    elif archetype == "standard":
                        sim_time = random.randint(35000, 75000)
                    else:
                        sim_time = random.randint(80000, 160000)

                    # Simular curva de Bézier sintética para pasar el control anti-bot
                    p0 = (random.randint(100, 300), random.randint(100, 200))
                    p3 = (random.randint(400, 900), random.randint(300, 700))
                    trajectory = generate_bezier_trajectory(p0, p3, steps=random.randint(15, 25))
                    mouse_events = []
                    last_pt = p0
                    for pt in trajectory:
                        dx = pt[0] - last_pt[0]
                        dy = pt[1] - last_pt[1]
                        dt = random.randint(16, 40)
                        mouse_events.append({"dx": round(dx, 1), "dy": round(dy, 1), "dt": dt})
                        last_pt = pt

                    scroll_events = [
                        {"y": y, "speed": round(random.uniform(0.8, 2.5), 2), "dt": random.randint(50, 150)}
                        for y in range(200, random.randint(600, 1400), 250)
                    ]

                    beacon_data = {
                        "session_id": f"pm_{random.randint(100000, 999999)}_{int(time.time())}",
                        "path": entry_section,
                        "time_on_page": sim_time,
                        "canvas_hash": f"cv_{random.randint(100000, 999999):x}",
                        "webgl_renderer": profile.get("gpu_renderer", "ANGLE (NVIDIA, NVIDIA GeForce RTX 3060 Direct3D11 vs_5_0 ps_5_0, D3D11)"),
                        "webgl_vendor": profile.get("gpu_vendor", "Google Inc. (NVIDIA)"),
                        "screen": {
                            "width": profile["viewport"]["width"],
                            "height": profile["viewport"]["height"],
                            "colorDepth": 24,
                            "pixelRatio": 1.0,
                            "viewport": {"w": profile["viewport"]["width"], "h": profile["viewport"]["height"]},
                        },
                        "mouse_events": mouse_events,
                        "scroll_events": scroll_events,
                        "timezone_offset": 180 if "Buenos_Aires" in profile["timezone"] else -120,
                        "touch_support": False,
                        "platform": profile["platform"],
                        "language": profile["locale"],
                        "do_not_track": "1",
                    }

                    # Enviar baliza biométrica a /api/beacon
                    beacon_headers = dict(headers)
                    beacon_headers["Content-Type"] = "application/json"
                    async with session.post(
                        TARGET_URL + "/api/beacon",
                        headers=beacon_headers,
                        data=json.dumps(beacon_data)
                    ) as b_resp:
                        await b_resp.read()

            except Exception as e:
                log.error(f"Error in visit: {type(e).__name__}: {e}")
                success = False

            async with lock:
                if success:
                    stats["ok"] += 1
                else:
                    stats["fail"] += 1
                total = stats["ok"] + stats["fail"]

            if total % config.LOG_EVERY == 0:
                elapsed = time.time() - stats["start"]
                rate = total / elapsed if elapsed > 0 else 0
                circadian = get_circadian_factor()
                log.info(
                    f"📡 [TELEMETRÍA] ✅ {stats['ok']:,} | ❌ {stats['fail']:,} | "
                    f"🚀 {rate:.2f} vis/s | ⏱ {elapsed / 3600:.1f}h | ⏰ Circadiano: {circadian:.2f}x"
                )

            # Pausa natural modulada por el ritmo circadiano
            base_pause = random.uniform(0.6, 1.8)
            circadian = get_circadian_factor()

            # ── Rotación de IP vía ADB (solo worker 0)
            if (
                worker_id == 0
                and IP_ROTATE_EVERY > 0
                and visit_count % IP_ROTATE_EVERY == 0
            ):
                log.info(f"📱 [ADB] Rotando IP del celular tras {visit_count} visitas...")
                new_ip = await asyncio.get_event_loop().run_in_executor(
                    None, lambda: rotate_mobile_ip(max_wait=14.0)
                )
                log.info(f"📱 [ADB] Nueva IP celular: {new_ip}")

            await asyncio.sleep(base_pause / circadian)


# ── Función Principal ───────────────────────────────────────────────────────
async def main():
    target_url = TARGET_URL
    job_sec_env = os.environ.get("JOB_DURATION_SECONDS")
    duration = float(job_sec_env) if (job_sec_env and job_sec_env.strip()) else config.JOB_DURATION_SECONDS
    deadline = time.monotonic() + duration
    stats = {"ok": 0, "fail": 0, "start": time.time()}
    lock = asyncio.Lock()

    # Verificar si Playwright está instalado
    has_playwright = False
    playwright_module = None
    try:
        from playwright.async_api import async_playwright
        has_playwright = True
    except ImportError:
        has_playwright = False

    override_w = os.environ.get("OVERRIDE_WORKERS")
    if _workers_arg > 0:
        num_workers = _workers_arg
    elif override_w and override_w.strip().isdigit():
        num_workers = int(override_w.strip())
    elif USE_MOBILE_IP:
        # En modo módem celular USB con rotación 1 a 1, usamos 1 worker para garantizar
        # ejecución secuencial limpia (Visita -> Rotar IP -> Visita) sin choques ni cortes
        num_workers = 1
    else:
        num_workers = getattr(config, "BROWSER_WORKERS_PER_JOB", 3) if has_playwright else config.WORKERS_PER_JOB

    log.info("=" * 60)
    log.info("🛡️  PulsoMundial — Bot con Biometría y Verificación Anti-Bot")
    log.info(f"   Destino : {target_url}")
    log.info(f"   Motor   : {'Playwright Chromium (Headless Real)' if has_playwright else 'Fallback HTTP + Telemetría Sintética'}")
    log.info(f"   Workers : {num_workers} | Duración: {config.JOB_DURATION_SECONDS / 3600:.1f}h")
    log.info(f"   IP Modo : {'Módem USB Móvil 4G/5G (Rotación cada ' + str(IP_ROTATE_EVERY) + ' visitas)' if USE_MOBILE_IP else 'IPs Simuladas Residenciales'}")
    log.info("=" * 60)

    if has_playwright:
        async with async_playwright() as p:
            tasks = [
                asyncio.create_task(playwright_worker(i, stats, lock, deadline, p))
                for i in range(num_workers)
            ]
            await asyncio.gather(*tasks)
    else:
        tasks = [
            asyncio.create_task(fallback_aiohttp_worker(i, stats, lock, deadline))
            for i in range(num_workers)
        ]
        await asyncio.gather(*tasks)

    elapsed = time.time() - stats["start"]
    log.info("=" * 60)
    log.info("🏁 Sesión finalizada")
    log.info(f"   ✅ Validadas : {stats['ok']:,}")
    log.info(f"   ❌ Fallidas  : {stats['fail']:,}")
    log.info(f"   ⏱ Tiempo    : {elapsed / 3600:.2f}h")
    log.info("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
