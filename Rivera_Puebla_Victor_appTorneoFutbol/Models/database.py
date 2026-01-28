"""
Módulo de gestión de base de datos SQLite para la aplicación de torneos de fútbol.
Incluye el DatabaseManager con todas las tablas necesarias y utilidades para rutas de recursos.
"""

import sqlite3
import os
import sys
from datetime import datetime
from typing import Optional, List, Tuple, Dict


def obtener_ruta_recurso(ruta_relativa: str) -> str:
    """
    Obtiene la ruta absoluta de un recurso.
    Compatible con PyInstaller para ejecutables (.exe).
    
    Args:
        ruta_relativa: Ruta relativa desde la raíz del proyecto
        
    Returns:
        Ruta absoluta del recurso
    """
    try:
        # PyInstaller crea una carpeta temporal _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        # En desarrollo, usa el directorio actual
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, ruta_relativa)


class DatabaseManager:
    """
    Gestor de base de datos SQLite para torneos de fútbol.
    Maneja equipos, participantes, partidos, resultados y eventos.
    """
    
    def __init__(self, db_name: str = "torneo_futbol.db"):
        """
        Inicializa el gestor de base de datos.
        
        Args:
            db_name: Nombre del archivo de base de datos
        """
        self.db_path = obtener_ruta_recurso(db_name)
        self.conn = None
        
    def conectar(self):
        """Establece conexión con la base de datos."""
        self.conn = sqlite3.connect(self.db_path, timeout=30.0)  # Timeout de 30 segundos
        self.conn.row_factory = sqlite3.Row  # Permite acceder a columnas por nombre
        # Habilitar claves foráneas
        self.conn.execute("PRAGMA foreign_keys = ON")
        # Configurar para mejor manejo de bloqueos
        self.conn.execute("PRAGMA busy_timeout = 30000")  # 30 segundos en milisegundos
        
    def desconectar(self):
        """Cierra la conexión con la base de datos."""
        if self.conn:
            self.conn.close()
            self.conn = None
            
    def inicializar_db(self):
        """
        Crea todas las tablas de la base de datos si no existen.
        Estructura: Equipos, Participantes, Jugadores, Arbitros, Partidos, 
        Resultados, Eventos, Torneo.
        """
        self.conectar()
        cursor = self.conn.cursor()
        
        # Tabla Equipos: información básica de cada equipo
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Equipos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL UNIQUE,
                curso TEXT NOT NULL,
                color TEXT NOT NULL,
                escudo_path TEXT NOT NULL,
                fecha_creacion TEXT NOT NULL
            )
        """)
        
        # Tabla Participantes: personas que participan en el torneo
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Participantes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                fecha_nacimiento TEXT NOT NULL,
                curso TEXT NOT NULL,
                tipo TEXT NOT NULL CHECK(tipo IN ('Jugador', 'Arbitro', 'Ambos')),
                fecha_registro TEXT NOT NULL
            )
        """)
        
        # Tabla Jugadores: participantes que son jugadores con posición
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Jugadores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                apellidos TEXT NOT NULL,
                fecha_nacimiento TEXT,
                curso TEXT,
                equipo_id INTEGER,
                posicion TEXT NOT NULL CHECK(posicion IN ('Portero', 'Defensa', 'Centrocampista', 'Delantero')),
                dorsal INTEGER,
                es_capitan INTEGER DEFAULT 0,
                tarjetas_amarillas INTEGER DEFAULT 0,
                tarjetas_rojas INTEGER DEFAULT 0,
                goles INTEGER DEFAULT 0,
                FOREIGN KEY (equipo_id) REFERENCES Equipos(id) ON DELETE SET NULL
            )
        """)
        
        # Tabla Arbitros: árbitros que pueden arbitrar partidos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Arbitros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                apellidos TEXT NOT NULL,
                fecha_nacimiento TEXT,
                experiencia INTEGER DEFAULT 0,
                categoria TEXT DEFAULT 'Regional'
            )
        """)
        
        # Tabla Participantes: tabla legacy (mantener por compatibilidad)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Participantes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                fecha_nacimiento TEXT,
                curso TEXT,
                tipo TEXT
            )
        """)
        
        # Tabla Torneo: información del torneo activo
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Torneo (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                num_equipos INTEGER NOT NULL CHECK(num_equipos IN (8, 16, 32)),
                estado TEXT NOT NULL CHECK(estado IN ('activo', 'finalizado')),
                fecha_inicio TEXT NOT NULL,
                fecha_finalizacion TEXT
            )
        """)
        
        # Tabla Partidos: partidos del torneo
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Partidos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                torneo_id INTEGER NOT NULL,
                equipo_a_id INTEGER,
                equipo_b_id INTEGER,
                fecha TEXT,
                hora TEXT,
                arbitro_id INTEGER,
                ronda TEXT NOT NULL,
                numero_partido INTEGER NOT NULL,
                estado TEXT NOT NULL CHECK(estado IN ('pendiente', 'en_curso', 'finalizado', 'cancelado')) DEFAULT 'pendiente',
                ganador_id INTEGER,
                FOREIGN KEY (torneo_id) REFERENCES Torneo(id) ON DELETE CASCADE,
                FOREIGN KEY (equipo_a_id) REFERENCES Equipos(id) ON DELETE CASCADE,
                FOREIGN KEY (equipo_b_id) REFERENCES Equipos(id) ON DELETE CASCADE,
                FOREIGN KEY (arbitro_id) REFERENCES Arbitros(id) ON DELETE SET NULL,
                FOREIGN KEY (ganador_id) REFERENCES Equipos(id) ON DELETE SET NULL
            )
        """)
        
        # Tabla Resultados: resultado de cada partido
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Resultados (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                partido_id INTEGER NOT NULL UNIQUE,
                goles_equipo_a INTEGER NOT NULL DEFAULT 0,
                goles_equipo_b INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (partido_id) REFERENCES Partidos(id) ON DELETE CASCADE
            )
        """)
        
        # Tabla Eventos: goles y tarjetas durante los partidos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Eventos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                partido_id INTEGER NOT NULL,
                jugador_id INTEGER NOT NULL,
                tipo_evento TEXT NOT NULL CHECK(tipo_evento IN ('gol', 'tarjeta_amarilla', 'tarjeta_roja')),
                minuto INTEGER,
                FOREIGN KEY (partido_id) REFERENCES Partidos(id) ON DELETE CASCADE,
                FOREIGN KEY (jugador_id) REFERENCES Jugadores(id) ON DELETE CASCADE
            )
        """)
        
        self.conn.commit()
        self.desconectar()
        
    # ========== MÉTODOS DE EQUIPOS ==========
    
    def crear_equipo(self, nombre: str, curso: str, color: str, escudo_path: str) -> int:
        """
        Crea un nuevo equipo en la base de datos.
        
        Args:
            nombre: Nombre del equipo
            curso: Curso del equipo
            color: Color representativo (formato hex o nombre)
            escudo_path: Ruta al archivo de escudo
            
        Returns:
            ID del equipo creado
        """
        self.conectar()
        cursor = self.conn.cursor()
        fecha_actual = datetime.now().strftime('%d/%m/%Y')
        
        cursor.execute("""
            INSERT INTO Equipos (nombre, curso, color, escudo_path, fecha_creacion)
            VALUES (?, ?, ?, ?, ?)
        """, (nombre, curso, color, escudo_path, fecha_actual))
        
        equipo_id = cursor.lastrowid
        self.conn.commit()
        self.desconectar()
        return equipo_id
        
    def obtener_todos_equipos(self) -> List[Dict]:
        """
        Obtiene todos los equipos registrados.
        
        Returns:
            Lista de diccionarios con información de equipos
        """
        self.conectar()
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM Equipos ORDER BY nombre")
        equipos = [dict(row) for row in cursor.fetchall()]
        self.desconectar()
        return equipos
        
    def obtener_equipo_por_id(self, equipo_id: int) -> Optional[Dict]:
        """
        Obtiene un equipo por su ID.
        
        Args:
            equipo_id: ID del equipo
            
        Returns:
            Diccionario con información del equipo o None
        """
        self.conectar()
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM Equipos WHERE id = ?", (equipo_id,))
        equipo = cursor.fetchone()
        self.desconectar()
        return dict(equipo) if equipo else None
        
    def actualizar_equipo(self, equipo_id: int, nombre: str, curso: str, color: str, escudo_path: str):
        """
        Actualiza información de un equipo existente.
        
        Args:
            equipo_id: ID del equipo a actualizar
            nombre: Nuevo nombre
            curso: Nuevo curso
            color: Nuevo color
            escudo_path: Nueva ruta de escudo
        """
        self.conectar()
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE Equipos 
            SET nombre = ?, curso = ?, color = ?, escudo_path = ?
            WHERE id = ?
        """, (nombre, curso, color, escudo_path, equipo_id))
        self.conn.commit()
        self.desconectar()
        
    def eliminar_equipo(self, equipo_id: int):
        """
        Elimina un equipo de la base de datos.
        CASCADE eliminará también jugadores asociados.
        
        Args:
            equipo_id: ID del equipo a eliminar
        """
        self.conectar()
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM Equipos WHERE id = ?", (equipo_id,))
        self.conn.commit()
        self.desconectar()
        
    def obtener_escudos_usados(self) -> List[str]:
        """
        Obtiene lista de rutas de escudos ya utilizados.
        
        Returns:
            Lista de rutas de escudos en uso
        """
        self.conectar()
        cursor = self.conn.cursor()
        cursor.execute("SELECT escudo_path FROM Equipos")
        escudos = [row['escudo_path'] for row in cursor.fetchall()]
        self.desconectar()
        return escudos
        
    def buscar_equipos(self, texto_busqueda: str) -> List[Dict]:
        """
        Busca equipos por nombre o curso.
        
        Args:
            texto_busqueda: Texto a buscar
            
        Returns:
            Lista de equipos que coinciden con la búsqueda
        """
        self.conectar()
        cursor = self.conn.cursor()
        patron = f"%{texto_busqueda}%"
        cursor.execute("""
            SELECT * FROM Equipos 
            WHERE nombre LIKE ? OR curso LIKE ?
            ORDER BY nombre
        """, (patron, patron))
        equipos = [dict(row) for row in cursor.fetchall()]
        self.desconectar()
        return equipos
        
    def contar_jugadores_por_equipo(self, equipo_id: int) -> int:
        """
        Cuenta el número de jugadores de un equipo.
        
        Args:
            equipo_id: ID del equipo
            
        Returns:
            Número de jugadores en el equipo
        """
        self.conectar()
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) as total 
            FROM Jugadores 
            WHERE equipo_id = ?
        """, (equipo_id,))
        total = cursor.fetchone()['total']
        self.desconectar()
        return total
        
    # ========== MÉTODOS DE PARTICIPANTES ==========
    
    def crear_participante(self, nombre: str, fecha_nacimiento: str, curso: str, tipo: str) -> int:
        """
        Crea un nuevo participante.
        
        Args:
            nombre: Nombre completo
            fecha_nacimiento: Fecha en formato DD/MM/YYYY
            curso: Curso del participante
            tipo: 'Jugador', 'Arbitro' o 'Ambos'
            
        Returns:
            ID del participante creado
        """
        self.conectar()
        cursor = self.conn.cursor()
        fecha_registro = datetime.now().strftime('%d/%m/%Y')
        
        cursor.execute("""
            INSERT INTO Participantes (nombre, fecha_nacimiento, curso, tipo, fecha_registro)
            VALUES (?, ?, ?, ?, ?)
        """, (nombre, fecha_nacimiento, curso, tipo, fecha_registro))
        
        participante_id = cursor.lastrowid
        self.conn.commit()
        self.desconectar()
        return participante_id
        
    def crear_jugador(self, nombre: str, apellidos: str, fecha_nacimiento: str,
                     curso: str, equipo_id: Optional[int], posicion: str,
                     dorsal: int = 1, es_capitan: bool = False,
                     tarjetas_amarillas: int = 0, tarjetas_rojas: int = 0, 
                     goles: int = 0) -> int:
        """
        Crea un nuevo jugador.
        
        Args:
            nombre: Nombre del jugador
            apellidos: Apellidos del jugador
            fecha_nacimiento: Fecha de nacimiento
            curso: Curso del jugador
            equipo_id: ID del equipo (puede ser None)
            posicion: Posición del jugador
            dorsal: Número de dorsal
            es_capitan: Si es capitán del equipo
            tarjetas_amarillas: Tarjetas amarillas acumuladas
            tarjetas_rojas: Tarjetas rojas acumuladas
            goles: Goles marcados
            
        Returns:
            ID del jugador creado
        """
        self.conectar()
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO Jugadores (nombre, apellidos, fecha_nacimiento, curso,
                                  equipo_id, posicion, dorsal, es_capitan,
                                  tarjetas_amarillas, tarjetas_rojas, goles)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (nombre, apellidos, fecha_nacimiento, curso, equipo_id,
              posicion, dorsal, 1 if es_capitan else 0, 
              tarjetas_amarillas, tarjetas_rojas, goles))
        jugador_id = cursor.lastrowid
        self.conn.commit()
        self.desconectar()
        return jugador_id
        
    def crear_arbitro(self, nombre: str, apellidos: str, fecha_nacimiento: str,
                     experiencia: int = 0, categoria: str = "Regional") -> int:
        """
        Crea un nuevo árbitro.
        
        Args:
            nombre: Nombre del árbitro
            apellidos: Apellidos del árbitro
            fecha_nacimiento: Fecha de nacimiento
            experiencia: Años de experiencia
            categoria: Categoría del árbitro
            
        Returns:
            ID del árbitro creado
        """
        self.conectar()
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO Arbitros (nombre, apellidos, fecha_nacimiento,
                                 experiencia, categoria)
            VALUES (?, ?, ?, ?, ?)
        """, (nombre, apellidos, fecha_nacimiento, experiencia, categoria))
        arbitro_id = cursor.lastrowid
        self.conn.commit()
        self.desconectar()
        return arbitro_id
        
    def obtener_todos_arbitros(self) -> List[Dict]:
        """
        Obtiene todos los árbitros disponibles.
        
        Returns:
            Lista de árbitros con información completa
        """
        self.conectar()
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM Arbitros
            ORDER BY nombre, apellidos
        """)
        arbitros = [dict(row) for row in cursor.fetchall()]
        self.desconectar()
        return arbitros
        
    def validar_arbitro_disponible(self, arbitro_id: int, fecha: str, hora: str, 
                                   partido_id_excluir: Optional[int] = None) -> Tuple[bool, Optional[str]]:
        """
        Valida si un árbitro está disponible en una fecha y hora específicas.
        
        Args:
            arbitro_id: ID del árbitro
            fecha: Fecha en formato DD/MM/YYYY
            hora: Hora en formato HH:MM
            partido_id_excluir: ID de partido a excluir de la validación (para edición)
            
        Returns:
            Tupla (disponible: bool, mensaje_error: str)
        """
        self.conectar()
        cursor = self.conn.cursor()
        
        # Buscar partidos del árbitro en la misma fecha y hora
        if partido_id_excluir:
            cursor.execute("""
                SELECT COUNT(*) as conflictos
                FROM Partidos
                WHERE arbitro_id = ? AND fecha = ? AND hora = ? AND id != ?
            """, (arbitro_id, fecha, hora, partido_id_excluir))
        else:
            cursor.execute("""
                SELECT COUNT(*) as conflictos
                FROM Partidos
                WHERE arbitro_id = ? AND fecha = ? AND hora = ?
            """, (arbitro_id, fecha, hora))
            
        conflictos = cursor.fetchone()['conflictos']
        
        if conflictos > 0:
            # Obtener nombre del árbitro para el mensaje
            cursor.execute("""
                SELECT a.nombre, a.apellidos
                FROM Arbitros a
                WHERE a.id = ?
            """, (arbitro_id,))
            arbitro_data = cursor.fetchone()
            nombre_arbitro = f"{arbitro_data['nombre']} {arbitro_data['apellidos']}"
            mensaje = f"El árbitro {nombre_arbitro} ya tiene un partido asignado el {fecha} a las {hora}"
            self.desconectar()
            return False, mensaje
            
        self.desconectar()
        return True, None
        
    def obtener_jugadores_por_equipo(self, equipo_id: int) -> List[Dict]:
        """
        Obtiene todos los jugadores de un equipo específico.
        
        Args:
            equipo_id: ID del equipo
            
        Returns:
            Lista de jugadores con información completa
        """
        self.conectar()
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                j.id,
                j.nombre,
                j.apellidos,
                j.posicion,
                j.curso,
                j.dorsal,
                j.es_capitan
            FROM Jugadores j
            WHERE j.equipo_id = ?
            ORDER BY 
                CASE j.posicion
                    WHEN 'Portero' THEN 1
                    WHEN 'Defensa' THEN 2
                    WHEN 'Centrocampista' THEN 3
                    WHEN 'Delantero' THEN 4
                END,
                j.nombre,
                j.apellidos
        """, (equipo_id,))
        jugadores = [dict(row) for row in cursor.fetchall()]
        self.desconectar()
        return jugadores
        
    def obtener_todos_jugadores(self) -> List[Dict]:
        """
        Obtiene todos los jugadores registrados con información del equipo.
        
        Returns:
            Lista de jugadores con sus datos
        """
        self.conectar()
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                j.id,
                j.nombre,
                j.apellidos,
                j.fecha_nacimiento,
                j.curso,
                j.posicion,
                j.dorsal,
                j.es_capitan,
                j.equipo_id,
                e.nombre as equipo_nombre
            FROM Jugadores j
            LEFT JOIN Equipos e ON j.equipo_id = e.id
            ORDER BY j.nombre, j.apellidos
        """)
        jugadores = [dict(row) for row in cursor.fetchall()]
        self.desconectar()
        return jugadores
        
    def obtener_jugador_por_id(self, jugador_id: int) -> Optional[Dict]:
        """
        Obtiene un jugador por su ID.
        
        Args:
            jugador_id: ID del jugador
            
        Returns:
            Diccionario con datos del jugador o None
        """
        self.conectar()
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                j.*,
                e.nombre as equipo_nombre
            FROM Jugadores j
            LEFT JOIN Equipos e ON j.equipo_id = e.id
            WHERE j.id = ?
        """, (jugador_id,))
        jugador = cursor.fetchone()
        self.desconectar()
        return dict(jugador) if jugador else None
        
    def obtener_jugadores_sin_equipo(self) -> List[Dict]:
        """
        Obtiene todos los jugadores que no tienen equipo asignado.
        
        Returns:
            Lista de jugadores sin equipo
        """
        self.conectar()
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                id,
                nombre,
                apellidos,
                posicion,
                curso
            FROM Jugadores
            WHERE equipo_id IS NULL
            ORDER BY nombre, apellidos
        """)
        jugadores = [dict(row) for row in cursor.fetchall()]
        self.desconectar()
        return jugadores
        
    def asignar_jugador_a_equipo(self, jugador_id: int, equipo_id: Optional[int]):
        """
        Asigna un jugador a un equipo o lo desasigna.
        
        Args:
            jugador_id: ID del jugador
            equipo_id: ID del equipo (None para desasignar)
        """
        self.conectar()
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE Jugadores
            SET equipo_id = ?
            WHERE id = ?
        """, (equipo_id, jugador_id))
        self.conn.commit()
        self.desconectar()
        
    def obtener_arbitro_por_id(self, arbitro_id: int) -> Optional[Dict]:
        """
        Obtiene un árbitro por su ID.
        
        Args:
            arbitro_id: ID del árbitro
            
        Returns:
            Diccionario con datos del árbitro o None
        """
        self.conectar()
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM Arbitros WHERE id = ?", (arbitro_id,))
        arbitro = cursor.fetchone()
        self.desconectar()
        return dict(arbitro) if arbitro else None
        
    def actualizar_jugador(self, jugador_id: int, nombre: str, apellidos: str,
                          fecha_nacimiento: str, curso: str, equipo_id: Optional[int],
                          posicion: str, dorsal: int, es_capitan: bool,
                          tarjetas_amarillas: int = 0, tarjetas_rojas: int = 0,
                          goles: int = 0):
        """
        Actualiza los datos de un jugador.
        
        Args:
            jugador_id: ID del jugador
            nombre: Nombre del jugador
            apellidos: Apellidos del jugador
            fecha_nacimiento: Fecha de nacimiento
            curso: Curso del jugador
            equipo_id: ID del equipo (puede ser None)
            posicion: Posición del jugador
            dorsal: Número de dorsal
            es_capitan: Si es capitán del equipo
            tarjetas_amarillas: Tarjetas amarillas acumuladas
            tarjetas_rojas: Tarjetas rojas acumuladas
            goles: Goles marcados
        """
        self.conectar()
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE Jugadores
            SET nombre = ?, apellidos = ?, fecha_nacimiento = ?, curso = ?,
                equipo_id = ?, posicion = ?, dorsal = ?, es_capitan = ?,
                tarjetas_amarillas = ?, tarjetas_rojas = ?, goles = ?
            WHERE id = ?
        """, (nombre, apellidos, fecha_nacimiento, curso, equipo_id,
              posicion, dorsal, 1 if es_capitan else 0, 
              tarjetas_amarillas, tarjetas_rojas, goles, jugador_id))
        self.conn.commit()
        self.desconectar()
        
    def actualizar_arbitro(self, arbitro_id: int, nombre: str, apellidos: str,
                          fecha_nacimiento: str, experiencia: int, categoria: str):
        """
        Actualiza los datos de un árbitro.
        
        Args:
            arbitro_id: ID del árbitro
            nombre: Nombre del árbitro
            apellidos: Apellidos del árbitro
            fecha_nacimiento: Fecha de nacimiento
            experiencia: Años de experiencia
            categoria: Categoría del árbitro
        """
        self.conectar()
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE Arbitros
            SET nombre = ?, apellidos = ?, fecha_nacimiento = ?,
                experiencia = ?, categoria = ?
            WHERE id = ?
        """, (nombre, apellidos, fecha_nacimiento, experiencia, categoria, arbitro_id))
        self.conn.commit()
        self.desconectar()
        
    # ========== MÉTODOS DE TORNEO ==========
    
    def torneo_activo_existe(self) -> Optional[Dict]:
        """
        Verifica si existe un torneo activo.
        
        Returns:
            Diccionario con información del torneo activo o None
        """
        self.conectar()
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM Torneo 
            WHERE estado = 'activo' 
            ORDER BY fecha_inicio DESC 
            LIMIT 1
        """)
        torneo = cursor.fetchone()
        self.desconectar()
        return dict(torneo) if torneo else None
        
    def crear_torneo(self, nombre: str, num_equipos: int) -> int:
        """
        Crea un nuevo torneo.
        
        Args:
            nombre: Nombre del torneo
            num_equipos: Número de equipos (8, 16 o 32)
            
        Returns:
            ID del torneo creado
        """
        self.conectar()
        cursor = self.conn.cursor()
        fecha_inicio = datetime.now().strftime('%d/%m/%Y')
        
        cursor.execute("""
            INSERT INTO Torneo (nombre, num_equipos, estado, fecha_inicio)
            VALUES (?, ?, 'activo', ?)
        """, (nombre, num_equipos, fecha_inicio))
        
        torneo_id = cursor.lastrowid
        self.conn.commit()
        self.desconectar()
        return torneo_id
        
    def finalizar_torneo_manual(self, torneo_id: int):
        """
        Marca un torneo como finalizado manualmente.
        
        Args:
            torneo_id: ID del torneo a finalizar
        """
        self.conectar()
        cursor = self.conn.cursor()
        fecha_finalizacion = datetime.now().strftime('%d/%m/%Y')
        
        cursor.execute("""
            UPDATE Torneo 
            SET estado = 'finalizado', fecha_finalizacion = ?
            WHERE id = ?
        """, (fecha_finalizacion, torneo_id))
        
        self.conn.commit()
        self.desconectar()
        
    # ========== MÉTODOS DE PARTIDOS ==========
    
    def crear_partido(self, torneo_id: int, equipo_a_id: int, equipo_b_id: int,
                     fecha: str, hora: str, arbitro_id: Optional[int],
                     ronda: str, numero_partido: int) -> int:
        """
        Crea un nuevo partido.
        
        Args:
            torneo_id: ID del torneo
            equipo_a_id: ID del primer equipo
            equipo_b_id: ID del segundo equipo
            fecha: Fecha en formato DD/MM/YYYY
            hora: Hora en formato HH:MM
            arbitro_id: ID del árbitro (puede ser None)
            ronda: Nombre de la ronda (ej: 'octavos', 'cuartos', 'semifinal', 'final')
            numero_partido: Número del partido en la ronda
            
        Returns:
            ID del partido creado
        """
        self.conectar()
        cursor = self.conn.cursor()
        
        cursor.execute("""
            INSERT INTO Partidos (torneo_id, equipo_a_id, equipo_b_id, fecha, hora, 
                                 arbitro_id, ronda, numero_partido, estado)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'pendiente')
        """, (torneo_id, equipo_a_id, equipo_b_id, fecha, hora, arbitro_id, ronda, numero_partido))
        
        partido_id = cursor.lastrowid
        self.conn.commit()
        self.desconectar()
        return partido_id
        
    def eliminar_partido(self, partido_id: int):
        """
        Elimina un partido. CASCADE eliminará resultados y eventos asociados.
        
        Args:
            partido_id: ID del partido a eliminar
        """
        self.conectar()
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM Partidos WHERE id = ?", (partido_id,))
        self.conn.commit()
        self.desconectar()
        
    def obtener_partidos_por_torneo(self, torneo_id: int) -> List[Dict]:
        """
        Obtiene todos los partidos de un torneo.
        Incluye partidos con equipos pendientes (NULL).
        
        Args:
            torneo_id: ID del torneo
            
        Returns:
            Lista de partidos con información de equipos
        """
        self.conectar()
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT p.*, 
                   ea.nombre as equipo_a_nombre, ea.escudo_path as equipo_a_escudo,
                   eb.nombre as equipo_b_nombre, eb.escudo_path as equipo_b_escudo
            FROM Partidos p
            LEFT JOIN Equipos ea ON p.equipo_a_id = ea.id
            LEFT JOIN Equipos eb ON p.equipo_b_id = eb.id
            WHERE p.torneo_id = ?
            ORDER BY 
                CASE p.ronda
                    WHEN 'dieciseisavos' THEN 1
                    WHEN 'octavos' THEN 2
                    WHEN 'cuartos' THEN 3
                    WHEN 'semifinal' THEN 4
                    WHEN 'final' THEN 5
                    ELSE 6
                END,
                p.numero_partido
        """, (torneo_id,))
        partidos = [dict(row) for row in cursor.fetchall()]
        self.desconectar()
        return partidos
        
    def registrar_resultado(self, partido_id: int, goles_equipo_a: int, 
                           goles_equipo_b: int, ganador_id: int):
        """
        Registra o actualiza el resultado de un partido.
        Automáticamente avanza el ganador a la siguiente ronda del bracket.
        
        Args:
            partido_id: ID del partido
            goles_equipo_a: Goles del equipo A
            goles_equipo_b: Goles del equipo B
            ganador_id: ID del equipo ganador
        """
        try:
            self.conectar()
            cursor = self.conn.cursor()
            
            # Actualizar o insertar resultado
            cursor.execute("""
                INSERT OR REPLACE INTO Resultados (partido_id, goles_equipo_a, goles_equipo_b)
                VALUES (?, ?, ?)
            """, (partido_id, goles_equipo_a, goles_equipo_b))
            
            # Actualizar estado del partido
            cursor.execute("""
                UPDATE Partidos 
                SET estado = 'finalizado', ganador_id = ?
                WHERE id = ?
            """, (ganador_id, partido_id))
            
            self.conn.commit()
            self.desconectar()
            
            # Avanzar el ganador a la siguiente ronda automáticamente
            try:
                from Models.torneo_logic import TorneoLogic
                torneo_logic = TorneoLogic()
                torneo_logic.avanzar_ronda_bracket(partido_id, ganador_id)
            except Exception as e:
                print(f"⚠️ Error al avanzar ronda: {e}")
                import traceback
                traceback.print_exc()
        except Exception as e:
            if self.conn:
                self.conn.rollback()
            self.desconectar()
            raise e
            # No lanzar el error para que el resultado se guarde de todos modos
        
    def registrar_evento(self, partido_id: int, jugador_id: int, tipo_evento: str, minuto: Optional[int] = None):
        """
        Registra un evento en un partido (gol o tarjeta).
        
        Args:
            partido_id: ID del partido
            jugador_id: ID del jugador
            tipo_evento: 'gol', 'tarjeta_amarilla' o 'tarjeta_roja'
            minuto: Minuto del evento (opcional)
        """
        self.conectar()
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO Eventos (partido_id, jugador_id, tipo_evento, minuto)
            VALUES (?, ?, ?, ?)
        """, (partido_id, jugador_id, tipo_evento, minuto))
        self.conn.commit()
        self.desconectar()
        
    def obtener_resultado_partido(self, partido_id: int) -> Optional[Dict]:
        """
        Obtiene el resultado de un partido específico.
        
        Args:
            partido_id: ID del partido
            
        Returns:
            Diccionario con resultado o None si no existe
        """
        self.conectar()
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM Resultados WHERE partido_id = ?
        """, (partido_id,))
        resultado = cursor.fetchone()
        self.desconectar()
        return dict(resultado) if resultado else None
        
    def obtener_eventos_partido(self, partido_id: int) -> List[Dict]:
        """
        Obtiene todos los eventos de un partido.
        
        Args:
            partido_id: ID del partido
            
        Returns:
            Lista de eventos con información de jugadores
        """
        self.conectar()
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT e.*, p.nombre as jugador_nombre, j.posicion
            FROM Eventos e
            JOIN Jugadores j ON e.jugador_id = j.id
            JOIN Participantes p ON j.participante_id = p.id
            WHERE e.partido_id = ?
            ORDER BY e.minuto
        """, (partido_id,))
        eventos = [dict(row) for row in cursor.fetchall()]
        self.desconectar()
        return eventos
        
    def obtener_partido_por_id(self, partido_id: int) -> Optional[Dict]:
        """
        Obtiene un partido por su ID.
        Incluye partidos con equipos pendientes (NULL).
        
        Args:
            partido_id: ID del partido
            
        Returns:
            Diccionario con datos del partido o None
        """
        self.conectar()
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT p.*,
                   ea.nombre as equipo_a_nombre, ea.escudo_path as equipo_a_escudo,
                   eb.nombre as equipo_b_nombre, eb.escudo_path as equipo_b_escudo
            FROM Partidos p
            LEFT JOIN Equipos ea ON p.equipo_a_id = ea.id
            LEFT JOIN Equipos eb ON p.equipo_b_id = eb.id
            WHERE p.id = ?
        """, (partido_id,))
        partido = cursor.fetchone()
        self.desconectar()
        return dict(partido) if partido else None
        
    def actualizar_partido(self, partido_id: int, equipo_a_id: int, equipo_b_id: int,
                          fecha: str, hora: str, arbitro_id: Optional[int], ronda: str):
        """
        Actualiza los datos de un partido.
        
        Args:
            partido_id: ID del partido
            equipo_a_id: ID del primer equipo
            equipo_b_id: ID del segundo equipo
            fecha: Fecha en formato YYYY-MM-DD
            hora: Hora en formato HH:MM
            arbitro_id: ID del árbitro (puede ser None)
            ronda: Ronda del partido
        """
        self.conectar()
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE Partidos
            SET equipo_a_id = ?, equipo_b_id = ?, fecha = ?, hora = ?,
                arbitro_id = ?, ronda = ?
            WHERE id = ?
        """, (equipo_a_id, equipo_b_id, fecha, hora, arbitro_id, ronda, partido_id))
        self.conn.commit()
        self.desconectar()
        
    def obtener_partidos_por_ronda(self, torneo_id: int, ronda: str) -> List[Dict]:
        """
        Obtiene todos los partidos de una ronda específica.
        
        Args:
            torneo_id: ID del torneo
            ronda: Nombre de la ronda
            
        Returns:
            Lista de partidos de la ronda
        """
        self.conectar()
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT p.*, 
                   ea.nombre as equipo_a_nombre, ea.escudo_path as equipo_a_escudo,
                   eb.nombre as equipo_b_nombre, eb.escudo_path as equipo_b_escudo
            FROM Partidos p
            LEFT JOIN Equipos ea ON p.equipo_a_id = ea.id
            LEFT JOIN Equipos eb ON p.equipo_b_id = eb.id
            WHERE p.torneo_id = ? AND p.ronda = ?
            ORDER BY p.numero_partido
        """, (torneo_id, ronda))
        partidos = [dict(row) for row in cursor.fetchall()]
        self.desconectar()
        return partidos
        
    def eliminar_eventos_partido(self, partido_id: int):
        """
        Elimina todos los eventos de un partido.
        
        Args:
            partido_id: ID del partido
        """
        self.conectar()
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM Eventos WHERE partido_id = ?", (partido_id,))
        self.conn.commit()
        self.desconectar()
        
    def actualizar_estadisticas_jugadores_desde_eventos(self):
        """
        Actualiza las estadísticas de todos los jugadores basándose en los eventos registrados.
        Recalcula goles, tarjetas amarillas y tarjetas rojas desde la tabla Eventos.
        """
        self.conectar()
        cursor = self.conn.cursor()
        
        # Primero, resetear todas las estadísticas
        cursor.execute("""
            UPDATE Jugadores
            SET goles = 0, tarjetas_amarillas = 0, tarjetas_rojas = 0
        """)
        
        # Actualizar goles
        cursor.execute("""
            UPDATE Jugadores
            SET goles = (
                SELECT COUNT(*)
                FROM Eventos
                WHERE Eventos.jugador_id = Jugadores.id
                AND Eventos.tipo_evento = 'gol'
            )
        """)
        
        # Actualizar tarjetas amarillas
        cursor.execute("""
            UPDATE Jugadores
            SET tarjetas_amarillas = (
                SELECT COUNT(*)
                FROM Eventos
                WHERE Eventos.jugador_id = Jugadores.id
                AND Eventos.tipo_evento = 'tarjeta_amarilla'
            )
        """)
        
        # Actualizar tarjetas rojas
        cursor.execute("""
            UPDATE Jugadores
            SET tarjetas_rojas = (
                SELECT COUNT(*)
                FROM Eventos
                WHERE Eventos.jugador_id = Jugadores.id
                AND Eventos.tipo_evento = 'tarjeta_roja'
            )
        """)
        
        self.conn.commit()
        self.desconectar()
        
    def actualizar_estado_partido(self, partido_id: int, nuevo_estado: str) -> bool:
        """
        Actualiza el estado de un partido.
        
        Args:
            partido_id: ID del partido
            nuevo_estado: Nuevo estado ('pendiente', 'en_curso', 'finalizado', 'cancelado')
            
        Returns:
            bool: True si se actualizó correctamente, False en caso contrario
        """
        estados_validos = ['pendiente', 'en_curso', 'finalizado', 'cancelado']
        if nuevo_estado not in estados_validos:
            return False
            
        self.conectar()
        cursor = self.conn.cursor()
        
        cursor.execute("""
            UPDATE Partidos
            SET estado = ?
            WHERE id = ?
        """, (nuevo_estado, partido_id))
        
        self.conn.commit()
        exito = cursor.rowcount > 0
        self.desconectar()
        
        return exito
        
    def migrar_estados_partidos(self):
        """
        Migración para actualizar la tabla Partidos si existe con el esquema antiguo.
        Recrea la tabla con los nuevos estados.
        """
        self.conectar()
        cursor = self.conn.cursor()
        
        try:
            cursor.execute("""
                SELECT sql FROM sqlite_master
                WHERE type = 'table' AND name = 'Partidos'
            """)
            tabla_sql = cursor.fetchone()
            if not tabla_sql or not tabla_sql[0]:
                return
            definicion = tabla_sql[0].lower()
            estados_requeridos = ['pendiente', 'en_curso', 'finalizado', 'cancelado']
            if all(estado in definicion for estado in estados_requeridos):
                return
            cursor.execute("""
                CREATE TABLE Partidos_estado_tmp (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    torneo_id INTEGER NOT NULL,
                    equipo_a_id INTEGER,
                    equipo_b_id INTEGER,
                    fecha TEXT,
                    hora TEXT,
                    arbitro_id INTEGER,
                    ronda TEXT NOT NULL,
                    numero_partido INTEGER NOT NULL,
                    estado TEXT NOT NULL CHECK(estado IN ('pendiente', 'en_curso', 'finalizado', 'cancelado')) DEFAULT 'pendiente',
                    ganador_id INTEGER,
                    FOREIGN KEY (torneo_id) REFERENCES Torneo(id) ON DELETE CASCADE,
                    FOREIGN KEY (equipo_a_id) REFERENCES Equipos(id) ON DELETE CASCADE,
                    FOREIGN KEY (equipo_b_id) REFERENCES Equipos(id) ON DELETE CASCADE,
                    FOREIGN KEY (arbitro_id) REFERENCES Arbitros(id) ON DELETE SET NULL,
                    FOREIGN KEY (ganador_id) REFERENCES Equipos(id) ON DELETE SET NULL
                )
            """)
            cursor.execute("""
                INSERT INTO Partidos_estado_tmp (
                    id, torneo_id, equipo_a_id, equipo_b_id, fecha, hora,
                    arbitro_id, ronda, numero_partido, estado, ganador_id
                )
                SELECT
                    id, torneo_id, equipo_a_id, equipo_b_id, fecha, hora,
                    arbitro_id, ronda, numero_partido,
                    CASE estado
                        WHEN 'pendiente' THEN 'pendiente'
                        WHEN 'en_curso' THEN 'en_curso'
                        WHEN 'finalizado' THEN 'finalizado'
                        WHEN 'cancelado' THEN 'cancelado'
                        ELSE 'pendiente'
                    END,
                    ganador_id
                FROM Partidos
            """)
            cursor.execute("DROP TABLE Partidos")
            cursor.execute("ALTER TABLE Partidos_estado_tmp RENAME TO Partidos")
            self.conn.commit()
            print("✅ Migración completada: Partidos admite todos los estados")
        except Exception as e:
            print(f"⚠️ Error en migración de estados de partidos: {e}")
            self.conn.rollback()
            raise
        finally:
            self.desconectar()
        
    def migrar_partidos_nullable_equipos(self):
        """
        Migración para permitir que equipo_a_id y equipo_b_id sean NULL.
        Esto permite crear partidos de rondas futuras antes de que se conozcan los equipos.
        """
        self.conectar()
        cursor = self.conn.cursor()
        
        try:
            # Verificar si necesita migración consultando la estructura actual
            cursor.execute("PRAGMA table_info(Partidos)")
            columnas = {col[1]: col for col in cursor.fetchall()}
            
            # Verificar si equipo_a_id o equipo_b_id son NOT NULL
            equipo_a_info = columnas.get('equipo_a_id')
            equipo_b_info = columnas.get('equipo_b_id')
            
            # Si ambas columnas ya permiten NULL (notnull=0), no migrar
            if equipo_a_info and equipo_b_info:
                if equipo_a_info[3] == 0 and equipo_b_info[3] == 0:
                    self.desconectar()
                    return
            
            # Crear tabla temporal con nueva estructura (equipos pueden ser NULL)
            cursor.execute("""
                CREATE TABLE Partidos_nullable (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    torneo_id INTEGER NOT NULL,
                    equipo_a_id INTEGER,
                    equipo_b_id INTEGER,
                    fecha TEXT,
                    hora TEXT,
                    arbitro_id INTEGER,
                    ronda TEXT NOT NULL,
                    numero_partido INTEGER NOT NULL,
                    estado TEXT NOT NULL CHECK(estado IN ('pendiente', 'en_curso', 'finalizado', 'cancelado')) DEFAULT 'pendiente',
                    ganador_id INTEGER,
                    FOREIGN KEY (torneo_id) REFERENCES Torneo(id) ON DELETE CASCADE,
                    FOREIGN KEY (equipo_a_id) REFERENCES Equipos(id) ON DELETE CASCADE,
                    FOREIGN KEY (equipo_b_id) REFERENCES Equipos(id) ON DELETE CASCADE,
                    FOREIGN KEY (arbitro_id) REFERENCES Arbitros(id) ON DELETE SET NULL,
                    FOREIGN KEY (ganador_id) REFERENCES Equipos(id) ON DELETE SET NULL
                )
            """)
            
            # Copiar datos existentes
            cursor.execute("""
                INSERT INTO Partidos_nullable 
                SELECT * FROM Partidos
            """)
            
            # Eliminar tabla antigua
            cursor.execute("DROP TABLE Partidos")
            
            # Renombrar tabla nueva
            cursor.execute("ALTER TABLE Partidos_nullable RENAME TO Partidos")
            
            self.conn.commit()
            print("✅ Migración completada: Partidos ahora permite equipos NULL para rondas futuras")
            
        except Exception as e:
            print(f"⚠️ Error en migración de partidos: {e}")
            self.conn.rollback()
        
        self.desconectar()
