
import sqlite3
import os

from fastapi import FastAPI
from fastapi.responses import HTMLResponse


# --------------------------------------------------
# CONFIGURACIÓN
# --------------------------------------------------

app = FastAPI()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "iapark.db")


# --------------------------------------------------
# PÁGINA PRINCIPAL
# --------------------------------------------------

@app.get("/", response_class=HTMLResponse)
def parking_status():

    # Conexión con la base de datos
    conexion = sqlite3.connect(DB_PATH)
    cursor = conexion.cursor()

    # Consultamos plazas y sesiones activas
    cursor.execute("""
    SELECT
        parking_spaces.name,
        parking_spaces.occupied,
        vehicles.plate,
        parking_sessions.entry_time

    FROM parking_spaces

    LEFT JOIN parking_sessions
        ON parking_spaces.id = parking_sessions.space_id
        AND parking_sessions.status = 'ACTIVE'

    LEFT JOIN vehicles
        ON parking_sessions.vehicle_id = vehicles.id

    ORDER BY parking_spaces.id
    """)

    plazas = cursor.fetchall()

    conexion.close()

    # Contadores
    libres = 0
    ocupadas = 0

    # Aquí iremos construyendo las plazas
    html_plazas = ""

    for plaza in plazas:

        nombre = plaza[0]
        ocupada = plaza[1]
        matricula = plaza[2]
        entrada = plaza[3]

        if ocupada == 1:

            ocupadas += 1

            estado = "OCUPADA"
            clase = "ocupada"

            if matricula is None:
                matricula = "Desconocida"

            if entrada is None:
                entrada = "-"

            else:
                entrada = entrada[11:19]

            informacion = f"""
            Plaza: {nombre}
            Estado: {estado}
            Matrícula: {matricula}
            Entrada: {entrada}
            """

        else:

            libres += 1

            estado = "LIBRE"
            clase = "libre"

            informacion = f"""
            Plaza: {nombre}
            Estado: {estado}
            """

        html_plazas += f"""
        <div class="plaza {clase}">

            <div class="numero">
                {nombre}
            </div>

            <div class="tooltip">
                {informacion.replace(chr(10), "<br>")}
            </div>

        </div>
        """

    total = len(plazas)

    if total > 0:
        porcentaje = (ocupadas / total) * 100
    else:
        porcentaje = 0


    # --------------------------------------------------
    # HTML
    # --------------------------------------------------

    html = f"""
    <!DOCTYPE html>

    <html lang="es">

    <head>

        <meta charset="UTF-8">

        <title>IA Park</title>

          
        <meta http-equiv="refresh" content="2"> 

        <style>

            body {{
                font-family: Arial, sans-serif;
                background-color: #f4f4f4;
                text-align: center;
                margin: 0;
                padding: 30px;
            }}

            h1 {{
                margin-bottom: 5px;
            }}

            .resumen {{
                margin: 30px;
                font-size: 20px;
            }}

            .parking {{
                display: grid;
                grid-template-columns: repeat(5, 100px);
                gap: 20px;
                justify-content: center;
                margin-top: 30px;
            }}

            .plaza {{
                width: 100px;
                height: 70px;

                display: flex;
                align-items: center;
                justify-content: center;

                border-radius: 10px;

                font-weight: bold;

                position: relative;

                cursor: pointer;
            }}

            .libre {{
                background-color: #4CAF50;
                color: white;
            }}

            .ocupada {{
                background-color: #F44336;
                color: white;
            }}

            .tooltip {{

                visibility: hidden;

                width: 190px;

                background-color: #222;
                color: white;

                text-align: left;

                padding: 10px;

                border-radius: 8px;

                position: absolute;

                z-index: 10;

                bottom: 85px;
                left: 50%;

                transform: translateX(-50%);

                font-size: 14px;
                font-weight: normal;
            }}

            .plaza:hover .tooltip {{
                visibility: visible;
            }}

            .leyenda {{
                margin-top: 40px;
            }}

        </style>

    </head>


    <body>

        <h1>IA PARK</h1>

        <div>Panel de control del parking</div>


        <div class="resumen">

            🟢 Libres: <strong>{libres}</strong>

            &nbsp;&nbsp;&nbsp;

            🔴 Ocupadas: <strong>{ocupadas}</strong>

            &nbsp;&nbsp;&nbsp;

            Ocupación: <strong>{porcentaje:.1f}%</strong>

        </div>


        <div class="parking">

            {html_plazas}

        </div>


        <div class="leyenda">

            🟢 Plaza libre
            &nbsp;&nbsp;&nbsp;
            🔴 Plaza ocupada

        </div>

    </body>

    </html>
    """

    return HTMLResponse(content=html)