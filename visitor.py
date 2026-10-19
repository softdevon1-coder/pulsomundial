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
from typing import Optional, List, Tuple
from urllib.parse import urljoin, urlparse

import config

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

REFERRERS = [
    "",
    "https://www.google.com/",
    "https://www.google.com.ar/",
    "https://www.google.es/",
    "https://www.bing.com/",
    "https://t.co/",
    "https://www.facebook.com/",
    "https://news.google.com/",
]

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


async def run_playwright_visit(browser, client_ip: str, profile: dict) -> bool:
    """Ejecuta una visita completa en un contexto de navegador real."""
    referrer = random.choice(REFERRERS)
    headers = {
        "X-Forwarded-For": client_ip,
        "X-Real-IP": client_ip,
        "Accept-Language": profile.get("locale", "es-AR") + ",es;q=0.9,en;q=0.8",
        "DNT": "1",
    }
    if referrer:
        headers["Referer"] = referrer

    context = await browser.new_context(
        user_agent=profile["ua"],
        viewport=profile["viewport"],
        locale=profile["locale"],
        timezone_id=profile["timezone"],
        extra_http_headers=headers,
    )

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
        scroll_px = random.randint(450, 1200)
        await simulate_human_scroll(page, scroll_px)

        # 4. Exploración y clic en artículos
        # Busca enlaces de artículos
        article_elements = await page.query_selector_all('a[href*="/articulo/"]')
        if article_elements and random.random() < config.SUBPAGE_PROBABILITY:
            # Selecciona un artículo
            chosen_el = random.choice(article_elements[:8])
            box = await chosen_el.bounding_box()
            if box:
                # Mueve el mouse de forma curva hacia el botón o título
                target_x = box["x"] + box["width"] * random.uniform(0.3, 0.7)
                target_y = box["y"] + box["height"] * random.uniform(0.3, 0.7)
                mouse_pos = await simulate_human_mouse(page, target_x, target_y, mouse_pos)

                # Pausa previa al clic (deliberación cognitiva)
                await asyncio.sleep(random.uniform(0.3, 0.8))
                await page.mouse.click(target_x, target_y)

                # Espera carga del artículo
                try:
                    await page.wait_for_load_state("domcontentloaded", timeout=25000)
                except Exception:
                    pass

                # Lectura del artículo: lectura progresiva hacia abajo
                await asyncio.sleep(random.uniform(1.5, 3.0))
                article_scroll = random.randint(800, 1800)
                await simulate_human_scroll(page, article_scroll)

                # Micro-movimiento en el artículo
                tx = random.randint(200, int(w * 0.7))
                ty = random.randint(300, int(h * 0.6))
                mouse_pos = await simulate_human_mouse(page, tx, ty, mouse_pos)

                # Pausa final de lectura
                await asyncio.sleep(random.uniform(4.0, 10.0))

        # El script de telemetría inyectado en base.html se encarga de enviar el beacon
        # Forzar un pequeño retardo antes de cerrar para asegurar el envío de la señal
        await asyncio.sleep(random.uniform(1.0, 2.0))
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
    try:
        while time.monotonic() < deadline:
            client_ip = generate_random_ip()
            profile = random.choice(DEVICE_PROFILES)
            success = await run_playwright_visit(browser, client_ip, profile)

            async with lock:
                if success:
                    stats["ok"] += 1
                else:
                    stats["fail"] += 1
                total = stats["ok"] + stats["fail"]

            if total % config.LOG_EVERY == 0:
                elapsed = time.time() - stats["start"]
                rate = total / elapsed if elapsed > 0 else 0
                log.info(
                    f"🛡️  [BIOMÉTRICO] ✅ {stats['ok']:,} validadas | ❌ {stats['fail']:,} | "
                    f"🚀 {rate:.2f} vis/s | ⏱ {elapsed / 3600:.1f}h"
                )

            # Pausa natural entre sesiones consecutivas del mismo worker
            await asyncio.sleep(random.uniform(1.5, 4.0))
    finally:
        await browser.close()


# ── Motor 2: Fallback aiohttp con Telemetría Sintética Biométricamente Válida
async def fallback_aiohttp_worker(worker_id: int, stats: dict, lock: asyncio.Lock, deadline: float):
    """Fallback ligero si Playwright no está instalado o en entornos restringidos."""
    import aiohttp
    import json

    connector = aiohttp.TCPConnector(limit=50, ssl=False)
    async with aiohttp.ClientSession(connector=connector, timeout=aiohttp.ClientTimeout(total=45)) as session:
        while time.monotonic() < deadline:
            client_ip = generate_random_ip()
            profile = random.choice(DEVICE_PROFILES)
            entry_section = random.choices(SECTIONS, weights=SECTION_WEIGHTS, k=1)[0]
            url = TARGET_URL + entry_section

            headers = {
                "User-Agent": profile["ua"],
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": profile.get("locale", "es-AR") + ",es;q=0.9,en;q=0.8",
                "X-Forwarded-For": client_ip,
                "X-Real-IP": client_ip,
                "DNT": "1",
            }

            success = False
            try:
                # 1. Petición GET a la página
                async with session.get(url, headers=headers) as resp:
                    await resp.read()
                    if resp.status < 400:
                        success = True
                    else:
                        success = False

                # 2. Generación y envío de telemetría biométrica compatible con nuestro detector
                if success:
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
                        "time_on_page": random.randint(18000, 45000),
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
                log.info(
                    f"📡 [TELEMETRÍA] ✅ {stats['ok']:,} | ❌ {stats['fail']:,} | "
                    f"🚀 {rate:.2f} vis/s | ⏱ {elapsed / 3600:.1f}h"
                )

            await asyncio.sleep(random.uniform(0.4, 1.2))


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
    if override_w and override_w.strip().isdigit():
        num_workers = int(override_w.strip())
    else:
        num_workers = getattr(config, "BROWSER_WORKERS_PER_JOB", 3) if has_playwright else config.WORKERS_PER_JOB

    log.info("=" * 60)
    log.info("🛡️  PulsoMundial — Bot con Biometría y Verificación Anti-Bot")
    log.info(f"   Destino : {target_url}")
    log.info(f"   Motor   : {'Playwright Chromium (Headless Real)' if has_playwright else 'Fallback HTTP + Telemetría Sintética'}")
    log.info(f"   Workers : {num_workers} | Duración: {config.JOB_DURATION_SECONDS / 3600:.1f}h")
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
