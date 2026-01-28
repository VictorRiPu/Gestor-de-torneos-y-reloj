"""
Script para generar equipos y jugadores adicionales.
Genera hasta 32 equipos en total para poder probar torneos de dieciseisavos.
"""

from Models.database import DatabaseManager
import random
import sqlite3
from datetime import datetime, timedelta

def generar_fecha_nacimiento():
    """Genera una fecha de nacimiento aleatoria entre 15 y 25 años."""
    hoy = datetime.now()
    años_atras = random.randint(15, 25)
    dias_atras = random.randint(0, 365)
    fecha = hoy - timedelta(days=años_atras * 365 + dias_atras)
    return fecha.strftime("%Y-%m-%d")

def generar_equipos_adicionales():
    """Genera equipos y jugadores adicionales hasta llegar a 32 equipos."""
    db = DatabaseManager()
    
    print("Generando equipos y jugadores adicionales...")
    print("=" * 60)
    
    # Verificar cuántos equipos hay actualmente
    db.conectar()
    cursor = db.conn.cursor()
    cursor.execute("SELECT COUNT(*) as total FROM Equipos")
    equipos_existentes = cursor.fetchone()['total']
    db.desconectar()
    
    print(f"\n✓ Equipos existentes: {equipos_existentes}")
    equipos_a_crear = 32 - equipos_existentes
    
    if equipos_a_crear <= 0:
        print("\n✓ Ya tienes 32 equipos o más. No es necesario generar más.")
        return
    
    print(f"✓ Se crearán {equipos_a_crear} equipos nuevos\n")
    
    # Nombres creativos para equipos
    nombres_equipos = [
        "Dragones FC", "Fénix United", "Cóndores Team", "Panteras Club",
        "Lobos Grises", "Toros Bravos", "Halcones Rojos", "Tiburones FC",
        "Zorros Plateados", "Jaguares Club", "Búfalos Team", "Rinocerontes FC",
        "Mustangs United", "Caballos Salvajes", "Osos Polares", "Pumas FC",
        "Gorilas Team", "Serpientes Club", "Escorpiones FC", "Leones Marinos",
        "Delfines Club", "Ballenas Team", "Pulpos FC", "Medusas United",
        "Arañas Rojas", "Avispas Club", "Abejas Team", "Hormigas FC",
        "Mantis United", "Grillos Club", "Cigarras Team", "Luciérnagas FC",
        "Cometas FC", "Estrellas United", "Galaxias Team", "Meteoros Club",
        "Planetas FC", "Satélites United", "Asteroides Team", "Constelaciones FC"
    ]
    
    # Obtener nombres de equipos existentes
    db.conectar()
    cursor = db.conn.cursor()
    cursor.execute("SELECT nombre FROM Equipos")
    equipos_existentes_nombres = set(row['nombre'] for row in cursor.fetchall())
    db.desconectar()
    
    # Filtrar nombres disponibles
    nombres_disponibles = [n for n in nombres_equipos if n not in equipos_existentes_nombres]
    
    if len(nombres_disponibles) < equipos_a_crear:
        print(f"⚠️  Solo hay {len(nombres_disponibles)} nombres únicos disponibles")
        equipos_a_crear = len(nombres_disponibles)
    
    colores = [
        "#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#FF00FF", "#00FFFF",
        "#800000", "#008000", "#000080", "#808000", "#800080", "#008080",
        "#FFA500", "#A52A2A", "#DC143C", "#00CED1", "#9400D3", "#FF1493",
        "#FFD700", "#ADFF2F", "#4B0082", "#F0E68C", "#E0FFFF", "#90EE90",
        "#FF6347", "#40E0D0", "#EE82EE", "#F5DEB3", "#FFFFFF", "#7FFFD4",
        "#BC8F8F", "#8B4513"
    ]
    
    escudos = [
        "aguila.png", "leon.png", "tigre.png", "oso.png", "lobo.png",
        "pantera.png", "dragon.png", "tiburon.png"
    ]
    
    cursos = ["1º DAM", "2º DAM", "1º Bachillerato", "2º Bachillerato", "1º ESO", "2º ESO"]
    
    nombres = [
        "Alejandro", "Carlos", "David", "Eduardo", "Fernando", "Gabriel", "Hugo",
        "Iván", "Javier", "Lucas", "Miguel", "Nicolás", "Oscar", "Pablo", "Ricardo",
        "Sergio", "Tomás", "Vicente", "Alberto", "Andrés", "Bruno", "Daniel",
        "Emilio", "Francisco", "Guillermo", "Héctor", "Ignacio", "Jorge", "Luis",
        "Manuel", "Ángel", "Antonio"
    ]
    
    apellidos = [
        "García", "Rodríguez", "Martínez", "López", "Sánchez", "Pérez", "Gómez",
        "Fernández", "Díaz", "Álvarez", "Moreno", "Jiménez", "Ruiz", "Hernández",
        "Torres", "Ramírez", "Flores", "Rivera", "Cruz", "Reyes", "Silva", "Ramos",
        "Castro", "Ortiz", "Mendoza", "Vargas", "Medina", "Núñez", "Guerrero"
    ]
    
    posiciones = ["Portero", "Defensa", "Centrocampista", "Delantero"]
    
    equipos_ids = []
    equipos_creados = 0
    
    print("\n1. Creando equipos...")
    for i in range(equipos_a_crear):
        nombre_equipo = nombres_disponibles[i]
        color = colores[i % len(colores)]
        escudo = escudos[i % len(escudos)]
        curso = random.choice(cursos)
        
        try:
            equipo_id = db.crear_equipo(
                nombre=nombre_equipo,
                curso=curso,
                color=color,
                escudo_path=escudo
            )
            equipos_ids.append(equipo_id)
            equipos_creados += 1
            print(f"   ✓ Equipo creado: {nombre_equipo} ({curso})")
        except sqlite3.IntegrityError:
            print(f"   ⚠️  Equipo ya existe: {nombre_equipo} (saltando)")
        except Exception as e:
            print(f"   ✗ Error creando equipo {nombre_equipo}: {e}")
    
    print(f"\n   Total equipos creados: {equipos_creados}")
    
    # Crear jugadores para cada equipo
    print("\n2. Creando jugadores...")
    nombres_usados = set()
    total_jugadores = 0
    
    for equipo_id in equipos_ids:
        num_jugadores = random.randint(8, 11)  # Entre 8 y 11 jugadores
        
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
                # Obtener info del equipo
                db.conectar()
                cursor = db.conn.cursor()
                cursor.execute("SELECT nombre, curso FROM Equipos WHERE id = ?", (equipo_id,))
                equipo = cursor.fetchone()
                db.desconectar()
                
                posicion = posiciones[j % len(posiciones)]
                dorsal = j + 1
                es_capitan = (j == 0)
                
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
        
        if equipo:
            print(f"   ✓ {num_jugadores} jugadores creados para {equipo['nombre']}")
    
    # Crear algunos árbitros adicionales
    print("\n3. Creando árbitros adicionales...")
    categorias = ["Regional", "Nacional", "Internacional"]
    total_arbitros = 0
    
    for i in range(10):
        while True:
            nombre = random.choice(nombres)
            apellido1 = random.choice(apellidos)
            apellido2 = random.choice(apellidos)
            nombre_completo = f"{nombre} {apellido1} {apellido2}"
            
            if nombre_completo not in nombres_usados:
                nombres_usados.add(nombre_completo)
                break
        
        categoria = random.choice(categorias)
        curso = random.choice(cursos)
        
        try:
            db.crear_arbitro(
                nombre=nombre,
                apellidos=f"{apellido1} {apellido2}",
                fecha_nacimiento=generar_fecha_nacimiento(),
                curso=curso,
                categoria=categoria
            )
            total_arbitros += 1
            print(f"   ✓ Árbitro creado: {nombre} {apellido1} ({categoria})")
        except Exception as e:
            print(f"   ✗ Error creando árbitro: {e}")
    
    # Resumen final
    print("\n" + "=" * 60)
    print("RESUMEN FINAL:")
    
    db.conectar()
    cursor = db.conn.cursor()
    cursor.execute("SELECT COUNT(*) as total FROM Equipos")
    total_equipos = cursor.fetchone()['total']
    cursor.execute("SELECT COUNT(*) as total FROM Jugadores")
    total_jugadores_db = cursor.fetchone()['total']
    cursor.execute("SELECT COUNT(*) as total FROM Arbitros")
    total_arbitros_db = cursor.fetchone()['total']
    db.desconectar()
    
    print(f"  • Total de equipos en BD: {total_equipos}")
    print(f"  • Total de jugadores en BD: {total_jugadores_db}")
    print(f"  • Total de árbitros en BD: {total_arbitros_db}")
    print("=" * 60)
    print(f"\n✓ ¡Datos adicionales generados exitosamente!")
    print(f"  Ahora puedes crear un torneo de 32 equipos (dieciseisavos).\n")

if __name__ == "__main__":
    try:
        generar_equipos_adicionales()
    except Exception as e:
        print(f"\n✗ Error durante la generación de datos: {e}")
        import traceback
        traceback.print_exc()
