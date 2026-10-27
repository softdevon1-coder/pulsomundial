"""
CF Bot WiFi — Edición PC (Windows Desktop)
Automatización de Visitas Orgánicas con Rotación de Módem de Fibra Óptica / Enchufe Inteligente
"""

import sys
import os
import shutil
import time
import json
import random
import threading
import subprocess
import urllib.request
import urllib.parse
import base64
import socket
import ssl
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox

# Contexto SSL para aceptar certificados autofirmados de módems
ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE

# Soporte UTF-8 en consola de Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cfbot_wifi_config.json")
DEFAULT_TARGET_URL = "https://criteriofinanciero.onrender.com"

PATHS = [
    "/",
    "/guias",
    "/comparativas",
    "/mercados",
    "/calculadoras/interes-compuesto",
    "/calculadoras/rendimiento-billeteras",
    "/calculadoras/conversor-dolar",
    "/sobre-nosotros",
    "/articulo/como-invertir-en-cedears-argentina-guia-paso-a-paso",
    "/articulo/mejores-brokers-argentina-comparativa-comisiones",
    "/articulo/que-billetera-virtual-paga-mas-tasa-argentina",
    "/articulo/como-comprar-dolar-mep-home-banking-sin-cepo",
    "/articulo/dolar-cripto-como-comprar-usdt-pesos-argentinos",
    "/articulo/fondos-comunes-inversion-fci-guia-completa",
    "/articulo/resena-completa-balanz-capital-opiniones-comisiones",
    "/articulo/invertironline-iol-analisis-cuenta-remunerada-costos",
    "/articulo/como-salir-de-deudas-tarjeta-credito-metodo-bola-nieve",
    "/articulo/staking-criptomonedas-rendimientos-en-dolares-pasivos",
    "/articulo/bienes-personales-inversiones-exentas-argentina-2026",
    "/articulo/lemon-cash-vs-belo-vs-buenbit-mejor-tarjeta-cripto",
    "/articulo/bonos-soberanos-al30-gd30-como-operar-calcular-tir",
    "/articulo/obligaciones-negociables-como-cobrar-renta-en-dolares",
    "/articulo/calculadora-inflacion-perdida-poder-adquisitivo",
    "/articulo/plazo-fijo-tradicional-vs-plazo-fijo-uva-cual-conviene-2026",
    "/articulo/como-enviar-dolares-exterior-argentina-metodos-legales",
    "/articulo/cuenta-bancaria-en-usa-desde-argentina-abrir-online",
    "/articulo/brecha-cambiaria-explicada-oficial-mep-ccl-blue",
    "/articulo/7-errores-mas-comunes-al-empezar-a-invertir-evitarlos"
]

MODEM_BRANDS = [
    "Movistar HGU (Smart WiFi / Askey / MitraStar)",
    "Huawei (HG8245 / ONT Fibra)",
    "ZTE (F660 / F670 / F680)",
    "Sagemcom (Fast 3890 / 5655)",
    "TP-Link / Genérico"
]


def find_browser_path():
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe")
    ]
    for p in chrome_paths:
        if os.path.exists(p):
            return p, "chrome"

    edge_paths = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
    ]
    for p in edge_paths:
        if os.path.exists(p):
            return p, "edge"

    return None, None


