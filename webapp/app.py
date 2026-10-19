import sqlite3
import os
from datetime import datetime, timedelta
from flask import Flask, request, render_template, g, jsonify
from collections import Counter
import re

app = Flask(__name__)

DB_PATH = os.path.join(os.path.dirname(__file__), 'visits.db')

# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exc):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    db = sqlite3.connect(DB_PATH)
    db.execute('''
        CREATE TABLE IF NOT EXISTS visits (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            ip        TEXT,
            user_agent TEXT,
            referrer  TEXT,
            path      TEXT,
            timestamp TEXT
        )
    ''')
    db.execute('''
        CREATE TABLE IF NOT EXISTS behavioral_data (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id      TEXT,
            ip              TEXT,
            path            TEXT,
            timestamp       TEXT,
            canvas_hash     TEXT,
            webgl_renderer  TEXT,
            webgl_vendor    TEXT,
            screen_w        INTEGER,
            screen_h        INTEGER,
            color_depth     INTEGER,
            pixel_ratio     REAL,
            viewport_w      INTEGER,
            viewport_h      INTEGER,
            time_on_page    INTEGER,
            scroll_depth    INTEGER,
            scroll_events   INTEGER,
            max_scroll_speed REAL,
            mouse_events    INTEGER,
            mouse_linearity REAL,
            mouse_avg_speed REAL,
            timezone_offset INTEGER,
            touch_support   INTEGER,
            platform        TEXT,
            language        TEXT,
            do_not_track    TEXT
        )
    ''')
    db.commit()
    db.close()


init_db()


# ---------------------------------------------------------------------------
# Visit tracking middleware
# ---------------------------------------------------------------------------

@app.before_request
def track_visit():
    if request.path.startswith('/static') or request.path == '/favicon.ico':
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
# Article data
# ---------------------------------------------------------------------------

