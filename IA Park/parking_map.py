
# ==========================================================
# IA PARK
# MAPA LÓGICO DEL APARCAMIENTO simulado
# ==========================================================

import heapq


# ==========================================================
# CONFIGURACIÓN
# ==========================================================

NUM_PLANTAS = 3
PLAZAS_POR_PLANTA = 10

# Distancias simuladas en metros

DISTANCIA_NODOS = 5
DISTANCIA_PLAZA = 3

# Longitud física simulada de la rampa
DISTANCIA_RAMPA = 25

# Factor de penalización por "pendiente y maniobras", entendiendo esto como un factor que aumenta el coste debido a que es una rampa y no una simple recta.
FACTOR_PENALIZACION_RAMPA = 2.0

# Coste equivalente utilizado por Dijkstra
COSTE_RAMPA = (
    DISTANCIA_RAMPA * FACTOR_PENALIZACION_RAMPA
)
DISTANCIA_ENTRADA = 5

# Nodo de entrada principal
ENTRADA = "ENTRADA"

# Grafo del aparcamiento
grafo = {}


# ==========================================================
# AÑADIR CONEXIONES 
# ==========================================================

def conectar(nodo1, nodo2, distancia):

    if nodo1 not in grafo:
        grafo[nodo1] = {}

    if nodo2 not in grafo:
        grafo[nodo2] = {}

    # Conexión bidireccional
    grafo[nodo1][nodo2] = distancia
    grafo[nodo2][nodo1] = distancia


# ==========================================================
# CREAR LAS TRES PLANTAS grafo - programa
# ==========================================================

def crear_mapa():

    grafo.clear()

    for planta in range(NUM_PLANTAS):

        # Cinco nodos en el carril central
        for posicion in range(5):

            nodo = f"N{planta}_{posicion}"

            grafo[nodo] = {}

        # Conectar los nodos del carril
        for posicion in range(4):

            nodo1 = f"N{planta}_{posicion}"
            nodo2 = f"N{planta}_{posicion + 1}"

            conectar(
                nodo1,
                nodo2,
                DISTANCIA_NODOS
            )

        # Conectar las diez plazas
        for posicion in range(5):

            nodo = f"N{planta}_{posicion}"

            numero_superior = (
                planta * PLAZAS_POR_PLANTA
                + posicion
                + 1
            )

            numero_inferior = (
                planta * PLAZAS_POR_PLANTA
                + posicion
                + 6
            )

            plaza_superior = f"P{numero_superior:02d}"
            plaza_inferior = f"P{numero_inferior:02d}"

            conectar(
                nodo,
                plaza_superior,
                DISTANCIA_PLAZA
            )

            conectar(
                nodo,
                plaza_inferior,
                DISTANCIA_PLAZA
            )

    # ======================================================
    # ENTRADA PRINCIPAL
    # ======================================================

    conectar(
        ENTRADA,
        "N0_0",
        DISTANCIA_ENTRADA
    )

    # ======================================================
    # RAMPAS ENTRE PLANTAS, para evaluar el aumento de coste de subir una rampa
    # ======================================================

    conectar(
        "N0_4",
        "N1_4",
        COSTE_RAMPA
    )

    conectar(
        "N1_4",
        "N2_4",
        COSTE_RAMPA
    )


# ==========================================================
# DIJKSTRA - CAMINO MÁS CORTO a la plaza
# ==========================================================

def dijkstra(origen):

    distancias = {
        nodo: float("inf")
        for nodo in grafo
    }

    anteriores = {
        nodo: None
        for nodo in grafo
    }

    distancias[origen] = 0

    cola = [(0, origen)]

    while cola:

        distancia_actual, nodo_actual = heapq.heappop(cola)

        if distancia_actual > distancias[nodo_actual]:
            continue

        for vecino, peso in grafo[nodo_actual].items():

            nueva_distancia = distancia_actual + peso

            if nueva_distancia < distancias[vecino]:

                distancias[vecino] = nueva_distancia

                anteriores[vecino] = nodo_actual

                heapq.heappush(
                    cola,
                    (nueva_distancia, vecino)
                )

    return distancias, anteriores


