"""
visitor.py — Simulador de visitas humanas para PulsoMundial
Comportamiento simulado:
  1. Carga la sección aleatoria (home, mundo, economia, etc.)
  2. Descarga CSS, JS e imágenes de la página
  3. "Lee" durante unos segundos (pausa de lectura)
  4. Hace clic en 1-3 artículos de la página
  5. Lee cada artículo con su tiempo correspondiente
  6. A veces navega a otra sección antes de salir
"""

import asyncio
import random
import time
import logging
import sys
import os
import re
from urllib.parse import urljoin, urlparse
from typing import Optional

import aiohttp
from bs4 import BeautifulSoup

import config

TARGET_URL = os.environ.get("TARGET_URL", config.TARGET_URL)

# ── Logging ────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [JOB-%(job_id)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
JOB_ID = os.environ.get("JOB_ID", "local")
logger = logging.getLogger("visitor")
log = logging.LoggerAdapter(logger, {"job_id": JOB_ID})

# ── User-Agents realistas ──────────────────────────────────────────────────
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14.6; rv:130.0) Gecko/20100101 Firefox/130.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Safari/605.1.15",
    "Mozilla/5.0 (Linux; Android 14; Pixel 9) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 14; Samsung Galaxy S24) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Mobile Safari/537.36",
]

# ── Referrers realistas para un sitio de noticias ─────────────────────────
REFERRERS = [
    "",                                      # directo (escribió la URL)
    "https://www.google.com/",
    "https://www.google.com.ar/",
    "https://www.google.es/",
    "https://www.google.com.mx/",
    "https://www.bing.com/",
    "https://duckduckgo.com/",
    "https://www.facebook.com/",
    "https://www.instagram.com/",
    "https://t.co/",                         # Twitter/X
    "https://www.linkedin.com/",
    "https://www.reddit.com/",
    "https://news.google.com/",
    "https://www.whatsapp.com/",             # link compartido por WhatsApp
]

# ── Secciones del sitio de noticias ───────────────────────────────────────
SECTIONS = ["/", "/mundo", "/economia", "/tecnologia", "/deportes", "/salud", "/ciencia"]

# Pesos de probabilidad (home recibe más tráfico)
SECTION_WEIGHTS = [30, 15, 15, 15, 10, 8, 7]

ACCEPT_LANGUAGES = [
    "es-AR,es;q=0.9,en;q=0.8",
    "es-ES,es;q=0.9,en;q=0.8",
    "es-MX,es;q=0.9,en;q=0.8",
    "en-US,en;q=0.9,es;q=0.8",
    "pt-BR,pt;q=0.9,es;q=0.7",
]


def generate_random_ip() -> str:
    """Genera una dirección IPv4 pública y realista de distintos proveedores globales."""
    pool = random.choice([
        # Argentina / América Latina (Telecom, Fibertel, Movistar, Claro)
        (181, random.randint(16, 220)),
        (186, random.randint(10, 240)),
        (190, random.randint(1, 245)),
        (200, random.randint(5, 125)),
        (201, random.randint(15, 250)),
        # España / Europa (Telefónica, Vodafone, Orange)
        (80, random.randint(1, 250)),
        (81, random.randint(1, 250)),
        (88, random.randint(1, 250)),
        # Estados Unidos (Comcast, AT&T, Verizon, Spectrum)
        (24, random.randint(1, 250)),
        (67, random.randint(1, 250)),
        (73, random.randint(1, 250)),
        (98, random.randint(1, 250)),
        # México / Brasil (Telmex, Totalplay, Vivo, Claro)
        (187, random.randint(10, 240)),
        (189, random.randint(10, 240)),
        (177, random.randint(10, 240)),
    ])
    return f"{pool[0]}.{pool[1]}.{random.randint(1, 254)}.{random.randint(1, 254)}"


def build_headers(user_agent: str, client_ip: str, referrer: Optional[str] = None,
                  is_asset: bool = False, is_subpage: bool = False) -> dict:
    """Headers HTTP realistas con IP única por visitante."""
    if is_asset:
        return {
            "User-Agent": user_agent,
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Referer": TARGET_URL,
            "X-Forwarded-For": client_ip,
            "X-Real-IP": client_ip,
            "CF-Connecting-IP": client_ip,
        }
    headers = {
        "User-Agent": user_agent,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": random.choice(ACCEPT_LANGUAGES),
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin" if is_subpage else ("cross-site" if referrer else "none"),
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
        "DNT": random.choice(["1", "0"]),
        "X-Forwarded-For": client_ip,
        "X-Real-IP": client_ip,
        "CF-Connecting-IP": client_ip,
    }
    if referrer:
        headers["Referer"] = referrer
    return headers


