# 🗞️ PulsoMundial — Portal de Noticias Globales + Bot de Tráfico Inteligente

Sistema web integral: **Portal internacional de noticias completo** (estilo BBC / El País / Reuters) con **auditoría de tráfico en tiempo real** y **bot simulador en la nube** con comportamiento humano interactivo (navega secciones, descarga contenidos y hace clic en artículos).

Todo diseñado para desplegarse de forma **100% gratuita** en la nube (Render.com + GitHub Actions).

---

## 🌐 Estructura del Portal: PulsoMundial

El portal cuenta con diseño editorial oscuro, marquesina de noticias urgentes en tiempo real, metadatos enriquecidos y 36 artículos de actualidad mundial distribuidos en 6 grandes secciones:

| Sección / Pestaña | Ruta | Temática |
|---|---|---|
| 🏠 **Portada Principal** | `/` | Noticia principal de cabecera, grilla destacada, sidebar de última hora y previas de cada categoría |
| 🌍 **Mundo** | `/mundo` | Geopolítica, cumbres internacionales, crisis humanitarias y diplomacia |
| 💰 **Economía** | `/economia` | Bancos centrales, criptoactivos institucionales, comercio global y mercados |
| 💻 **Tecnología** | `/tecnologia` | Regulación de IA, semiconductores cuánticos, ciberseguridad y realidad mixta |
| ⚽ **Deportes** | `/deportes` | Mundial 2026, Champions League, tenis, Fórmula 1 y Juegos Olímpicos |
| 🏥 **Salud** | `/salud` | Vacunas universales, neurotecnología médica, longevidad y telemedicina |
| 🔬 **Ciencia** | `/ciencia` | Fusión nuclear neta, telescopios espaciales, misiones a Marte y cambio climático |
| 📖 **Páginas de Noticia** | `/articulo/<slug>` | Cuerpo editorial completo, autor, tiempo de lectura, tags y artículos relacionados |
| 📊 **Panel de Analítica** | `/analytics` | Centro de telemetría y auditoría en tiempo real con contadores y gráficos interactivos |

---

## 🤖 Cómo funciona el Bot Simulador de Tráfico

A diferencia de los scripts convencionales que sólo hacen solicitudes vacías, este bot simula **comportamiento humano verídico**:

1. **Selección de Sección:** El bot aterriza en la Portada (30% de probabilidad) o en alguna de las 6 secciones temáticas.
2. **Descarga de Recursos:** Descarga el código HTML y los archivos CSS, JS e imágenes para registrar actividad de red completa.
3. **Pausa de Lectura Humana:** Simula el tiempo que una persona tarda en observar la página (entre 20 y 50 segundos en pausas fraccionadas).
4. **Interacción y Clic en Artículos:** Analiza los enlaces de la página y **hace clic en 1, 2 o 3 noticias**. Abre el artículo individual (`/articulo/...`), lo lee y carga los recursos correspondientes con cabeceras `Referer` y `same-origin` fidedignas.
5. **Navegación Profunda:** 20% de las veces salta a un artículo relacionado desde dentro de la nota, y 30% de las veces navega a otra sección antes de finalizar la sesión.
6. **Huella Digital Realista:** Alterna User-Agents de Chrome, Safari, Firefox y Edge en Windows, Mac, Linux, iPhone y Android, con idiomas de cabecera internacionales y fuentes de referencia simuladas (Google, Bing, X/Twitter, WhatsApp, etc.).

---

## 🗺️ Arquitectura Cloud (100% Gratis)

```
┌────────────────────────────────────────────────────────┐
│           GitHub (Repositorio Público)                 │
│                                                        │
│  ┌─────────────────────────┐  ┌─────────────────────┐  │
│  │   .github/workflows/    │  │       webapp/       │  │
│  │   traffic.yml           │  │   app.py (Flask)    │  │
│  │   (Corre 4 veces al día)│  │   templates/        │  │
│  │                         │  │     base.html       │  │
│  │   visitor.py            │  │     home.html       │  │
│  │   config.py             │  │     section.html    │  │
│  │   requirements.txt      │  │     article.html    │  │
│  │                         │  │     analytics.html  │  │
│  └───────────┬─────────────┘  └──────────┬──────────┘  │
└──────────────┼───────────────────────────┼─────────────┘
               │                           │ Deploy automático
               │ 250 navegadores           ▼
               │ simultáneos        ┌─────────────┐
               └───────────────────►│ Render.com  │ (Hosting gratuito)
                                    │ Tu portal   │
                                    └──────┬──────┘
                                           │
                                           ▼
                                 /analytics (En Vivo)
```

