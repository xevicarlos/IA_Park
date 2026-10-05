
import sqlite3
import os


# --------------------------------------------------
# RUTA DE LA BASE DE DATOS
# --------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "iapark.db")


# --------------------------------------------------
# CONEXIÓN CON SQLITE
# --------------------------------------------------

conexion = sqlite3.connect(DB_PATH)
cursor = conexion.cursor()


# --------------------------------------------------
# CONSULTAR ESTADO DE TODAS LAS PLAZAS
# --------------------------------------------------

cursor.execute("""
SELECT
    parking_spaces.id,
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


# --------------------------------------------------
# CONTADORES
# --------------------------------------------------

total_plazas = len(plazas)
plazas_ocupadas = 0
plazas_libres = 0


# --------------------------------------------------
# CABECERA
# --------------------------------------------------

print("\n============================================================")
print("                    IA PARK - ESTADO")
print("============================================================")

print()
print(
    f"{'PLAZA':<10}"
    f"{'ESTADO':<15}"
    f"{'MATRÍCULA':<15}"
    f"{'ENTRADA':<20}"
)

print("-" * 60)


# --------------------------------------------------
# MOSTRAR PLAZAS
# --------------------------------------------------

for plaza in plazas:

    id_plaza = plaza[0]
    nombre = plaza[1]
    ocupada = plaza[2]
    matricula = plaza[3]
    hora_entrada = plaza[4]

    if ocupada == 1:

        estado = "OCUPADA"
        plazas_ocupadas += 1

        if matricula is None:
            matricula = "DESCONOCIDA"

        if hora_entrada is None:
            hora_entrada = "-"

        else:
            # Mostramos solamente fecha y hora
            hora_entrada = hora_entrada[:19]

    else:

        estado = "LIBRE"
        plazas_libres += 1
        matricula = "-"
        hora_entrada = "-"

    print(
        f"{nombre:<10}"
        f"{estado:<15}"
        f"{matricula:<15}"
        f"{hora_entrada:<20}"
    )


# --------------------------------------------------
# RESUMEN DEL PARKING
# --------------------------------------------------

print("-" * 60)

print("\nRESUMEN DEL PARKING")

print("Total de plazas:   ", total_plazas)
print("Plazas libres:     ", plazas_libres)
print("Plazas ocupadas:   ", plazas_ocupadas)

if total_plazas > 0:

    porcentaje = (plazas_ocupadas / total_plazas) * 100

    print(
        "Ocupación:          ",
        f"{porcentaje:.1f} %"
    )


# --------------------------------------------------
# CERRAR CONEXIÓN
# --------------------------------------------------

conexion.close()