def extract_assets(base_url: str, html: str) -> list[str]:
    """Extrae URLs de CSS, JS e imágenes del HTML."""
    soup = BeautifulSoup(html, "html.parser")
    assets = []
    base_domain = urlparse(base_url).netloc

    for tag in soup.find_all("link", rel=lambda r: r and "stylesheet" in r):
        href = tag.get("href", "")
        if href and not href.startswith("data:"):
            assets.append(urljoin(base_url, href))

    for tag in soup.find_all("script", src=True):
        src = tag.get("src", "")
        if src and not src.startswith("data:"):
            assets.append(urljoin(base_url, src))

    images = soup.find_all("img", src=True)[: config.MAX_IMAGES_PER_PAGE]
    for tag in images:
        src = tag.get("src", "")
        if src and not src.startswith("data:"):
            assets.append(urljoin(base_url, src))

    # Solo assets del mismo dominio o CDNs externos (Bootstrap, FontAwesome, etc.)
    filtered = []
    for a in assets:
        domain = urlparse(a).netloc
        if domain in ("", base_domain) or any(
            cdn in domain for cdn in ["cdn.jsdelivr", "cdnjs.cloudflare", "fonts.googleapis",
                                       "fonts.gstatic", "picsum.photos"]
        ):
            filtered.append(a)

    return filtered[: config.MAX_ASSETS_PER_PAGE]


def extract_article_links(base_url: str, html: str) -> list[str]:
    """
    Extrae links a artículos de la página.
    Busca hrefs que contengan '/articulo/' (rutas de artículos de PulsoMundial).
    """
    soup = BeautifulSoup(html, "html.parser")
    base_domain = urlparse(base_url).netloc
    links = set()

    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]
        full_url = urljoin(base_url, href)
        # Solo links de artículos del mismo sitio
        if urlparse(full_url).netloc == base_domain and "/articulo/" in full_url:
            links.add(full_url)

    return list(links)


async def fetch_assets(session: aiohttp.ClientSession, urls: list[str], user_agent: str, client_ip: str) -> None:
    """Descarga assets en paralelo con la IP del visitante."""
    if not urls or not config.DOWNLOAD_ASSETS:
        return

    headers = build_headers(user_agent, client_ip, is_asset=True)

    async def fetch_one(url: str) -> None:
        try:
            async with session.get(url, headers=headers,
                                   timeout=aiohttp.ClientTimeout(total=8)) as resp:
                await resp.read()
        except Exception:
            pass

    await asyncio.gather(*[fetch_one(u) for u in urls], return_exceptions=True)


async def simulate_reading(min_s: float, max_s: float, elapsed: float) -> None:
    """Simula lectura humana: tiempo dividido en pausas aleatorias."""
    target = random.uniform(min_s, max_s)
    remaining = max(0.0, target - elapsed)
    if remaining <= 0:
        return
    num_pauses = random.randint(3, 6)
    for _ in range(num_pauses):
        fraction = random.uniform(0.1, 0.4)
        pause = remaining * fraction
        await asyncio.sleep(pause)
        remaining -= pause
        if remaining <= 0:
            break
    if remaining > 0:
        await asyncio.sleep(remaining)


async def fetch_page(
    session: aiohttp.ClientSession,
    url: str,
    user_agent: str,
    client_ip: str,
    referrer: Optional[str],
    is_subpage: bool = False,
) -> Optional[str]:
    """Descarga una página y sus assets. Devuelve el HTML o None si falla."""
    headers = build_headers(user_agent, client_ip, referrer=referrer, is_subpage=is_subpage)
    try:
        async with session.get(url, headers=headers,
                               timeout=aiohttp.ClientTimeout(total=30)) as resp:
            if resp.status >= 400:
                return None
            html = await resp.text(errors="replace")

        # Simula tiempo de procesamiento del browser
        await asyncio.sleep(random.uniform(0.4, 1.2))

        # Descarga assets en paralelo
        assets = extract_assets(url, html)
        await fetch_assets(session, assets, user_agent, client_ip)

        return html
    except Exception:
        return None


