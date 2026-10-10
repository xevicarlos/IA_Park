
import html
import os
import sqlite3

from fastapi import FastAPI
from fastapi.responses import HTMLResponse


# ==========================================================
# IA PARK - CONFIGURACIÓN
# ==========================================================

app = FastAPI(title="IA Park")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "iapark.db")


# ==========================================================
# COCHE SVG REALISTA VISTO DESDE ARRIBA
# ==========================================================

CAR_SVG = """
<svg class="car" viewBox="0 0 90 154"
     xmlns="http://www.w3.org/2000/svg"
     aria-hidden="true">

    <defs>

        <linearGradient id="paint" x1="0" y1="0" x2="1" y2="0">
            <stop stop-color="#6d8197"/>
            <stop offset=".18" stop-color="#dce9f3"/>
            <stop offset=".48" stop-color="#ffffff"/>
            <stop offset=".82" stop-color="#aabdd0"/>
            <stop offset="1" stop-color="#536a83"/>
        </linearGradient>

        <linearGradient id="glass" x1="0" y1="0" x2=".8" y2="1">
            <stop stop-color="#a4c8dd"/>
            <stop offset=".45" stop-color="#2d536d"/>
            <stop offset="1" stop-color="#102c42"/>
        </linearGradient>

        <linearGradient id="roof" x1="0" y1="0" x2="1" y2="0">
            <stop stop-color="#8ca3b7"/>
            <stop offset=".45" stop-color="#e9f2f9"/>
            <stop offset="1" stop-color="#7b91a7"/>
        </linearGradient>

        <filter id="shadow">
            <feGaussianBlur stdDeviation="3"/>
        </filter>

    </defs>

    <!-- SOMBRA -->

    <ellipse cx="48" cy="80" rx="35" ry="70"
             fill="#030a12" opacity=".4"
             filter="url(#shadow)"/>

    <!-- RUEDAS -->

    <rect x="6" y="29" width="12" height="30"
          rx="5" fill="#111820"/>

    <rect x="72" y="29" width="12" height="30"
          rx="5" fill="#111820"/>

    <rect x="6" y="105" width="12" height="30"
          rx="5" fill="#111820"/>

    <rect x="72" y="105" width="12" height="30"
          rx="5" fill="#111820"/>

    <!-- CARROCERÍA -->

    <path
        d="M45 4
           C23 4 15 14 14 33
           L12 119
           Q12 148 31 150
           L59 150
           Q78 148 78 119
           L76 33
           C75 14 67 4 45 4Z"
        fill="url(#paint)"
        stroke="#536779"
        stroke-width="1.5"
    />

    <!-- CAPÓ -->

    <path
        d="M20 27 Q45 17 70 27 L73 37 L17 37Z"
        fill="#c7d8e7"
        opacity=".65"
    />

    <!-- PARABRISAS DELANTERO -->

    <path
        d="M23 44
           Q24 36 33 34
           L57 34
           Q66 36 67 44
           L65 58
           Q45 63 25 58Z"
        fill="url(#glass)"
        stroke="#344e62"
        stroke-width="1.5"
    />

    <!-- CRISTAL TRASERO -->

    <path
        d="M25 105
           Q45 100 65 105
           L68 123
           Q45 130 22 123Z"
        fill="url(#glass)"
        stroke="#344e62"
        stroke-width="1.5"
    />

    <!-- TECHO -->

    <path
        d="M25 60
           Q45 65 65 60
           L65 104
           Q45 99 25 104Z"
        fill="url(#roof)"
        stroke="#8299ae"
        stroke-width="1"
    />

    <!-- REFLEJOS -->

    <path
        d="M30 66 L30 96"
        stroke="#ffffff"
        opacity=".65"
        stroke-width="2"
        stroke-linecap="round"
    />

    <!-- PILARES -->

    <path
        d="M19 41 L23 61
           M71 41 L67 61
           M22 105 L20 121
           M68 105 L70 121"
        stroke="#d4e3ef"
        stroke-width="2"
    />

    <!-- RETROVISORES -->

    <path
        d="M13 50 L5 47 Q2 49 5 55 L14 57Z
           M77 50 L85 47 Q88 49 85 55 L76 57Z"
        fill="#8b9eb0"
        stroke="#44576a"
        stroke-width="1"
    />

    <!-- PARRILLA DELANTERA -->

    <path
        d="M31 12 Q45 8 59 12"
        stroke="#2d4357"
        stroke-width="3"
        stroke-linecap="round"
    />

    <!-- FAROS DELANTEROS -->

    <path
        d="M20 16 L32 13 L30 21 L18 23Z
           M70 16 L58 13 L60 21 L72 23Z"
        fill="#fff6cf"
        stroke="#ffffff"
        stroke-width="1"
    />

    <!-- PILOTOS TRASEROS -->

    <path
        d="M20 137 L34 140 L32 146 L19 144Z
           M70 137 L56 140 L58 146 L71 144Z"
        fill="#d52c45"
        stroke="#ff8290"
        stroke-width="1"
    />

    <!-- PARAGOLPES TRASERO -->

    <path
        d="M33 145 L57 145"
        stroke="#607588"
        stroke-width="2"
    />

</svg>
"""


