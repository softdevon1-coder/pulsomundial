"""
traffic_bot.py — Simulador de tráfico web con Tor + Playwright
Genera visitas con IPs rotativas y comportamiento de navegador real.
"""

import asyncio
import random
import logging
import time
import sys
from datetime import datetime, timedelta
from typing import Optional

# ── Dependencias externas ──────────────────────────────────────────────────
try:
    from playwright.async_api import async_playwright, Browser, BrowserContext, Page
except ImportError:
    print("❌ Playwright no instalado. Ejecutá: pip install playwright && playwright install chromium")
    sys.exit(1)

try:
    import stem
    import stem.control
    import stem.process
except ImportError:
    print("❌ stem no instalado. Ejecutá: pip install stem")
    sys.exit(1)

import config

# ── Logging ────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(config.LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("traffic_bot")

# ── Contadores globales ────────────────────────────────────────────────────
stats = {
    "completed": 0,
    "failed": 0,
    "start_time": time.time(),
}
stats_lock = asyncio.Lock()

# ── User-Agents realistas ──────────────────────────────────────────────────
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14.5; rv:126.0) Gecko/20100101 Firefox/126.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
]

# ── Resoluciones de pantalla comunes ──────────────────────────────────────
VIEWPORTS = [
    {"width": 1920, "height": 1080},
    {"width": 1366, "height": 768},
    {"width": 1440, "height": 900},
    {"width": 1536, "height": 864},
    {"width": 1280, "height": 720},
    {"width": 375,  "height": 812},   # móvil
    {"width": 390,  "height": 844},   # iPhone 14
    {"width": 768,  "height": 1024},  # tablet
]


# ── Control de IP con Tor ──────────────────────────────────────────────────
def rotate_tor_ip() -> bool:
    """Solicita un nuevo circuito Tor (nueva IP de salida)."""
    try:
        with stem.control.Controller.from_port(port=config.TOR_CONTROL_PORT) as controller:
            if config.TOR_PASSWORD:
                controller.authenticate(password=config.TOR_PASSWORD)
            else:
                controller.authenticate()
            controller.signal(stem.Signal.NEWNYM)
            time.sleep(stem.control.Controller.get_newnym_wait(controller))
        return True
    except Exception as e:
        log.warning(f"No se pudo rotar IP de Tor: {e}")
        return False


async def get_current_tor_ip() -> Optional[str]:
    """Devuelve la IP actual de Tor (útil para debug)."""
    try:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "http://httpbin.org/ip",
                proxy=f"socks5://127.0.0.1:{config.TOR_SOCKS_PORT}",
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                data = await resp.json()
                return data.get("origin")
    except Exception:
        return None


# ── Comportamiento humano ──────────────────────────────────────────────────
async def human_scroll(page: Page) -> None:
    """Simula scroll humano: hacia abajo y a veces de vuelta arriba."""
    try:
        viewport_height = page.viewport_size["height"] if page.viewport_size else 768
        scroll_height = await page.evaluate("document.body.scrollHeight")
        
        position = 0
        while position < scroll_height:
            scroll_amount = random.randint(100, 400)
            position = min(position + scroll_amount, scroll_height)
            await page.evaluate(f"window.scrollTo({{top: {position}, behavior: 'smooth'}})")
            pause = random.uniform(config.SCROLL_PAUSE_MIN, config.SCROLL_PAUSE_MAX)
            await asyncio.sleep(pause)
        
        # A veces volver a subir un poco
        if random.random() < 0.3:
            scroll_back = random.randint(200, 600)
            await page.evaluate(f"window.scrollBy({{top: -{scroll_back}, behavior: 'smooth'}})")
            await asyncio.sleep(random.uniform(1, 2))
    except Exception:
        pass


async def human_mouse(page: Page) -> None:
    """Mueve el mouse a posiciones aleatorias."""
    try:
        viewport = page.viewport_size or {"width": 1280, "height": 720}
        for _ in range(random.randint(2, 5)):
            x = random.randint(50, viewport["width"] - 50)
            y = random.randint(50, viewport["height"] - 50)
            await page.mouse.move(x, y)
            await asyncio.sleep(random.uniform(0.3, 1.2))
    except Exception:
        pass


