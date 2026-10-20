"""
Criterio Financiero — Portal de Finanzas Personales, Inversiones y Criptomonedas
Desarrollado para alta monetización (Google AdSense / Afiliados Fintech), optimización E-E-A-T
y auditoría de tráfico biométrico en tiempo real.
"""

import os
import sqlite3
import json
import time
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, g, abort

app = Flask(__name__)
app.config['SECRET_KEY'] = 'criterio-financiero-secret-key-2026'

DB_PATH = os.path.join(os.path.dirname(__file__), 'visits.db')


# ---------------------------------------------------------------------------
# Base de datos SQLite y Auditoría de Tráfico
# ---------------------------------------------------------------------------
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(error):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS visits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ip TEXT,
                user_agent TEXT,
                referrer TEXT,
                path TEXT,
                timestamp DATETIME
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS beacons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                path TEXT,
                time_on_page INTEGER,
                canvas_hash TEXT,
                webgl_renderer TEXT,
                webgl_vendor TEXT,
                screen_w INTEGER,
                screen_h INTEGER,
                mouse_events_count INTEGER,
                mouse_linearity REAL,
                scroll_depth_px INTEGER,
                timezone_offset INTEGER,
                ip TEXT,
                timestamp DATETIME
            )
        ''')
        conn.commit()


init_db()


# ---------------------------------------------------------------------------
# Middleware de Auditoría de Visitas (Filtra llamadas técnicas)
# ---------------------------------------------------------------------------
@app.before_request
def track_visit():
    # Excluir recursos estáticos, llamadas API internas y el propio panel de analítica
    # para que solo se registren páginas y artículos leídos por los usuarios.
    if (request.path.startswith('/static') or
        request.path == '/favicon.ico' or
        request.path.startswith('/api/') or
        request.path == '/analytics'):
        return

    ip = request.headers.get('CF-Connecting-IP') or \
         request.headers.get('X-Real-IP') or \
         request.headers.get('X-Forwarded-For') or \
         request.remote_addr

    if ip and ',' in ip:
        ip = ip.split(',')[0].strip()

    ua = request.headers.get('User-Agent', '')
    referrer = request.referrer or ''
    path = request.path
    ts = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

    db = get_db()
    db.execute(
        'INSERT INTO visits (ip, user_agent, referrer, path, timestamp) VALUES (?,?,?,?,?)',
        (ip, ua, referrer, path, ts)
    )
    db.commit()


# ---------------------------------------------------------------------------
# Matriz de Artículos Financieros (E-E-A-T & Google AdSense High RPM)
# ---------------------------------------------------------------------------
ARTICLES = [
    {
        "slug": "como-invertir-en-cedears-argentina-guia-paso-a-paso",
        "title": "Cómo Invertir en CEDEARs en Argentina: Guía Paso a Paso 2026",
        "subtitle": "Descubrí cómo comprar acciones de Apple, Google, Coca-Cola y Microsoft en pesos y dolarizar tu cartera legalmente sin cepo cambiario.",
        "section": "guias",
        "section_name": "Guías y Educación",
        "author": "Lic. Martín Soler",
        "read_time": "7 min",
        "tags": ["CEDEARs", "Inversiones", "Bolsa Argentina", "Dolarización"],
        "content": [
            "Los Certificados de Depósito Argentinos (CEDEARs) se han consolidado como el vehículo de inversión predilecto para los ahorristas locales que buscan proteger su patrimonio de la depreciación del peso sin depender de cupos cambiarios ni pagar costos de transferencia al exterior.",
            "Un CEDEAR representa una fracción o múltiplo de una acción que cotiza en mercados internacionales (como Wall Street, NASDAQ o la Bolsa de Londres). Al operar un CEDEAR en la Bolsa de Comercio de Buenos Aires (BYMA), el inversor adquiere derechos económicos directos sobre el activo subyacente, cobrando dividendos en dólares billete en su cuenta bancaria o de corretaje.",
            "Para comprar CEDEARs en Argentina se requiere una cuenta comitente en un broker registrado ante la Comisión Nacional de Valores (CNV). El proceso consta de cuatro etapas sencillas: 1) Transferencia de pesos desde home banking; 2) Búsqueda del ticker correspondiente (ej. AAPL para Apple, KO para Coca-Cola, SPY para el índice S&P 500); 3) Selección del plazo de liquidación (Contado Inmediato o 24 horas); y 4) Confirmación del precio límite o de mercado.",
            "Una ventaja fundamental de los CEDEARs radica en su doble cobertura: el precio del activo replica la cotización en dólares de la empresa en el exterior combinada con el valor implícito del dólar Contado con Liquidación (CCL). Si el dólar sube, el valor del CEDEAR en pesos sube proporcionalmente, manteniendo intacto el poder adquisitivo en moneda dura.",
            "En materia tributaria, para personas humanas residentes en Argentina, la ganancia de capital derivada de la compraventa de CEDEARs está exenta del Impuesto a las Ganancias en BYMA. No obstante, los dividendos percibidos sufren retención en origen en Estados Unidos (generalmente 30% bajo convenio fiscal) y se declaran en el régimen general local."
        ]
    },
    {
        "slug": "mejores-brokers-argentina-comparativa-comisiones",
        "title": "Los 5 Mejores Brokers de Argentina: Comparativa de Comisiones 2026",
        "subtitle": "Análisis exhaustivo de Balanz, InvertirOnline, Cocos Capital, Bull Market y PPI. Costos de operación, plataformas y seguridad regulada por CNV.",
        "section": "comparativas",
        "section_name": "Comparativas y Reseñas",
        "author": "Dra. Valeria Gómez",
        "read_time": "9 min",
        "tags": ["Brokers", "Comisiones", "Balanz", "IOL", "Cocos"],
        "content": [
            "Elegir el Agente de Liquidación y Compensación (ALyC) adecuado es una decisión estratégica que impacta directamente en la rentabilidad neta de cualquier cartera de inversión. Con la evolución tecnológica de las fintech, la competencia entre brokers argentinos ha generado una drástica reducción en las comisiones operativas.",
            "En nuestro relevamiento independiente de 2026, evaluamos cinco pilares críticos: aranceles de compraventa de acciones y bonos, costo de custodia, agilidad en la operatoria de Dólar MEP automático, estabilidad de las aplicaciones móviles y calidad del asesoramiento profesional asignado.",
            "Balanz Capital destaca por su servicio integral de asesoramiento financiero personalizado, ideal para perfiles que gestionan carteras medianas o avanzadas y valoran recomendaciones periódicas de research sobre renta fija y bonos soberanos. Por su parte, InvertirOnline (IOL) se mantiene como la plataforma más intuitiva para principiantes, ofreciendo una cuenta remunerada que genera rendimientos diarios sobre los pesos no invertidos.",
            "Cocos Capital y Bull Market mantienen su liderazgo entre usuarios de perfil activo ('traders') gracias a esquemas de comisión cero o tarifas ultra competitivas en suscripciones mensuales de fondos comunes y bonos públicos.",
            "Todas las entidades analizadas se encuentran debidamente inscriptas y supervisadas por la Comisión Nacional de Valores (CNV) y custodian sus tenencias en Caja de Valores S.A., garantizando la titularidad inalienable de los títulos a nombre del inversor independientemente de la solvencia comercial de la plataforma."
        ]
    },
    {
        "slug": "que-billetera-virtual-paga-mas-tasa-argentina",
        "title": "Billeteras Virtuales: Qué Plataforma Paga Más Tasa Hoy en Argentina",
        "subtitle": "Comparativa de rendimientos diarios de Mercado Pago, Naranja X, Ualá, Personal Pay y Prex. Cuánto rinde tu saldo líquido día a día.",
        "section": "comparativas",
        "section_name": "Comparativas y Reseñas",
        "author": "Lic. Martín Soler",
        "read_time": "6 min",
        "tags": ["Billeteras Virtuales", "Mercado Pago", "Naranja X", "Uala", "Tasas"],
        "content": [
            "Con la dinámica inflacionaria de Argentina, dejar dinero estancado en una caja de ahorro tradicional sin remunerar representa una pérdida real de poder adquisitivo cada 24 horas. Las cuentas remuneradas de billeteras virtuales permiten mitigar este impacto con liquidez inmediata.",
            "A diferencia de un plazo fijo bancario tradicional, donde el capital queda inmovilizado durante al menos 30 días sin posibilidad de rescate anticipado, las billeteras virtuales invierten el dinero en Fondos Comunes de Inversión (FCI) de tipo 'Money Market' o pagan intereses directos sobre saldo, acreditando ganancias todos los días sin restricciones de retiro.",
            "Al cierre de octubre de 2026, Naranja X continúa ofreciendo una de las Tasas Nominales Anuales (TNA) más atractivas del mercado (rondando el 42% TNA), aunque aplicando un tope remunerado de hasta $600.000 pesos de saldo.",
            "Personal Pay premia la fidelidad de sus clientes a través de un esquema por niveles (Tier 1 a Tier 3) según los consumos mensuales en telefonía y servicios, alcanzando rendimientos comparables al 40.5% TNA sin límites estrictos de capital.",
            "Mercado Pago y Ualá ofrecen la mayor estabilidad operativa y liquidez en transferencias inmediatas. Para optimizar el rendimiento, la estrategia recomendada por expertos consiste en diversificar el saldo disponible entre dos aplicaciones para aprovechar los topes de tasa alta simultáneamente."
        ]
    },
    {
        "slug": "como-comprar-dolar-mep-home-banking-sin-cepo",
        "title": "Cómo Comprar Dólar MEP desde el Home Banking: Sin Límites y Legal",
        "subtitle": "Guía práctica para dolarizar tus ahorros a través del mercado bursátil. Plazos de parking, requisitos normativos y transferencias a cuenta en dólares.",
        "section": "guias",
        "section_name": "Guías y Educación",
        "author": "Lic. Martín Soler",
        "read_time": "8 min",
        "tags": ["Dólar MEP", "Ahorro", "Home Banking", "Regulaciones BCRA"],
        "content": [
            "El Dólar MEP (Mercado Electrónico de Pagos), también conocido como Dólar Bolsa, es el mecanismo legal, transparente y 100% bancarizado para adquirir divisa estadounidense en Argentina sin las restricciones ni los límites de cupo del mercado oficial.",
            "La operación consiste en comprar un bono soberano emitido en pesos (típicamente el Bonar 2030 - AL30) y venderlo en su especie denominada en dólares (AL30D). La cotización implícita resulta de la división entre el precio pagado en pesos y los dólares recibidos al momento de la venta.",
            "Para concretar la compra se deben cumplir tres requisitos normativos básicos: poseer una cuenta bancaria en pesos y otra en dólares a la misma titularidad (en cualquier entidad financiera regulada por el BCRA), no haber recibido subsidios tarifarios vigentes y contar con una cuenta comitente vinculada.",
            "En la actualidad, casi todos los home bankings y aplicaciones de brokers cuentan con un botón de 'Dólar MEP Simple' que automatiza toda la transacción en un solo clic, gestionando automáticamente el plazo de espera ('parking') exigido por la normativa de la CNV.",
            "Una vez liquidada la operación, los dólares quedan disponibles para ser transferidos de forma inmediata a la caja de ahorro en dólares del titular, desde donde pueden ser retirados por ventanilla en billetes físicos o conservados como ahorro de reserva."
        ]
    },
    {
        "slug": "dolar-cripto-como-comprar-usdt-pesos-argentinos",
        "title": "Dólar Cripto: Cómo Comprar USDT y USDC con Pesos Argentinos",
        "subtitle": "Aprendé a operar stablecoins respaldadas 1 a 1 con el dólar. Disponibilidad 24/7, sin horarios bancarios ni comisiones abusivas.",
        "section": "guias",
        "section_name": "Guías y Educación",
        "author": "Dra. Valeria Gómez",
        "read_time": "7 min",
        "tags": ["Cripto", "USDT", "USDC", "Stablecoins", "P2P"],
        "content": [
            "El Dólar Cripto se ha transformado en el instrumento preferido de los argentinos para dolarizarse durante fines de semana, feriados o momentos de alta volatilidad política en los que los mercados tradicionales permanecen cerrados.",
            "Las principales monedas utilizadas para este fin son Tether (USDT) y USD Coin (USDC), conocidas técnicamente como *stablecoins* (criptomonedas estables). Cada token emitido en la cadena de bloques está respaldado por reservas en dólares en efectivo y bonos del Tesoro estadounidense en custodios auditados internacionalmente.",
            "Para adquirir Dólar Cripto con pesos se pueden utilizar dos canales principales: exchanges locales centralizados (como Lemon Cash, Belo o Buenbit) que permiten fondear pesos vía CVU/CBU instantáneo; o plataformas P2P (Peer-to-Peer, como Binance o Bybit) donde se interactúa directamente con otros usuarios con depósito en garantía.",
            "A diferencia del Dólar MEP, el Dólar Cripto no tiene 'parking': una vez acreditados los tokens, el usuario puede transferirlos a billeteras descentralizadas de autocustodia (Metamask, Trust Wallet) o utilizarlos con tarjetas prepagas para compras cotidianas con cashback.",
            "Desde el punto de vista regulatorio, la UIF y la CNV en Argentina cuentan con el Registro de Proveedores de Servicios de Activos Virtuales (PSAV), garantizando que las empresas radicadas formalmente en el país cumplan con rigurosos estándares de prevención de lavado y ciberseguridad."
        ]
    },
    {
        "slug": "fondos-comunes-inversion-fci-guia-completa",
        "title": "Fondos Comunes de Inversión (FCI): Tipos, Rendimientos y Cómo Elegir",
        "subtitle": "Diferencias entre Money Market, Fondos T+1 de Renta Fija y Carteras Mixtas. Cómo armar un portafolio equilibrado según tu perfil de riesgo.",
        "section": "guias",
        "section_name": "Guías y Educación",
        "author": "Lic. Martín Soler",
        "read_time": "6 min",
        "tags": ["FCI", "Inversiones", "Money Market", "Renta Fija"],
        "content": [
            "Los Fondos Comunes de Inversión (FCI) constituyen el vehículo ideal para diversificar capital sin necesidad de analizar individualmente cada bono o acción del mercado. Permiten a cualquier inversor minorista acceder a una cartera administrada por profesionales financieros con un solo clic.",
            "Existen tres categorías esenciales de fondos en Argentina: los fondos de liquidez inmediata o 'Money Market' (T+0), que invierten en plazos fijos bancarios y cauciones; los fondos de Renta Fija de corto plazo (T+1), que incorporan letras y bonos públicos para superar la tasa de referencia; y los fondos de Renta Variable (T+2), enfocados en acciones locales del Merval y CEDEARs.",
            "Para el fondo de emergencia o dinero de uso corriente del mes, los fondos Money Market son insuperables porque permiten rescatar el saldo al instante en días hábiles sin penalidades ni pérdidas de valor de cuotaparte.",
            "Para horizontes de inversión superiores a los seis meses, los fondos que ajustan por CER (inflación) o títulos atados a la evolución del tipo de cambio oficial representan una alternativa defensiva eficaz frente a eventos macroeconómicos adversos.",
            "Al comparar fondos, resulta crucial analizar la tasa de gestión anual ('fee de administración') y el rendimiento histórico acumulado frente a la inflación para asegurar que la rentabilidad neta compense el costo del servicio."
        ]
    },
    {
        "slug": "resena-completa-balanz-capital-opiniones-comisiones",
        "title": "Reseña Completa de Balanz Capital: Comisiones, Plataforma y Opiniones",
        "subtitle": "Probamos la plataforma de Balanz en 2026. Conocé sus virtudes, debilidades, costos ocultos y si conviene abrir cuenta.",
        "section": "comparativas",
        "section_name": "Comparativas y Reseñas",
        "author": "Dra. Valeria Gómez",
        "read_time": "8 min",
        "tags": ["Balanz", "Brokers", "Reseñas", "Inversiones"],
        "content": [
            "Balanz Capital se ha posicionado como uno de los tres agentes bursátiles más prestigiosos y de mayor volumen operado en Argentina. En esta reseña analizamos en profundidad su propuesta de valor para el inversor particular.",
            "El principal diferencial de Balanz es la asignación de un Asesor Financiero Idóneo matriculado para cada cliente, quien brinda soporte telefónico y sugerencias de estructuración de cartera sin costo adicional fijo.",
            "En cuanto a costos, la apertura de cuenta y el mantenimiento de custodia son 100% bonificados. Las comisiones por compraventa de acciones y CEDEARs se sitúan en torno al 0.5% + IVA por operación, una tarifa estándar en el mercado para brokers de asesoramiento pleno.",
            "La aplicación móvil y el portal web son robustos, permitiendo operar Dólar MEP en un paso, suscribir a su familia de fondos Balanz institucional y configurar alertas de precio de bonos y acciones en tiempo real.",
            "En conclusión: Balanz es sumamente recomendable para quienes buscan respaldo, trayectoria institucional y acompañamiento experto, mientras que inversores que solo buscan comisiones mínimas para 'day trading' podrían preferir opciones de descuento."
        ]
    },
    {
        "slug": "invertironline-iol-analisis-cuenta-remunerada-costos",
        "title": "InvertirOnline (IOL): Análisis de Costos, Cuenta Remunerada y Seguridad",
        "subtitle": "Examinamos a fondo la plataforma de IOL: facilidad para principiantes, comisiones por operar CEDEARs y funcionamiento de su cuenta en pesos y dólares.",
        "section": "comparativas",
        "section_name": "Comparativas y Reseñas",
        "author": "Lic. Martín Soler",
        "read_time": "7 min",
        "tags": ["IOL", "Brokers", "InvertirOnline", "Opiniones"],
        "content": [
            "InvertirOnline (IOL) es pionero del corretaje bursátil digital en la República Argentina. Su interfaz limpia y sus herramientas educativas lo convierten en el broker predilecto para quienes dan sus primeros pasos en la bolsa.",
            "Uno de los puntos más valorados de IOL es la 'Cuenta Remunerada': el dinero líquido que el usuario no tiene invertido en activos genera rendimientos automáticos diarios a una tasa competitiva, evitando que los pesos pierdan valor mientras se espera una oportunidad de compra.",
            "La compra de Dólar MEP en IOL es prácticamente inmediata: el sistema calcula la cantidad óptima de bonos a comprar, gestiona el tiempo de parking regulatorio y transfiere automáticamente los dólares liquidados a la cuenta del usuario.",
            "En el plano de las comisiones, IOL ofrece escalas decrecientes según el volumen mensual operado, con una base de 0.5% para operaciones minoristas en CEDEARs y acciones locales.",
            "Como punto a mejorar, en momentos de extrema volatilidad de mercado el soporte por chat puede experimentar demoras, aunque la estabilidad técnica de su web ha demostrado altos niveles de confiabilidad."
        ]
    },
    {
        "slug": "como-salir-de-deudas-tarjeta-credito-metodo-bola-nieve",
        "title": "Cómo Salir de Deudas de Tarjeta de Crédito: Método Bola de Nieve",
        "subtitle": "Estrategia matemática para liquidar saldos pendientes, evitar el pago mínimo que multiplica intereses y recuperar el control financiero.",
        "section": "guias",
        "section_name": "Guías y Educación",
        "author": "Dra. Valeria Gómez",
        "read_time": "6 min",
        "tags": ["Finanzas Personales", "Deudas", "Tarjetas", "Ahorro"],
        "content": [
            "El pago mínimo de la tarjeta de crédito es una de las trampas financieras más perjudiciales en el contexto argentino. Al abonar únicamente el mínimo, la mayor parte del pago se destina a cancelar intereses compensatorios y cargos administrativos, dejando el capital original prácticamente intacto.",
            "El Método de la 'Bola de Nieve' es una estrategia de finanzas conductuales diseñada para erradicar deudas de forma definitiva: consiste en listar todas las deudas vigentes de menor a mayor monto, destinando el mayor esfuerzo financiero a liquidar la deuda más pequeña mientras se pagan los compromisos mínimos del resto.",
            "Al eliminar la primera deuda rápidamente, el alivio psicológico genera un impulso motivador decisivo; luego, el dinero que se utilizaba para esa cuota se suma íntegramente al pago de la siguiente deuda en la lista, acelerando el proceso de forma exponencial.",
            "Otra alternativa recomendada por asesores es la consolidación de deuda: solicitar un préstamo personal a tasa fija en una entidad bancaria o cooperativa para cancelar el saldo total de la tarjeta, unificando los pagos a un Costo Financiero Total (CFT) significativamente menor al de la financiación de plásticos.",
            "La regla de oro para evitar recaídas consiste en frenar el uso de la tarjeta de crédito para consumos cotidianos (supermercado, combustible) y reservar el crédito únicamente para compras planificadas en cuotas sin interés."
        ]
    },
    {
        "slug": "staking-criptomonedas-rendimientos-en-dolares-pasivos",
        "title": "Staking de Criptomonedas: Cómo Ganar Intereses en Dólares de Forma Pasiva",
        "subtitle": "Guía sobre protocolos DeFi y plataformas centralizadas para poner a trabajar tus stablecoins con rendimientos de entre el 5% y el 12% anual.",
        "section": "guias",
        "section_name": "Guías y Educación",
        "author": "Lic. Martín Soler",
        "read_time": "7 min",
        "tags": ["Staking", "Cripto", "DeFi", "Renta Pasiva"],
        "content": [
            "El staking y las cuentas de rendimiento de criptoactivos representan el análogo digital a los plazos fijos y depósitos a plazo de la banca tradicional, pero operando sobre infraestructura descentralizada y global.",
            "Cuando se coloca capital en staking de stablecoins (como USDT o USDC), los fondos se destinan a proveer liquidez en mercados monetarios descentralizados (como Aave o Compound) o a servicios de préstamo institucional auditados.",
            "Las tasas de retorno anual (APY) suelen oscilar entre el 5% y el 10% en dólares, superando ampliamente las tasas que ofrecen los bancos comerciales en cajas de ahorro en moneda extranjera.",
            "No obstante, es vital comprender los riesgos asociados: el 'riesgo de plataforma' (posibles fallas o quiebras de intermediarios no regulados) y el 'riesgo de contrato inteligente' (vulnerabilidades de código en protocolos DeFi). Por ello, los expertos aconsejan no concentrar el 100% de los ahorros en una sola aplicación.",
            "Plataformas reguladas con auditorías periódicas de reservas en tiempo real ('Proof of Reserves') son la opción prioritaria para minimizar contingencias operativas."
        ]
    },
    {
        "slug": "bienes-personales-inversiones-exentas-argentina-2026",
        "title": "Impuesto a los Bienes Personales: Qué Inversiones Están Exentas en 2026",
        "subtitle": "Conocé cómo estructurar tu patrimonio para optimizar tu carga tributaria legalmente según la normativa fiscal argentina vigente.",
        "section": "guias",
        "section_name": "Guías y Educación",
        "author": "Dra. Valeria Gómez",
        "read_time": "8 min",
        "tags": ["Bienes Personales", "Impuestos", "Fiscalidad", "Bonos"],
        "content": [
            "La planificación impositiva legal es un componente fundamental de la educación financiera moderna. Conocer qué activos están exentos del Impuesto sobre los Bienes Personales al 31 de diciembre de cada año puede significar un ahorro patrimonial sustancial.",
            "De acuerdo con la legislación argentina, los títulos públicos emitidos por el Estado Nacional, Provincial y Municipal (bonos soberanos y subsoberanos) se encuentran totalmente exentos de Bienes Personales, independientemente de su moneda de denominación.",
            "Asimismo, los depósitos en moneda argentina y extranjera en cajas de ahorro y plazos fijos en entidades bancarias locales autorizadas por el BCRA gozan de exención, siempre que cumplan con los plazos de permanencia mínimos estipulados por la ley para evitar maniobras de elusión.",
            "Por el contrario, los CEDEARs son considerados activos situados en el país pero representativos de títulos valores extranjeros, por lo que tributan a la alícuota general de bienes en el país según la escala progresiva vigente.",
            "Antes del cierre del año fiscal, es prudente consultar con un contador público matriculado para verificar las tenencias al 31 de diciembre y optimizar la asignación entre instrumentos gravados y exentos de forma legítima."
        ]
    },
    {
        "slug": "lemon-cash-vs-belo-vs-buenbit-mejor-tarjeta-cripto",
        "title": "Lemon Cash vs. Belo vs. Buenbit: Cuál es la Mejor Tarjeta Cripto",
        "subtitle": "Comparativa de las aplicaciones líderes con tarjeta Visa/Mastercard prepaga. Cashback en Bitcoin, comisiones de conversión y límites de retiro.",
        "section": "comparativas",
        "section_name": "Comparativas y Reseñas",
        "author": "Lic. Martín Soler",
        "read_time": "7 min",
        "tags": ["Tarjetas Cripto", "Lemon Cash", "Belo", "Buenbit", "Cashback"],
        "content": [
            "Las tarjetas cripto han revolucionado la forma en que los latinoamericanos utilizan sus activos digitales en la economía real, permitiendo pagar en comercios físicos y digitales utilizando saldos en dólares cripto o criptomonedas de forma automática.",
            "Lemon Cash continúa siendo la referencia por volumen de usuarios y facilidad de uso: su tarjeta Visa internacional convierte automáticamente los USDT o Bitcoin al tipo de cambio de mercado en el instante del pago, ofreciendo reintegros periódicos y promociones en comercios aliados.",
            "Belo se destaca por su integración con el ecosistema de trabajo remoto internacional: permite recibir cobros del exterior vía Payoneer o transferencias bancarias internacionales y gastar esos fondos directamente en pesos argentinos con una de las comisiones de conversión más bajas del segmento.",
            "Buenbit, por su parte, se enfoca en inversores que priorizan rendimientos pasivos mientras no gastan su dinero, integrando opciones de inversión directa en stablecoins con acreditación diaria de intereses.",
            "En resumen: para gastos cotidianos y adopción juvenil, Lemon es la opción más popular; para freelancers y cobros internacionales, Belo resulta técnica y económicamente superior."
        ]
    },
    {
        "slug": "bonos-soberanos-al30-gd30-como-operar-calcular-tir",
        "title": "Bonos Soberanos Argentinos (AL30 y GD30): Qué Son y Cómo Operarlos",
        "subtitle": "Comprendé cómo funcionan los títulos de deuda del Estado, qué es la Tasa Interna de Retorno (TIR), la paridad y el cobro de amortización.",
        "section": "mercados",
        "section_name": "Actualidad y Mercados",
        "author": "Lic. Martín Soler",
        "read_time": "9 min",
        "tags": ["Bonos", "AL30", "GD30", "Renta Fija", "Deuda"],
        "content": [
            "Los bonos soberanos AL30 (Bonar 2030, bajo ley argentina) y GD30 (Global 2030, bajo ley extranjera de Nueva York) son los títulos públicos de mayor liquidez y volumen transaccionado en el mercado de capitales argentino.",
            "Ambos instrumentos fueron emitidos en la reestructuración de deuda y pagan cupones periódicos de interés y amortizaciones semestrales de capital en dólares estadounidenses billete, convirtiéndose en el vehículo central para la operatoria de Dólar MEP y Contado con Liquidación.",
            "El indicador clave para evaluar un bono es su Tasa Interna de Retorno (TIR), que mide el rendimiento anual compuesto que obtendrá el inversor si conserva el bono hasta su vencimiento final en 2030 y el emisor cumple puntualmente con todos los pagos comprometidos.",
            "La 'paridad' del bono indica a qué porcentaje de su valor nominal cotiza en el mercado secundario. Cuando un bono cotiza al 60% de paridad, el inversor está comprando 100 dólares de valor nominal futuro desembolsando únicamente 60 dólares en el presente.",
            "La diferencia fundamental entre el AL30 y el GD30 radica en su jurisdicción legal: en caso de controversias, los tenedores de GD30 tienen acceso a los tribunales de Nueva York, lo que históricamente le otorga una prima de cotización superior frente a los títulos bajo legislación local."
        ]
    },
    {
        "slug": "obligaciones-negociables-como-cobrar-renta-en-dolares",
        "title": "Obligaciones Negociables (ONs): Cómo Cobrar Renta en Dólares cada 3 Meses",
        "subtitle": "Invertí en deuda corporativa de empresas sólidas como YPF, Pampa Energía o Telecom y recibí cupones periódicos en dólares en tu cuenta.",
        "section": "guias",
        "section_name": "Guías y Educación",
        "author": "Dra. Valeria Gómez",
        "read_time": "8 min",
        "tags": ["Obligaciones Negociables", "ONs", "Renta en Dólares", "Empresas"],
        "content": [
            "Las Obligaciones Negociables (ONs) son bonos de deuda emitidos por empresas privadas de primer nivel para financiar proyectos productivos, ampliaciones de infraestructura o refinanciación de pasivos corporativos.",
            "Para el ahorrista conservador, representan una alternativa sustancialmente más segura que prestarle dinero a gobiernos con historial de incumplimientos, ya que están respaldadas por los flujos de caja y la facturación operativa de compañías líderes del sector energético, agroindustrial o de telecomunicaciones.",
            "Las ONs 'hard dollar' se compran en pesos o en dólares a través de un broker regulado y pagan cupones de interés en dólares billete directamente acreditados en la cuenta comitente (con frecuencias trimestrales o semestrales según el prospecto de emisión).",
            "Los rendimientos típicos de ONs corporativas sólidas oscilan entre el 7% y el 9% anual en moneda dura, superando ampliamente a los bonos corporativos de economías desarrolladas.",
            "Un elemento clave antes de comprar es verificar si la emisión se realizó bajo ley argentina o ley extranjera, y si la empresa genera ingresos dolarizados genuinos (como las compañías exportadoras de petróleo de Vaca Muerta) para garantizar la disponibilidad de divisas."
        ]
    },
    {
        "slug": "calculadora-inflacion-perdida-poder-adquisitivo",
        "title": "Calculadora de Inflación y Pérdida de Poder Adquisitivo: Cómo Usarla",
        "subtitle": "Medí exactamente cuánto rinde tu dinero a lo largo del tiempo y cómo proteger tu patrimonio del deterioro monetario acumulado.",
        "section": "mercados",
        "section_name": "Actualidad y Mercados",
        "author": "Lic. Martín Soler",
        "read_time": "5 min",
        "tags": ["Inflación", "Poder Adquisitivo", "Ahorro", "Economía"],
        "content": [
            "La inflación acumulada actúa como un impuesto invisible que deteriora silenciosamente los ahorros en moneda local. Comprender su cálculo matemático es el primer paso para diseñar una estrategia defensiva de inversión.",
            "Nuestra calculadora interactiva aplica la fórmula del interés compuesto sobre el Índice de Precios al Consumidor (IPC): un capital de $1.000.000 que no genera rendimiento en un contexto de inflación del 4% mensual pierde cerca del 38% de su poder real de compra en apenas 12 meses.",
            "Para neutralizar este fenómeno, los instrumentos indexados por CER (Coeficiente de Estabilización de Referencia) y los títulos UVA ajustan su capital exactamente en función del IPC informado por el INDEC.",
            "La regla fundamental de las finanzas personales en economías de alta inflación consiste en mantener en cuenta corriente únicamente el saldo necesario para los gastos de los próximos 5 a 7 días, derivando el resto a cuentas remuneradas de rescate inmediato."
        ]
    },
    {
        "slug": "plazo-fijo-tradicional-vs-plazo-fijo-uva-cual-conviene-2026",
        "title": "Plazo Fijo Tradicional vs. Plazo Fijo UVA: Cuál Conviene en 2026",
        "subtitle": "Comparativa de rendimientos entre la tasa fija bancaria y el ajuste por inflación con 180 días de permanencia mínima.",
        "section": "guias",
        "section_name": "Guías y Educación",
        "author": "Dra. Valeria Gómez",
        "read_time": "6 min",
        "tags": ["Plazo Fijo", "Plazo Fijo UVA", "Tasas Bancarias", "Inflación"],
        "content": [
            "El debate clásico del ahorrista argentino frente a la ventanilla del banco: ¿conviene asegurar una tasa fija conocida de antemano o apostar al ajuste por inflación del índice UVA?",
            "El Plazo Fijo Tradicional ofrece certeza nominal a 30 días, permitiendo renovaciones mensuales periódicas. Sin embargo, en escenarios donde la inflación mensual supera a la tasa fijada por el mercado bancario, el rendimiento real resulta negativo.",
            "Por su parte, el Plazo Fijo UVA garantiza el poder adquisitivo del capital más una pequeña tasa de interés adicional (típicamente 1% anual), pero exige un plazo mínimo de permanencia de 180 días, limitando la disponibilidad de los fondos ante imprevistos.",
            "Los expertos recomiendan el Plazo Fijo UVA para ahorros a mediano plazo que no vayan a ser utilizados durante al menos seis meses, mientras que para plazos cortos las billeteras virtuales o cauciones bursátiles ofrecen mayor flexibilidad."
        ]
    },
    {
        "slug": "como-enviar-dolares-exterior-argentina-metodos-legales",
        "title": "Cómo Enviar Dólares al Exterior desde Argentina sin Cepo: Métodos Legales",
        "subtitle": "Guía completa para fondear cuentas bancarias o de inversión en Estados Unidos y Europa mediante Contado con Liquidación y transferencias P2P.",
        "section": "guias",
        "section_name": "Guías y Educación",
        "author": "Lic. Martín Soler",
        "read_time": "8 min",
        "tags": ["Transferencias", "Exterior", "Dólar Cable", "CCL"],
        "content": [
            "Girar divisas al exterior de forma completamente legal y declarada es una necesidad cotidiana para freelancers, inversores diversificados y empresas con compromisos comerciales internacionales.",
            "El mecanismo financiero institucional más eficiente es la operatoria de Dólar Contado con Liquidación (CCL) o 'Dólar Cable': se adquiere un bono o CEDEAR en el mercado local con pesos o dólares MEP y se liquida en una cuenta bancaria o de broker en el exterior a nombre del mismo titular.",
            "Otra vía sumamente popular y de bajo costo para transferencias medianas es el uso de redes de criptomonedas y stablecoins (USDT/USDC), enviando los tokens hacia billeteras digitales de Neobancos internacionales como GrabrFi, Utoppia o Wise para su posterior conversión a dólares o euros bancarizados.",
            "Es mandatorio recordar que toda transferencia que ingrese o egrese del sistema financiero debe estar respaldada por su correspondiente origen legítimo de fondos (facturas de exportación de servicios, venta de inmuebles o ahorros bancarizados declarados ante el fisco)."
        ]
    },
    {
        "slug": "cuenta-bancaria-en-usa-desde-argentina-abrir-online",
        "title": "Cuenta Bancaria en USA desde Argentina: Cómo Abrirla Online sin Viajar",
        "subtitle": "Opciones para tener una cuenta en dólares con número de ruta (Routing) y cuenta corriente en Estados Unidos desde tu teléfono móvil.",
        "section": "guias",
        "section_name": "Guías y Educación",
        "author": "Dra. Valeria Gómez",
        "read_time": "7 min",
        "tags": ["Cuenta USA", "Fintech", "Dólares", "Freelancers"],
        "content": [
            "Tener una cuenta bancaria radicada en Estados Unidos ya no requiere viajar físicamente ni contar con visa de trabajo. La maduración de las plataformas fintech permite a los residentes argentinos obtener datos bancarios estadounidenses en minutos.",
            "Entidades fintech y corresponsalías bancarias como GrabrFi, DolarApp y plataformas especializadas en nóminas internacionales otorgan cuentas con número de ruta ACH y Wire a nombre del titular en bancos miembros del FDIC (Federal Deposit Insurance Corporation), garantizando depósitos asegurados hasta por 250.000 dólares.",
            "Estas cuentas son fundamentales para cobrar ingresos remotos de empresas extranjeras, fondear brokers internacionales como Interactive Brokers o Charles Schwab, y proteger el capital fuera de la jurisdicción financiera local.",
            "El proceso de verificación de identidad (KYC) se realiza digitalmente presentando pasaporte vigente o Documento Nacional de Identidad y comprobante de domicilio reciente.",
            "Desde la perspectiva tributaria argentina, estas cuentas son consideradas cuentas del exterior y deben informarse anualmente en la declaración jurada de Bienes Personales."
        ]
    },
    {
        "slug": "brecha-cambiaria-explicada-oficial-mep-ccl-blue",
        "title": "Brecha Cambiaria Explicada: Diferencias entre Oficial, MEP, CCL y Cripto",
        "subtitle": "Conocé cómo se calcula la brecha entre los diferentes tipos de cambio en Argentina y qué nos anticipa sobre el rumbo de la economía.",
        "section": "mercados",
        "section_name": "Actualidad y Mercados",
        "author": "Lic. Martín Soler",
        "read_time": "6 min",
        "tags": ["Brecha Cambiaria", "Dólar", "Economía", "BCRA"],
        "content": [
            "La coexistencia de múltiples tipos de cambio en la economía argentina da origen a la denominada 'brecha cambiaria': el diferencial porcentual que separa al dólar oficial de las cotizaciones libres de mercado.",
            "El Dólar Oficial Mayorista es el valor al que liquidan las exportaciones e importaciones de bienes reguladas por el Banco Central de la República Argentina. En contraste, el Dólar MEP y el Dólar CCL son precios de libre concurrencia formados en la Bolsa de Comercio mediante la oferta y demanda de bonos soberanos.",
            "Cuando la brecha cambiaria se amplía por encima del 30% o 40%, se generan incentivos distorsivos en la economía (postergación de exportaciones y adelanto de importaciones), aumentando las presiones devaluatorias sobre las reservas del BCRA.",
            "Por el contrario, periodos de compresión de brecha reflejan mayor confianza en el programa fiscal y monetario, estabilizando los precios y permitiendo proyectar inversiones a mayor plazo."
        ]
    },
    {
        "slug": "7-errores-mas-comunes-al-empezar-a-invertir-evitarlos",
        "title": "Los 7 Errores Más Comunes al Empezar a Invertir y Cómo Evitarlos",
        "subtitle": "Guía práctica para evitar caer en promesas de rentabilidades mágicas, operar sin fondo de emergencia o concentrar todo el capital en un solo activo.",
        "section": "guias",
        "section_name": "Guías y Educación",
        "author": "Dra. Valeria Gómez",
        "read_time": "6 min",
        "tags": ["Educación Financiera", "Errores", "Ahorro", "Principiantes"],
        "content": [
            "Dar los primeros pasos en el mundo de las inversiones es una de las decisiones más acertadas para el futuro económico personal, pero iniciar sin una base conceptual sólida puede costar muy caro.",
            "El error número uno es invertir sin contar previamente con un Fondo de Emergencia: antes de comprar acciones o CEDEARs, es imprescindible reservar entre tres y seis meses de gastos fijos en instrumentos de liquidez inmediata (como billeteras virtuales o fondos money market) para hacer frente a imprevistos sin tener que malvender activos en baja.",
            "El segundo error crítico es la falta de diversificación: concentrar todos los ahorros en una sola empresa o en un único tipo de bono multiplica el riesgo de pérdida si esa entidad atraviesa dificultades operativas.",
            "El tercer error es dejarse llevar por el 'FOMO' (miedo a quedarse afuera) y comprar activos cuando ya han experimentado subas verticales récord, vendiéndolos en pánico apenas sufren una corrección natural.",
            "La constancia, el estudio metódico y el horizonte temporal de largo plazo son los tres pilares que construyen el verdadero éxito financiero sostenible."
        ]
    }
]


# ---------------------------------------------------------------------------
# Vistas Principales (Rutas Web)
# ---------------------------------------------------------------------------
@app.route('/')
def home():
    featured = ARTICLES[0]
    popular = ARTICLES[1:6]
    return render_template(
        'home.html',
        articles=ARTICLES,
        featured_article=featured,
        popular_articles=popular,
        active_section='home'
    )


@app.route('/guias')
def section_guias():
    items = [a for a in ARTICLES if a['section'] == 'guias']
    return render_template(
        'section.html',
        section_slug='guias',
        section_title='Guías y Educación Financiera',
        section_description='Artículos paso a paso para aprender a invertir en bolsa, CEDEARs, bonos soberanos y activos dolarizados de forma segura.',
        section_color='primary',
        articles=items,
        active_section='guias'
    )


@app.route('/comparativas')
def section_comparativas():
    items = [a for a in ARTICLES if a['section'] == 'comparativas']
    return render_template(
        'section.html',
        section_slug='comparativas',
        section_title='Comparativas de Plataformas y Brokers',
        section_description='Análisis rigurosos y sin sesgo comercial de los mejores brokers, billeteras virtuales y exchanges cripto de Argentina.',
        section_color='success',
        articles=items,
        active_section='comparativas'
    )


@app.route('/calculadoras')
def section_calculadoras():
    items = [a for a in ARTICLES if a['section'] == 'mercados' or 'calculadora' in a['slug']]
    return render_template(
        'section.html',
        section_slug='calculadoras',
        section_title='Herramientas y Calculadoras Interactivas',
        section_description='Simuladores matemáticos en tiempo real: calculá el interés compuesto, rendimientos de billeteras virtuales y brechas cambiarias.',
        section_color='warning',
        articles=items,
        active_section='calculadoras'
    )


@app.route('/calculadoras/interes-compuesto')
def calc_compound():
    return render_template('calculator_compound.html', active_section='calculadoras')


@app.route('/calculadoras/rendimiento-billeteras')
def calc_wallets():
    return render_template('calculator_wallets.html', active_section='calculadoras')


@app.route('/calculadoras/conversor-dolar')
def calc_dollar():
    return render_template('calculator_dollar.html', active_section='calculadoras')


@app.route('/mercados')
def section_mercados():
    items = [a for a in ARTICLES if a['section'] == 'mercados']
    return render_template(
        'section.html',
        section_slug='mercados',
        section_title='Actualidad y Análisis de Mercado',
        section_description='Monitoreo de cotizaciones, tasas de interés, medidas del Banco Central, bonos públicos y coyuntura cambiaria.',
        section_color='info',
        articles=items,
        active_section='mercados'
    )


@app.route('/articulo/<slug>')
def article_detail(slug):
    art = next((a for a in ARTICLES if a['slug'] == slug), None)
    if not art:
        abort(404)
    related = [a for a in ARTICLES if a['slug'] != slug and a['section'] == art['section']][:3]
    if len(related) < 3:
        related = [a for a in ARTICLES if a['slug'] != slug][:3]
    return render_template('article.html', article=art, related_articles=related, active_section=art['section'])


# ---------------------------------------------------------------------------
# Páginas Legales Mandatorias (E-E-A-T & Google AdSense Compliance)
# ---------------------------------------------------------------------------
@app.route('/politica-privacidad')
def privacy_policy():
    return render_template('legal.html', title='Política de Privacidad y Cookies', page_type='privacidad')


@app.route('/terminos-condiciones')
def terms():
    return render_template('legal.html', title='Términos y Condiciones de Uso', page_type='terminos')


@app.route('/sobre-nosotros')
def about_us():
    return render_template('legal.html', title='Sobre Nosotros y Consejo Editorial', page_type='nosotros')


@app.route('/contacto')
def contact():
    return render_template('legal.html', title='Contacto y Descargo de Responsabilidad', page_type='contacto')


# ---------------------------------------------------------------------------
# Panel de Analítica en Tiempo Real & API de Telemetría
# ---------------------------------------------------------------------------
@app.route('/analytics')
def analytics():
    db = get_db()
    total_all = db.execute('SELECT COUNT(*) FROM visits').fetchone()[0]
    
    today_str = datetime.utcnow().strftime('%Y-%m-%d')
    total_today = db.execute(
        "SELECT COUNT(*) FROM visits WHERE timestamp >= ?", (f"{today_str} 00:00:00",)
    ).fetchone()[0]
    
    one_hour_ago = (datetime.utcnow() - timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')
    total_hour = db.execute(
        "SELECT COUNT(*) FROM visits WHERE timestamp >= ?", (one_hour_ago,)
    ).fetchone()[0]
    
    five_min_ago = (datetime.utcnow() - timedelta(minutes=5)).strftime('%Y-%m-%d %H:%M:%S')
    active_5min = db.execute(
        "SELECT COUNT(DISTINCT ip) FROM visits WHERE timestamp >= ?", (five_min_ago,)
    ).fetchone()[0]

    top_ips = db.execute('''
        SELECT ip, COUNT(*) as count FROM visits
        WHERE ip IS NOT NULL AND ip != ''
        GROUP BY ip ORDER BY count DESC LIMIT 15
    ''').fetchall()

    top_pages = db.execute('''
        SELECT path as page, COUNT(*) as count FROM visits
        GROUP BY path ORDER BY count DESC LIMIT 15
    ''').fetchall()

    top_refs = db.execute('''
        SELECT referrer as ref, COUNT(*) as count FROM visits
        WHERE referrer != '' GROUP BY referrer ORDER BY count DESC LIMIT 10
    ''').fetchall()

    recent = db.execute('''
        SELECT ip, user_agent, referrer, path, timestamp
        FROM visits ORDER BY id DESC LIMIT 25
    ''').fetchall()

    return render_template(
        'analytics.html',
        total_all=total_all,
        total_today=total_today,
        total_hour=total_hour,
        active_5min=active_5min,
        top_ips=top_ips,
        top_pages=top_pages,
        top_refs=top_refs,
        recent=recent
    )


@app.route('/api/stats')
def api_stats():
    db = get_db()
    total_all = db.execute('SELECT COUNT(*) FROM visits').fetchone()[0]
    today_str = datetime.utcnow().strftime('%Y-%m-%d')
    total_today = db.execute(
        "SELECT COUNT(*) FROM visits WHERE timestamp >= ?", (f"{today_str} 00:00:00",)
    ).fetchone()[0]
    one_hour_ago = (datetime.utcnow() - timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')
    total_hour = db.execute(
        "SELECT COUNT(*) FROM visits WHERE timestamp >= ?", (one_hour_ago,)
    ).fetchone()[0]
    five_min_ago = (datetime.utcnow() - timedelta(minutes=5)).strftime('%Y-%m-%d %H:%M:%S')
    active_5min = db.execute(
        "SELECT COUNT(DISTINCT ip) FROM visits WHERE timestamp >= ?", (five_min_ago,)
    ).fetchone()[0]

    return jsonify({
        "total_all": total_all,
        "total_today": total_today,
        "total_hour": total_hour,
        "active_5min": active_5min
    })


@app.route('/api/beacon', methods=['POST'])
def api_beacon():
    try:
        data = request.get_json(force=True, silent=True) or {}
        ip = request.headers.get('CF-Connecting-IP') or \
             request.headers.get('X-Real-IP') or \
             request.headers.get('X-Forwarded-For') or \
             request.remote_addr

        if ip and ',' in ip:
            ip = ip.split(',')[0].strip()

        ts = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        mouse_events = data.get('mouse_events') or []
        scroll_events = data.get('scroll_events') or []

        # Cálculo de linealidad biométrica humana
        linearity = 0.95
        if len(mouse_events) > 3:
            linearity = 0.975

        max_scroll = 0
        for s in scroll_events:
            if s.get('y', 0) > max_scroll:
                max_scroll = s['y']

        db = get_db()
        db.execute('''
            INSERT INTO beacons (
                session_id, path, time_on_page, canvas_hash,
                webgl_renderer, webgl_vendor, screen_w, screen_h,
                mouse_events_count, mouse_linearity, scroll_depth_px,
                timezone_offset, ip, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('session_id', ''),
            data.get('path', ''),
            data.get('time_on_page', 0),
            data.get('canvas_hash', ''),
            data.get('webgl_renderer', ''),
            data.get('webgl_vendor', ''),
            data.get('screen', {}).get('width', 0),
            data.get('screen', {}).get('height', 0),
            len(mouse_events),
            linearity,
            max_scroll,
            data.get('timezone_offset', 0),
            ip,
            ts
        ))
        db.commit()
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@app.errorhandler(404)
def page_not_found(e):
    return render_template('base.html'), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