---

## 🚀 Guía de Puesta en Marcha (Paso a Paso)

### Paso 1: Crear el Repositorio en GitHub

1. Ingresá en [github.com/new](https://github.com/new).
2. Nombre del repositorio: `pulsomundial` (o el nombre que prefieras).
3. Seleccioná **Público** (*Public*) — obligatorio para tener minutos ilimitados de GitHub Actions gratis.
4. Hacé clic en **Create repository**.
5. Desde la consola en tu máquina, subí los archivos:

```bash
cd web-traffic-bot
git init
git add .
git commit -m "feat: PulsoMundial news portal and traffic bot"
git branch -M main
git remote add origin https://github.com/TU-USUARIO/pulsomundial.git
git push -u origin main
```

---

### Paso 2: Publicar la Página Web en Render.com (Gratis)

1. Creá una cuenta gratuita en [render.com](https://render.com) (podés iniciar sesión con tu GitHub).
2. En el panel de Render, hacé clic en **"New +"** y elegí **"Web Service"**.
3. Seleccioná tu repositorio de GitHub `pulsomundial`.
4. Completá los campos con esta configuración:

| Parámetro | Valor Exacto |
|---|---|
| **Name** | `pulsomundial` (o el subdominio que quieras) |
| **Region** | Oregon o Frankfurt (cualquiera) |
| **Branch** | `main` |
| **Root Directory** | `webapp` |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn app:app` |
| **Instance Type** | `Free` |

5. Hacé clic en **"Create Web Service"**.
6. En 2-3 minutos tu sitio estará en línea con una dirección HTTPS pública, por ejemplo:
   `https://pulsomundial.onrender.com`

---

### Paso 3: Configurar la URL en el Bot

Podés hacerlo de cualquiera de estas dos formas:

- **Opción A (Recomendada):** Editá [`config.py`](config.py) y colocá tu dirección:
  ```python
  TARGET_URL = "https://pulsomundial.onrender.com"
  ```
  Guardá los cambios y subilos:
  ```bash
  git add config.py
  git commit -m "fix: update production target url"
  git push
  ```

- **Opción B (Sin editar código):** En tu repositorio de GitHub, andá a **Settings** > **Secrets and variables** > **Actions** > **Variables** y creá una variable llamada `TARGET_URL` con el valor de tu URL de Render.

---

### Paso 4: Activar los Bots en GitHub Actions

1. En tu repositorio de GitHub, ingresá a la pestaña **Actions**.
2. Si aparece un aviso de confirmación, presioná **"I understand my workflows, go ahead and enable them"**.
3. Seleccioná el workflow **"Web Traffic Bot"** en el panel izquierdo.
4. Para iniciarlo inmediatamente sin esperar al reloj:
   - Hacé clic en el desplegable **Run workflow**.
   - Presioná el botón verde **Run workflow**.
5. Verás 10 jobs paralelos corriendo concurrentemente de forma autónoma. El cron automático se encargará de renovar las visitas 4 veces al día (cubriendo las 24 horas del día).

---

### Paso 5: Supervisar las Visitas en Directo

Abrí en tu navegador:
```
https://pulsomundial.onrender.com/analytics
```

El panel de control te mostrará:
- Contador de **Visitas Hoy**, **Última Hora**, **IPs Activas (5 min)** y **Total Histórico** (con actualización automática cada 10 segundos).
- Gráficos interactivos de distribución horaria, diaria y por navegadores.
- Tablas de las noticias más leídas y fuentes de tráfico.
- Tabla de **telemetría en vivo** con las últimas 100 peticiones con IP, hora, página solicitada y User-Agent.

---

## 📈 Proyección y Capacidad

| Configuración | Concurrencia | Visitas Estimadas / Día |
|---|---|---|
| **10 jobs × 25 workers** (Por defecto) | 250 sesiones activas | **~250.000 a 320.000 visitas/día** ✅ |
| **10 jobs × 15 workers** | 150 sesiones activas | ~180.000 visitas/día |
| **10 jobs × 35 workers** | 350 sesiones activas | ~400.000+ visitas/día |

> La concurrencia distribuida en la nube de GitHub Actions evita la suspensión del servicio gratuito de Render, garantizando disponibilidad 24/7.