# ── Lógica de una visita ───────────────────────────────────────────────────
async def do_visit(browser: Browser, visit_num: int) -> bool:
    """
    Abre un contexto de navegador aislado, visita el sitio,
    simula comportamiento humano y cierra.
    """
    context: Optional[BrowserContext] = None
    page: Optional[Page] = None
    
    try:
        # Contexto con proxy Tor + user-agent y viewport aleatorios
        context = await browser.new_context(
            proxy={"server": f"socks5://127.0.0.1:{config.TOR_SOCKS_PORT}"},
            user_agent=random.choice(USER_AGENTS),
            viewport=random.choice(VIEWPORTS),
            locale=random.choice(["es-AR", "es-ES", "en-US", "pt-BR", "fr-FR"]),
            timezone_id=random.choice(["America/Argentina/Buenos_Aires", "Europe/Madrid", "America/New_York"]),
            java_script_enabled=True,
            bypass_csp=False,
        )
        
        page = await context.new_page()
        
        # Ocultar que es un bot (evasión básica de detección)
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
            Object.defineProperty(navigator, 'languages', { get: () => ['es-AR', 'es', 'en'] });
            window.chrome = { runtime: {} };
        """)
        
        # Visitar página principal
        await page.goto(config.TARGET_URL, wait_until="domcontentloaded", timeout=30_000)
        
        visit_start = time.time()
        
        # Simular comportamiento humano en la página principal
        if config.SIMULATE_SCROLL:
            await human_scroll(page)
        if config.SIMULATE_MOUSE:
            await human_mouse(page)
        
        # Navegar a páginas adicionales si están configuradas
        if config.EXTRA_PAGES:
            pages_to_visit = random.sample(
                config.EXTRA_PAGES,
                k=min(random.randint(1, 2), len(config.EXTRA_PAGES))
            )
            for extra_path in pages_to_visit:
                await asyncio.sleep(random.uniform(2, 5))
                try:
                    full_url = config.TARGET_URL.rstrip("/") + extra_path
                    await page.goto(full_url, wait_until="domcontentloaded", timeout=20_000)
                    if config.SIMULATE_SCROLL:
                        await human_scroll(page)
                    if config.SIMULATE_MOUSE:
                        await human_mouse(page)
                except Exception:
                    pass
        
        # Asegurar que la visita dure el tiempo mínimo configurado
        elapsed = time.time() - visit_start
        target_duration = random.uniform(config.VISIT_DURATION_MIN, config.VISIT_DURATION_MAX)
        remaining = target_duration - elapsed
        if remaining > 0:
            await asyncio.sleep(remaining)
        
        return True
    
    except Exception as e:
        log.debug(f"Visita {visit_num} fallida: {e}")
        return False
    
    finally:
        if page:
            try:
                await page.close()
            except Exception:
                pass
        if context:
            try:
                await context.close()
            except Exception:
                pass


# ── Worker: consume visitas de una cola ───────────────────────────────────
async def worker(browser: Browser, queue: asyncio.Queue, worker_id: int) -> None:
    while True:
        try:
            visit_num = queue.get_nowait()
        except asyncio.QueueEmpty:
            break
        
        # Rotar IP según configuración
        if config.ROTATE_IP_EVERY > 0 and visit_num % config.ROTATE_IP_EVERY == 0:
            rotate_tor_ip()
        
        success = await do_visit(browser, visit_num)
        
        async with stats_lock:
            if success:
                stats["completed"] += 1
            else:
                stats["failed"] += 1
            total_done = stats["completed"] + stats["failed"]
        
        # Mostrar estadísticas periódicamente
        if total_done % config.STATS_EVERY == 0:
            elapsed = time.time() - stats["start_time"]
            rate = total_done / elapsed if elapsed > 0 else 0
            remaining_visits = config.TOTAL_VISITS - total_done
            eta_seconds = remaining_visits / rate if rate > 0 else 0
            eta = str(timedelta(seconds=int(eta_seconds)))
            log.info(
                f"📊 Progreso: {total_done:,}/{config.TOTAL_VISITS:,} | "
                f"✅ {stats['completed']:,} | ❌ {stats['failed']:,} | "
                f"🚀 {rate:.1f} visitas/seg | ⏱ ETA: {eta}"
            )
        
        queue.task_done()


# ── Verificar que Tor está corriendo ──────────────────────────────────────
def check_tor_running() -> bool:
    """Verifica conectividad con el proxy SOCKS de Tor."""
    import socket
    try:
        sock = socket.create_connection(("127.0.0.1", config.TOR_SOCKS_PORT), timeout=3)
        sock.close()
        return True
    except Exception:
        return False


# ── Main ───────────────────────────────────────────────────────────────────
async def main():
    log.info("=" * 60)
    log.info("🤖 Web Traffic Bot arrancando")
    log.info(f"   Target : {config.TARGET_URL}")
    log.info(f"   Visitas: {config.TOTAL_VISITS:,}")
    log.info(f"   Workers: {config.CONCURRENT_BROWSERS}")
    log.info(f"   Duración/visita: {config.VISIT_DURATION_MIN}-{config.VISIT_DURATION_MAX}s")
    log.info("=" * 60)
    
    # Verificar Tor
    if not check_tor_running():
        log.error(
            "❌ No se puede conectar a Tor en el puerto "
            f"{config.TOR_SOCKS_PORT}.\n"
            "   Asegurate de tener Tor Browser o el Tor daemon corriendo.\n"
            "   Ver instrucciones en README.md"
        )
        sys.exit(1)
    
    log.info("✅ Tor detectado y disponible")
    
    # Poblar la cola con todos los números de visita
    queue: asyncio.Queue = asyncio.Queue()
    for i in range(1, config.TOTAL_VISITS + 1):
        await queue.put(i)
    
    stats["start_time"] = time.time()
    
    async with async_playwright() as pw:
        # Lanzar un navegador headless compartido entre workers
        browser = await pw.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
            ],
        )
        
        log.info(f"🌐 Navegador lanzado — iniciando {config.CONCURRENT_BROWSERS} workers")
        
        # Lanzar workers concurrentes
        workers = [
            asyncio.create_task(worker(browser, queue, wid))
            for wid in range(config.CONCURRENT_BROWSERS)
        ]
        
        await asyncio.gather(*workers)
        await browser.close()
    
    # Resumen final
    elapsed = time.time() - stats["start_time"]
    log.info("=" * 60)
    log.info("🏁 Finalizado")
    log.info(f"   ✅ Completadas : {stats['completed']:,}")
    log.info(f"   ❌ Fallidas    : {stats['failed']:,}")
    log.info(f"   ⏱ Tiempo total: {str(timedelta(seconds=int(elapsed)))}")
    log.info(f"   🚀 Promedio   : {stats['completed']/elapsed:.2f} visitas/seg")
    log.info("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
