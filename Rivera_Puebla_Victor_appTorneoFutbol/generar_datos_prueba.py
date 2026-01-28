"""
Script para generar datos de prueba para el sistema de torneos.
Crea equipos, jugadores y árbitros automáticamente.
"""

from Models.database import DatabaseManager
import random
from datetime import datetime, timedelta

def generar_fecha_nacimiento():
    """Genera una fecha de nacimiento aleatoria entre 15 y 25 años."""
    edad = random.randint(15, 25)
    fecha = datetime.now() - timedelta(days=edad*365)
    return fecha.strftime("%Y-%m-%d")

def generar_datos_prueba():
    """Genera todos los datos de prueba necesarios."""
    db = DatabaseManager()
    
    # Inicializar base de datos (crear tablas si no existen)
    print("Inicializando base de datos...")
    db.inicializar_db()
    print("✓ Base de datos inicializada\n")
    
    print("Generando datos de prueba para torneos...")
    print("=" * 50)
    
    # Definir equipos
    equipos_data = [
        {"nombre": "Los Tigres", "curso": "2º DAM", "escudo": "tigre.png", "color": "#FF6B00"},
        {"nombre": "Águilas FC", "curso": "1º DAM", "escudo": "aguila.png", "color": "#0066CC"},
        {"nombre": "Leones United", "curso": "2º Bachillerato", "escudo": "leon.png", "color": "#FFD700"},
        {"nombre": "Dragones FC", "curso": "1º Bachillerato", "escudo": "dragon.png", "color": "#DC143C"},
        {"nombre": "Lobos Team", "curso": "4º ESO", "escudo": "lobo.png", "color": "#808080"},
        {"nombre": "Panteras", "curso": "3º ESO", "escudo": "pantera.png", "color": "#000000"},
        {"nombre": "Halcones", "curso": "2º ESO", "escudo": "halcon.png", "color": "#4169E1"},
        {"nombre": "Osos FC", "curso": "1º ESO", "escudo": "oso.png", "color": "#8B4513"}
    ]
    
    # Nombres de ejemplo para jugadores
    nombres = [
        "Carlos", "Miguel", "David", "José", "Juan", "Antonio", "Pedro", "Luis",
        "Francisco", "Javier", "Daniel", "Alberto", "Manuel", "Rafael", "Fernando",
        "Sergio", "Pablo", "Jorge", "Rubén", "Diego", "Adrián", "Álvaro", "Iván",
        "Raúl", "Óscar", "Víctor", "Marcos", "Andrés", "Gabriel", "Hugo",
        "Mario", "Alejandro", "Samuel", "Nicolás", "Ángel", "Martín", "Lucas",
        "Jaime", "Eduardo", "Roberto", "Ricardo", "Emilio", "Guillermo", "Ignacio",
        "Felipe", "Lorenzo", "Mateo", "Tomás", "Rodrigo", "Gonzalo", "Santiago",
        "Cristian", "Julio", "Simón", "Leonardo", "Fabián", "Esteban", "Joaquín"
    ]
    
    apellidos = [
        "García", "Rodríguez", "Martínez", "López", "Sánchez", "Pérez", "Gómez",
        "Fernández", "Díaz", "Álvarez", "Moreno", "Jiménez", "Ruiz", "Hernández"
    ]
    
    posiciones = ["Portero", "Defensa", "Centrocampista", "Delantero"]
    
    # Crear equipos
    print("\n1. Creando equipos...")
    equipos_ids = []
    for equipo_data in equipos_data:
        try:
            # Verificar si el equipo ya existe
            equipos_existentes = db.obtener_todos_equipos()
            existe = any(e['nombre'] == equipo_data['nombre'] for e in equipos_existentes)
            
            if not existe:
                equipo_id = db.crear_equipo(
                    nombre=equipo_data['nombre'],
                    curso=equipo_data['curso'],
                    color=equipo_data['color'],
                    escudo_path=equipo_data['escudo']
                )
                equipos_ids.append(equipo_id)
                print(f"   ✓ Equipo creado: {equipo_data['nombre']}")
            else:
                # Obtener el ID del equipo existente
                for e in equipos_existentes:
                    if e['nombre'] == equipo_data['nombre']:
                        equipos_ids.append(e['id'])
                        print(f"   ⚠ Equipo ya existe: {equipo_data['nombre']}")
                        break
        except Exception as e:
            print(f"   ✗ Error creando equipo {equipo_data['nombre']}: {e}")
    
    # Crear jugadores para cada equipo
    print("\n2. Creando jugadores...")
    nombres_usados = set()
    total_jugadores = 0
    
    for idx, equipo_id in enumerate(equipos_ids):
        equipo = equipos_data[idx]
        num_jugadores = random.randint(7, 9)  # Entre 7 y 9 jugadores por equipo
        
        for j in range(num_jugadores):
            # Generar nombre único
            while True:
                nombre = random.choice(nombres)
                apellido1 = random.choice(apellidos)
                apellido2 = random.choice(apellidos)
                nombre_completo = f"{nombre} {apellido1} {apellido2}"
                
                if nombre_completo not in nombres_usados:
                    nombres_usados.add(nombre_completo)
                    break
            
            try:
                posicion = posiciones[j % len(posiciones)]
                dorsal = j + 1
                es_capitan = (j == 0)  # Primer jugador es capitán
                
                db.crear_jugador(
                    nombre=nombre,
                    apellidos=f"{apellido1} {apellido2}",
                    fecha_nacimiento=generar_fecha_nacimiento(),
                    curso=equipo['curso'],
                    equipo_id=equipo_id,
                    posicion=posicion,
                    dorsal=dorsal,
                    es_capitan=es_capitan,
                    tarjetas_amarillas=0,
                    tarjetas_rojas=0,
                    goles=0
                )
                total_jugadores += 1
            except Exception as e:
                print(f"   ✗ Error creando jugador: {e}")
        
        print(f"   ✓ {num_jugadores} jugadores creados para {equipo['nombre']}")
    
    # Crear árbitros
    print("\n3. Creando árbitros...")
    nombres_arbitros = [
        ("José Luis", "Martínez López", 5, "Regional"),
        ("Antonio", "García Sánchez", 8, "Nacional"),
        ("Carlos", "Fernández Ruiz", 3, "Regional"),
        ("Manuel", "Rodríguez Pérez", 10, "Internacional"),
        ("Francisco", "López González", 6, "Nacional")
    ]
    
    total_arbitros = 0
    for nombre, apellidos, experiencia, categoria in nombres_arbitros:
        try:
            db.crear_arbitro(
                nombre=nombre,
                apellidos=apellidos,
                fecha_nacimiento=generar_fecha_nacimiento(),
                experiencia=experiencia,
                categoria=categoria
            )
            total_arbitros += 1
            print(f"   ✓ Árbitro creado: {nombre} {apellidos} ({categoria})")
        except Exception as e:
            print(f"   ✗ Error creando árbitro: {e}")
    
    # Resumen
    print("\n" + "=" * 50)
    print("RESUMEN DE DATOS GENERADOS:")
    print(f"  • Equipos: {len(equipos_ids)}")
    print(f"  • Jugadores: {total_jugadores}")
    print(f"  • Árbitros: {total_arbitros}")
    print("=" * 50)
    print("\n✓ ¡Datos de prueba generados exitosamente!")
    print("  Ahora puedes crear un torneo con estos equipos.\n")

if __name__ == "__main__":
    try:
        generar_datos_prueba()
    except Exception as e:
        print(f"\n✗ Error durante la generación de datos: {e}")
        import traceback
        traceback.print_exc()