async def do_visit(session: aiohttp.ClientSession) -> bool:
    """
    Simula una visita completa con navegación realista:
    Cada visitante tiene una IP pública única generada en cada sesión.
    1. Elige una sección aleatoria de entrada
    2. Carga la sección + assets con su IP única
    3. Lee la sección (pausa)
    4. Hace clic en 1-3 artículos y los lee con la misma IP
    5. A veces navega a otra sección antes de salir
    """
    user_agent = random.choice(USER_AGENTS)
    client_ip = generate_random_ip()
    referrer = random.choice(REFERRERS) or None

    # ── Paso 1: Elegir página de entrada ──────────────────────────────────
    entry_section = random.choices(SECTIONS, weights=SECTION_WEIGHTS, k=1)[0]
    entry_url = TARGET_URL.rstrip("/") + entry_section

    t0 = time.monotonic()
    html = await fetch_page(session, entry_url, user_agent, client_ip, referrer)
    if html is None:
        return False

    # ── Paso 2: Leer la sección (scroll inicial) ──────────────────────────
    await simulate_reading(
        config.READING_TIME_MIN * 0.4,
        config.READING_TIME_MAX * 0.4,
        time.monotonic() - t0,
    )

    # ── Paso 3: Hacer clic en artículos ───────────────────────────────────
    article_links = extract_article_links(entry_url, html)

    if article_links:
        num_articles = random.choices(
            [1, 2, 3],
            weights=[50, 35, 15],  # mayoría lee 1, algunos leen 2-3
            k=1
        )[0]
        articles_to_read = random.sample(
            article_links,
            k=min(num_articles, len(article_links))
        )

        for article_url in articles_to_read:
            # Pausa antes de "clickear" el artículo (como un humano leyendo el título)
            await asyncio.sleep(random.uniform(config.NAV_PAUSE_MIN, config.NAV_PAUSE_MAX))

            t_article = time.monotonic()
            article_html = await fetch_page(
                session,
                article_url,
                user_agent,
                client_ip,
                referrer=entry_url,       # Referer = la sección de donde viene
                is_subpage=True,
            )

            if article_html:
                # Lee el artículo completo
                await simulate_reading(
                    config.READING_TIME_MIN,
                    config.READING_TIME_MAX,
                    time.monotonic() - t_article,
                )

                # 20% de chance: hace clic en un artículo relacionado desde el artículo actual
                if random.random() < 0.20:
                    related_links = extract_article_links(article_url, article_html)
                    related_links = [l for l in related_links if l != article_url]
                    if related_links:
                        next_article = random.choice(related_links)
                        await asyncio.sleep(random.uniform(2, 5))
                        t_related = time.monotonic()
                        related_html = await fetch_page(
                            session, next_article, user_agent, client_ip,
                            referrer=article_url, is_subpage=True
                        )
                        if related_html:
                            await simulate_reading(
                                config.READING_TIME_MIN * 0.5,
                                config.READING_TIME_MAX * 0.6,
                                time.monotonic() - t_related,
                            )

    # ── Paso 4: A veces navega a otra sección antes de irse ───────────────
    if random.random() < 0.30:
        other_sections = [s for s in SECTIONS if s != entry_section]
        next_section = random.choice(other_sections)
        next_url = TARGET_URL.rstrip("/") + next_section

        await asyncio.sleep(random.uniform(1.5, 4))
        t_sec = time.monotonic()
        sec_html = await fetch_page(
            session, next_url, user_agent, client_ip,
            referrer=entry_url, is_subpage=True
        )
        if sec_html:
            await simulate_reading(
                config.READING_TIME_MIN * 0.3,
                config.READING_TIME_MAX * 0.3,
                time.monotonic() - t_sec,
            )

    return True


# ── Worker ─────────────────────────────────────────────────────────────────
async def worker(worker_id: int, stats: dict, lock: asyncio.Lock, deadline: float) -> None:
    connector = aiohttp.TCPConnector(limit=1, ssl=False)
    async with aiohttp.ClientSession(connector=connector,
                                     timeout=aiohttp.ClientTimeout(total=60)) as session:
        while time.monotonic() < deadline:
            success = await do_visit(session)
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
                    f"✅ {stats['ok']:,} | ❌ {stats['fail']:,} | "
                    f"🚀 {rate:.2f} vis/seg | "
                    f"⏱ {elapsed / 3600:.1f}h transcurridas"
                )
            await asyncio.sleep(random.uniform(0.3, 1.5))


# ── Main ───────────────────────────────────────────────────────────────────
async def main():
    target_url = os.environ.get("TARGET_URL", config.TARGET_URL)
    override_w = os.environ.get("OVERRIDE_WORKERS")
    if override_w and override_w.strip().isdigit():
        num_workers = int(override_w.strip())
    else:
        num_workers = config.WORKERS_PER_JOB

    deadline = time.monotonic() + config.JOB_DURATION_SECONDS
    stats = {"ok": 0, "fail": 0, "start": time.time()}
    lock = asyncio.Lock()

    log.info("=" * 55)
    log.info(f"🗞️  PulsoMundial Traffic Bot arrancando")
    log.info(f"   Target : {target_url}")
    log.info(f"   Workers: {num_workers} | Duración: {config.JOB_DURATION_SECONDS / 3600:.1f}h")
    log.info(f"   Secciones: {', '.join(SECTIONS)}")
    log.info("=" * 55)

    tasks = [
        asyncio.create_task(worker(i, stats, lock, deadline))
        for i in range(num_workers)
    ]
    await asyncio.gather(*tasks)

    elapsed = time.time() - stats["start"]
    log.info("=" * 55)
    log.info(f"🏁 Job finalizado")
    log.info(f"   ✅ Exitosas : {stats['ok']:,}")
    log.info(f"   ❌ Fallidas : {stats['fail']:,}")
    log.info(f"   ⏱ Tiempo   : {elapsed / 3600:.2f}h")
    rate = stats['ok'] / elapsed if elapsed > 0 else 0
    log.info(f"   🚀 Rate     : {rate:.2f} vis/seg")
    log.info("=" * 55)


if __name__ == "__main__":
    asyncio.run(main())