class ModemRebooter:
    @staticmethod
    def reboot(use_plug, plug_url, host, user, password, brand, log_func):
        if use_plug:
            return ModemRebooter.trigger_smart_plug(plug_url, log_func)
        else:
            return ModemRebooter.trigger_modem(host, user, password, brand, log_func)

    @staticmethod
    def trigger_smart_plug(raw_url, log_func):
        if not raw_url or not raw_url.strip():
            log_func("⚠ Error: URL o IP del Enchufe Inteligente vacía.")
            return False

        target = raw_url.strip()
        if not target.startswith("http://") and not target.startswith("https://"):
            target = "http://" + target

        log_func(f"🔌 Enviando orden de corte de energía al enchufe: {target}")
        ok = ModemRebooter.send_request(target, "POST", None, None, log_func)
        if not ok:
            ok = ModemRebooter.send_request(target, "GET", None, None, log_func)

        if not ok and "?" not in target and len(target.split("/")) <= 4:
            clean = target.rstrip("/")
            log_func("Probando endpoint Shelly (/relay/0?turn=toggle)...")
            ok = ModemRebooter.send_request(clean + "/relay/0?turn=toggle", "GET", None, None, log_func)
            if not ok:
                log_func("Probando endpoint Tasmota (/cm?cmnd=Power%20TOGGLE)...")
                ok = ModemRebooter.send_request(clean + "/cm?cmnd=Power%20TOGGLE", "GET", None, None, log_func)

        if ok:
            log_func("✔ Señal recibida por el Enchufe Inteligente.")
        else:
            log_func("⚡ Señal enviada al enchufe. Iniciando ciclo de reinicio...")
        return True

    @staticmethod
    def trigger_modem(host, user, password, brand, log_func):
        host = (host or "192.168.1.1").strip()
        if not host.startswith("http://") and not host.startswith("https://"):
            host = "http://" + host
        base = host.rstrip("/")

        log_func(f"📡 Enviando orden de reinicio al módem ({brand}) en: {base}")

        auth = None
        if user and password:
            creds = f"{user.strip()}:{password.strip()}"
            auth = "Basic " + base64.b64encode(creds.encode("utf-8")).decode("utf-8")

        success = False
        if "Movistar" in brand:
            success = ModemRebooter.reboot_movistar_hgu(host, user, password, log_func)
        elif "Huawei" in brand:
            success = ModemRebooter.send_request(base + "/api/system/reboot", "POST", b"<request><Control>1</Control></request>", auth, log_func)
            if not success:
                success = ModemRebooter.send_request(base + "/index/reboot.cgi", "POST", b"reboot=1", auth, log_func)
            if not success:
                success = ModemRebooter.send_request(base + "/api/system/device-reboot", "POST", None, auth, log_func)
        elif "ZTE" in brand:
            success = ModemRebooter.send_request(base + "/getpage.gch?pid=1002&nextpage=diagnose_reboot.gch&reboot_type=1", "POST", None, auth, log_func)
            if not success:
                success = ModemRebooter.send_request(base + "/getpage.gch?pid=1001", "POST", b"Action=Reboot", auth, log_func)
        elif "Sagemcom" in brand:
            payload = b'{"method":"reboot","parameters":{}}'
            success = ModemRebooter.send_request(base + "/json-rpc", "POST", payload, auth, log_func)
            if not success:
                success = ModemRebooter.send_request(base + "/gui/reboot", "POST", None, auth, log_func)
        else:
            success = ModemRebooter.send_request(base + "/userRpm/SysRebootRpm.htm?Reboot=Reboot", "GET", None, auth, log_func)
            if not success:
                success = ModemRebooter.send_request(base + "/cgi/reboot", "POST", None, auth, log_func)
            if not success:
                success = ModemRebooter.send_request(base + "/reboot.cgi", "POST", b"reboot=1", auth, log_func)
            if not success:
                success = ModemRebooter.send_request(base + "/api/system/reboot", "POST", None, auth, log_func)

        if success:
            log_func("✔ Petición de reinicio aceptada por el módem.")
        else:
            log_func("⚡ Peticiones enviadas al módem. Iniciando ciclo de reconexión...")
        return True

    @staticmethod
    def reboot_movistar_hgu(host, user, password, log_func):
        clean_ip = host.replace("http://", "").replace("https://", "").split("/")[0].split(":")[0].strip()
        clean_ip = clean_ip or "192.168.1.1"
        pw = (password or "").strip()
        
        # Combinaciones de puertos y protocolos comunes en MitraStar GPT y Askey
        endpoints = [
            ("https", f"{clean_ip}:8000"),
            ("http", f"{clean_ip}:8000"),
            ("http", clean_ip),
            ("https", clean_ip)
        ]
        
        usernames = [user.strip() if user else "1234", "1234", "admin"]
        # Evitar duplicados
        usernames = list(dict.fromkeys([u for u in usernames if u]))
        
        log_func(f"📡 Conectando con Módem Movistar GPT ({clean_ip})...")
        
        # 1. Intentar Login formal para capturar la Cookie de sesión
        for scheme, host_port in endpoints:
            base_url = f"{scheme}://{host_port}"
            for u in usernames:
                for login_path in ["/cgi-bin/logIn_mhs.cgi", "/cgi-bin/login.cgi", "/login.cgi"]:
                    try:
                        data = urllib.parse.urlencode({"Username": u, "Password": pw}).encode("utf-8")
                        req = urllib.request.Request(f"{base_url}{login_path}", data=data, method="POST")
                        req.add_header("User-Agent", "Mozilla/5.0")
                        req.add_header("Content-Type", "application/x-www-form-urlencoded")
                        with urllib.request.urlopen(req, timeout=3.5, context=ssl_ctx) as resp:
                            # Buscar cookies
                            cookies = []
                            for k, v in resp.headers.items():
                                if k.lower() == "set-cookie":
                                    cookies.append(v.split(";")[0])
                            
                            cookie_header = "; ".join(cookies) if cookies else ""
                            log_func(f"✔ Sesión iniciada en {base_url} (usuario: {u})")
                            
                            # 2. Enviar orden de reboot con la cookie
                            for r_path in ["/cgi-bin/reboot.cgi", "/cgi-bin/te_reboot.cgi"]:
                                try:
                                    r_req = urllib.request.Request(f"{base_url}{r_path}", data=b"reboot=1", method="POST")
                                    if cookie_header:
                                        r_req.add_header("Cookie", cookie_header)
                                    r_req.add_header("User-Agent", "Mozilla/5.0")
                                    with urllib.request.urlopen(r_req, timeout=3.5, context=ssl_ctx) as r_resp:
                                        if r_resp.getcode() < 400:
                                            log_func(f"✔ ¡Orden de reinicio aceptada por el módem Movistar GPT!")
                                            return True
                                except Exception:
                                    pass
                    except Exception:
                        pass
        
        # 3. Fallback directo a endpoints comunes si no requiere login de sesión
        log_func("Probando rutas directas de reinicio Movistar...")
        for scheme, host_port in endpoints:
            base_url = f"{scheme}://{host_port}"
            auth_str = None
            if user and password:
                creds = f"{user.strip()}:{password.strip()}"
                auth_str = "Basic " + base64.b64encode(creds.encode("utf-8")).decode("utf-8")
                
            for r_path in ["/cgi-bin/te_reboot.cgi", "/cgi-bin/reboot.cgi", "/reboot.cgi"]:
                try:
                    req = urllib.request.Request(f"{base_url}{r_path}", data=b"reboot=1", method="POST")
                    if auth_str:
                        req.add_header("Authorization", auth_str)
                    with urllib.request.urlopen(req, timeout=3, context=ssl_ctx) as resp:
                        if resp.getcode() < 400:
                            log_func(f"✔ Orden enviada a {base_url}{r_path}")
                            return True
                except Exception:
                    pass
                    
        log_func("⚡ Peticiones enviadas al módem Movistar. Iniciando ciclo de espera...")
        return True

    @staticmethod
    def send_request(url, method, data, auth, log_func):
        try:
            req = urllib.request.Request(url, data=data, method=method)
            req.add_header("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) CFBotWiFi-PC/1.0")
            if auth:
                req.add_header("Authorization", auth)
            if data:
                req.add_header("Content-Type", "application/x-www-form-urlencoded")
            with urllib.request.urlopen(req, timeout=4.5, context=ssl_ctx) as resp:
                return (200 <= resp.getcode() < 400)
        except Exception:
            return False


class CFBotWiFiPCApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CF Bot WiFi — Edición PC (Módem & Fibra Óptica)")
        self.root.geometry("680x860")
        self.root.minsize(620, 750)
        self.root.configure(bg="#070d19")

        self.is_running = False
        self.visit_count = 0
        self.last_ip = ""
        self.current_process = None
        self.current_temp_profile = None

        self.load_config()
        self.build_ui()
        self.log("CF Bot WiFi Edición PC inicializado.")

        # Chequear IP inicial en segundo plano
        threading.Thread(target=self.check_public_ip, daemon=True).start()

    def load_config(self):
        self.config = {
            "target_url": DEFAULT_TARGET_URL,
            "modem_ip": "192.168.0.1",
            "modem_user": "admin",
            "modem_pass": "",
            "modem_brand": "Sagemcom (Fast 3890 / 5655)",
            "use_smart_plug": False,
            "smart_plug_url": "http://192.168.1.150/relay/0?turn=toggle",
            "show_browser": False
        }
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                    self.config.update(saved)
            except Exception:
                pass

    def save_config(self):
        self.config["target_url"] = self.clean_url(self.entry_url.get())
        self.config["modem_ip"] = self.entry_modem_ip.get().strip()
        self.config["modem_user"] = self.entry_modem_user.get().strip()
        self.config["modem_pass"] = self.entry_modem_pass.get()
        self.config["modem_brand"] = self.combo_brand.get()
        self.config["use_smart_plug"] = bool(self.var_plug.get())
        self.config["smart_plug_url"] = self.entry_plug_url.get().strip()
        self.config["show_browser"] = bool(self.var_show_browser.get())

        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.log(f"⚠ Error guardando config: {e}")

    def clean_url(self, raw):
        raw = (raw or DEFAULT_TARGET_URL).strip()
        if not raw.startswith("http://") and not raw.startswith("https://"):
            raw = "https://" + raw
        return raw.rstrip("/")

    def build_ui(self):
        # Frame Principal con Scrollbar si hiciera falta
        main_frame = tk.Frame(self.root, bg="#070d19", padx=20, pady=16)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Encabezado
        lbl_title = tk.Label(
            main_frame,
            text="CF BOT — MÓDEM & FIBRA ÓPTICA (PC)",
            font=("Segoe UI", 15, "bold"),
            fg="#38bdf8",
            bg="#070d19"
        )
        lbl_title.pack(anchor="w")

        lbl_sub = tk.Label(
            main_frame,
            text="Automatización de Visitas de Alta Retención (50s) con Rotación de Módem Residencial",
            font=("Segoe UI", 9),
            fg="#94a3b8",
            bg="#070d19"
        )
        lbl_sub.pack(anchor="w", pady=(2, 12))

        # 1. URL Destino
        lbl_url = tk.Label(main_frame, text="URL de la Página Web Destino:", font=("Segoe UI", 10, "bold"), fg="#34d399", bg="#070d19")
        lbl_url.pack(anchor="w")

        self.entry_url = tk.Entry(main_frame, font=("Segoe UI", 11), bg="#0f1a2e", fg="#ffffff", insertbackground="#ffffff", relief="flat", highlightthickness=2, highlightbackground="#1f3358", highlightcolor="#10b981")
        self.entry_url.insert(0, self.config["target_url"])
        self.entry_url.pack(fill=tk.X, pady=(4, 12), ipady=6)

        # 2. Card Configuración de Módem / Enchufe
        card_modem = tk.LabelFrame(
            main_frame,
            text=" Configuración de Red & Módem ",
            font=("Segoe UI", 10, "bold"),
            fg="#38bdf8",
            bg="#0f1a2e",
            padx=16,
            pady=12,
            relief="solid",
            highlightthickness=1,
            highlightbackground="#1f3358"
        )
        card_modem.pack(fill=tk.X, pady=(0, 12))

        self.var_plug = tk.BooleanVar(value=self.config["use_smart_plug"])
        chk_plug = tk.Checkbutton(
            card_modem,
            text="Usar Enchufe Inteligente WiFi (Smart Plug) en vez de acceso al módem",
            variable=self.var_plug,
            font=("Segoe UI", 9, "bold"),
            fg="#fde047",
            bg="#0f1a2e",
            activebackground="#0f1a2e",
            activeforeground="#fde047",
            selectcolor="#070d19",
            command=self.toggle_plug_ui
        )
        chk_plug.pack(anchor="w", pady=(0, 8))

        # Contenedor Módem
        self.frame_modem_fields = tk.Frame(card_modem, bg="#0f1a2e")
        self.frame_modem_fields.pack(fill=tk.X)

        lbl_mip = tk.Label(self.frame_modem_fields, text="Dirección IP Interna del Módem:", font=("Segoe UI", 9), fg="#cbd5e1", bg="#0f1a2e")
        lbl_mip.pack(anchor="w")
        self.entry_modem_ip = tk.Entry(self.frame_modem_fields, font=("Segoe UI", 10), bg="#070d19", fg="#ffffff", insertbackground="#ffffff", relief="flat", highlightthickness=1, highlightbackground="#3b82f6")
        self.entry_modem_ip.insert(0, self.config["modem_ip"])
        self.entry_modem_ip.pack(fill=tk.X, pady=(2, 6), ipady=4)

        row_creds = tk.Frame(self.frame_modem_fields, bg="#0f1a2e")
        row_creds.pack(fill=tk.X, pady=(2, 6))

        col_u = tk.Frame(row_creds, bg="#0f1a2e")
        col_u.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))
        lbl_u = tk.Label(col_u, text="Usuario Admin:", font=("Segoe UI", 9), fg="#cbd5e1", bg="#0f1a2e")
        lbl_u.pack(anchor="w")
        self.entry_modem_user = tk.Entry(col_u, font=("Segoe UI", 10), bg="#070d19", fg="#ffffff", insertbackground="#ffffff", relief="flat", highlightthickness=1, highlightbackground="#3b82f6")
        self.entry_modem_user.insert(0, self.config["modem_user"])
        self.entry_modem_user.pack(fill=tk.X, ipady=4)

        col_p = tk.Frame(row_creds, bg="#0f1a2e")
        col_p.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(6, 0))
        lbl_p = tk.Label(col_p, text="Contraseña Admin (etiqueta):", font=("Segoe UI", 9), fg="#cbd5e1", bg="#0f1a2e")
        lbl_p.pack(anchor="w")
        self.entry_modem_pass = tk.Entry(col_p, font=("Segoe UI", 10), show="•", bg="#070d19", fg="#ffffff", insertbackground="#ffffff", relief="flat", highlightthickness=1, highlightbackground="#3b82f6")
        self.entry_modem_pass.insert(0, self.config["modem_pass"])
        self.entry_modem_pass.pack(fill=tk.X, ipady=4)

        lbl_br = tk.Label(self.frame_modem_fields, text="Marca o Modelo del Módem:", font=("Segoe UI", 9), fg="#cbd5e1", bg="#0f1a2e")
        lbl_br.pack(anchor="w")
        self.combo_brand = ttk.Combobox(self.frame_modem_fields, values=MODEM_BRANDS, state="readonly", font=("Segoe UI", 10))
        if self.config["modem_brand"] in MODEM_BRANDS:
            self.combo_brand.set(self.config["modem_brand"])
        else:
            self.combo_brand.set(MODEM_BRANDS[0])
        self.combo_brand.pack(fill=tk.X, pady=(2, 4))

        # Contenedor Enchufe Inteligente
        self.frame_plug_fields = tk.Frame(card_modem, bg="#0f1a2e")
        lbl_plug_url = tk.Label(self.frame_plug_fields, text="URL o IP del Enchufe Inteligente WiFi:", font=("Segoe UI", 9), fg="#cbd5e1", bg="#0f1a2e")
        lbl_plug_url.pack(anchor="w")
        self.entry_plug_url = tk.Entry(self.frame_plug_fields, font=("Segoe UI", 10), bg="#070d19", fg="#ffffff", insertbackground="#ffffff", relief="flat", highlightthickness=1, highlightbackground="#f59e0b")
        self.entry_plug_url.insert(0, self.config["smart_plug_url"])
        self.entry_plug_url.pack(fill=tk.X, pady=(2, 4), ipady=4)

        self.toggle_plug_ui()

        # Opciones Adicionales (Mostrar Navegador)
        self.var_show_browser = tk.BooleanVar(value=self.config["show_browser"])
        chk_show_b = tk.Checkbutton(
            main_frame,
            text="👁 Mostrar ventana del navegador Chrome/Edge en pantalla (destildar para modo invisible)",
            variable=self.var_show_browser,
            font=("Segoe UI", 9),
            fg="#94a3b8",
            bg="#070d19",
            activebackground="#070d19",
            activeforeground="#ffffff",
            selectcolor="#0f1a2e"
        )
        chk_show_b.pack(anchor="w", pady=(0, 10))

        # 3. Card de Métricas en Vivo
        card_metrics = tk.Frame(main_frame, bg="#0f1a2e", padx=16, pady=10, relief="solid", highlightthickness=1, highlightbackground="#1f3358")
        card_metrics.pack(fill=tk.X, pady=(0, 12))

        self.lbl_status = tk.Label(card_metrics, text="ESTADO: DETENIDO", font=("Segoe UI", 11, "bold"), fg="#fde047", bg="#0f1a2e")
        self.lbl_status.pack(anchor="w")

        self.lbl_ip = tk.Label(card_metrics, text="IP Pública WiFi actual: Consultando...", font=("Segoe UI", 10), fg="#f1f5f9", bg="#0f1a2e")
        self.lbl_ip.pack(anchor="w", pady=(3, 2))

        self.lbl_visits = tk.Label(card_metrics, text="Visitas enviadas en esta sesión: 0", font=("Segoe UI", 10, "bold"), fg="#34d399", bg="#0f1a2e")
        self.lbl_visits.pack(anchor="w")

        # 4. Botones de Control
        row_btns = tk.Frame(main_frame, bg="#070d19")
        row_btns.pack(fill=tk.X, pady=(0, 12))

        self.btn_toggle = tk.Button(
            row_btns,
            text="▶ INICIAR BOT PC",
            font=("Segoe UI", 11, "bold"),
            fg="#ffffff",
            bg="#10b981",
            activebackground="#059669",
            activeforeground="#ffffff",
            relief="flat",
            command=self.toggle_bot,
            cursor="hand2"
        )
        self.btn_toggle.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8, padx=(0, 6))

        btn_manual = tk.Button(
            row_btns,
            text="🔄 REINICIAR MÓDEM AHORA",
            font=("Segoe UI", 10, "bold"),
            fg="#ffffff",
            bg="#0284c7",
            activebackground="#0369a1",
            activeforeground="#ffffff",
            relief="flat",
            command=self.trigger_manual_reboot,
            cursor="hand2"
        )
        btn_manual.pack(side=tk.RIGHT, fill=tk.X, expand=True, ipady=8, padx=(6, 0))

        # 5. Consola de Logs en Vivo
        lbl_log = tk.Label(main_frame, text="Registro de Actividad en Vivo:", font=("Segoe UI", 9), fg="#cbd5e1", bg="#070d19")
        lbl_log.pack(anchor="w")

        frame_log = tk.Frame(main_frame, bg="#030710")
        frame_log.pack(fill=tk.BOTH, expand=True)

        self.txt_log = tk.Text(frame_log, font=("Consolas", 9), bg="#030710", fg="#e2e8f0", insertbackground="#ffffff", relief="flat", wrap="word", height=10)
        scroll_y = tk.Scrollbar(frame_log, command=self.txt_log.yview)
        self.txt_log.configure(yscrollcommand=scroll_y.set)

        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.txt_log.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def toggle_plug_ui(self):
        if self.var_plug.get():
            self.frame_modem_fields.pack_forget()
            self.frame_plug_fields.pack(fill=tk.X, pady=(4, 0))
        else:
            self.frame_plug_fields.pack_forget()
            self.frame_modem_fields.pack(fill=tk.X, pady=(4, 0))

    def log(self, message):
        t = datetime.now().strftime("%H:%M:%S")
        line = f"[{t}] {message}\n"
        try:
            print(line.strip())
        except Exception:
            pass

        def _append():
            try:
                self.txt_log.insert(tk.END, line)
                self.txt_log.see(tk.END)
            except Exception:
                pass

        if threading.current_thread() is threading.main_thread():
            _append()
        else:
            self.root.after(0, _append)

    def set_status(self, text, color):
        def _set():
            self.lbl_status.config(text=text, fg=color)
        if threading.current_thread() is threading.main_thread():
            _set()
        else:
            self.root.after(0, _set)

    def check_public_ip(self):
        try:
            req = urllib.request.Request("https://api.ipify.org", headers={"User-Agent": "CFBotWiFi-PC/1.0"})
            with urllib.request.urlopen(req, timeout=5) as r:
                ip = r.read().decode("utf-8").strip()
                if ip:
                    changed = (ip != self.last_ip)
                    self.last_ip = ip

                    def _update():
                        self.lbl_ip.config(text=f"IP Pública WiFi actual: {ip}")
                        if changed:
                            self.log(f"★ Nueva IP pública detectada: {ip}")

                    self.root.after(0, _update)
                    return ip
        except Exception:
            def _update_err():
                self.lbl_ip.config(text="IP Pública WiFi actual: Sin conexión o reconectando...")
            self.root.after(0, _update_err)
        return None

    def toggle_bot(self):
        self.is_running = not self.is_running
        self.save_config()

        if self.is_running:
            self.btn_toggle.config(text="⏹ DETENER BOT", bg="#ef4444", activebackground="#dc2626")
            self.set_status("ESTADO: EJECUTANDO VISITAS...", "#34d399")
            self.log(f"Bot iniciado hacia: {self.config['target_url']}")
            threading.Thread(target=self.bot_loop, daemon=True).start()
        else:
            self.btn_toggle.config(text="▶ INICIAR BOT PC", bg="#10b981", activebackground="#059669")
            self.set_status("ESTADO: DETENIDO", "#fde047")
            self.log("Bot detenido por el usuario.")
            if self.current_process:
                try:
                    self.current_process.terminate()
                except Exception:
                    pass

    def trigger_manual_reboot(self):
        self.save_config()
        self.log("Disparando reinicio manual de red...")
        threading.Thread(target=self.execute_reboot, args=(False,), daemon=True).start()

    def execute_reboot(self, continue_after=False):
        self.set_status("ESTADO: ENVIANDO REINICIO...", "#38bdf8")
        ModemRebooter.reboot(
            self.config["use_smart_plug"],
            self.config["smart_plug_url"],
            self.config["modem_ip"],
            self.config["modem_user"],
            self.config["modem_pass"],
            self.config["modem_brand"],
            self.log
        )

        self.set_status("ESTADO: ESPERANDO RECONEXIÓN FIBRA/WIFI...", "#f97316")
        self.log("Esperando 15 segundos a que caiga el enlace de fibra...")
        time.sleep(15)

        self.wait_for_internet(continue_after)

    def wait_for_internet(self, continue_after=False):
        self.log("Comprobando reconexión a Internet...")
        attempts = 0
        connected = False

        while attempts < 40 and (not continue_after or self.is_running):
            attempts += 1
            try:
                socket.create_connection(("8.8.8.8", 53), timeout=3)
                # Verificar HTTP
                req = urllib.request.Request("https://api.ipify.org", headers={"User-Agent": "CFBotWiFi-PC/1.0"})
                with urllib.request.urlopen(req, timeout=4) as r:
                    if r.getcode() == 200:
                        connected = True
                        break
            except Exception:
                pass
            time.sleep(4)

        if connected:
            self.log("✔ Conexión a internet restablecida exitosamente.")
            self.set_status("ESTADO: CONECTADO (NUEVA IP)", "#34d399")
            new_ip = self.check_public_ip()
            if continue_after and self.is_running:
                # Continuar siguiente visita
                time.sleep(2)
                threading.Thread(target=self.bot_loop, daemon=True).start()
        else:
            self.log("⚠ Tiempo de reconexión agotado. Reintentando...")
            if continue_after and self.is_running:
                time.sleep(5)
                self.wait_for_internet(True)

    def bot_loop(self):
        if not self.is_running:
            return

        browser_path, b_type = find_browser_path()
        if not browser_path:
            self.log("❌ Error: No se encontró Google Chrome ni Microsoft Edge instalado en esta PC.")
            self.root.after(0, self.toggle_bot)
            return

        self.visit_count += 1
        def _up_v():
            self.lbl_visits.config(text=f"Visitas enviadas en esta sesión: {self.visit_count}")
        self.root.after(0, _up_v)

        base = self.config["target_url"]
        path1 = random.choice(PATHS)
        full_url1 = (base + path1) if "criteriofinanciero" in base else base

        self.log(f"Visita #{self.visit_count} (IP {self.last_ip}) -> {full_url1}")

        temp_profile = os.path.join(os.environ.get("TEMP", r"C:\Windows\Temp"), f"cfbot_profile_{os.getpid()}_{self.visit_count}_{random.randint(1000, 9999)}")
        self.current_temp_profile = temp_profile

        cmd = [
            browser_path,
            f"--user-data-dir={temp_profile}",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-popup-blocking",
            "--disable-infobars",
            "--disable-features=Translate",
            "--mute-audio"
        ]

        if not self.config["show_browser"]:
            cmd.append("--headless=new")

        cmd.append(full_url1)

        try:
            self.current_process = subprocess.Popen(cmd)
        except Exception as e:
            self.log(f"Error abriendo navegador: {e}")
            return

        # Simular estancia de lectura en Página 1 (~24 segundos)
        for sec in range(24):
            if not self.is_running:
                self.kill_browser()
                return
            time.sleep(1)

        self.log("↳ Navegando a lectura interna / segundo artículo (~26s más)...")
        # Enviar segunda página si es Criterio Financiero
        if "criteriofinanciero" in base:
            path2 = random.choice(PATHS[8:])
            full_url2 = base + path2
            self.log(f"↳ Leyendo artículo: {path2}")
            # Cargar segunda página en el mismo perfil
            subprocess.Popen([browser_path, f"--user-data-dir={temp_profile}", full_url2])

        # Simular estancia en Página 2 (~26 segundos)
        for sec in range(26):
            if not self.is_running:
                self.kill_browser()
                return
            time.sleep(1)

        self.kill_browser()
        self.log("Fin de permanencia orgánica (50s cumplidos).")

        if self.is_running:
            self.execute_reboot(continue_after=True)

    def kill_browser(self):
        if self.current_process:
            try:
                self.current_process.terminate()
                self.current_process.wait(timeout=2)
            except Exception:
                try:
                    self.current_process.kill()
                except Exception:
                    pass
            self.current_process = None

        if self.current_temp_profile and os.path.exists(self.current_temp_profile):
            time.sleep(0.5)
            try:
                shutil.rmtree(self.current_temp_profile, ignore_errors=True)
            except Exception:
                pass
            self.current_temp_profile = None


if __name__ == "__main__":
    root = tk.Tk()
    app = CFBotWiFiPCApp(root)
    root.mainloop()
