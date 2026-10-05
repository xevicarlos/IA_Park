import sqlite3
import os

# --------------------------------------------------
# RUTA DE LA BASE DE DATOS
# --------------------------------------------------

# Carpeta donde se encuentra database.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Base de datos dentro de esa misma carpeta
DB_PATH = os.path.join(BASE_DIR, "iapark.db")


# --------------------------------------------------
# CONEXIÓN CON SQLITE
# --------------------------------------------------

conexion = sqlite3.connect(DB_PATH)
cursor = conexion.cursor()


# --------------------------------------------------
# CREACIÓN DE LA TABLA DE PLAZAS (PXX)
# --------------------------------------------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS parking_spaces (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    occupied INTEGER NOT NULL DEFAULT 0
)
""")

# --------------------------------------------------
# CREACIÓN DE LA TABLA DE VEHÍCULOS (VH)
# --------------------------------------------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS vehicles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plate TEXT NOT NULL UNIQUE
)
""")

# --------------------------------------------------
# CREACIÓN DE LA TABLA DE SESIONES DE PARKING (IN/OUT)
# --------------------------------------------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS parking_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicle_id INTEGER NOT NULL,
    space_id INTEGER,
    entry_time DATETIME NOT NULL,
    exit_time DATETIME,
    status TEXT NOT NULL DEFAULT 'ACTIVE',

    FOREIGN KEY (vehicle_id)
        REFERENCES vehicles(id),

    FOREIGN KEY (space_id)
        REFERENCES parking_spaces(id)
)
""")



# --------------------------------------------------
# CREACIÓN DE 30 PLAZAS SIMULADAS
# --------------------------------------------------

for numero in range(1, 31):

    # Genera P01, P02, P03 ... P30
    nombre = f"P{numero:02d}"

    # Coordenadas provisionales para nuestra simulación  --> aqui en un futuro habria que poner las coordenadas reales
    latitud = 41.000000 + (numero * 0.000010)
    longitud = -4.000000

    # Todas empiezan libres    -->0 es libre --> 1 es ocupada
    ocupada = 0

    cursor.execute("""
        INSERT OR IGNORE INTO parking_spaces
        (name, latitude, longitude, occupied)
        VALUES (?, ?, ?, ?)
    """, (nombre, latitud, longitud, ocupada))


# Guardar cambios
conexion.commit()


# --------------------------------------------------
# MOSTRAR LAS PLAZAS GUARDADAS
# --------------------------------------------------

cursor.execute("""
SELECT id, name, latitude, longitude, occupied
FROM parking_spaces
""")

plazas = cursor.fetchall()

print("\n--- IA PARK ---")
print("Plazas registradas:", len(plazas))
print()

for plaza in plazas:

    id_plaza = plaza[0]
    nombre = plaza[1]
    latitud = plaza[2]
    longitud = plaza[3]
    ocupada = plaza[4]

    if ocupada == 0:
        estado = "LIBRE"
    else:
        estado = "OCUPADA"

    print(
        id_plaza,
        nombre,
        latitud,
        longitud,
        estado
    )


# Cerrar conexión
conexion.close()