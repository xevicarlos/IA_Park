
import sqlite3
import os
from datetime import datetime


# --------------------------------------------------
# RUTA DE LA BASE DE DATOS
# --------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "iapark.db")


# --------------------------------------------------
# CONEXIÓN
# --------------------------------------------------

conexion = sqlite3.connect(DB_PATH)
cursor = conexion.cursor()


# --------------------------------------------------
# PEDIR MATRÍCULA
# --------------------------------------------------

print("\n==============================")
print("           IA PARK")
print("==============================")

matricula = input("\nIntroduzca la matrícula: ")

# Convertimos a mayúsculas y eliminamos espacios
matricula = matricula.upper().replace(" ", "")


# --------------------------------------------------
# REGISTRAR VEHÍCULO
# --------------------------------------------------

cursor.execute("""
INSERT OR IGNORE INTO vehicles (plate)
VALUES (?)
""", (matricula,))

conexion.commit()


# Obtener ID del vehículo
cursor.execute("""
SELECT id
FROM vehicles
WHERE plate = ?
""", (matricula,))

vehiculo = cursor.fetchone()

vehicle_id = vehiculo[0]

print("\nVehículo:", matricula)
print("ID vehículo:", vehicle_id)


# --------------------------------------------------
# BUSCAR PLAZAS LIBRES
# --------------------------------------------------

cursor.execute("""
SELECT id, name, latitude, longitude
FROM parking_spaces
WHERE occupied = 0
""")

plazas_libres = cursor.fetchall()

print("Plazas libres:", len(plazas_libres))


# --------------------------------------------------
# COMPROBAR SI HAY PLAZAS
# --------------------------------------------------

if len(plazas_libres) == 0:

    print("\nPARKING COMPLETO")

else:

    # De momento seleccionamos la primera plaza libre
    plaza = plazas_libres[0]

    space_id = plaza[0]
    nombre_plaza = plaza[1]
    latitud = plaza[2]
    longitud = plaza[3]

    print("\nPlaza asignada:", nombre_plaza)
    print("Coordenadas:", latitud, longitud)


    # --------------------------------------------------
    # REGISTRAR HORA DE ENTRADA
    # --------------------------------------------------

    hora_entrada = datetime.now()

    cursor.execute("""
    INSERT INTO parking_sessions
    (vehicle_id, space_id, entry_time, status)
    VALUES (?, ?, ?, 'ACTIVE')
    """, (
        vehicle_id,
        space_id,
        hora_entrada.isoformat()
    ))


    # --------------------------------------------------
    # MARCAR PLAZA COMO OCUPADA
    # --------------------------------------------------

    cursor.execute("""
    UPDATE parking_spaces
    SET occupied = 1
    WHERE id = ?
    """, (space_id,))


    conexion.commit()

    print("Hora de entrada:", hora_entrada.strftime("%H:%M:%S"))
    print("Estado: ACTIVE")


# --------------------------------------------------
# CERRAR CONEXIÓN
# --------------------------------------------------

conexion.close()