# ==========================================================
# PÁGINA PRINCIPAL
# ==========================================================

@app.get("/", response_class=HTMLResponse)
def dashboard():

    # ------------------------------------------------------
    # COMPROBAR BASE DE DATOS
    # ------------------------------------------------------

    if not os.path.isfile(DB_PATH):

        return HTMLResponse(
            "<h2>No se encuentra iapark.db junto a app.py</h2>",
            status_code=500
        )

    # ------------------------------------------------------
    # CONSULTAR PLAZAS Y VEHÍCULOS
    # ------------------------------------------------------

    with sqlite3.connect(DB_PATH) as conexion:

        plazas_db = conexion.execute("""
            SELECT
                p.id,
                p.name,
                p.occupied,

                (
                    SELECT v.plate
                    FROM parking_sessions s
                    JOIN vehicles v
                        ON v.id = s.vehicle_id
                    WHERE s.space_id = p.id
                      AND s.status = 'ACTIVE'
                    ORDER BY s.id DESC
                    LIMIT 1
                ),

                (
                    SELECT s.entry_time
                    FROM parking_sessions s
                    WHERE s.space_id = p.id
                      AND s.status = 'ACTIVE'
                    ORDER BY s.id DESC
                    LIMIT 1
                )

            FROM parking_spaces p

            ORDER BY p.id
        """).fetchall()

    # ------------------------------------------------------
    # ORGANIZAR LAS 30 PLAZAS EN TRES PLANTAS
    # ------------------------------------------------------

    plantas = {
        0: [],
        1: [],
        2: []
    }

    for indice, (id_plaza, nombre, ocupada,
                 matricula, entrada) in enumerate(plazas_db):

        numero_planta = min(indice // 10, 2)

        plantas[numero_planta].append({

            "nombre": html.escape(str(nombre)),

            "ocupada": bool(ocupada),

            "matricula": html.escape(
                str(matricula or "Sin matrícula")
            ),

            "entrada": html.escape(
                str(entrada or "—").replace("T", " ")[:19]
            )

        })

    # ------------------------------------------------------
    # ESTADÍSTICAS GENERALES
    # ------------------------------------------------------

    total = len(plazas_db)

    ocupadas = sum(
        bool(plaza[2])
        for plaza in plazas_db
    )

    libres = total - ocupadas

    porcentaje = (
        ocupadas / total * 100
        if total > 0
        else 0
    )

    # ======================================================
    # GENERAR CADA PLANTA
    # ======================================================

    def generar_planta(numero):

        plazas = plantas[numero]

        ocupadas_planta = sum(
            plaza["ocupada"]
            for plaza in plazas
        )

        libres_planta = len(plazas) - ocupadas_planta

        html_plazas = []

        for plaza in plazas:

            nombre = plaza["nombre"]

            ocupada = plaza["ocupada"]

            if ocupada:

                estado = "occupied"

                descripcion = (
                    f"Matrícula: {plaza['matricula']}"
                    f" · Entrada: {plaza['entrada']}"
                )

                dibujo = CAR_SVG

            else:

                estado = "free"

                descripcion = "Plaza disponible"

                dibujo = '<span class="empty-mark">✓</span>'

            html_plazas.append(f"""
                <div class="slot {estado}"
                     tabindex="0">

                    <span class="slot-label">
                        {nombre}
                    </span>

                    {dibujo}

                    <span class="tooltip">
                        <b>{nombre}</b>
                        <br>
                        {descripcion}
                    </span>

                </div>
            """)

        fila_superior = "".join(html_plazas[:5])

        fila_inferior = "".join(html_plazas[5:])

        ocultar = "hidden" if numero != 0 else ""

        return f"""
        <section class="floor"
                 id="floor-{numero}"
                 {ocultar}>

            <div class="floor-info">

                <strong>
                    Planta {numero}
                </strong>

                <span>
                    {libres_planta} libres ·
                    {ocupadas_planta} ocupadas
                </span>

            </div>

            <div class="scene-wrap">

                <div class="scene">

                    <!-- FILA SUPERIOR -->

                    <div class="bay-row">
                        {fila_superior}
                    </div>

                    <!-- CARRIL CENTRAL -->

                    <div class="lane">

                        <span>
                            ENTRADA →
                        </span>

                        <span class="lane-center"></span>

                        <span>
                            → CIRCULACIÓN
                        </span>

                    </div>

                    <!-- FILA INFERIOR -->

                    <div class="bay-row">
                        {fila_inferior}
                    </div>

                    <!-- RAMPA -->

                    <div class="ramp">
                        ↗ RAMPA · PLANTA {numero}
                    </div>

                </div>

            </div>

        </section>
        """

    html_plantas = "".join(
        generar_planta(numero)
        for numero in range(3)
    )

    # ======================================================
    # HTML COMPLETO
    # ======================================================

    pagina = f"""
    <!DOCTYPE html>

    <html lang="es">

    <head>

        <meta charset="UTF-8">

        <meta name="viewport"
              content="width=device-width, initial-scale=1">

        <!-- ACTUALIZACIÓN AUTOMÁTICA -->

        <meta http-equiv="refresh" content="2">

        <title>IA Park - Panel</title>

        <style>

            * {{
                box-sizing: border-box;
            }}

            body {{

                margin: 0;

                background: #0b1422;

                color: #e7eef7;

                font-family:
                    Segoe UI,
                    Arial,
                    sans-serif;

            }}

            main {{

                max-width: 1120px;

                margin: auto;

                padding: 30px 20px 55px;

            }}

            /* ==========================================
               CABECERA
            ========================================== */

            header {{

                display: flex;

                justify-content: space-between;

                align-items: center;

                gap: 15px;

                flex-wrap: wrap;

            }}

            h1 {{

                margin: 0;

                font-size: 32px;

                letter-spacing: 2px;

            }}

            .sub {{

                color: #9cacc1;

                margin-top: 5px;

            }}

            .live {{

                font-size: 13px;

                color: #86efac;

                background: #14332c;

                border: 1px solid #25684c;

                padding: 8px 12px;

                border-radius: 30px;

            }}

            /* ==========================================
               ESTADÍSTICAS
            ========================================== */

            .stats {{

                display: grid;

                grid-template-columns: repeat(3, 1fr);

                gap: 14px;

                margin: 26px 0;

            }}

            .stat {{

                background: #17263a;

                border: 1px solid #2a3b50;

                padding: 18px;

                border-radius: 14px;

            }}

            .stat strong {{

                display: block;

                font-size: 30px;

                margin-top: 5px;

            }}

            .stat small {{

                color: #9cacc1;

            }}

            /* ==========================================
               SELECTOR DE PLANTAS
            ========================================== */

            .tabs {{

                display: flex;

                gap: 10px;

                flex-wrap: wrap;

                margin: 20px 0;

            }}

            .tab {{

                cursor: pointer;

                border: 1px solid #34485e;

                background: #17263a;

                color: #dbe7f4;

                padding: 12px 22px;

                border-radius: 11px;

                font-size: 15px;

            }}

            .tab.active {{

                background: #2563eb;

                border-color: #60a5fa;

                color: white;

            }}

            /* ==========================================
               CONTENEDOR DE PLANTA
            ========================================== */

            .floor {{

                background: #142338;

                border: 1px solid #2a3b50;

                border-radius: 18px;

                padding: 20px;

            }}

            .floor[hidden] {{

                display: none;

            }}

            .floor-info {{

                display: flex;

                justify-content: space-between;

                gap: 10px;

                flex-wrap: wrap;

                margin-bottom: 14px;

            }}

            .floor-info span {{

                color: #9cacc1;

            }}

            /* ==========================================
               ESCENA ISOMÉTRICA
            ========================================== */

            .scene-wrap {{

                overflow-x: auto;

                overflow-y: visible;

                padding: 40px 20px 90px;

            }}

            .scene {{

                position: relative;

                width: 750px;

                margin: 0 auto;

                background: #344250;

                padding: 28px 24px 78px;

                border: 6px solid #596a79;

                border-radius: 12px;

                transform:
                    perspective(1100px)
                    rotateX(22deg)
                    rotateZ(-7deg);

                box-shadow:
                    22px 34px 0 #101a29,
                    30px 45px 35px #050b14;

            }}

            /* ==========================================
               FILAS DE PLAZAS
            ========================================== */

            .bay-row {{

                display: grid;

                grid-template-columns: repeat(5, 1fr);

                gap: 9px;

            }}

            /* ==========================================
               PLAZAS
            ========================================== */

            .slot {{

                height: 142px;

                border: 3px solid #4ade80;

                background: #293d46;

                border-radius: 5px;

                position: relative;

                display: flex;

                align-items: center;

                justify-content: center;

                cursor: default;

                outline-offset: 3px;

            }}

            .slot.occupied {{

                border-color: #fb7185;

                background: #463942;

            }}

            .slot-label {{

                position: absolute;

                top: 5px;

                left: 7px;

                font-weight: 700;

                font-size: 14px;

                color: white;

                z-index: 2;

            }}

            /* ==========================================
               COCHE REALISTA
            ========================================== */

            .car {{

                width: 86px;

                height: 124px;

                overflow: visible;

                filter:
                    drop-shadow(
                        3px 6px 4px #111b28
                    );

            }}

            .empty-mark {{

                font-size: 33px;

                color: #4ade80;

                opacity: .65;

            }}

            /* ==========================================
               CARRIL CENTRAL
            ========================================== */

            .lane {{

                height: 110px;

                display: flex;

                justify-content: space-around;

                align-items: center;

                position: relative;

                color: #f5ce67;

                font-size: 13px;

                font-weight: bold;

                letter-spacing: 2px;

            }}

            .lane-center {{

                position: absolute;

                left: 0;

                right: 0;

                top: 50%;

                border-top: 3px dashed #b4a36b;

                opacity: .65;

            }}

            .lane span:not(.lane-center) {{

                position: relative;

                z-index: 1;

                background: #344250;

                padding: 6px;

            }}

            /* ==========================================
               RAMPA
            ========================================== */

            .ramp {{

                position: absolute;

                bottom: 13px;

                right: 24px;

                border: 2px dashed #f5ce67;

                color: #f5ce67;

                border-radius: 7px;

                padding: 9px 18px;

                font-size: 13px;

                font-weight: 700;

            }}

            /* ==========================================
               INFORMACIÓN AL PASAR EL RATÓN
            ========================================== */

            .tooltip {{

                display: none;

                position: absolute;

                bottom: 105%;

                left: 50%;

                transform: translateX(-50%);

                background: #07111e;

                border: 1px solid #66819d;

                color: white;

                padding: 10px 13px;

                border-radius: 9px;

                min-width: 215px;

                font-size: 12px;

                line-height: 1.7;

                z-index: 20;

                box-shadow: 0 8px 20px #0008;

            }}

            .slot:hover .tooltip,
            .slot:focus .tooltip {{

                display: block;

            }}

            /* ==========================================
               LEYENDA
            ========================================== */

            .legend {{

                display: flex;

                gap: 20px;

                flex-wrap: wrap;

                margin-top: 20px;

                color: #afc0d4;

                font-size: 14px;

            }}

            .dot {{

                display: inline-block;

                width: 11px;

                height: 11px;

                border-radius: 50%;

                margin-right: 6px;

            }}

            .green {{
                background: #4ade80;
            }}

            .red {{
                background: #fb7185;
            }}

            .note {{

                color: #8fa2b9;

                font-size: 13px;

                margin-top: 20px;

            }}

            /* ==========================================
               PANTALLAS PEQUEÑAS
            ========================================== */

            @media (max-width: 650px) {{

                main {{
                    padding: 18px 10px;
                }}

                .stats {{
                    gap: 7px;
                }}

                .stat {{
                    padding: 11px;
                }}

                .stat strong {{
                    font-size: 23px;
                }}

                .scene-wrap {{
                    padding: 20px 0 75px;
                    min-height: 445px;
                }}

                .scene {{

                    transform:
                        scale(.65)
                        perspective(1100px)
                        rotateX(22deg)
                        rotateZ(-7deg);

                    transform-origin: top left;

                    margin-bottom: -160px;

                }}

            }}

        </style>

    </head>

    <body>

        <main>

            <!-- CABECERA -->

            <header>

                <div>

                    <h1>IA PARK</h1>

                    <div class="sub">
                        Sistema inteligente de aparcamiento
                        · Vista isométrica
                    </div>

                </div>

                <div class="live">
                    ● Datos desde SQLite
                </div>

            </header>

            <!-- ESTADÍSTICAS -->

            <div class="stats">

                <div class="stat">

                    <small>Plazas libres</small>

                    <strong>{libres}</strong>

                </div>

                <div class="stat">

                    <small>Plazas ocupadas</small>

                    <strong>{ocupadas}</strong>

                </div>

                <div class="stat">

                    <small>Ocupación total</small>

                    <strong>{porcentaje:.1f}%</strong>

                </div>

            </div>

            <!-- SELECTOR DE PLANTAS -->

            <nav class="tabs">

                <button class="tab active"
                        data-floor="0">
                    Planta 0
                </button>

                <button class="tab"
                        data-floor="1">
                    Planta 1
                </button>

                <button class="tab"
                        data-floor="2">
                    Planta 2
                </button>

            </nav>

            <!-- DIBUJO DE LAS TRES PLANTAS -->

            {html_plantas}

            <!-- LEYENDA -->

            <div class="legend">

                <span>
                    <i class="dot green"></i>
                    Libre
                </span>

                <span>
                    <i class="dot red"></i>
                    Ocupada
                </span>

                <span>
                    ↗ Rampa de acceso
                </span>

            </div>

            <p class="note">

                Vista esquemática de demostración.
                Planta 0: P01-P10.
                Planta 1: P11-P20.
                Planta 2: P21-P30.

                Los estados se actualizan cada 2 segundos.

            </p>

        </main>

        <!-- ==============================================
             JAVASCRIPT - SELECTOR DE PLANTAS
        =============================================== -->

        <script>

            function showFloor(numero) {{

                document.querySelectorAll('.floor')
                    .forEach(elemento => {{

                        elemento.hidden =
                            elemento.id !== 'floor-' + numero;

                    }});

                document.querySelectorAll('.tab')
                    .forEach(elemento => {{

                        elemento.classList.toggle(
                            'active',
                            elemento.dataset.floor === numero
                        );

                    }});

                sessionStorage.setItem(
                    'iapark-floor',
                    numero
                );

            }}

            document.querySelectorAll('.tab')
                .forEach(boton => {{

                    boton.addEventListener(
                        'click',
                        () => showFloor(boton.dataset.floor)
                    );

                }});

            showFloor(
                sessionStorage.getItem('iapark-floor') || '0'
            );

        </script>

    </body>

    </html>
    """

    return HTMLResponse(content=pagina)