ARTICLES = {

    # ── MUNDO ────────────────────────────────────────────────────────────────
    'colapso-diplomatico-oriente-medio': {
        'slug': 'colapso-diplomatico-oriente-medio',
        'title': 'Colapso diplomático en Oriente Medio: las potencias buscan una salida negociada',
        'subtitle': 'Tras meses de escalada, Estados Unidos, China y la Unión Europea impulsan una cumbre de emergencia en Ginebra.',
        'content': [
            'Las tensiones en Oriente Medio alcanzaron un punto crítico esta semana cuando las delegaciones de doce países se reunieron de urgencia en la sede de las Naciones Unidas en Ginebra para intentar frenar un conflicto que amenaza con desestabilizar toda la región. Los ministros de Exteriores de Estados Unidos, China, Francia, Alemania y Arabia Saudí participaron en conversaciones maratonianas que se extendieron durante más de cuarenta horas consecutivas, según confirmaron fuentes diplomáticas. El secretario general de la ONU calificó el momento como "el más delicado de la última década" y pidió a todas las partes que antepongan el diálogo a cualquier acción militar unilateral.',
            'En el centro del debate se encuentra la disputa por el control de tres zonas fronterizas estratégicas cuya soberanía llevan décadas en litigio. Los analistas señalan que la combinación de un ciclo electoral en varios países clave, el alza de los precios del crudo y la proliferación de milicias armadas con acceso a tecnología de drones avanzada ha creado un cóctel explosivo sin precedentes. "Nunca antes habíamos visto una concentración tan alta de actores no estatales capaces de proyectar fuerza a distancias de cientos de kilómetros", explicó la directora del Centro de Estudios Estratégicos de Berlín en declaraciones a PulsoMundial.',
            'El borrador de acuerdo provisional que circula entre las delegaciones contempla una zona desmilitarizada supervisada por observadores internacionales, el congelamiento de movimientos de tropas durante noventa días y la apertura de corredores humanitarios para los tres millones de civiles desplazados. Sin embargo, dos de las partes principales aún no han firmado el documento y exigen garantías adicionales antes de comprometerse formalmente. Las próximas setenta y dos horas serán decisivas para determinar si la diplomacia puede imponerse sobre la lógica del enfrentamiento.',
            'Mientras tanto, en las capitales occidentales crece la presión de la opinión pública para que sus gobiernos adopten una posición más activa. Miles de personas se manifestaron en Londres, París y Berlín exigiendo un cese inmediato de hostilidades y el envío de ayuda humanitaria de emergencia. Los mercados financieros reaccionaron con volatilidad: el barril de Brent superó los 105 dólares durante la sesión asiática antes de estabilizarse cerca de los 98 dólares tras los primeros anuncios positivos desde Ginebra.',
        ],
        'author': 'Carmen Villalba',
        'date': '14 oct 2026',
        'image_id': 10,
        'section': 'mundo',
        'section_name': 'Mundo',
        'section_color': '#3b82f6',
        'read_time': '6 min',
        'tags': ['diplomacia', 'Oriente Medio', 'ONU', 'conflicto'],
    },
    'elecciones-india-2026': {
        'slug': 'elecciones-india-2026',
        'title': 'India celebra las elecciones regionales más vigiladas de su historia',
        'subtitle': 'Más de 400 millones de votantes acuden a las urnas en un proceso marcado por la presencia masiva de sistemas de verificación biométrica.',
        'content': [
            'Con una participación sin precedentes que los organismos electorales estiman por encima del 74%, India ha vivido este mes la jornada electoral regional más compleja de su historia democrática. Los comicios, que abarcan ocho estados del norte y el este del país, son considerados un termómetro clave para medir el apoyo al gobierno central antes de las elecciones generales previstas para 2027. Más de un millón de agentes electorales, apoyados por drones de vigilancia y sistemas de inteligencia artificial para detectar irregularidades, han supervisado un proceso que se extiende a lo largo de cuatro días consecutivos.',
            'La introducción masiva de máquinas de votación con verificación de huella dactilar y reconocimiento de iris ha generado debate entre los partidos de la oposición, algunos de los cuales exigen una auditoría independiente del software utilizado. El gobierno defiende que el nuevo sistema reduce el fraude a prácticamente cero y acelera el recuento, prometiendo resultados preliminares en menos de seis horas tras el cierre de los colegios. Organizaciones internacionales de observación electoral, incluida la Unión Europea, han enviado delegaciones que por ahora no han detectado irregularidades sistemáticas.',
            'Las encuestas a pie de urna apuntan a una fragmentación del voto que podría dar lugar a gobiernos de coalición en al menos cuatro de los ocho estados en disputa. Las cuestiones económicas, especialmente el desempleo juvenil y el precio de los alimentos, han dominado la campaña por encima de los tradicionales ejes identitarios. La candidata del principal partido de oposición afirmó que los resultados "enviarán un mensaje claro a Nueva Delhi sobre las prioridades reales de la ciudadanía".',
            'Los analistas internacionales prestan especial atención a los estados de Uttar Pradesh y Bihar, cuyo peso demográfico los convierte en auténticos árbitros del equilibrio político nacional. Una victoria de la oposición en ambos pondría en aprietos la agenda legislativa del gobierno central para los próximos meses. Los resultados finales se esperan para el miércoles, aunque las impugnaciones legales podrían prolongar el proceso durante semanas en algunos distritos.',
        ],
        'author': 'Rakesh Mehra',
        'date': '10 oct 2026',
        'image_id': 22,
        'section': 'mundo',
        'section_name': 'Mundo',
        'section_color': '#3b82f6',
        'read_time': '5 min',
        'tags': ['India', 'elecciones', 'democracia', 'Asia'],
    },
    'refugiados-africa-corredor': {
        'slug': 'refugiados-africa-corredor',
        'title': 'El Sahel afronta su mayor crisis de desplazamiento en dos décadas',
        'subtitle': 'ACNUR cifra en 8,3 millones los desplazados internos en la región y pide una respuesta internacional urgente.',
        'content': [
            'La agencia de refugiados de la ONU (ACNUR) publicó esta semana su informe trimestral sobre el Sahel con cifras que superan cualquier registro previo: 8,3 millones de personas desplazadas internamente en Mali, Burkina Faso, Níger y Chad, con un incremento del 23% respecto al mismo período del año anterior. La combinación de conflictos armados protagonizados por grupos yihadistas, las consecuencias de una sequía histórica que ha destruido las cosechas en tres temporadas consecutivas y la inestabilidad política derivada de los sucesivos golpes de Estado explica la magnitud de la catástrofe humanitaria.',
            'Los campos de acogida improvisados en las periferias de ciudades como Niamey, Bamako y N\'Djamena operan al triple de su capacidad prevista. El acceso al agua potable, los alimentos y la atención médica básica es deficitario para más de la mitad de los desplazados. Médicos Sin Fronteras denunció esta semana tasas de malnutrición aguda en niños menores de cinco años que superan el umbral de emergencia definido por la Organización Mundial de la Salud en varias zonas del norte de Burkina Faso.',
            'La respuesta internacional ha sido calificada de insuficiente por las organizaciones sobre el terreno. El llamamiento humanitario de la ONU para el Sahel, dotado con 2.100 millones de dólares, apenas ha recibido el 38% de financiación prometida por los estados donantes. Varios países europeos han reducido sus contribuciones alegando presiones presupuestarias internas, una decisión que ha generado una ola de críticas de las ONG especializadas en cooperación al desarrollo.',
            'El director regional de ACNUR visitó la semana pasada varios campos en Niger y describió las condiciones como "las peores que he presenciado en veinte años de carrera". Los líderes de los países afectados han solicitado una reunión de urgencia del Consejo de Seguridad de la ONU para reclamar apoyo militar coordinado contra las milicias armadas y fondos adicionales para la reconstrucción de infraestructuras básicas destruidas durante los conflictos.',
        ],
        'author': 'Aminata Diallo',
        'date': '8 oct 2026',
        'image_id': 34,
        'section': 'mundo',
        'section_name': 'Mundo',
        'section_color': '#3b82f6',
        'read_time': '5 min',
        'tags': ['Sahel', 'refugiados', 'humanitario', 'África'],
    },
    'ue-ampliacion-balcanes': {
        'slug': 'ue-ampliacion-balcanes',
        'title': 'La UE cierra el capítulo más difícil de la adhesión de los Balcanes Occidentales',
        'subtitle': 'El Parlamento Europeo aprueba por amplia mayoría el inicio formal de negociaciones de acceso con Albania y Macedonia del Norte.',
        'content': [
            'El Parlamento Europeo aprobó el martes con 487 votos a favor, 112 en contra y 34 abstenciones la apertura formal del proceso de adhesión para Albania y Macedonia del Norte, dando un paso histórico que pone fin a años de bloqueos políticos internos. La votación, celebrada en Estrasburgo, fue recibida con euforia en Tirana y Skopie, donde miles de ciudadanos se congregaron frente a las sedes de gobierno para celebrar lo que los líderes regionales describieron como "el inicio de un futuro europeo real". La presidenta de la Comisión Europea calificó el momento como "una victoria de los valores fundacionales de la Unión".',
            'El camino hasta aquí ha sido extraordinariamente tortuoso. Albania y Macedonia del Norte esperaban el inicio formal de negociaciones desde 2019, cuando el Consejo Europeo lo aprobó en principio pero varios estados miembros impusieron vetos sucesivos vinculados a disputas bilaterales. La resolución de la querella de nombre que durante décadas enfrentó a Macedonia del Norte con Grecia, y los avances en el estado de derecho exigidos por los informes anuales de la Comisión, han sido los elementos clave que finalmente desbloquearon la situación.',
            'Las negociaciones de adhesión son un proceso complejo que puede durar entre cinco y diez años, durante los cuales los países candidatos deben adoptar y aplicar el acervo comunitario en 35 capítulos temáticos que abarcan desde la política comercial hasta los derechos fundamentales. Los expertos estiman que tanto Albania como Macedonia del Norte necesitarán reformas profundas en sus sistemas judiciales, en la lucha contra la corrupción y en la gestión de sus fronteras antes de poder cumplir todos los requisitos.',
            'Serbia, Montenegro, Bosnia-Herzegovina y Kosovo observan el proceso con atención, conscientes de que el avance de sus vecinos puede acelerar o complicar sus propias trayectorias de integración. La guerra en Ucrania y la necesidad geopolítica de consolidar el flanco suroriental de Europa han dado nuevo impulso político a una ampliación que muchos analistas consideraban aparcada indefinidamente. Bruselas espera que el proceso sirva también como ancla de estabilidad democrática en una subregión históricamente convulsa.',
        ],
        'author': 'Petra Kovačević',
        'date': '6 oct 2026',
        'image_id': 45,
        'section': 'mundo',
        'section_name': 'Mundo',
        'section_color': '#3b82f6',
        'read_time': '4 min',
        'tags': ['Unión Europea', 'Balcanes', 'ampliación', 'diplomacia'],
    },
    'cambio-climatico-cop31': {
        'slug': 'cambio-climatico-cop31',
        'title': 'COP31 en Sídney: las naciones divergen sobre el fondo de pérdidas y daños',
        'subtitle': 'Las negociaciones climáticas más importantes del año arrancan con diferencias profundas entre países desarrollados y en desarrollo.',
        'content': [
            'La trigésimo primera Conferencia de las Partes sobre el Clima (COP31) inauguró esta semana sus sesiones en el Centro de Convenciones Internacional de Sídney con la participación de delegaciones de 198 países y más de 40.000 acreditados entre diplomáticos, científicos, periodistas y representantes de la sociedad civil. El punto más conflictivo del orden del día es la operacionalización del Fondo de Pérdidas y Daños creado en la COP27 de Sharm el-Sheij: los países en desarrollo exigen que esté plenamente capitalizado con al menos 400.000 millones de dólares anuales, mientras que las naciones ricas proponen cifras muy inferiores y mecanismos de préstamo en lugar de donaciones directas.',
            'Los informes científicos presentados en la sesión inaugural no dejan lugar al optimismo: el Panel Intergubernamental sobre el Cambio Climático (IPCC) confirmó que 2025 fue el año más caluroso jamás registrado en la historia de la humanidad, superando el umbral de 1,5°C de calentamiento respecto a los niveles preindustriales por undécimo mes consecutivo. Las emisiones globales de CO₂, lejos de reducirse, aumentaron un 1,2% respecto al año anterior, impulsadas por el crecimiento industrial de Asia meridional y el repunte de la demanda energética en Europa tras los cortes de suministro del invierno pasado.',
            'La presidencia australiana de la COP ha propuesto un texto de negociación en tres bloques: el primero aborda la aceleración del abandono de los combustibles fósiles; el segundo trata la financiación climática para los países más vulnerables; y el tercero introduce por primera vez un mecanismo vinculante de revisión quinquenal de las contribuciones nacionales determinadas. Los expertos consideran este último elemento el más revolucionario y también el más difícil de alcanzar, dado el rechazo frontal de varios grandes emisores.',
            'Al margen de las negociaciones formales, una coalición de 47 islas Estado y países costeros de baja altitud presentó una demanda colectiva ante el Tribunal Internacional de Justicia para que reconozca el derecho a un ambiente estable como un derecho humano fundamental. La acción legal, preparada durante cuatro años, marca un punto de inflexión en la estrategia de los países más vulnerables, que ya no confían exclusivamente en las vías diplomáticas para proteger su existencia.',
        ],
        'author': 'Lena Fischer',
        'date': '4 oct 2026',
        'image_id': 58,
        'section': 'mundo',
        'section_name': 'Mundo',
        'section_color': '#3b82f6',
        'read_time': '6 min',
        'tags': ['cambio climático', 'COP31', 'medioambiente', 'ONU'],
    },
    'taiwan-ejercicios-militares': {
        'slug': 'taiwan-ejercicios-militares',
        'title': 'Tensión en el estrecho: China lanza sus mayores ejercicios militares en cinco años',
        'subtitle': 'Washington y Tokio emiten declaraciones conjuntas de preocupación mientras Taipéi activa su protocolo de defensa.',
        'content': [
            'Las Fuerzas Armadas de la República Popular China iniciaron el lunes una serie de maniobras militares en el estrecho de Taiwán descritas por el Ministerio de Defensa de Pekín como "ejercicios de entrenamiento rutinarios", pero que por su escala y sofisticación han encendido todas las alarmas en las capitales de la región Indo-Pacífico. Más de ochenta aeronaves de combate, cuarenta navíos de guerra y submarinos nucleares han participado en las maniobras, según datos satelitales analizados por el Instituto Internacional de Estudios Estratégicos de Londres. Es la mayor concentración de fuerza china cerca de la isla desde los ejercicios de agosto de 2022.',
            'El gobierno de Taipéi activó su protocolo de defensa nacional, desplegando cazas F-16V y misiles antibuque a lo largo de la costa occidental y convocando sesiones de emergencia del Consejo de Seguridad Nacional. La presidenta taiwanesa afirmó en una comparecencia televisada que "Taiwán no cederá ante la presión ni abandonará su camino democrático" y agradeció la solidaridad expresada por sus aliados internacionales. El Ministerio de Defensa taiwanés reportó la incursión de 47 aeronaves en la zona de identificación de defensa aérea durante las primeras 24 horas de ejercicios.',
            'Estados Unidos respondió enviando dos grupos de combate de portaaviones a las proximidades del estrecho y emitiendo una declaración conjunta con Japón y Australia en la que califican los ejercicios de "desestabilizadores e injustificados". El secretario de Estado norteamericano realizó llamadas urgentes a sus homólogos de la región y reafirmó el compromiso de Washington con la defensa de Taiwán bajo la Ley de Relaciones con Taiwán. China rechazó las críticas calificándolas de "injerencia en asuntos internos soberanos".',
            'Los mercados asiáticos reaccionaron con caídas generalizadas en las primeras horas de la mañana del lunes, aunque recuperaron parte de las pérdidas al cierre de la sesión europea. Las acciones de las principales empresas de semiconductores con sede en Taiwán sufrieron especial presión dada su posición central en las cadenas de suministro globales de tecnología. Los analistas geopolíticos advierten que aunque las probabilidades de un conflicto armado siguen siendo bajas a corto plazo, la repetición de estos ciclos de escalada erosiona progresivamente los mecanismos de gestión de crisis existentes.',
        ],
        'author': 'James Wei',
        'date': '2 oct 2026',
        'image_id': 67,
        'section': 'mundo',
        'section_name': 'Mundo',
        'section_color': '#3b82f6',
        'read_time': '5 min',
        'tags': ['Taiwán', 'China', 'geopolítica', 'Indo-Pacífico'],
    },

    # ── ECONOMÍA ─────────────────────────────────────────────────────────────
    'recesion-europa-2026': {
        'slug': 'recesion-europa-2026',
        'title': 'Europa al borde de la recesión técnica: el BCE debate una nueva bajada de tipos',
        'subtitle': 'El PIB de la zona euro cae un 0,3% en el tercer trimestre y la inflación repunta al 3,1%, complicando la hoja de ruta monetaria.',
        'content': [
            'La oficina de estadísticas de la Unión Europea (Eurostat) publicó el jueves los datos preliminares del PIB de la zona euro para el tercer trimestre de 2026 y las cifras han generado una sacudida en los mercados financieros: la economía del bloque se contrajo un 0,3% respecto al trimestre anterior, encadenando así dos trimestres consecutivos de crecimiento negativo y cumpliendo la definición técnica de recesión. Alemania, la mayor economía de la región, encabeza la contracción con una caída del 0,6%, arrastrada por el desplome de las exportaciones industriales y la debilidad de la demanda interna.',
            'El Banco Central Europeo se reúne la próxima semana en una sesión que promete ser de las más tensas de los últimos años. Una parte del Consejo de Gobierno aboga por una nueva reducción de los tipos de interés de referencia, actualmente en el 2,75%, argumentando que la economía necesita estímulo urgente. La facción contraria advierte de que la inflación, que ha repuntado al 3,1% en septiembre desde el 2,4% de julio impulsada por los precios energéticos y los alimentos, hace prematuro cualquier nuevo relajamiento monetario. La presidenta del BCE ha preferido no adelantar la decisión y ha insistido en que se tomarán "los datos como guía, no los calendarios".',
            'La crisis industrial en Alemania tiene raíces estructurales que van más allá del ciclo económico: la transición energética está resultando más costosa y lenta de lo previsto, los precios de la electricidad industrial siguen siendo tres veces más altos que en Estados Unidos, y la competencia china en automóviles eléctricos ha erosionado cuotas de mercado que se creían intocables. El gobierno federal anunció esta semana un paquete de emergencia de 40.000 millones de euros en inversión pública e incentivos fiscales para la reindustrialización, pero los economistas debaten si llega tarde y si es suficiente.',
            'Los países del sur de Europa, paradójicamente, presentan una imagen más resistente: España creció un 0,4% y Portugal un 0,5% en el mismo período, gracias al turismo, la inversión en energías renovables y la atracción de empresas tecnológicas que relocalizar operaciones desde Asia. Esta divergencia interna complica la gestión de una política monetaria única que debe servir simultáneamente a economías en situaciones muy distintas, un dilema clásico del diseño institucional de la eurozona que vuelve a estar sobre la mesa con toda su crudeza.',
        ],
        'author': 'Friedrich Bauer',
        'date': '15 oct 2026',
        'image_id': 78,
        'section': 'economia',
        'section_name': 'Economía',
        'section_color': '#10b981',
        'read_time': '6 min',
        'tags': ['economía', 'BCE', 'recesión', 'Europa'],
    },
    'bitcoin-etf-aprobacion': {
        'slug': 'bitcoin-etf-aprobacion',
        'title': 'El mercado de ETFs de Bitcoin supera el billón de dólares en activos gestionados',
        'subtitle': 'Dos años después de la aprobación masiva por la SEC, los fondos cotizados de criptomonedas se consolidan como categoría de inversión mainstream.',
        'content': [
            'El conjunto de fondos cotizados en bolsa (ETF) respaldados directamente por Bitcoin superó esta semana el umbral histórico de un billón de dólares en activos bajo gestión a nivel global, según datos agregados de Bloomberg Intelligence. El hito se produce a poco más de dos años de la aprobación masiva de estos instrumentos por parte de la Comisión de Valores y Bolsa de Estados Unidos (SEC) en enero de 2024, que marcó el punto de inflexión para la adopción institucional de los activos digitales. BlackRock, Fidelity y Vanguard controlan conjuntamente el 61% del mercado, con el ETF iShares Bitcoin de BlackRock como el mayor vehículo individual con 387.000 millones bajo gestión.',
            'El precio de Bitcoin ha respondido al contexto macroeconómico con volatilidad pero con una tendencia alcista sostenida a largo plazo: cotiza actualmente en torno a los 94.000 dólares, habiendo tocado un máximo histórico de 121.000 dólares en marzo pasado antes de la corrección provocada por las turbulencias bancarias en Asia. Los gestores de fondos de pensiones, antes completamente ausentes de la clase de activo, representan ya el 14% de los inversores en ETFs de Bitcoin según la encuesta trimestral de JP Morgan a inversores institucionales.',
            'La consolidación del mercado de ETFs ha tenido efectos secundarios sobre el ecosistema cripto más amplio. Las plataformas de intercambio descentralizadas han perdido cuota de volumen frente a los instrumentos regulados, y varios exchanges independientes han anunciado reestructuraciones o cierres al no poder competir con los costes de distribución y la confianza que ofrecen los grandes gestores de activos tradicionales. Los defensores de la descentralización expresan preocupación por la creciente concentración del mercado de Bitcoin en manos de pocos actores institucionales.',
            'El Congreso de Estados Unidos debate actualmente la Ley de Mercados de Activos Digitales, que establecería un marco regulatorio integral para las criptomonedas, clarificando qué activos son valores, cuáles son materias primas y cómo deben supervisarse los intermediarios. La aprobación de dicha ley, prevista para el primer trimestre de 2027 si las negociaciones avanzan según lo esperado, podría abrir la puerta a la aprobación de ETFs sobre otras criptomonedas y a la participación de fondos soberanos en el mercado.',
        ],
        'author': 'Sofía Mendoza',
        'date': '13 oct 2026',
        'image_id': 89,
        'section': 'economia',
        'section_name': 'Economía',
        'section_color': '#10b981',
        'read_time': '5 min',
        'tags': ['Bitcoin', 'ETF', 'criptomonedas', 'inversión'],
    },
    'cadenas-suministro-reshoring': {
        'slug': 'cadenas-suministro-reshoring',
        'title': 'El regreso a casa: por qué el "reshoring" industrial está transformando la economía global',
        'subtitle': 'Empresas europeas y norteamericanas invierten récord en traer producción de vuelta, pero el proceso tiene costes y límites inesperados.',
        'content': [
            'La tendencia al "reshoring" o relocalización industrial, impulsada inicialmente por las disrupciones logísticas de la pandemia y acelerada por las tensiones geopolíticas de los últimos años, está generando una reconfiguración sin precedentes del mapa fabril global. Según datos del Instituto McKinsey de 2026, las empresas del Fortune 500 han anunciado inversiones por valor de 1,8 billones de dólares en nuevas plantas y centros de producción en sus países de origen entre 2023 y 2026, frente a los 340.000 millones del período equivalente anterior a la pandemia. El sector de semiconductores, baterías para vehículos eléctricos y productos farmacéuticos lidera la tendencia.',
            'El caso más emblemático es el de la industria de chips en Estados Unidos, donde la ley CHIPS Act ha catalizado la construcción de doce nuevas fábricas de producción avanzada en suelo norteamericano. TSMC ya tiene operativas sus primeras líneas de producción en Arizona, Intel ha inaugurado plantas en Ohio y Ohio, y Samsung completa las instalaciones de Texas. Sin embargo, los analistas advierten que los costes operativos de estas fábricas son entre un 40% y un 60% superiores a los de sus equivalentes en Asia, lo que se traslada inevitablemente a los precios finales de los dispositivos electrónicos.',
            'En Europa, el fenómeno se concentra especialmente en la fabricación de baterías para automóviles eléctricos, donde compañías como Northvolt, ACC y CATL (con su filial europea) han anunciado gigafactorías en Suecia, Francia y Hungría respectivamente. La dependencia de materiales críticos como el litio, el cobalto y el níquel, todavía extraídos mayoritariamente fuera de Europa, supone el principal cuello de botella para que el modelo sea completamente autónomo. La Comisión Europea trabaja en acuerdos bilaterales con países productores para garantizar el suministro a largo plazo.',
            'El "nearshoring" —la variante que implica trasladar la producción a países cercanos geográficamente pero con menores costes— ha convertido a México, Polonia, Marruecos y Vietnam en destinos estrella de la inversión extranjera directa. México ha recibido más inversión manufacturera en los dos últimos años que en cualquier otra etapa de su historia moderna, especialmente de empresas del sector automotriz y electrónico que buscan proximidad al mercado norteamericano con costes inferiores a los de operar dentro de Estados Unidos.',
        ],
        'author': 'Marco Bellini',
        'date': '11 oct 2026',
        'image_id': 100,
        'section': 'economia',
        'section_name': 'Economía',
        'section_color': '#10b981',
        'read_time': '6 min',
        'tags': ['industria', 'reshoring', 'globalización', 'economía'],
    },
    'amazon-trabajadores-huelga': {
        'slug': 'amazon-trabajadores-huelga',
        'title': 'Huelga global en Amazon: trabajadores de 28 países paralizan almacenes en el Black Friday',
        'subtitle': 'La mayor acción sindical coordinada en la historia de la empresa exige mejores condiciones laborales y límites a la vigilancia algorítmica.',
        'content': [
            'Trabajadores de Amazon en 28 países coordinaron el jueves la mayor huelga simultánea en la historia de la empresa, paralizando parcialmente operaciones en más de 340 centros de distribución y almacenes logísticos en un momento especialmente delicado para la compañía: la víspera de la semana de grandes descuentos que precede al Black Friday, uno de los períodos de mayor volumen de ventas del año. La acción, organizada bajo el paraguas de la alianza internacional "Amazon Workers United", reunió según sus organizadores a más de 85.000 trabajadores en protesta activa en Europa, América del Norte, América Latina y Asia.',
            'Las demandas centrales del movimiento incluyen la eliminación de los sistemas de monitorización de productividad en tiempo real que utilizan algoritmos para evaluar el rendimiento de cada empleado en fracciones de segundo, la reducción de los ritmos de trabajo que los sindicatos atribuyen a un aumento alarmante de lesiones musculoesqueléticas, y la garantía de contratos indefinidos para trabajadores que llevan años encadenando contratos temporales. En varios países europeos, donde la legislación laboral es más favorable para los trabajadores, los sindicatos han logrado acuerdos preliminares que reconocen su representación formal frente a la dirección.',
            'Amazon publicó un comunicado afirmando que la acción afectó "de forma mínima" a sus operaciones globales y que dispone de "suficiente redundancia en su red logística para garantizar las entregas a tiempo". Sin embargo, datos independientes de seguimiento de entregas mostraron retrasos de entre 24 y 72 horas en las principales ciudades europeas afectadas. Las acciones de la empresa cayeron un 3,4% en la sesión de Wall Street antes de recuperar terreno parcialmente al cierre.',
            'El movimiento sindical en Amazon representa un cambio cultural profundo en un sector tecnológico que históricamente había resistido la organización laboral. El ejemplo se extiende más allá de Amazon: trabajadores de otras plataformas de comercio electrónico y logística en varios países han iniciado procesos similares, citando explícitamente las victorias obtenidas en algunos almacenes de Amazon como prueba de que la organización colectiva es posible también en el sector tecnológico.',
        ],
        'author': 'Laura Jennings',
        'date': '9 oct 2026',
        'image_id': 111,
        'section': 'economia',
        'section_name': 'Economía',
        'section_color': '#10b981',
        'read_time': '5 min',
        'tags': ['Amazon', 'huelga', 'sindicalismo', 'trabajo'],
    },
    'oro-precio-record': {
        'slug': 'oro-precio-record',
        'title': 'El oro bate su récord histórico y supera los 3.400 dólares la onza',
        'subtitle': 'La incertidumbre geopolítica, la debilidad del dólar y las compras de bancos centrales impulsan al metal precioso a nuevos máximos.',
        'content': [
            'El precio del oro alcanzó esta semana un nuevo máximo histórico al tocar los 3.412 dólares por onza troy en el mercado spot durante la sesión asiática del martes, superando el récord anterior de 3.187 dólares establecido en mayo pasado. El rally del metal precioso, que acumula una revalorización del 38% en lo que va de año, refleja la confluencia de varios factores que los inversores identifican como el entorno más propicio para el oro en décadas: tensiones geopolíticas elevadas, perspectiva de debilidad del dólar ante posibles bajadas de tipos por la Fed, y un ritmo de compras por parte de bancos centrales que no tiene precedente en la historia moderna.',
            'Los bancos centrales de China, India, Polonia, Turquía y varios países del Golfo han sido los compradores más activos, añadiendo a sus reservas más de 1.100 toneladas en los primeros nueve meses de 2026, según datos del Consejo Mundial del Oro. La motivación es doble: diversificar reservas alejándose del dólar en el contexto de la creciente fragmentación del sistema monetario internacional, y disponer de un activo que no puede ser bloqueado ni confiscado mediante sanciones financieras, como ocurrió con las reservas rusas en 2022.',
            'La demanda de inversores minoristas a través de ETFs respaldados por oro físico también ha experimentado un repunte significativo. Los fondos cotizados globales de oro acumulan entradas netas de 47.000 millones de dólares en el tercer trimestre, la cifra trimestral más alta desde los máximos de incertidumbre del período COVID-19. La demanda de joyería en Asia, especialmente en India de cara a la temporada de bodas y festividades de otoño, aporta un componente adicional de presión compradora al mercado.',
            'Algunos analistas advierten de que el mercado del oro muestra señales de sobrecompra técnica y que una resolución positiva de las tensiones geopolíticas, junto a datos de inflación más moderados que redujeran las expectativas de bajadas de tipos, podría provocar una corrección rápida. Sin embargo, la mayoría de bancos de inversión han revisado al alza sus objetivos de precio para los próximos doce meses, con Goldman Sachs y JP Morgan señalando rangos de entre 3.500 y 3.800 dólares si las condiciones actuales se mantienen.',
        ],
        'author': 'Carlos Fernández',
        'date': '7 oct 2026',
        'image_id': 123,
        'section': 'economia',
        'section_name': 'Economía',
        'section_color': '#10b981',
        'read_time': '4 min',
        'tags': ['oro', 'mercados', 'inversión', 'bancos centrales'],
    },
    'china-deflacion-exportaciones': {
        'slug': 'china-deflacion-exportaciones',
        'title': 'China exporta deflación al mundo mientras su economía interna sigue estancada',
        'subtitle': 'Los precios al productor chinos llevan 22 meses en territorio negativo, presionando a la baja a los productores de todo el mundo.',
        'content': [
            'El Buró Nacional de Estadísticas de China publicó los datos de septiembre con una lectura de precios al productor (PPI) del -2,8% interanual, el vigésimo segundo mes consecutivo de deflación en los precios de fábrica del gigante asiático. El fenómeno, que refleja la sobreproducción estructural en varios sectores clave de la economía china y la debilidad de la demanda doméstica, tiene consecuencias que se propagan rápidamente al resto de la economía global. Los productores europeos, norteamericanos y latinoamericanos de acero, aluminio, paneles solares, baterías y automóviles eléctricos se enfrentan a una competencia de precios que muchos califican de insostenible.',
            'La respuesta de los gobiernos occidentales ha sido una escalada arancelaria sin precedentes. La Unión Europea aprobó en julio aranceles adicionales de hasta el 48% sobre vehículos eléctricos chinos, Estados Unidos elevó las tarifas sobre paneles solares al 50% y Australia impuso restricciones a la importación de acero y aluminio chinos. Pekín respondió con contramedidas que afectan a exportaciones europeas de maquinaria agrícola, productos lácteos y vinos, agudizando las fricciones comerciales que los economistas comparan con las guerras arancelarias de los años treinta del siglo pasado.',
            'Dentro de China, el escenario económico sigue siendo preocupante a pesar de los repetidos paquetes de estímulo lanzados por el gobierno central. El sector inmobiliario, que representa directa e indirectamente cerca del 25% del PIB chino, continúa en contracción tras el colapso de Evergrande y varios desarrolladores más. El consumo interno no termina de despegar, lastrado por el paro juvenil —que supera el 20% según estimaciones independientes— y por la cautela de los hogares ante la incertidumbre sobre el valor de sus propiedades.',
            'El Banco Popular de China ha recortado los tipos de interés cuatro veces en el año y ha reducido el coeficiente de reservas obligatorias de los bancos para liberar liquidez adicional, sin que estas medidas hayan logrado todavía reactivar el crédito con la intensidad necesaria. Algunos economistas proponen medidas más heterodoxas, como transferencias directas a los hogares al estilo del "helicóptero de dinero", pero el gobierno chino ha resistido hasta ahora las presiones en esa dirección, fiel a su preferencia por estímulos orientados a la inversión productiva.',
        ],
        'author': 'Mei Zhang',
        'date': '5 oct 2026',
        'image_id': 134,
        'section': 'economia',
        'section_name': 'Economía',
        'section_color': '#10b981',
        'read_time': '5 min',
        'tags': ['China', 'deflación', 'comercio', 'economía global'],
    },

    # ── TECNOLOGÍA ───────────────────────────────────────────────────────────
    'ia-generativa-regulacion-ue': {
        'slug': 'ia-generativa-regulacion-ue',
        'title': 'La IA Act europea entra en vigor: primeras multas y un sector en reajuste',
        'subtitle': 'Las principales disposiciones de la Ley de Inteligencia Artificial de la UE son ya obligatorias y las empresas tecnológicas aceleran su adaptación.',
        'content': [
            'La plena entrada en vigor de la Ley de Inteligencia Artificial de la Unión Europea, conocida como IA Act, ha marcado un antes y un después en la industria tecnológica global durante este octubre. Las autoridades nacionales de supervisión de los estados miembros recibieron sus primeros expedientes sancionadores esta semana: tres empresas, dos de ellas con sede en Estados Unidos y una con sede en Corea del Sur, han sido notificadas de procedimientos de infracción relacionados con el uso de sistemas de reconocimiento facial en espacios públicos, una práctica prohibida para la mayoría de aplicaciones bajo la nueva regulación. Las multas potenciales podrían alcanzar el 6% de la facturación global de cada empresa.',
            'El reglamento, que clasifica los sistemas de IA en función de su nivel de riesgo, ha obligado a cientos de empresas a llevar a cabo auditorías internas exhaustivas de sus productos y a adaptarlos a los nuevos requisitos de transparencia, explicabilidad y supervisión humana. Los sistemas de alto riesgo —que incluyen aquellos utilizados en selección de personal, evaluación de crédito, gestión de infraestructuras críticas o administración de justicia— deben pasar por procedimientos de evaluación de conformidad antes de ser comercializados en el mercado europeo. La industria estima que los costes de cumplimiento superan los 3.000 millones de euros en el conjunto del sector.',
            'Las grandes plataformas de IA generativa, como los modelos de lenguaje de gran escala, deben cumplir además con obligaciones adicionales de transparencia sobre los datos utilizados en su entrenamiento, las limitaciones de sus sistemas y los riesgos sistémicos potenciales. OpenAI, Google DeepMind, Anthropic y Meta han designado representantes legales en Europa y han publicado sus primeros informes de transparencia bajo el nuevo marco regulatorio, aunque las organizaciones de defensa de derechos digitales critican que los informes carecen de suficiente detalle sobre los conjuntos de datos de entrenamiento.',
            'El debate sobre si la regulación europea frenará la innovación o si, por el contrario, establecerá un estándar global que proteja a ciudadanos y empresas de los riesgos asociados a la IA, está lejos de resolverse. Varios países, incluidos Reino Unido, Japón, Canadá y Brasil, observan atentamente cómo se implementa el IA Act europeo con vistas a diseñar sus propios marcos regulatorios. La competencia entre jurisdicciones por convertirse en referencia global en la gobernanza de la inteligencia artificial se perfila como uno de los grandes ejes geopolíticos de la próxima década.',
        ],
        'author': 'Ana García',
        'date': '14 oct 2026',
        'image_id': 145,
        'section': 'tecnologia',
        'section_name': 'Tecnología',
        'section_color': '#8b5cf6',
        'read_time': '6 min',
        'tags': ['inteligencia artificial', 'regulación', 'UE', 'tecnología'],
    },
    'computacion-cuantica-google': {
        'slug': 'computacion-cuantica-google',
        'title': 'Google anuncia el primer procesador cuántico con corrección de errores a escala práctica',
        'subtitle': 'Willow 2.0 demuestra supremacía cuántica en problemas de simulación química relevantes para la industria farmacéutica.',
        'content': [
            'Google Quantum AI presentó esta semana en la revista Nature los resultados de su nuevo procesador cuántico Willow 2.0, que por primera vez demuestra corrección de errores cuánticos a una escala suficiente para resolver problemas de simulación molecular con relevancia práctica directa para la industria. El procesador, con 1.024 qubits lógicos —un concepto diferente al de los qubits físicos totales—, realizó en 47 minutos una simulación de la dinámica de plegamiento de una proteína relacionada con el Alzheimer que los supercomputadores clásicos más potentes del mundo necesitarían, según los cálculos de los autores, alrededor de diez años para completar.',
            'La clave del avance reside en el sistema de corrección de errores cuánticos, el talón de Aquiles histórico de esta tecnología. Los qubits físicos son intrínsecamente inestables y propensos a errores de decoherencia; la solución es utilizar múltiples qubits físicos para representar un único qubit lógico fiable. El equipo de Google logró mantener la tasa de error por debajo del umbral necesario para que la corrección sea efectiva en operaciones de más de dos horas de duración, un récord absoluto en el campo. "Es el equivalente, en términos de impacto histórico, al transistor para la computación clásica", declaró uno de los investigadores principales.',
            'Las implicaciones para la industria farmacéutica son particularmente significativas. La simulación precisa de moléculas complejas podría acelerar radicalmente el descubrimiento de nuevos fármacos, reduciendo los ciclos de investigación preclínica de años a meses en ciertos tipos de compuestos. Roche, AstraZeneca y Pfizer tienen ya acuerdos de colaboración con Google para explorar aplicaciones en diseño de fármacos. La industria de materiales avanzados y la química de catalizadores para pilas de combustible son otros campos que podrían transformarse radicalmente.',
            'Sin embargo, los expertos independientes piden cautela antes de declarar que la era de la computación cuántica práctica ha llegado definitivamente. IBM, Microsoft, IonQ y Quantinuum también trabajan en arquitecturas competidoras con enfoques técnicos distintos, y la carrera para alcanzar la "ventaja cuántica" en problemas de interés comercial está lejos de resolverse. Los críticos señalan que el problema de plegamiento de proteínas elegido por Google podría no ser representativo de la clase de problemas más relevantes para la industria y piden replicación independiente de los resultados.',
        ],
        'author': 'David Kim',
        'date': '12 oct 2026',
        'image_id': 156,
        'section': 'tecnologia',
        'section_name': 'Tecnología',
        'section_color': '#8b5cf6',
        'read_time': '6 min',
        'tags': ['computación cuántica', 'Google', 'ciencia', 'tecnología'],
    },
    'ciberataque-infraestructura': {
        'slug': 'ciberataque-infraestructura',
        'title': 'El mayor ciberataque coordinado de la historia pone en jaque a tres gobiernos europeos',
        'subtitle': 'Grupos APT vinculados a actores estatales inutilizan temporalmente sistemas de energía, transporte y banca en Alemania, Francia y Polonia.',
        'content': [
            'Durante la madrugada del pasado martes, sistemas críticos de infraestructura en Alemania, Francia y Polonia sufrieron un ataque cibernético coordinado de una sofisticación y escala sin precedentes. Redes eléctricas regionales, sistemas de gestión del tráfico ferroviario y plataformas de banca online experimentaron interrupciones que duraron entre tres y ocho horas, afectando a millones de ciudadanos. Las agencias nacionales de ciberseguridad de los tres países —BSI, ANSSI y CERT Polska— declararon estado de emergencia digital y activaron sus protocolos de respuesta a incidentes coordinados bajo el marco europeo NISD2.',
            'Los análisis forenses preliminares apuntan a la participación de al menos dos grupos de amenaza persistente avanzada (APT) con infraestructura técnica y tácticas consistentes con actores estatales, aunque los investigadores se abstuvieron de realizar atribuciones formales públicas durante la fase aguda del incidente. Los vectores de entrada identificados hasta ahora incluyen vulnerabilidades de día cero en software de gestión industrial (SCADA) ampliamente utilizado en instalaciones de energía, y correos de spear-phishing altamente personalizados dirigidos a empleados de nivel técnico con acceso a sistemas de control.',
            'La Agencia Europea de Seguridad de Redes e Información (ENISA) convocó una reunión de emergencia con los responsables de ciberseguridad de todos los estados miembros para coordinar la respuesta y evaluar el riesgo de propagación a otros países. NATO también activó sus mecanismos de consulta bajo el artículo 4 del tratado tras la petición de Polonia. El incidente ha reavivado el debate sobre la necesidad de establecer una capacidad cibernética defensiva colectiva de la UE con recursos propios, independiente de los medios nacionales.',
            'Las consecuencias económicas del ataque se estiman provisionalmente en más de 4.000 millones de euros entre pérdidas operativas, costes de restauración de sistemas y daños a la reputación del sector financiero europeo. El incidente ha dado nuevo impulso a las negociaciones en curso en el Consejo Europeo para crear un Escudo Cibernético Europeo dotado de 6.000 millones de euros anuales, un proyecto que llevaba dos años bloqueado por disputas presupuestarias entre estados miembros.',
        ],
        'author': 'Tomasz Wiśniewski',
        'date': '10 oct 2026',
        'image_id': 167,
        'section': 'tecnologia',
        'section_name': 'Tecnología',
        'section_color': '#8b5cf6',
        'read_time': '5 min',
        'tags': ['ciberseguridad', 'hackers', 'Europa', 'infraestructura'],
    },
    'neuralink-implante-humano': {
        'slug': 'neuralink-implante-humano',
        'title': 'Neuralink implanta su chip en el décimo paciente y publica los datos del primer año',
        'subtitle': 'Los resultados clínicos preliminares muestran mejoras significativas en comunicación y control motor para personas con parálisis.',
        'content': [
            'Neuralink, la empresa de interfaces cerebro-computadora fundada por Elon Musk, anunció esta semana tanto el implante de su dispositivo N1 en el décimo paciente de su ensayo clínico pivotal como la publicación de los datos de seguimiento del primer año del primer grupo de participantes. Los resultados, aparecidos como preprint en medRxiv y pendientes de revisión por pares, describen mejoras significativas en la capacidad de los pacientes con parálisis tetraplégica para controlar dispositivos digitales mediante el pensamiento. El primer paciente del estudio logra escribir una media de 62 palabras por minuto utilizando únicamente señales cerebrales, superando ampliamente los 40 palabras por minuto que representaban el estado del arte previo en interfaces neuronales no invasivas.',
            'El dispositivo N1 se implanta quirúrgicamente en la corteza motora mediante un robot de precisión que minimiza el daño tisular. Contiene 1.024 electrodos distribuidos en 64 hilos ultradelgados más finos que un cabello humano, que registran la actividad de miles de neuronas individuales. Los datos se procesan mediante algoritmos de inteligencia artificial que aprenden a decodificar las intenciones de movimiento del usuario, mejorando su precisión con el tiempo. La batería se recarga de forma inalámbrica desde el exterior del cráneo y tiene una duración de aproximadamente 24 horas.',
            'Los datos de seguridad son el elemento más vigilado por la comunidad científica. El informe reporta tres casos de reacción inflamatoria leve controlada con medicación, un caso de migración parcial de uno de los hilos que requirió ajuste del algoritmo de decodificación, y ningún caso de infección severa ni de daño neurológico permanente. Sin embargo, los periodos de seguimiento son todavía cortos y los neurocientíficos independientes señalan que los efectos de la presencia crónica de cuerpos extraños en el tejido cerebral son desconocidos a largo plazo.',
            'Más allá de las aplicaciones médicas actuales, Neuralink ha comenzado a hablar públicamente de una segunda generación de dispositivo orientada eventualmente a usuarios sin discapacidad, planteando un debate ético y regulatorio de enorme complejidad. La FDA aprobó el dispositivo solo para uso en condiciones médicas graves; cualquier expansión a usuarios sanos requeriría un proceso regulatorio nuevo. Académicos especializados en neuroética advierten de los riesgos de la comercialización de implantes cerebrales para mejora cognitiva sin un marco de gobernanza robusto.',
        ],
        'author': 'Isabel Torres',
        'date': '8 oct 2026',
        'image_id': 178,
        'section': 'tecnologia',
        'section_name': 'Tecnología',
        'section_color': '#8b5cf6',
        'read_time': '6 min',
        'tags': ['Neuralink', 'neurociencia', 'tecnología', 'salud'],
    },
    'apple-vision-pro-2': {
        'slug': 'apple-vision-pro-2',
        'title': 'Apple Vision Pro 2: más ligero, más barato y con conectividad espacial entre dispositivos',
        'subtitle': 'La segunda generación del visor de realidad espacial de Apple llega con un precio de 2.499 dólares y nuevas funciones de colaboración.',
        'content': [
            'Apple presentó la segunda generación de su visor de realidad espacial Vision Pro en un evento especial celebrado en su campus de Cupertino, confirmando las filtraciones que circulaban desde el verano y añadiendo características que la primera versión prometía pero no entregaba completamente. El Vision Pro 2 pesa 380 gramos, un 22% menos que su predecesor, gracias al uso de titanio de mayor pureza y al rediseño de la óptica que elimina uno de los módulos de procesamiento periférico. El precio de lanzamiento se fija en 2.499 dólares en Estados Unidos, frente a los 3.499 del modelo original, una bajada que Apple atribuye a las economías de escala alcanzadas en la producción.',
            'Las mejoras técnicas incluyen un chip M4 Ultra personalizado que duplica la capacidad de cómputo para el renderizado de entornos tridimensionales, pantallas micro-OLED de 4K por ojo con frecuencia de actualización de 120 Hz y un campo de visión ampliado en un 15%. Pero la novedad más comentada es el sistema de "Continuity Spatial", que permite que múltiples dispositivos Apple —iPhone, iPad, Mac y el propio Vision Pro— compartan un espacio virtual común: los usuarios pueden ver y manipular ventanas de sus otros dispositivos flotando en el espacio físico a su alrededor, y varios usuarios con sus respectivos visores pueden colaborar en el mismo entorno compartido.',
            'El catálogo de aplicaciones para visionOS, el sistema operativo del visor, ha crecido significativamente respecto al lanzamiento original: Apple cifra en 4.200 el número de aplicaciones nativas disponibles el día del lanzamiento, frente a las 600 de la primera generación. Los sectores de diseño industrial, arquitectura, cirugía asistida, formación profesional y entretenimiento inmersivo concentran las aplicaciones más utilizadas por los usuarios del primer Vision Pro según datos de uso publicados por Apple.',
            'La competencia no se queda quieta: Meta lanzó hace tres meses el Quest 4 Pro a 799 dólares con especificaciones técnicas inferiores pero un precio cinco veces menor, y Sony anunció su visor de realidad mixta PSVR3 para el primer trimestre de 2027. La batalla por definir el paradigma dominante en la computación espacial está en sus primeras etapas y ningún competidor tiene todavía el dominio que Apple ha logrado en categorías previas como los smartphones o los smartwatches.',
        ],
        'author': 'Roberto Vega',
        'date': '6 oct 2026',
        'image_id': 189,
        'section': 'tecnologia',
        'section_name': 'Tecnología',
        'section_color': '#8b5cf6',
        'read_time': '5 min',
        'tags': ['Apple', 'realidad virtual', 'tecnología', 'Vision Pro'],
    },
    'starship-mision-luna': {
        'slug': 'starship-mision-luna',
        'title': 'SpaceX completa el cuarto test orbital de Starship con reentrada y aterrizaje perfectos',
        'subtitle': 'El cohete más grande jamás construido supera su prueba más exigente y queda listo para la primera misión lunar tripulada en 2027.',
        'content': [
            'SpaceX completó el jueves por la tarde el cuarto test de vuelo orbital completo de Starship con un éxito que la compañía de Elon Musk y las autoridades espaciales describen como un hito histórico para la exploración humana del espacio. Por primera vez, tanto el Super Heavy Booster como la nave Starship completaron sus respectivas misiones de forma impecable: el propulsor fue capturado con precisión milimétrica por los brazos mecánicos de la torre de lanzamiento en Boca Chica, Texas, y la nave principal realizó una reentrada atmosférica controlada y un amerizaje suave en las coordenadas previstas del Pacífico norte, a unos 80 kilómetros de la costa de California.',
            'El vuelo, que duró en total 58 minutos desde el encendido de los motores hasta el amerizaje de Starship, incluyó por primera vez una maniobra de reencendido de los motores Raptor en el vacío del espacio y una prueba del sistema de transferencia de propelente en órbita, crítico para las misiones lunares de larga distancia. Los 33 motores Raptor del Super Heavy y los 6 de Starship funcionaron con una fiabilidad del 100% durante todo el vuelo, eliminando el principal factor de riesgo que había complicado los tests anteriores.',
            'La NASA observa el progreso con especial atención porque Starship es el vehículo elegido como módulo de alunizaje para la misión Artemis IV, que pretende llevar a los primeros astronautas a la superficie lunar desde 1972. La agencia espacial estadounidense ha vinculado el calendario de Artemis IV al progreso de las pruebas de Starship, y el éxito del cuarto vuelo permite mantener el objetivo de la misión tripulada lunar para el primer semestre de 2027. El contrato entre NASA y SpaceX para el módulo de alunizaje Starship asciende a 4.200 millones de dólares.',
            'La comunidad astronáutica internacional también sigue de cerca el desarrollo de Starship por sus implicaciones para la reducción de costes de acceso al espacio. Con una capacidad de carga de 150 toneladas a órbita baja terrestre y un coste por lanzamiento objetivo de menos de 10 millones de dólares una vez alcanzada la plena reutilización, Starship podría transformar la economía espacial de forma tan radical como lo hizo el Falcon 9 con el mercado de lanzadores medios. La Agencia Espacial Europea, que hasta ahora apostaba por el Ariane 6, ha iniciado estudios internos sobre posibles colaboraciones con SpaceX.',
        ],
        'author': 'Miguel Ángel Ruiz',
        'date': '3 oct 2026',
        'image_id': 12,
        'section': 'tecnologia',
        'section_name': 'Tecnología',
        'section_color': '#8b5cf6',
        'read_time': '5 min',
        'tags': ['SpaceX', 'Starship', 'espacio', 'NASA'],
    },

    # ── DEPORTES ─────────────────────────────────────────────────────────────
    'mundial-futbol-2026-resumen': {
        'slug': 'mundial-futbol-2026-resumen',
        'title': 'El Mundial 2026 ya tiene sus ocho equipos cuartofinales y las sorpresas no dejan de llegar',
        'subtitle': 'Marruecos elimina a Brasil, Japón vence a Alemania y Argentina busca el bicampeonato ante Países Bajos.',
        'content': [
            'La fase de grupos y los octavos de final del Mundial de Fútbol 2026, celebrado conjuntamente en Estados Unidos, Canadá y México, han deparado una tanda de sorpresas que ha trastocado todos los pronósticos previos al torneo. La eliminación de Brasil a manos de Marruecos en un partido vibrante disputado en el SoFi Stadium de Los Ángeles, con un gol de cabeza de Hakimi en el minuto 94 de prórroga, es ya uno de los momentos más comentados en la historia del campeonato. La selección marroquí, campeona de África y semifinalista en Qatar 2022, confirmó que aquel resultado no fue casualidad.',
            'Japón completó su segunda gran victoria del torneo al superar a Alemania en los penaltis tras un partido de 120 minutos en el que los europeos dominaron la posesión pero no encontraron la manera de superar la organización defensiva nipona. El portero Suzuki detuvo dos penaltis decisivos para llevar a los samurais azules a unos cuartos de final históricos. La federación japonesa ya ha anunciado que el partido se emitió en Japón con una audiencia televisiva de 98 millones de espectadores, el programa más visto de la historia del país.',
            'Argentina, vigente campeona del mundo, avanzó a cuartos sin excesivos apuros tras eliminar a Uruguay en un derbi rioplatense cargado de tensión e incidentes. Messi, a sus 39 años, volvió a demostrar que los límites de la edad no se aplican a su categoría: marcó el segundo gol con un disparo desde fuera del área que provocó el delirio de los miles de aficionados argentinos que llenaron el estadio de Dallas. El astro del Inter Miami declaró que este será "definitivamente" su último Mundial.',
            'Los cuartos de final enfrentarán a España-Portugal en el que los aficionados ya bautizan como la "Final Ibérica", a Francia-Estados Unidos en un partido que promete un ambiente eléctrico en el estadio de Nueva York, a Argentina-Países Bajos en una repetición de la semifinal de Qatar, y a Marruecos-Japón en lo que sería el sueño de muchos neutrales: una final entre las dos selecciones revelación del torneo. Los partidos se disputarán entre el 16 y el 18 de octubre.',
        ],
        'author': 'Juan Ramírez',
        'date': '13 oct 2026',
        'image_id': 23,
        'section': 'deportes',
        'section_name': 'Deportes',
        'section_color': '#ef4444',
        'read_time': '5 min',
        'tags': ['fútbol', 'Mundial 2026', 'Marruecos', 'Argentina'],
    },
    'nba-temporada-2026': {
        'slug': 'nba-temporada-2026',
        'title': 'La NBA arranca su temporada 2026-27 con LeBron James batiendo el récord de partidos jugados',
        'subtitle': 'Los Lakers abre la temporada con derrota pero LeBron marca historia al disputar su 1.500º partido regular en la liga.',
        'content': [
            'La temporada regular de la NBA 2026-27 comenzó oficialmente esta semana con la celebración de ocho partidos de apertura que congregaron estadios llenos en las principales ciudades del país y audiencias televisivas que, según las primeras estimaciones de Nielsen, superan en un 12% las del año pasado. El partido más seguido fue el inaugural de los Los Angeles Lakers, que a pesar de caer ante los Golden State Warriors 118-109 fue el escenario del momento más celebrado de la noche: LeBron James disputó su partido número 1.500 en la temporada regular de la NBA, un hito al que ningún jugador había llegado en la historia de la liga.',
            'James, que cumplirá 42 años en diciembre, firmó una línea de 21 puntos, 9 rebotes y 11 asistencias en el partido de apertura, demostrando una longevidad atlética que desafía cualquier comparación histórica. Su compañero en los Lakers, el alero español Usman Garuba, vivió su mejor noche como profesional al anotar 28 puntos con un 6 de 9 en triples. El pivot esloveno Luka Dončić, en su cuarta temporada con Los Angeles Clippers, también tuvo un debut estelar con 34 puntos y 12 rebotes en la victoria de su equipo sobre los Phoenix Suns.',
            'Las apuestas previas a la temporada sitúan a Boston Celtics, bicampeones en 2024 y 2025, como favoritos para el tercer título consecutivo. Sin embargo, los Oklahoma City Thunder, liderados por el MVP Shai Gilgeous-Alexander, y los Denver Nuggets de Nikola Jokić —de vuelta tras perderse gran parte de la temporada pasada por lesión— amenazan con desafiar la hegemonía de los Celtics en la Conferencia Oeste. En el Este, los Milwaukee Bucks con Giannis Antetokounmpo y los New York Knicks, reforzados en el mercado de verano, parten como principales amenazas para los campeones.',
            'La liga ha introducido este año varias innovaciones tecnológicas que prometen cambiar la experiencia del espectador: un sistema de visualización de estadísticas en tiempo real integrado en las retransmisiones, árbitros asistidos por inteligencia artificial para decisiones de fuera de campo, y una nueva aplicación de realidad aumentada que permite a los aficionados en el estadio acceder a repeticiones desde múltiples ángulos apuntando su teléfono a la cancha. El comisionado de la NBA calificó la temporada como "la más tecnológicamente avanzada de la historia del baloncesto".',
        ],
        'author': 'Kevin Thompson',
        'date': '11 oct 2026',
        'image_id': 35,
        'section': 'deportes',
        'section_name': 'Deportes',
        'section_color': '#ef4444',
        'read_time': '4 min',
        'tags': ['NBA', 'LeBron James', 'baloncesto', 'deporte'],
    },
    'formula1-titulo-2026': {
        'slug': 'formula1-titulo-2026',
        'title': 'Max Verstappen a un punto del quinto título mundial: el drama de Austin decidirá el campeonato',
        'subtitle': 'Red Bull y Mercedes se juegan el campeonato de constructores y pilotos en un Gran Premio de Estados Unidos de máxima tensión.',
        'content': [
            'El Gran Premio de Estados Unidos en el Circuito de las Américas de Austin se prepara para vivir uno de los finales de temporada más dramáticos de la historia de la Fórmula 1. Max Verstappen lidera el campeonato de pilotos con 387 puntos, apenas un punto por delante de George Russell (Mercedes), en lo que se configura como el duelo más igualado en la categoría reina desde el mítico Hamilton-Rosberg de 2016. Con solo tres carreras por disputar —Austin, México y Abu Dabi— cada décima de segundo, cada estrategia de pits y cada salida del safety car puede marcar la diferencia entre la gloria y la derrota.',
            'Verstappen llega a Austin en un momento de forma extraordinaria: tres victorias consecutivas en los últimos cuatro Grandes Premios le han permitido recuperar una desventaja que en julio llegaba a ser de 31 puntos. El RB22 de Red Bull ha resuelto finalmente los problemas de equilibrio aerodinámico que lo lastraban en condiciones de temperatura elevada, y el equipo austriaco ha realizado una actualización del fondo plano del monoplaza que ha reducido significativamente el porpoising que Verstappen sufrió durante el verano.',
            'Russell, por su parte, llega con la ventaja psicológica de haber conseguido su primer título mundial el año pasado y de liderar un equipo Mercedes que ha recuperado la competitividad perdida durante los primeros años del reglamento de efecto suelo. Lewis Hamilton, ahora piloto de Ferrari, completa el podio del campeonato con 356 puntos y tiene posibilidades matemáticas de título aunque necesitaría una combinación de resultados improbable. El heptacampeón ha reconocido que "Austin será su carrera favorita del año independientemente del resultado".',
            'El Gran Premio de Estados Unidos genera además un enorme interés comercial para la Fórmula 1, cuya popularidad en Norteamérica ha disparado tras la entrada de varios pilotos americanos en la parrilla y el éxito de la serie documental de Netflix. El circuito de Austin estará lleno con más de 400.000 aficionados a lo largo del fin de semana, un nuevo récord para un evento de la categoría fuera de Mónaco, y las estimaciones de impacto económico para la ciudad de Austin superan los 800 millones de dólares.',
        ],
        'author': 'Pedro Alonso',
        'date': '9 oct 2026',
        'image_id': 46,
        'section': 'deportes',
        'section_name': 'Deportes',
        'section_color': '#ef4444',
        'read_time': '5 min',
        'tags': ['Fórmula 1', 'Verstappen', 'automovilismo', 'campeonato'],
    },
    'olimpiadas-paris-2028-preparativos': {
        'slug': 'olimpiadas-paris-2028-preparativos',
        'title': 'Los Ángeles 2028: la organización olímpica supera los primeros obstáculos presupuestarios',
        'subtitle': 'El Comité Organizador de Los Ángeles confirma el presupuesto definitivo de 6.800 millones de dólares con soporte récord de patrocinadores privados.',
        'content': [
            'El Comité Organizador de los Juegos Olímpicos de Los Ángeles 2028 (LA28) presentó esta semana ante el Comité Olímpico Internacional el presupuesto definitivo de los Juegos, fijado en 6.800 millones de dólares, y anunció que el 97% de la financiación ya está asegurada a través de contratos de patrocinio y derechos de retransmisión sin necesidad de garantías públicas adicionales. El modelo organizativo de Los Ángeles, que aprovecha infraestructuras existentes en lugar de construir nuevas, ha sido señalado por el COI como referencia para futuros organizadores después de los desbordamientos presupuestarios de Tokio 2020 y París 2024.',
            'Los Ángeles puede presumir de ser la única ciudad del mundo con infraestructuras olímpicas permanentes ya construidas, fruto de haber organizado los Juegos en 1932 y 1984: el Coliseo de Los Ángeles volverá a ser el estadio principal, el Staples Center —rebautizado como Crypto.com Arena— albergará los torneos de baloncesto y boxeo, y el SoFi Stadium, uno de los más modernos del mundo, acogerá el fútbol americano olímpico y el fútbol. Solo se construirán dos instalaciones nuevas permanentes: la Villa Olímpica y el Centro Acuático.',
            'El programa deportivo de Los Ángeles 2028 incluye por primera vez en la historia los videojuegos como deporte olímpico en la categoría de "esports", una decisión del COI que ha generado debate intenso en el mundo del deporte tradicional. Los cinco títulos confirmados para el debut olímpico son FIFA 27, League of Legends, Fortnite, Rocket League y un juego de atletismo virtual desarrollado específicamente para los Juegos. El formato de competición, los criterios de elegibilidad y el control antidopaje en la categoría todavía están en proceso de definición.',
            'La candidatura de Los Ángeles llega en un momento en que el modelo tradicional de Juegos Olímpicos está bajo cuestionamiento creciente por los costes asociados, la huella ambiental y las disrupciones urbanísticas que generan en las ciudades sede. El COI trabajó durante el proceso de elección para asegurarse de que Los Ángeles 2028 será un modelo sostenible, y uno de los compromisos adquiridos es que la huella de carbono de los Juegos será compensada íntegramente mediante proyectos de conservación y reforestación certificados en California y en países en desarrollo.',
        ],
        'author': 'Sandra López',
        'date': '7 oct 2026',
        'image_id': 57,
        'section': 'deportes',
        'section_name': 'Deportes',
        'section_color': '#ef4444',
        'read_time': '5 min',
        'tags': ['Olimpiadas', 'Los Ángeles 2028', 'deporte', 'COI'],
    },
    'rafael-nadal-academia': {
        'slug': 'rafael-nadal-academia',
        'title': 'La Academia Rafa Nadal abre su segundo campus en Dubai y lanza programa para 500 becarios',
        'subtitle': 'El extenista español expande su modelo educativo deportivo a nivel global dos años después de su retirada del tenis profesional.',
        'content': [
            'Dos años después de su emotiva despedida del tenis profesional en la Copa Davis de 2024, Rafael Nadal sigue dejando huella en el mundo del deporte desde su nueva faceta como empresario y educador deportivo. La Rafa Nadal Academy anunció esta semana la apertura de su segundo campus internacional en Dubai, en colaboración con el Departamento de Economía y Turismo de los Emiratos Árabes Unidos, con una inversión de 180 millones de dólares y capacidad para entrenar simultáneamente a 300 tenistas de entre 8 y 18 años. El campus, que abrirá sus puertas en enero de 2027, replicará el modelo del campus principal de Manacor en Mallorca.',
            'Paralelamente, la fundación vinculada a la academia anunció el programa de becas más ambicioso de su historia: 500 jóvenes talentos de países con menores recursos recibirán formación deportiva completa, educación académica reglada y alojamiento gratuito durante hasta tres años. Los candidatos serán seleccionados a través de pruebas realizadas en colaboración con las federaciones nacionales de tenis de 80 países, con especial énfasis en América Latina, África y Asia meridional. Nadal, presente en la rueda de prensa de Dubai, declaró que el programa "es el proyecto del que me sentiré más orgulloso al final de mi vida".',
            'El modelo pedagógico de la academia combina el entrenamiento técnico intensivo con una formación académica completa adaptada al calendario deportivo, apoyo psicológico individual, nutrición deportiva personalizada y formación en inglés y español. El índice de tenistas formados en la academia que alcanzan el circuito profesional es del 34%, significativamente superior al promedio de las academias de élite de Europa, según datos publicados por la ATP. Ocho exalumnos de la academia figuran actualmente entre los 100 primeros del ranking mundial.',
            'El mercado del tenis juvenil de élite vive un momento de expansión global impulsado por el crecimiento del deporte en Asia y la creación de nuevos torneos en el circuito menor. La academia de Nadal compite con proyectos similares respaldados por Novak Djokovic en Serbia y por el Williams Sisters Fund en Estados Unidos, creando un ecosistema de formación de alto nivel que algunos expertos creen que cambiará la geografía del tenis mundial en los próximos veinte años.',
        ],
        'author': 'Carles Puigdomènech',
        'date': '5 oct 2026',
        'image_id': 68,
        'section': 'deportes',
        'section_name': 'Deportes',
        'section_color': '#ef4444',
        'read_time': '4 min',
        'tags': ['Nadal', 'tenis', 'academia', 'deporte'],
    },
    'ciclismo-vuelta-espana': {
        'slug': 'ciclismo-vuelta-espana',
        'title': 'Pogačar domina la Vuelta a España 2026 y suma su tercer Grande en el mismo año',
        'subtitle': 'El esloveno completa el doblete Giro-Tour-Vuelta y entra en la historia del ciclismo junto a Eddy Merckx.',
        'content': [
            'Tadej Pogačar escribió este domingo el capítulo más glorioso de su ya extraordinaria carrera deportiva al cruzar la meta de la última etapa de la Vuelta a España 2026 en Madrid con el maillot rojo de líder y convertirse, a sus 28 años, en el tercer ciclista de la historia en ganar los tres grandes vueltas en un mismo año natural. El esloveno del equipo UAE Emirates conquistó el Giro de Italia en mayo, el Tour de Francia en julio y la Vuelta a España en octubre, replicando la proeza que solo habían conseguido antes Eddy Merckx en 1974 y Gino Bartali en los años cuarenta del siglo pasado.',
            'La Vuelta 2026 fue una prueba de resistencia extrema frente a un rival de excepción: el ciclista colombiano Santiago Buitrago (Bahrain Victorious) defendió durante quince etapas una ventaja que llegó a ser de 2 minutos y 43 segundos, poniendo en serias dificultades a un Pogačar que tardó en encontrar el ritmo óptimo en las primeras semanas de la carrera. La remontada del esloveno comenzó en la decimoquinta etapa con final en el Pico Veleta en Sierra Nevada, donde distanció a todos sus rivales con un ataque a 20 kilómetros de la cima que dejó imágenes que ya se consideran legendarias.',
            'El director deportivo de UAE Emirates, Mauro Gianetti, describió la temporada de Pogačar como "algo que no estaba en nuestros planes más optimistas" al inicio del año. El corredor esloveno ha acumulado un total de ocho victorias en lo que va de temporada, entre ellas la Strade Bianche, la Lieja-Bastoña-Lieja y los tres grandes. Pocas semanas antes de la Vuelta había pedido al equipo permiso para participar en el Campeonato del Mundo en Kigali, donde acabó segundo en una llegada de grupo en la que fue víctima de la superioridad numérica del equipo esloveno de sus rivales.',
            'Los aficionados y los medios especializados en ciclismo llevan semanas debatiendo si Pogačar ya puede ser considerado el mejor ciclista de la historia, un debate que inevitablemente invoca el nombre de Eddy Merckx. Los defensores del belga señalan la mayor dureza del calendario de los años sesenta y setenta, con etapas más largas y sin el apoyo de la ciencia del rendimiento moderna. Los defensores de Pogačar replican con la mayor profundidad del pelotón actual y la mayor sofisticación táctica de las carreras contemporáneas. El debate, afortunadamente, no tiene una respuesta definitiva.',
        ],
        'author': 'María Saez',
        'date': '2 oct 2026',
        'image_id': 79,
        'section': 'deportes',
        'section_name': 'Deportes',
        'section_color': '#ef4444',
        'read_time': '5 min',
        'tags': ['ciclismo', 'Pogačar', 'Vuelta España', 'deporte'],
    },

    # ── SALUD ─────────────────────────────────────────────────────────────────
    'vacuna-cancer-mrna': {
        'slug': 'vacuna-cancer-mrna',
        'title': 'La vacuna personalizada de ARNm contra el melanoma reduce las recidivas un 44% en ensayo de fase III',
        'subtitle': 'Moderna y Merck publican los resultados de su terapia oncológica más prometedora, que podría estar disponible en 2028.',
        'content': [
            'Moderna y Merck publicaron esta semana en The New England Journal of Medicine los resultados completos de la fase III del ensayo clínico de su vacuna personalizada de ARNm contra el melanoma, la forma más peligrosa de cáncer de piel. Los datos, que comprenden el seguimiento de 1.134 pacientes durante una mediana de 36 meses, confirman que la adición de la vacuna mRNA-4157/V940 al tratamiento estándar con pembrolizumab reduce el riesgo de recidiva o muerte en un 44% respecto al tratamiento con pembrolizumab solo. Es el primer ensayo de fase III en demostrar eficacia estadísticamente significativa para una vacuna oncológica personalizada.',
            'La vacuna funciona de manera radicalmente diferente a las vacunas convencionales: no combate un patógeno externo, sino que enseña al sistema inmunitario del propio paciente a reconocer y atacar las células tumorales identificadas por sus mutaciones únicas (neoantigéenos). El proceso comienza con la secuenciación genómica del tumor del paciente, que identifica las mutaciones específicas de ese cáncer individual. A partir de esta información, un algoritmo de inteligencia artificial diseña una secuencia de ARN mensajero codificando hasta 34 neoantígenos tumorales específicos del paciente. La vacuna se produce en unas seis semanas y se administra junto con el inhibidor de punto de control inmunitario.',
            'El oncólogo jefe del ensayo, el doctor Konstantinos Drakakis del Memorial Sloan Kettering Cancer Center, calificó los resultados de "un cambio de paradigma en la oncología". La personalización de la terapia significa que cada dosis es única para cada paciente, lo que plantea desafíos logísticos y económicos formidables. El coste estimado de producción de una vacuna individualizada actualmente ronda los 300.000 dólares, aunque Moderna prevé reducirlo significativamente con la automatización industrial. Las negociaciones con los sistemas de salud pública de varios países europeos ya han comenzado.',
            'El éxito en melanoma abre la puerta a la extensión de la tecnología a otros tipos de cáncer. Moderna tiene actualmente doce ensayos clínicos en marcha con vacunas similares para cáncer de pulmón, colorrectal, pancreático y de vejiga, entre otros. Los resultados preliminares de algunos de estos ensayos son prometedores, aunque ninguno ha alcanzado todavía la fase III. Los expertos en oncología esperan que la próxima década suponga una transformación fundamental en el tratamiento del cáncer gracias a la combinación de inmunoterapia personalizada y edición genética.',
        ],
        'author': 'Dra. Carmen Soler',
        'date': '14 oct 2026',
        'image_id': 90,
        'section': 'salud',
        'section_name': 'Salud',
        'section_color': '#f59e0b',
        'read_time': '6 min',
        'tags': ['oncología', 'vacuna', 'ARNm', 'cáncer'],
    },
    'diabetes-tipo-1-cura': {
        'slug': 'diabetes-tipo-1-cura',
        'title': 'Un ensayo con células madre pancreáticas elimina la dependencia de insulina en diabéticos tipo 1',
        'subtitle': 'Seis de los doce pacientes del estudio piloto de Vertex Pharmaceuticals llevan más de un año sin necesidad de insulina exógena.',
        'content': [
            'Vertex Pharmaceuticals anunció resultados preliminares que la comunidad médica ha calificado de "extraordinarios" en su ensayo clínico de fase I/II con células madre pluripotentes diferenciadas a células beta pancreáticas para tratar la diabetes tipo 1. De los doce pacientes incluidos en el estudio, seis han conseguido la independencia completa de la insulina exógena durante períodos que oscilan entre los 14 y los 26 meses, mientras que los restantes han reducido sus necesidades de insulina en más del 80%. Si estos resultados se confirman en ensayos más amplios, representarían la primera aproximación a una cura funcional para una enfermedad que afecta a más de 8 millones de personas en Europa y 25 millones en todo el mundo.',
            'El tratamiento experimental implica la infusión de células beta pancreáticas derivadas de células madre en el hígado del paciente, donde colonizan parcialmente los conductos biliares y comienzan a producir insulina en respuesta a los niveles de glucosa en sangre, replicando la función que las células beta del páncreas nativo realizan en personas sin diabetes. Para evitar el rechazo inmunológico, los pacientes reciben un régimen de inmunosupresión moderada, aunque Vertex trabaja en versiones de las células diseñadas genéticamente para evadir el sistema inmunitario sin necesidad de inmunosupresión.',
            'Los pacientes del ensayo describen la transformación como revolucionaria en términos de calidad de vida: eliminar la necesidad de monitorizar constantemente los niveles de glucosa, calcular dosis de insulina y gestionar hipoglucemias e hiperglucemias libera tiempo y energía mental que los diabéticos tipo 1 destinan permanentemente al manejo de su enfermedad. "Es como si me hubieran devuelto años de mi vida", declaró uno de los participantes en el ensayo en una entrevista con el New York Times.',
            'Los obstáculos que quedan por superar antes de que el tratamiento pueda generalizarse son significativos: los ensayos de fase III necesarios para la aprobación regulatoria incluirán a cientos de pacientes durante varios años, la inmunosupresión sigue siendo un factor de riesgo a gestionar cuidadosamente, y el coste del tratamiento podría ser prohibitivo sin políticas específicas de acceso. Competidores como CRISPR Therapeutics y Sana Biotechnology trabajan en enfoques alternativos, lo que sugiere que la próxima década podría ver múltiples opciones terapéuticas cuasi-curativas para la diabetes tipo 1.',
        ],
        'author': 'Dr. Pablo Moreno',
        'date': '12 oct 2026',
        'image_id': 101,
        'section': 'salud',
        'section_name': 'Salud',
        'section_color': '#f59e0b',
        'read_time': '6 min',
        'tags': ['diabetes', 'células madre', 'medicina', 'salud'],
    },
    'alzheimer-diagnostico-ia': {
        'slug': 'alzheimer-diagnostico-ia',
        'title': 'Una IA detecta el Alzheimer con 10 años de antelación analizando datos de salud rutinarios',
        'subtitle': 'El modelo desarrollado por investigadores del MIT y el Hospital Clínic de Barcelona alcanza una precisión del 83% en poblaciones de riesgo.',
        'content': [
            'Un equipo de investigadores del Instituto Tecnológico de Massachusetts (MIT) y el Hospital Clínic de Barcelona publicó esta semana en Nature Medicine los resultados de un sistema de inteligencia artificial capaz de predecir con diez años de antelación el desarrollo del Alzheimer con una precisión del 83% a partir exclusivamente de datos de salud rutinaria no invasivos: análisis de sangre anuales, mediciones de presión arterial, datos de sueño de dispositivos wearables, resultados de pruebas cognitivas simples administradas mediante smartphone y, en algunos casos, imágenes de retina que reflejan cambios vasculares asociados a la neurodegeneración.',
            'La detección precoz del Alzheimer es uno de los grandes desafíos de la neurología moderna porque los tratamientos modificadores de la enfermedad actualmente en desarrollo son mucho más eficaces en las fases presintomáticas o sintomáticas muy tempranas, antes de que se produzca la pérdida masiva de neuronas que caracteriza las fases avanzadas. El sistema, denominado ALERTA (Alzheimer Long-term Early Risk Tool and Assessment), fue entrenado con datos anonimizados de más de 340.000 pacientes de doce países europeos con seguimiento longitudinal de hasta veinte años.',
            'El modelo integra más de 200 variables biométricas y de estilo de vida utilizando una arquitectura de transformers adaptada para datos de series temporales de salud. Entre los predictores más relevantes identificados por el sistema se encuentran las variaciones en los patrones de sueño profundo, los cambios sutiles en la velocidad de procesamiento cognitivo medidos mediante pruebas de reacción digital, ciertos perfiles de marcadores inflamatorios en sangre y la progresión de la tensión arterial sistólica nocturna. Ninguno de estos indicadores por sí solo tiene valor predictivo suficiente, pero su combinación en el modelo resulta extraordinariamente informativa.',
            'Las implicaciones clínicas y éticas son profundas y aún no resueltas. Saber con diez años de antelación que probablemente se desarrollará Alzheimer puede permitir intervenciones preventivas —dieta, ejercicio, control vascular, participación en ensayos clínicos— que podrían retrasar o mitigar la enfermedad. Pero también puede generar ansiedad, discriminación en seguros y empleo, y dilemas bioéticos sobre el derecho a no saber. Los autores del estudio abogan por un marco de consejería genética y psicológica antes de cualquier uso clínico del sistema.',
        ],
        'author': 'Núria Puig',
        'date': '10 oct 2026',
        'image_id': 112,
        'section': 'salud',
        'section_name': 'Salud',
        'section_color': '#f59e0b',
        'read_time': '6 min',
        'tags': ['Alzheimer', 'inteligencia artificial', 'neurología', 'diagnóstico'],
    },
    'longevidad-semaglutide': {
        'slug': 'longevidad-semaglutide',
        'title': 'El semaglutide reduce el riesgo cardiovascular en un 20% también en personas sin diabetes',
        'subtitle': 'Un ensayo con 17.600 participantes confirma que Ozempic y Wegovy protegen el corazón independientemente del control glucémico.',
        'content': [
            'Los fármacos basados en semaglutide, el ingrediente activo de Ozempic y Wegovy, continúan revelando beneficios que van mucho más allá de su indicación original como tratamiento para la diabetes tipo 2 y la obesidad. Los resultados del ensayo SUSTAIN-Heart, presentados en el Congreso de la Sociedad Europea de Cardiología y publicados simultáneamente en The Lancet, demuestran que el semaglutide reduce el riesgo de eventos cardiovasculares mayores —infarto de miocardio, accidente cerebrovascular y muerte cardiovascular— en un 20% en personas con sobrepeso u obesidad pero sin diabetes, extendiendo al conjunto de la población obesa los beneficios previamente documentados solo en diabéticos.',
            'El ensayo incluyó 17.604 participantes de 41 países, con una edad media de 61 años, índice de masa corporal superior a 27 y al menos un factor de riesgo cardiovascular establecido como hipertensión, dislipemia o tabaquismo. Los participantes fueron aleatorizados a recibir semaglutide semanal subcutáneo o placebo durante un seguimiento mediano de 4,2 años. Los resultados muestran reducciones estadísticamente significativas en infarto, ictus y hospitalizaciones por insuficiencia cardíaca, con un perfil de seguridad consistente con los ensayos previos.',
            'Los mecanismos que explican el beneficio cardiovascular del semaglutide van más allá de la simple pérdida de peso. Los investigadores identifican efectos directos sobre la inflamación vascular, mejoras en la función endotelial, reducción de la presión arterial sistólica y efectos antiateroscleróticos independientes del control glucémico o de la reducción ponderal. Esta multi-acción del fármaco lo convierte, según los autores, en un "agente cardiometabólico de nueva generación" más que en un simple tratamiento para la obesidad.',
            'Las agencias reguladoras de Estados Unidos y Europa están revisando los nuevos datos para evaluar si amplían la indicación aprobada del semaglutide. Si la aprobación se concede, el número de pacientes elegibles para el tratamiento se multiplicaría por varios órdenes de magnitud, con implicaciones de acceso y coste farmacéutico enormes para los sistemas de salud. El precio actual de Wegovy en Estados Unidos supera los 1.300 dólares mensuales, una cifra que la mayoría de sistemas públicos de salud europeos consideran insostenible para un uso masivo sin acuerdos de precio negociados a la baja.',
        ],
        'author': 'Dra. Elena Castellanos',
        'date': '8 oct 2026',
        'image_id': 124,
        'section': 'salud',
        'section_name': 'Salud',
        'section_color': '#f59e0b',
        'read_time': '5 min',
        'tags': ['semaglutide', 'cardiología', 'obesidad', 'farmacología'],
    },
    'pandemia-preparacion-oms': {
        'slug': 'pandemia-preparacion-oms',
        'title': 'La OMS aprueba el Tratado sobre Pandemias después de tres años de negociaciones',
        'subtitle': 'El acuerdo vinculante establece un sistema de alerta temprana global y garantías de acceso equitativo a vacunas en emergencias.',
        'content': [
            'La Asamblea Mundial de la Salud aprobó por consenso el texto definitivo del Tratado Internacional sobre la Prevención, Preparación y Respuesta a Pandemias, un proceso negociador que comenzó en 2023 y que durante tres años estuvo al borde del colapso en múltiples ocasiones debido a las profundas diferencias entre países desarrollados y en desarrollo sobre el acceso a tecnología médica. El tratado, que entrará en vigor cuando sea ratificado por 60 estados, establece por primera vez obligaciones jurídicamente vinculantes para el intercambio de muestras patógenas y de secuencias genómicas entre países, el fortalecimiento de las capacidades de vigilancia epidemiológica nacionales, y un mecanismo de distribución equitativa de contramedidas médicas —vacunas, diagnósticos y tratamientos— en situaciones de pandemia declarada.',
            'El elemento más controvertido del texto final es el "acceso y reparto de beneficios" (ABS): los países que comparten muestras de patógenos con la red global de laboratorios tienen derecho a recibir el 10% de las vacunas y tratamientos desarrollados a partir de esas muestras a precio de costo, además de transferencia de tecnología para producirlos localmente. Este principio, resistido hasta el último momento por la industria farmacéutica occidental, fue el que más cerca estuvo de hundir las negociaciones, y su inclusión final se considera una victoria diplomática de los países de renta media y baja.',
            'El director general de la OMS calificó la aprobación como "la reforma más importante de la arquitectura de salud global desde la creación de la propia OMS en 1948". Sin embargo, varios actores clave de la sociedad civil señalan lagunas importantes: el tratado no establece mecanismos de financiación predecible para las capacidades de preparación en países con menor renta, no incluye obligaciones específicas sobre transparencia de precios de medicamentos en emergencias, y el mecanismo de verificación de cumplimiento es considerado demasiado débil.',
            'La experiencia del COVID-19, que infectó a más de 700 millones de personas y causó cerca de 7 millones de muertes oficiales antes de que la OMS declarara el fin de la emergencia de salud pública internacional, fue el motor político que finalmente superó los bloqueos. Los expertos advierten que el tiempo entre la aprobación del tratado y su implementación efectiva será crítico: la siguiente pandemia —que según los modelos epidemiológicos más pesimistas podría llegar antes de 2035— encontrará un mundo mejor preparado solo si la ratificación y la implementación avanzan con urgencia real.',
        ],
        'author': 'Dr. Kwame Asante',
        'date': '6 oct 2026',
        'image_id': 135,
        'section': 'salud',
        'section_name': 'Salud',
        'section_color': '#f59e0b',
        'read_time': '5 min',
        'tags': ['pandemia', 'OMS', 'salud global', 'tratado'],
    },
    'salud-mental-jovenes': {
        'slug': 'salud-mental-jovenes',
        'title': 'Crisis silenciosa: la salud mental de los jóvenes, la emergencia sanitaria del siglo XXI',
        'subtitle': 'Un informe global revela que el 32% de los menores de 25 años presenta síntomas clínicamente significativos de ansiedad o depresión.',
        'content': [
            'Un informe conjunto de la Organización Mundial de la Salud y UNICEF publicado esta semana ofrece los datos más completos disponibles hasta la fecha sobre la salud mental de la población joven a escala global: el 32% de los menores de 25 años en los países estudiados presenta síntomas clínicamente significativos de ansiedad, depresión o ambas condiciones, con tasas que superan el 40% en algunos países de ingresos altos como Estados Unidos, Australia y Corea del Sur. La prevalencia de los problemas de salud mental en este grupo de edad ha aumentado un 60% respecto a las mediciones equivalentes de 2019, antes de la pandemia.',
            'Los factores identificados por el informe como principales contribuyentes incluyen el impacto de las redes sociales sobre la autoestima y los patrones de comparación social, la exposición continua a contenidos relacionados con la violencia, la catástrofe climática y el conflicto, las presiones académicas y laborales en un mercado de trabajo percibido como precario, y los efectos persistentes del aislamiento social durante la pandemia en las etapas de desarrollo más vulnerables. El informe no adopta una posición causal definitiva sobre las redes sociales dado que la evidencia científica sigue siendo objeto de debate, pero documenta la correlación temporal con fuerza.',
            'La brecha entre la demanda de atención en salud mental y la oferta disponible es alarmante: se estima que menos del 30% de los jóvenes con problemas de salud mental tienen acceso a atención profesional adecuada, con diferencias enormes entre países según el nivel de recursos del sistema sanitario y la presencia o ausencia de programas de salud mental escolar. En muchos países de ingresos medios y bajos, la proporción cae por debajo del 5%. La escasez de profesionales de salud mental formados es otro cuello de botella: el ratio global es de apenas 13 psicólogos por cada 100.000 habitantes.',
            'Las recomendaciones del informe incluyen la regulación más estricta de las plataformas de redes sociales para proteger a menores, la integración de la atención en salud mental en los servicios de atención primaria, la formación de docentes en detección temprana y primeros auxilios psicológicos, y el aumento del gasto público en salud mental hasta alcanzar al menos el 10% del presupuesto sanitario total. Actualmente, ningún país del mundo alcanza ese umbral; la mayoría de países europeos destina entre el 5% y el 7%, y la media global es del 2,1%.',
        ],
        'author': 'Alicia Vega',
        'date': '3 oct 2026',
        'image_id': 146,
        'section': 'salud',
        'section_name': 'Salud',
        'section_color': '#f59e0b',
        'read_time': '5 min',
        'tags': ['salud mental', 'jóvenes', 'ansiedad', 'depresión'],
    },

    # ── CIENCIA ───────────────────────────────────────────────────────────────
    'james-webb-galaxia-primitiva': {
        'slug': 'james-webb-galaxia-primitiva',
        'title': 'James Webb observa la galaxia más antigua conocida: formada apenas 280 millones de años tras el Big Bang',
        'subtitle': 'El hallazgo desafía los modelos estándar de formación galáctica y abre preguntas fundamentales sobre los albores del cosmos.',
        'content': [
            'Astrónomas del Instituto de Ciencia del Telescopio Espacial (STScI) anunciaron esta semana el descubrimiento de lo que actualmente se considera la galaxia más antigua jamás observada por la humanidad, designada provisionalmente JADES-GS-z16-0. Con un corrimiento al rojo espectroscópico confirmado de z≈16, la galaxia existía apenas 280 millones de años después del Big Bang, en un período en que el universo tenía menos del 2% de su edad actual. La observación se realizó con el instrumento NIRSpec del telescopio espacial James Webb en una serie de apuntamientos de exposición larga sobre el campo profundo del Telescopio Espacial Hubble en el sur de Fornax.',
            'Lo que hace especialmente sorprendente al hallazgo no es solo la antigüedad de la galaxia, sino su tamaño y madurez: JADES-GS-z16-0 parece contener ya varios miles de millones de masas solares en estrellas y muestra una metalicidad —proporción de elementos más pesados que el hidrógeno y el helio— significativamente mayor que la esperada en una galaxia tan joven. Esto sugiere que múltiples generaciones de estrellas masivas ya habían nacido, vivido y muerto en apenas cientos de millones de años, expulsando metales al medio interestelar de forma muy más eficiente de lo que predicen los modelos actuales.',
            'Los teóricos de la formación de galaxias llevan meses trabajando en explicaciones para una acumulación de descubrimientos del James Webb que desafían sistemáticamente los modelos estándar de cosmología. La existencia de galaxias grandes y maduras en el universo temprano parece requerir mecanismos de formación estelar mucho más eficientes que los conocidos, posiblemente relacionados con condiciones de densidad extremas en los halos de materia oscura primordial o con propiedades de los primeros agujeros negros supermasivos que aún no comprendemos bien.',
            'El descubrimiento tiene implicaciones que van más allá de la astronomía observacional: si las galaxias se formaron mucho más rápido de lo previsto, esto podría tener consecuencias para nuestra comprensión de la naturaleza de la materia oscura, del período de reionización del universo y posiblemente de la propia naturaleza de la energía oscura. Los próximos ciclos de observación del James Webb, ya programados para apuntar a campos aún más profundos con tiempos de exposición más largos, prometen más sorpresas sobre los orígenes del cosmos.',
        ],
        'author': 'Dr. Alejandro Cosmos',
        'date': '15 oct 2026',
        'image_id': 157,
        'section': 'ciencia',
        'section_name': 'Ciencia',
        'section_color': '#06b6d4',
        'read_time': '6 min',
        'tags': ['astronomía', 'James Webb', 'galaxias', 'cosmología'],
    },
    'fusión-nuclear-iter': {
        'slug': 'fusión-nuclear-iter',
        'title': 'ITER alcanza el plasma de prueba: la fusión nuclear comercial está más cerca que nunca',
        'subtitle': 'El reactor experimental internacional logra su primer plasma controlado, un hito de 35 años en la búsqueda de la energía de las estrellas.',
        'content': [
            'El proyecto ITER (International Thermonuclear Experimental Reactor), ubicado en Cadarache en el sur de Francia y fruto de la colaboración de 35 países que representan el 80% de la población mundial, logró el pasado lunes su primer plasma de prueba controlado, un hito que los científicos del proyecto describen como "la culminación de tres décadas y media de trabajo de miles de ingenieros y físicos en todo el mundo". El plasma de deuterio, a una temperatura de 100 millones de grados Celsius —seis veces más caliente que el núcleo del Sol—, se mantuvo estable durante siete segundos en la primera operación, superando los cinco segundos exigidos como demostración mínima.',
            'ITER no está diseñado para producir electricidad —ese será el objetivo de DEMO, el reactor demostrativo que lo suceda— sino para demostrar que la fusión nuclear puede producir diez veces más energía de la que consume para mantener el plasma en condiciones adecuadas. El objetivo de un factor Q=10 no se alcanzará en este primer plasma, sino en experimentos progresivamente más ambiciosos que se extenderán durante la próxima década. El primer plasma con deuterio y tritio —los dos isótopos del hidrógeno que se fusionarán en condiciones de operación plena— está previsto para 2030.',
            'El proyecto privado de fusión nuclear también está viviendo momentos de aceleración histórica. Commonwealth Fusion Systems, financiada por Microsoft y un consorcio de fondos de capital riesgo, opera ya su imán superconductor de alta temperatura SPARC con un campo magnético de 20 teslas —el más potente jamás logrado en condiciones de fusión—, y Helion Energy tiene un contrato preliminar con Microsoft para suministrarle energía de fusión antes de 2028, aunque los expertos independientes consideran ese calendario extremadamente optimista.',
            'La energía de fusión promete resolver de manera casi definitiva los problemas del suministro energético de la humanidad: el deuterio se puede extraer del agua de mar de forma prácticamente ilimitada, el tritio se genera en el propio reactor a partir del litio, los residuos son de baja actividad y tienen períodos de desintegración de décadas —no milenios como en la fisión—, y es imposible que un reactor de fusión sufra un accidente tipo Chernóbil o Fukushima por razones físicas fundamentales. Los escépticos señalan que la fusión lleva setenta años siendo "la energía del futuro" y advierten de que los plazos de comercialización siguen siendo inciertos.',
        ],
        'author': 'Dr. Valentina Cruz',
        'date': '13 oct 2026',
        'image_id': 168,
        'section': 'ciencia',
        'section_name': 'Ciencia',
        'section_color': '#06b6d4',
        'read_time': '6 min',
        'tags': ['fusión nuclear', 'ITER', 'energía', 'física'],
    },
    'crispr-enfermedad-rara': {
        'slug': 'crispr-enfermedad-rara',
        'title': 'CRISPR elimina la enfermedad de Huntington en células humanas con una eficacia sin precedentes',
        'subtitle': 'Un equipo de la Universidad de Toronto logra suprimir el gen mutado en más del 90% de las células diana en un modelo in vitro.',
        'content': [
            'Investigadores de la Universidad de Toronto publicaron en la revista Cell resultados que abren una nueva vía prometedora en la búsqueda de tratamiento para la enfermedad de Huntington, un trastorno neurodegenerativo hereditario actualmente incurable que afecta a unas 30.000 personas en Europa. El equipo utilizó una versión de CRISPR mejorada denominada "prime editing" —que permite reescribir secuencias de ADN específicas con una precisión y eficiencia mucho mayores que el CRISPR-Cas9 convencional— para eliminar el segmento de ADN responsable de la producción de la proteína huntingtina mutada en más del 90% de las células neuronales humanas en cultivo.',
            'La enfermedad de Huntington se produce por la expansión anormal de una repetición de trinucleótidos (CAG) en el gen HTT, que da lugar a una proteína tóxica que destruye progresivamente las neuronas del estriado y la corteza cerebral. A diferencia de muchas otras enfermedades genéticas, Huntington tiene una causa genética única y bien conocida, lo que la convierte en un objetivo ideal para las terapias de edición genómica. El desafío hasta ahora era la eficiencia insuficiente de las herramientas disponibles para alcanzar y corregir el gen mutado en suficientes neuronas del cerebro vivo como para tener efecto terapéutico.',
            'El prime editing utilizado por el equipo de Toronto logra entregar el maquinaria de edición a las células mediante vectores virales adenoasociados (AAV) modificados para atravesar la barrera hematoencefálica, uno de los obstáculos más difíciles de superar en neurología terapéutica. Los experimentos en cultivo celular demostraron una tasa de edición superior al 90% sin evidencia de "edición fuera de diana" —modificaciones no intencionadas en otras partes del genoma— detectable mediante secuenciación de todo el genoma.',
            'El camino hasta un tratamiento clínico sigue siendo largo: el siguiente paso es reproducir los resultados en modelos animales (ratones transgénicos con el gen humano de Huntington), evaluar la seguridad y durabilidad de la edición in vivo, y diseñar sistemas de entrega que puedan alcanzar las regiones cerebrales afectadas con suficiente eficiencia en seres humanos. Las familias afectadas por Huntington llevan décadas esperando un avance terapéutico significativo, y aunque este no es todavía una cura clínica, la mayoría de expertos en la enfermedad lo califican de "el avance más esperanzador en la historia de la investigación en Huntington".',
        ],
        'author': 'Dra. Marta Rivas',
        'date': '11 oct 2026',
        'image_id': 179,
        'section': 'ciencia',
        'section_name': 'Ciencia',
        'section_color': '#06b6d4',
        'read_time': '6 min',
        'tags': ['CRISPR', 'Huntington', 'genética', 'medicina'],
    },
    'oceanos-acidificacion': {
        'slug': 'oceanos-acidificacion',
        'title': 'Los océanos alcanzan el nivel de acidez más alto en 300 millones de años según nuevo estudio',
        'subtitle': 'La absorción de CO₂ ha reducido el pH oceánico a niveles que amenazan con colapsar los ecosistemas de arrecifes de coral globalmente.',
        'content': [
            'Un estudio publicado en Science por un consorcio de oceanógrafos de doce instituciones internacionales revela que la acidificación de los océanos ha alcanzado niveles sin precedentes en al menos 300 millones de años, basándose en el análisis de proxies geoquímicos en sedimentos marinos y en una red de boyas de monitorización oceánica que cubre el 68% de la superficie marina global. El pH promedio de los océanos ha caído de 8,2 en la era preindustrial a 8,05 en la actualidad, una variación que aunque parece pequeña en escala absoluta representa un aumento de la acidez del 40% debido a la naturaleza logarítmica de la escala de pH.',
            'Las consecuencias sobre la vida marina son profundas y ya observables. Los organismos calcificadores —corales, moluscos, equinodermos, ciertos plancton— tienen dificultades crecientes para construir y mantener sus estructuras calcáreas en un agua más ácida que disuelve el carbonato cálcico con mayor facilidad. Los arrecifes de coral, ecosistemas que albergan el 25% de todas las especies marinas a pesar de ocupar menos del 1% del fondo oceánico, muestran tasas de calcificación reducidas en un 15-25% respecto a mediciones de referencia de los años ochenta. El Gran Arrecife de Coral australiano perdió el 50% de su cobertura coralina entre 2016 y 2024.',
            'Los investigadores modelizan que si las emisiones de CO₂ continúan según el escenario de altas emisiones del IPCC, el pH oceánico caerá por debajo de 7,95 hacia 2100 —un nivel en el que los modelos predicen el colapso funcional de la mayoría de ecosistemas de coral tropicales y cambios radicales en las cadenas alimentarias marinas de alta latitud. Incluso en el escenario de cumplimiento total de los compromisos actuales del Acuerdo de París, la acidificación continuará durante décadas debido a la inercia del sistema climático.',
            'Las propuestas de geoingeniería para frenar la acidificación incluyen la alcalinización oceánica mediante la adición de minerales como la olivina molida al agua de mar, o la fertilización con hierro para estimular el crecimiento de fitoplancton que absorba CO₂. Ambas propuestas tienen defensores y detractores en la comunidad científica, con preocupaciones sobre efectos secundarios no deseados sobre los ecosistemas marinos. El consenso mayoritario es que no existe sustituto para la reducción drástica y urgente de las emisiones de dióxido de carbono como medida fundamental.',
        ],
        'author': 'Dr. Jonas Weber',
        'date': '9 oct 2026',
        'image_id': 190,
        'section': 'ciencia',
        'section_name': 'Ciencia',
        'section_color': '#06b6d4',
        'read_time': '5 min',
        'tags': ['océanos', 'acidificación', 'cambio climático', 'biología marina'],
    },
    'cerebro-mapa-conectoma': {
        'slug': 'cerebro-mapa-conectoma',
        'title': 'Científicos publican el primer conectoma completo de un cerebro de ratón: 84.000 neuronas mapeadas',
        'subtitle': 'El proyecto, que costó diez años y 122 petabytes de datos, sienta las bases para comprender cómo el cerebro procesa la información.',
        'content': [
            'Un consorcio de laboratorios liderado por el Allen Institute for Brain Science, la Universidad Johns Hopkins y la Universidad de Cambridge publicó en la revista Cell el mapa sináptico completo del cerebro de un ratón adulto, con 84.000 neuronas y más de 500 millones de conexiones sinápticas descritas a resolución nanométrica. El proyecto, denominado MICrONS (Machine Intelligence from Cortical Networks), ha requerido diez años de trabajo, la generación de 122 petabytes de imágenes de microscopía electrónica y el desarrollo de algoritmos de segmentación con inteligencia artificial capaces de rastrear automáticamente los axones y dendritas de cada neurona a través de miles de secciones ultrafinas de tejido cerebral.',
            'La escala del logro es difícil de apreciar sin contexto: el cerebro del ratón, con sus 84.000 neuronas, es ya 1.000 veces más complejo que el conectoma del gusano Caenorhabditis elegans (con 302 neuronas) que fue el primer organismo en tener su conectoma completo publicado, en 1986. El cerebro humano contiene aproximadamente 86.000 millones de neuronas y 100 billones de sinapsis; mapear el conectoma humano completo a la misma resolución requeriría, con la tecnología actual, más de un exabyte de datos y décadas de trabajo, aunque los avances en automatización y en técnicas de imagen aceleran continuamente el proceso.',
            'Las primeras conclusiones científicas del análisis del conectoma del ratón ya están generando resultados significativos. Los investigadores han identificado motivos de conectividad recurrentes —"microcircuitos" de pocas decenas de neuronas que se repiten en diferentes regiones del córtex— que podrían ser los elementos básicos de computación del cerebro, análogos a los transistores en un circuito electrónico. También han descubierto una heterogeneidad inesperadamente alta entre neuronas del mismo tipo, lo que sugiere que la "identidad" de una neurona depende tanto de sus conexiones específicas como de sus propiedades moleculares.',
            'Las aplicaciones del conectoma van más allá de la neurociencia básica. Los ingenieros de inteligencia artificial estudian la organización del conectoma para inspirar nuevas arquitecturas de redes neuronales artificiales que puedan superar las limitaciones de los transformers actuales. Los neurólogos esperan que los mapas sinápticos de cerebros sanos sirvan como referencia para identificar las alteraciones de conectividad que caracterizan enfermedades como el autismo, la esquizofrenia o el Alzheimer. El siguiente objetivo del consorcio es el conectoma de un córtex de primate no humano, un proyecto que estiman requerirá otros quince años.',
        ],
        'author': 'Dr. Tomás Vidal',
        'date': '7 oct 2026',
        'image_id': 13,
        'section': 'ciencia',
        'section_name': 'Ciencia',
        'section_color': '#06b6d4',
        'read_time': '6 min',
        'tags': ['neurociencia', 'conectoma', 'cerebro', 'investigación'],
    },
    'antimateria-trampa': {
        'slug': 'antimateria-trampa',
        'title': 'El CERN almacena antimateria durante 12 minutos, un nuevo récord mundial',
        'subtitle': 'El experimento ALPHA confirma que el antihelio cae hacia abajo bajo la gravedad, cerrando un debate de décadas sobre la antimateria.',
        'content': [
            'El experimento ALPHA del CERN (Organización Europea para la Investigación Nuclear) publicó esta semana dos resultados de importancia histórica para la física fundamental. El primero es un nuevo récord mundial de tiempo de confinamiento de antimateria: el equipo logró mantener átomos de antihidrógeno atrapados magnéticamente durante 12 minutos y 17 segundos —casi el triple del récord anterior— en las condiciones de temperatura ultra-baja del interior de su trampa magnética. El segundo, quizás más significativo conceptualmente, es la confirmación experimental directa de que los átomos de antihidrógeno caen hacia abajo bajo la influencia de la gravedad terrestre, tal y como hacen los átomos de hidrógeno ordinario.',
            'Este segundo resultado cierra un debate que durante décadas fue más filosófico que experimental: ¿la antimateria cae hacia arriba o hacia abajo? La relatividad general de Einstein predice que la antimateria debe comportarse gravitacionalmente igual que la materia ordinaria, pero no existía prueba experimental directa porque confinar antimateria el tiempo suficiente para medir su comportamiento gravitacional era extraordinariamente difícil. El experimento ALPHA-g, especialmente diseñado para este propósito, midió la caída libre de átomos de antihidrógeno con una precisión del 5%, suficiente para confirmar inequívocamente el comportamiento gravitacional normal.',
            'El tiempo de confinamiento récord de 12 minutos tiene implicaciones directas para la agenda de investigación futura del CERN. Con antimateria confinada durante períodos más largos, es posible realizar mediciones espectroscópicas de alta precisión comparando las líneas espectrales del antihidrógeno con las del hidrógeno ordinario. Cualquier diferencia, por pequeña que fuera, sería una señal de violación de la simetría CPT —una de las simetrías fundamentales de la física de partículas— y podría ayudar a explicar por qué el universo observable está dominado por materia y no por antimateria.',
            'La pregunta de la asimetría materia-antimateria es una de las grandes preguntas sin respuesta de la cosmología: si el Big Bang creó cantidades iguales de materia y antimateria, ¿por qué existe el universo material tal y como lo conocemos en lugar de haber sido aniquilado en su totalidad? Los experimentos en el CERN buscan señales de violaciones de simetría que puedan dar pistas sobre los procesos físicos que inclinaron la balanza a favor de la materia. Cada avance en el control de la antimateria abre nuevas ventanas experimentales para investigar esta pregunta fundamental.',
        ],
        'author': 'Dra. Neus Fontana',
        'date': '4 oct 2026',
        'image_id': 24,
        'section': 'ciencia',
        'section_name': 'Ciencia',
        'section_color': '#06b6d4',
        'read_time': '5 min',
        'tags': ['CERN', 'antimateria', 'física', 'partículas'],
    },
}


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def get_section_articles(section, limit=None):
    arts = [a for a in ARTICLES.values() if a['section'] == section]
    if limit:
        return arts[:limit]
    return arts


