
import sqlite3
import os
from datetime import datetime


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
# PEDIR MATRÍCULA
# --------------------------------------------------

print("\n==============================")
print("        IA PARK - SALIDA")
print("==============================")

matricula = input("\nIntroduzca la matrícula: ")

# Convertimos la matrícula a mayúsculas
# y eliminamos los espacios
matricula = matricula.upper().replace(" ", "")


# --------------------------------------------------
# BUSCAR EL VEHÍCULO
# --------------------------------------------------

cursor.execute("""
SELECT id
FROM vehicles
WHERE plate = ?
""", (matricula,))

vehiculo = cursor.fetchone()


# --------------------------------------------------
# COMPROBAR SI EL VEHÍCULO EXISTE
# --------------------------------------------------

if vehiculo is None:

    print("\nERROR: La matrícula no está registrada.")

else:

    vehicle_id = vehiculo[0]

    # --------------------------------------------------
    # BUSCAR SESIÓN ACTIVA
    # --------------------------------------------------

    cursor.execute("""
    SELECT
        parking_sessions.id,
        parking_sessions.space_id,
        parking_sessions.entry_time,
        parking_spaces.name

    FROM parking_sessions

    INNER JOIN parking_spaces
        ON parking_sessions.space_id = parking_spaces.id

    WHERE parking_sessions.vehicle_id = ?
        AND parking_sessions.status = 'ACTIVE'
    """, (vehicle_id,))

    sesion = cursor.fetchone()


    # --------------------------------------------------
    # COMPROBAR SI TIENE SESIÓN ACTIVA
    # --------------------------------------------------

    if sesion is None:

        print("\nERROR: Este vehículo no tiene ninguna sesión activa.")

    else:

        session_id = sesion[0]
        space_id = sesion[1]
        entry_time = sesion[2]
        nombre_plaza = sesion[3]


        # --------------------------------------------------
        # HORA DE SALIDA
        # --------------------------------------------------

        hora_salida = datetime.now()


        # --------------------------------------------------
        # CERRAR SESIÓN
        # --------------------------------------------------

        cursor.execute("""
        UPDATE parking_sessions

        SET exit_time = ?,
            status = 'CLOSED'

        WHERE id = ?
        """, (
            hora_salida.isoformat(),
            session_id
        ))


        # --------------------------------------------------
        # LIBERAR PLAZA
        # --------------------------------------------------

        cursor.execute("""
        UPDATE parking_spaces

        SET occupied = 0

        WHERE id = ?
        """, (space_id,))


        # Guardamos los cambios
        conexion.commit()


        # --------------------------------------------------
        # CALCULAR TIEMPO DE ESTACIONAMIENTO
        # --------------------------------------------------

        hora_entrada = datetime.fromisoformat(entry_time)

        duracion = hora_salida - hora_entrada

        segundos_totales = int(duracion.total_seconds())

        horas = segundos_totales // 3600

        minutos = (segundos_totales % 3600) // 60

        segundos = segundos_totales % 60


        # --------------------------------------------------
        # MOSTRAR RESULTADO
        # --------------------------------------------------

        print("\n==============================")
        print("       SALIDA REGISTRADA")
        print("==============================")

        print("\nMatrícula:", matricula)
        print("Plaza:", nombre_plaza)

        print(
            "Hora de entrada:",
            hora_entrada.strftime("%H:%M:%S")
        )

        print(
            "Hora de salida:",
            hora_salida.strftime("%H:%M:%S")
        )

        print(
            "Tiempo estacionado:",
            horas, "h",
            minutos, "min",
            segundos, "s"
        )

        print("\nPlaza", nombre_plaza, "liberada.")

        print("Estado de sesión: CLOSED")


# --------------------------------------------------
# CERRAR CONEXIÓN
# --------------------------------------------------

conexion.close()