# ==========================================================
# RECONSTRUIR UNA RUTA
# ==========================================================

def obtener_ruta(anteriores, destino):

    ruta = []

    nodo = destino

    while nodo is not None:

        ruta.append(nodo)

        nodo = anteriores[nodo]

    ruta.reverse()

    return ruta



# ==========================================================
# ANALIZAR RECORRIDO PARA VER LOS DIFERENTES VALORES EN METROS Y EN FUNCION COSTE (EVALUAR MULTIPLICADORES TIPO RAMPA)
# ==========================================================

def analizar_recorrido(ruta):

    distancia_fisica = 0
    coste_ponderado = 0
    numero_rampas = 0

    # Recorrer cada conexión de la ruta
    for i in range(len(ruta) - 1):

        nodo_actual = ruta[i]
        nodo_siguiente = ruta[i + 1]

        # Coste almacenado en el grafo
        coste_tramo = grafo[nodo_actual][nodo_siguiente]

        coste_ponderado += coste_tramo

        # Identificar si la conexión es una rampa
        es_rampa = (
            nodo_actual.startswith("N")
            and nodo_siguiente.startswith("N")
            and nodo_actual.split("_")[0]
                != nodo_siguiente.split("_")[0]
        )

        if es_rampa:

            numero_rampas += 1

            # La distancia física de la rampa
            # no incluye su penalización
            distancia_fisica += DISTANCIA_RAMPA

        else:

            distancia_fisica += coste_tramo

    return {
        "distancia_fisica": distancia_fisica,
        "coste_ponderado": coste_ponderado,
        "numero_rampas": numero_rampas
    }


# ==========================================================
# PROGRAMA DE PRUEBA para su evaluación
# ==========================================================

if __name__ == "__main__":

    crear_mapa()

    print("\n===================================")
    print("       IA PARK - MAPA LÓGICO")
    print("===================================")

    print(f"\nPlantas: {NUM_PLANTAS}")
    print(f"Plazas: {NUM_PLANTAS * PLAZAS_POR_PLANTA}")
    print(f"Nodos totales: {len(grafo)}")

    # Calcular las rutas desde la entrada
    distancias, anteriores = dijkstra(ENTRADA)

    while True:

        print("\n-----------------------------------")
        print(" CONSULTA DE RUTAS")
        print("-----------------------------------")
        print("Introduce una plaza (P01 - P30)")
        print("Escribe SALIR para finalizar")

        destino = input("\nPlaza: ").strip().upper()

        if destino == "SALIR":
            print("\nFinalizando IA Park...")
            break

        # Aceptar P15, 15 o 015
        if destino.startswith("P"):
            destino = destino[1:]

        if not destino.isdigit():
            print("\nERROR: Introduce una plaza válida.")
            continue

        numero = int(destino)

        if not 1 <= numero <= NUM_PLANTAS * PLAZAS_POR_PLANTA:
            print("\nERROR: Plaza fuera de rango.")
            continue

        destino = f"P{numero:02d}"

        # Reconstruir ruta óptima
        ruta = obtener_ruta(anteriores, destino)

        # Analizar distancia y penalizaciones
        resultado = analizar_recorrido(ruta)

        # Identificar planta
        planta = (numero - 1) // PLAZAS_POR_PLANTA

        print("\n===================================")
        print(f" RESULTADO - PLAZA {destino}")
        print("===================================")

        print(f"\nPlanta: {planta}")

        print(
            f"Distancia física: "
            f"{resultado['distancia_fisica']:.1f} metros"
        )

        print(
            f"Coste ponderado: "
            f"{resultado['coste_ponderado']:.1f}"
        )

        print(
            f"Rampas recorridas: "
            f"{resultado['numero_rampas']}"
        )

        print("\nRuta recomendada:")
        print(" -> ".join(ruta))

        print("\n===================================")

    print("\nPrograma finalizado.")