def get_featured_articles(limit=6):
    all_arts = list(ARTICLES.values())
    return all_arts[:limit]


def get_recent_articles(limit=5):
    all_arts = list(ARTICLES.values())
    return all_arts[:limit]


SECTIONS = [
    {'id': 'mundo',      'name': 'Mundo',      'color': '#3b82f6'},
    {'id': 'economia',   'name': 'Economía',   'color': '#10b981'},
    {'id': 'tecnologia', 'name': 'Tecnología', 'color': '#8b5cf6'},
    {'id': 'deportes',   'name': 'Deportes',   'color': '#ef4444'},
    {'id': 'salud',      'name': 'Salud',       'color': '#f59e0b'},
    {'id': 'ciencia',    'name': 'Ciencia',    'color': '#06b6d4'},
]


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route('/')
def home():
    featured = get_featured_articles(limit=6)
    recent = get_recent_articles(limit=5)
    section_previews = []
    for sec in SECTIONS:
        arts = get_section_articles(sec['id'], limit=3)
        section_previews.append({'section': sec, 'articles': arts})
    return render_template(
        'home.html',
        featured_articles=featured,
        recent_articles=recent,
        section_previews=section_previews,
        sections=SECTIONS,
    )


@app.route('/mundo')
def mundo():
    arts = get_section_articles('mundo')
    other = [a for a in ARTICLES.values() if a['section'] != 'mundo'][:5]
    return render_template('section.html',
                           articles=arts,
                           section={'id': 'mundo', 'name': 'Mundo', 'color': '#3b82f6'},
                           trending=other, sections=SECTIONS)


@app.route('/economia')
def economia():
    arts = get_section_articles('economia')
    other = [a for a in ARTICLES.values() if a['section'] != 'economia'][:5]
    return render_template('section.html',
                           articles=arts,
                           section={'id': 'economia', 'name': 'Economía', 'color': '#10b981'},
                           trending=other, sections=SECTIONS)


@app.route('/tecnologia')
def tecnologia():
    arts = get_section_articles('tecnologia')
    other = [a for a in ARTICLES.values() if a['section'] != 'tecnologia'][:5]
    return render_template('section.html',
                           articles=arts,
                           section={'id': 'tecnologia', 'name': 'Tecnología', 'color': '#8b5cf6'},
                           trending=other, sections=SECTIONS)


@app.route('/deportes')
def deportes():
    arts = get_section_articles('deportes')
    other = [a for a in ARTICLES.values() if a['section'] != 'deportes'][:5]
    return render_template('section.html',
                           articles=arts,
                           section={'id': 'deportes', 'name': 'Deportes', 'color': '#ef4444'},
                           trending=other, sections=SECTIONS)


@app.route('/salud')
def salud():
    arts = get_section_articles('salud')
    other = [a for a in ARTICLES.values() if a['section'] != 'salud'][:5]
    return render_template('section.html',
                           articles=arts,
                           section={'id': 'salud', 'name': 'Salud', 'color': '#f59e0b'},
                           trending=other, sections=SECTIONS)


@app.route('/ciencia')
def ciencia():
    arts = get_section_articles('ciencia')
    other = [a for a in ARTICLES.values() if a['section'] != 'ciencia'][:5]
    return render_template('section.html',
                           articles=arts,
                           section={'id': 'ciencia', 'name': 'Ciencia', 'color': '#06b6d4'},
                           trending=other, sections=SECTIONS)


@app.route('/articulo/<slug>')
def article(slug):
    art = ARTICLES.get(slug)
    if not art:
        return render_template('404.html', sections=SECTIONS), 404
    related = [a for a in ARTICLES.values() if a['section'] == art['section'] and a['slug'] != slug][:3]
    section_list = get_section_articles(art['section'], limit=5)
    trending = get_recent_articles(limit=5)
    return render_template('article.html',
                           article=art,
                           related=related,
                           section_list=section_list,
                           trending=trending,
                           sections=SECTIONS)


@app.route('/analytics')
def analytics():
    db = get_db()
    now = datetime.utcnow()

    total_all = db.execute('SELECT COUNT(*) FROM visits').fetchone()[0]
    today_str = now.strftime('%Y-%m-%d')
    total_today = db.execute(
        "SELECT COUNT(*) FROM visits WHERE timestamp LIKE ?", (today_str + '%',)
    ).fetchone()[0]
    hour_ago = (now - timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')
    total_hour = db.execute(
        "SELECT COUNT(*) FROM visits WHERE timestamp >= ?", (hour_ago,)
    ).fetchone()[0]
    five_min_ago = (now - timedelta(minutes=5)).strftime('%Y-%m-%d %H:%M:%S')
    active_5min = db.execute(
        "SELECT COUNT(DISTINCT ip) FROM visits WHERE timestamp >= ?", (five_min_ago,)
    ).fetchone()[0]

    # Hourly data last 24h
    hourly_labels = []
    hourly_data = []
    for i in range(23, -1, -1):
        t = now - timedelta(hours=i)
        label = t.strftime('%H:00')
        start = t.strftime('%Y-%m-%d %H:00:00')
        end = t.strftime('%Y-%m-%d %H:59:59')
        count = db.execute(
            "SELECT COUNT(*) FROM visits WHERE timestamp BETWEEN ? AND ?", (start, end)
        ).fetchone()[0]
        hourly_labels.append(label)
        hourly_data.append(count)

    # Daily data last 30 days
    daily_labels = []
    daily_data = []
    for i in range(29, -1, -1):
        d = now - timedelta(days=i)
        label = d.strftime('%d/%m')
        day_str = d.strftime('%Y-%m-%d')
        count = db.execute(
            "SELECT COUNT(*) FROM visits WHERE timestamp LIKE ?", (day_str + '%',)
        ).fetchone()[0]
        daily_labels.append(label)
        daily_data.append(count)

    # Top pages
    top_pages_rows = db.execute(
        "SELECT path, COUNT(*) as cnt FROM visits GROUP BY path ORDER BY cnt DESC LIMIT 10"
    ).fetchall()
    top_pages = [{'path': r['path'], 'count': r['cnt']} for r in top_pages_rows]

    # Top referrers
    top_refs_rows = db.execute(
        "SELECT referrer, COUNT(*) as cnt FROM visits WHERE referrer != '' GROUP BY referrer ORDER BY cnt DESC LIMIT 10"
    ).fetchall()
    top_refs = [{'referrer': r['referrer'], 'count': r['cnt']} for r in top_refs_rows]

    # Top IPs
    top_ips_rows = db.execute(
        "SELECT ip, COUNT(*) as cnt FROM visits GROUP BY ip ORDER BY cnt DESC LIMIT 10"
    ).fetchall()
    top_ips = [{'ip': r['ip'], 'count': r['cnt']} for r in top_ips_rows]

    # Recent visits
    recent_rows = db.execute(
        "SELECT * FROM visits ORDER BY id DESC LIMIT 100"
    ).fetchall()
    recent = [dict(r) for r in recent_rows]

    # Browsers
    all_uas = db.execute('SELECT user_agent FROM visits').fetchall()
    browser_counts = Counter()
    for row in all_uas:
        ua = row['user_agent'] or ''
        if 'Chrome' in ua and 'Edg' not in ua and 'OPR' not in ua:
            browser_counts['Chrome'] += 1
        elif 'Firefox' in ua:
            browser_counts['Firefox'] += 1
        elif 'Safari' in ua and 'Chrome' not in ua:
            browser_counts['Safari'] += 1
        elif 'Edg' in ua:
            browser_counts['Edge'] += 1
        elif 'OPR' in ua or 'Opera' in ua:
            browser_counts['Opera'] += 1
        else:
            browser_counts['Otro'] += 1
    browsers = dict(browser_counts)

    # Behavioral / Biometric Auditing Metrics
    total_beacons = db.execute('SELECT COUNT(*) FROM behavioral_data').fetchone()[0]
    avg_mouse_lin_row = db.execute('SELECT AVG(mouse_linearity) FROM behavioral_data WHERE mouse_events > 0').fetchone()[0]
    avg_mouse_lin = round(avg_mouse_lin_row, 3) if avg_mouse_lin_row is not None else 0.425
    avg_scroll_row = db.execute('SELECT AVG(scroll_depth) FROM behavioral_data').fetchone()[0]
    avg_scroll_px = round(avg_scroll_row) if avg_scroll_row is not None else 0
    avg_time_row = db.execute('SELECT AVG(time_on_page) FROM behavioral_data').fetchone()[0]
    avg_time_sec = round((avg_time_row or 0) / 1000, 1)

    # Verification rate & human confidence score
    verified_beacons = db.execute(
        "SELECT COUNT(*) FROM behavioral_data WHERE canvas_hash != '' AND (mouse_events > 0 OR scroll_events > 0)"
    ).fetchone()[0]
    human_pass_count = db.execute(
        "SELECT COUNT(*) FROM behavioral_data WHERE canvas_hash != '' AND mouse_events >= 2 AND mouse_linearity < 0.85 AND scroll_events >= 1"
    ).fetchone()[0]
    human_confidence_pct = round((human_pass_count / total_beacons * 100), 1) if total_beacons > 0 else 0.0

    # Recent behavioral audit logs
    recent_beacon_rows = db.execute(
        "SELECT * FROM behavioral_data ORDER BY id DESC LIMIT 25"
    ).fetchall()
    recent_beacons = []
    for b in recent_beacon_rows:
        b_dict = dict(b)
        m_ev = b_dict.get('mouse_events', 0)
        m_lin = b_dict.get('mouse_linearity', 1.0)
        sc_ev = b_dict.get('scroll_events', 0)
        c_hash = b_dict.get('canvas_hash', '')
        if c_hash and m_ev >= 2 and m_lin < 0.85 and sc_ev >= 1:
            b_dict['verdict'] = 'PASS'
            b_dict['verdict_label'] = 'Orgánico / Humano'
            b_dict['badge_class'] = 'success'
        elif c_hash and (m_ev > 0 or sc_ev > 0):
            b_dict['verdict'] = 'WARN'
            b_dict['verdict_label'] = 'Huella Válida / Baja Act.'
            b_dict['badge_class'] = 'warning'
        else:
            b_dict['verdict'] = 'FAIL'
            b_dict['verdict_label'] = 'Robot / Lineal'
            b_dict['badge_class'] = 'danger'
        recent_beacons.append(b_dict)

    webgl_rows = db.execute(
        "SELECT webgl_renderer, COUNT(*) as cnt FROM behavioral_data WHERE webgl_renderer != '' GROUP BY webgl_renderer ORDER BY cnt DESC LIMIT 5"
    ).fetchall()
    top_webgl = [{'name': r['webgl_renderer'], 'count': r['cnt']} for r in webgl_rows]

    return render_template('analytics.html',
                           total_all=total_all,
                           total_today=total_today,
                           total_hour=total_hour,
                           active_5min=active_5min,
                           hourly_labels=hourly_labels,
                           hourly_data=hourly_data,
                           daily_labels=daily_labels,
                           daily_data=daily_data,
                           top_pages=top_pages,
                           top_refs=top_refs,
                           top_ips=top_ips,
                           recent=recent,
                           browsers=browsers,
                           sections=SECTIONS,
                           total_beacons=total_beacons,
                           avg_mouse_lin=avg_mouse_lin,
                           avg_scroll_px=avg_scroll_px,
                           avg_time_sec=avg_time_sec,
                           human_confidence_pct=human_confidence_pct,
                           recent_beacons=recent_beacons,
                           top_webgl=top_webgl)


@app.route('/api/beacon', methods=['POST'])
def api_beacon():
    """Recibe datos biométricos/fingerprint desde el JS del navegador."""
    try:
        import json as _json
        raw = request.get_data(as_text=True)
        data = _json.loads(raw) if raw else {}
    except Exception:
        return jsonify({'ok': False}), 400

    ip = request.headers.get('CF-Connecting-IP') or \
         request.headers.get('X-Real-IP') or \
         request.headers.get('X-Forwarded-For') or \
         request.remote_addr
    if ip and ',' in ip:
        ip = ip.split(',')[0].strip()

    # Calcular métricas derivadas de eventos de mouse
    mouse_events_raw = data.get('mouse_events', [])
    mouse_linearity = 0.0
    mouse_avg_speed = 0.0
    if len(mouse_events_raw) >= 2:
        # Linealidad: qué tan recta es la trayectoria (0=muy curva, 1=línea recta)
        dxs = [abs(e.get('dx', 0)) for e in mouse_events_raw]
        dys = [abs(e.get('dy', 0)) for e in mouse_events_raw]
        # Velocidad promedio en px/ms
        speeds = []
        for e in mouse_events_raw:
            dt = e.get('dt', 1) or 1
            dist = (e.get('dx', 0)**2 + e.get('dy', 0)**2) ** 0.5
            speeds.append(dist / dt)
        mouse_avg_speed = round(sum(speeds) / len(speeds), 4) if speeds else 0.0
        # Ratio de cambio de dirección (baja = movimiento recto = bot)
        direction_changes = sum(
            1 for i in range(1, len(mouse_events_raw))
            if (mouse_events_raw[i].get('dx', 0) * mouse_events_raw[i-1].get('dx', 1)) < 0
            or (mouse_events_raw[i].get('dy', 0) * mouse_events_raw[i-1].get('dy', 1)) < 0
        )
        mouse_linearity = round(1 - (direction_changes / max(1, len(mouse_events_raw))), 4)

    # Métricas de scroll
    scroll_events_raw = data.get('scroll_events', [])
    max_scroll_speed = 0.0
    scroll_depth = 0
    if scroll_events_raw:
        speeds_sc = [abs(e.get('speed', 0)) for e in scroll_events_raw]
        max_scroll_speed = round(max(speeds_sc), 4) if speeds_sc else 0.0
        scroll_depth = max((e.get('y', 0) for e in scroll_events_raw), default=0)

    screen = data.get('screen', {})
    ts = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

    db = get_db()
    db.execute('''
        INSERT INTO behavioral_data (
            session_id, ip, path, timestamp,
            canvas_hash, webgl_renderer, webgl_vendor,
            screen_w, screen_h, color_depth, pixel_ratio,
            viewport_w, viewport_h, time_on_page,
            scroll_depth, scroll_events, max_scroll_speed,
            mouse_events, mouse_linearity, mouse_avg_speed,
            timezone_offset, touch_support, platform, language, do_not_track
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    ''', (
        data.get('session_id', ''),
        ip,
        data.get('path', ''),
        ts,
        data.get('canvas_hash', ''),
        data.get('webgl_renderer', ''),
        data.get('webgl_vendor', ''),
        screen.get('width', 0),
        screen.get('height', 0),
        screen.get('colorDepth', 0),
        screen.get('pixelRatio', 1.0),
        screen.get('viewport', {}).get('w', 0),
        screen.get('viewport', {}).get('h', 0),
        data.get('time_on_page', 0),
        scroll_depth,
        len(scroll_events_raw),
        max_scroll_speed,
        len(mouse_events_raw),
        mouse_linearity,
        mouse_avg_speed,
        data.get('timezone_offset', 0),
        1 if data.get('touch_support') else 0,
        data.get('platform', ''),
        data.get('language', ''),
        data.get('do_not_track', ''),
    ))
    db.commit()
    return jsonify({'ok': True})


@app.route('/api/stats')
def api_stats():
    db = get_db()
    now = datetime.utcnow()
    today_str = now.strftime('%Y-%m-%d')
    total_all = db.execute('SELECT COUNT(*) FROM visits').fetchone()[0]
    total_today = db.execute(
        "SELECT COUNT(*) FROM visits WHERE timestamp LIKE ?", (today_str + '%',)
    ).fetchone()[0]
    hour_ago = (now - timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')
    total_hour = db.execute(
        "SELECT COUNT(*) FROM visits WHERE timestamp >= ?", (hour_ago,)
    ).fetchone()[0]
    five_min_ago = (now - timedelta(minutes=5)).strftime('%Y-%m-%d %H:%M:%S')
    active_5min = db.execute(
        "SELECT COUNT(DISTINCT ip) FROM visits WHERE timestamp >= ?", (five_min_ago,)
    ).fetchone()[0]
    # Behavioral stats
    total_beacons = db.execute('SELECT COUNT(*) FROM behavioral_data').fetchone()[0]
    avg_time = db.execute('SELECT AVG(time_on_page) FROM behavioral_data').fetchone()[0] or 0
    avg_scroll = db.execute('SELECT AVG(scroll_depth) FROM behavioral_data').fetchone()[0] or 0
    avg_mouse_linearity = db.execute('SELECT AVG(mouse_linearity) FROM behavioral_data').fetchone()[0] or 0
    return jsonify({
        'total_all': total_all,
        'total_today': total_today,
        'total_hour': total_hour,
        'active_5min': active_5min,
        'total_beacons': total_beacons,
        'avg_time_on_page_ms': round(avg_time),
        'avg_scroll_depth_px': round(avg_scroll),
        'avg_mouse_linearity': round(avg_mouse_linearity, 3),
    })


if __name__ == '__main__':
    app.run(debug=True, port=5000)

