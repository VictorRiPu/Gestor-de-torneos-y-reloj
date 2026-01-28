"""
Módulo de lógica de torneo.
Gestiona validaciones, generación de emparejamientos y progresión de brackets.
"""

import random
from typing import List, Dict, Tuple, Optional
from Models.database import DatabaseManager


class TorneoLogic:
    """
    Clase que maneja la lógica de negocio del torneo de fútbol.
    Incluye validaciones, generación de brackets y progresión del torneo.
    """
    
    def __init__(self):
        """Inicializa la lógica del torneo con el gestor de BD."""
        self.db = DatabaseManager()
        
    def validar_equipos_para_torneo(self, equipos_ids: List[int]) -> Tuple[bool, Dict[str, int]]:
        """
        Valida que los equipos cumplan requisitos para iniciar torneo.
        - Cantidad: 8, 16 o 32 equipos
        - Cada equipo debe tener mínimo 7 jugadores
        
        Args:
            equipos_ids: Lista de IDs de equipos participantes
            
        Returns:
            Tupla (es_valido: bool, equipos_invalidos: dict)
            equipos_invalidos = {nombre_equipo: jugadores_faltantes}
        """
        num_equipos = len(equipos_ids)
        equipos_invalidos = {}
        
        # Validar cantidad de equipos
        if num_equipos not in [8, 16, 32]:
            return False, {"error": f"Debe haber 8, 16 o 32 equipos. Actualmente hay {num_equipos}"}
            
        # Validar jugadores por equipo (mínimo 7)
        for equipo_id in equipos_ids:
            equipo = self.db.obtener_equipo_por_id(equipo_id)
            num_jugadores = self.db.contar_jugadores_por_equipo(equipo_id)
            
            if num_jugadores < 7:
                equipos_invalidos[equipo['nombre']] = 7 - num_jugadores
                
        if equipos_invalidos:
            return False, equipos_invalidos
            
        return True, {}
        
    def generar_emparejamientos_aleatorios(self, equipos_ids: List[int]) -> Dict[str, List[Tuple[int, int]]]:
        """
        Genera emparejamientos aleatorios para el torneo.
        Crea la estructura completa de brackets según número de equipos.
        
        Args:
            equipos_ids: Lista de IDs de equipos (ya validados)
            
        Returns:
            Diccionario con estructura {ronda: [(equipo_a, equipo_b), ...]}
            Ejemplo: {'octavos': [(1,2), (3,4)], 'cuartos': [...]}
        """
        num_equipos = len(equipos_ids)
        
        # Mezclar equipos aleatoriamente
        equipos_shuffled = equipos_ids.copy()
        random.shuffle(equipos_shuffled)
        
        # Determinar rondas según número de equipos
        if num_equipos == 8:
            rondas = ['cuartos', 'semifinal', 'final']
        elif num_equipos == 16:
            rondas = ['octavos', 'cuartos', 'semifinal', 'final']
        else:  # 32 equipos
            rondas = ['dieciseisavos', 'octavos', 'cuartos', 'semifinal', 'final']
            
        # Crear emparejamientos para la primera ronda
        brackets = {}
        primera_ronda = rondas[0]
        emparejamientos_primera = []
        
        for i in range(0, num_equipos, 2):
            emparejamientos_primera.append((equipos_shuffled[i], equipos_shuffled[i+1]))
            
        brackets[primera_ronda] = emparejamientos_primera
        
        # Crear estructura vacía para rondas siguientes
        # Se llenarán automáticamente conforme avance el torneo
        for ronda in rondas[1:]:
            brackets[ronda] = []
            
        return brackets
        
    def iniciar_nuevo_torneo(self, nombre: str, equipos_ids: List[int]) -> Tuple[bool, Optional[str]]:
        """
        Inicia un nuevo torneo con validaciones completas.
        
        Args:
            nombre: Nombre del torneo
            equipos_ids: Lista de IDs de equipos participantes
            
        Returns:
            Tupla (exito: bool, mensaje_error: str)
        """
        # Verificar que no haya torneo activo
        torneo_activo = self.db.torneo_activo_existe()
        if torneo_activo:
            return False, "Ya existe un torneo activo. Finalízalo antes de crear uno nuevo."
            
        # Validar equipos
        valido, equipos_invalidos = self.validar_equipos_para_torneo(equipos_ids)
        
        if not valido:
            # Construir mensaje de error detallado
            if "error" in equipos_invalidos:
                return False, equipos_invalidos["error"]
            else:
                mensaje = "Los siguientes equipos necesitan más jugadores:\n"
                for equipo, faltantes in equipos_invalidos.items():
                    mensaje += f"- {equipo}: faltan {faltantes} jugador(es)\n"
                return False, mensaje
                
        # Crear torneo
        num_equipos = len(equipos_ids)
        torneo_id = self.db.crear_torneo(nombre, num_equipos)
        
        # Generar emparejamientos
        brackets = self.generar_emparejamientos_aleatorios(equipos_ids)
        
        # Crear partidos de la primera ronda (sin fecha/hora asignada aún)
        primera_ronda = list(brackets.keys())[0]
        numero_partido = 1
        
        for equipo_a_id, equipo_b_id in brackets[primera_ronda]:
            self.db.crear_partido(
                torneo_id=torneo_id,
                equipo_a_id=equipo_a_id,
                equipo_b_id=equipo_b_id,
                fecha="",  # Se asignará desde el calendario
                hora="",
                arbitro_id=None,
                ronda=primera_ronda,
                numero_partido=numero_partido
            )
            numero_partido += 1
            
        return True, None
        
    def avanzar_ronda_bracket(self, partido_id: int, ganador_id: int) -> bool:
        """
        Avanza el bracket al registrar resultado de un partido.
        Crea automáticamente el partido de la siguiente ronda.
        
        Args:
            partido_id: ID del partido finalizado
            ganador_id: ID del equipo ganador
            
        Returns:
            True si se avanzó correctamente, False si es la final
        """
        try:
            self.db.conectar()
            cursor = self.db.conn.cursor()
            
            # Obtener información del partido
            cursor.execute("""
                SELECT torneo_id, ronda, numero_partido
                FROM Partidos
                WHERE id = ?
            """, (partido_id,))
            
            partido_info = cursor.fetchone()
            if not partido_info:
                print(f"❌ Partido {partido_id} no encontrado")
                self.db.desconectar()
                return False
                
            torneo_id = partido_info['torneo_id']
            ronda_actual = partido_info['ronda']
            numero_partido_actual = partido_info['numero_partido']
            
            print(f"📊 Avanzando ronda: {ronda_actual} -> partido #{numero_partido_actual}")
            
            # Definir secuencia de rondas (normalizar a minúsculas)
            secuencia_rondas = ['dieciseisavos', 'octavos', 'cuartos', 'semifinal', 'final']
            ronda_actual_lower = ronda_actual.lower()
            
            # Si es la final, no hay siguiente ronda
            if ronda_actual_lower == 'final':
                print("🏆 Es la final, no hay siguiente ronda")
                self.db.desconectar()
                return False
            
            # Verificar que la ronda esté en la lista
            if ronda_actual_lower not in secuencia_rondas:
                print(f"⚠️ Ronda '{ronda_actual}' no reconocida")
                self.db.desconectar()
                return False
                
            # Determinar siguiente ronda
            idx_actual = secuencia_rondas.index(ronda_actual_lower)
            siguiente_ronda = secuencia_rondas[idx_actual + 1]
            
            # Calcular el número de partido en la siguiente ronda
            # Los partidos se emparejan: (1,2)->1, (3,4)->2, etc.
            numero_partido_siguiente = (numero_partido_actual + 1) // 2
            
            print(f"➡️ Siguiente ronda: {siguiente_ronda}, partido #{numero_partido_siguiente}")
            
            # Verificar si ya existe el partido en la siguiente ronda
            cursor.execute("""
                SELECT id, equipo_a_id, equipo_b_id
                FROM Partidos
                WHERE torneo_id = ? AND ronda = ? AND numero_partido = ?
            """, (torneo_id, siguiente_ronda, numero_partido_siguiente))
            
            partido_siguiente = cursor.fetchone()
            
            if partido_siguiente:
                # Ya existe el partido, actualizarlo con el ganador
                print(f"✏️ Actualizando partido existente {partido_siguiente['id']}")
                if partido_siguiente['equipo_a_id'] is None:
                    # Actualizar equipo_a
                    cursor.execute("""
                        UPDATE Partidos
                        SET equipo_a_id = ?
                        WHERE id = ?
                    """, (ganador_id, partido_siguiente['id']))
                    print(f"✅ Equipo {ganador_id} asignado como equipo_a")
                elif partido_siguiente['equipo_b_id'] is None:
                    # Actualizar equipo_b
                    cursor.execute("""
                        UPDATE Partidos
                        SET equipo_b_id = ?
                        WHERE id = ?
                    """, (ganador_id, partido_siguiente['id']))
                    print(f"✅ Equipo {ganador_id} asignado como equipo_b")
                else:
                    print("⚠️ El partido ya tiene ambos equipos asignados")
            else:
                # Crear nuevo partido para la siguiente ronda
                # Si es impar, va como equipo_a; si es par, va como equipo_b
                if numero_partido_actual % 2 == 1:
                    equipo_a = ganador_id
                    equipo_b = None
                    print(f"➕ Creando nuevo partido con equipo_a={ganador_id}")
                else:
                    equipo_a = None
                    equipo_b = ganador_id
                    print(f"➕ Creando nuevo partido con equipo_b={ganador_id}")
                    
                # Insertar partido directamente (sin llamar a crear_partido para evitar conflicto de conexión)
                cursor.execute("""
                    INSERT INTO Partidos (torneo_id, equipo_a_id, equipo_b_id, fecha, hora, 
                                         arbitro_id, ronda, numero_partido, estado)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'pendiente')
                """, (torneo_id, equipo_a, equipo_b, "", "", None, siguiente_ronda, numero_partido_siguiente))
                print("✅ Partido creado exitosamente")
                
            self.db.conn.commit()
            self.db.desconectar()
            print("✅ Avance de ronda completado")
            return True
            
        except Exception as e:
            print(f"❌ Error en avanzar_ronda_bracket: {e}")
            import traceback
            traceback.print_exc()
            if self.db.conn:
                self.db.conn.rollback()
                self.db.desconectar()
            return False
        
    def obtener_arbol_bracket(self, torneo_id: int) -> Dict[str, List[Dict]]:
        """
        Obtiene la estructura completa del bracket del torneo.
        Incluye información de equipos, logos y estados.
        
        Args:
            torneo_id: ID del torneo
            
        Returns:
            Diccionario con estructura del bracket por rondas
            Ejemplo: {
                'cuartos': [
                    {
                        'partido_id': 1,
                        'equipo_a': {'id': 1, 'nombre': 'X', 'escudo': 'path'},
                        'equipo_b': {'id': 2, 'nombre': 'Y', 'escudo': 'path'},
                        'estado': 'pendiente',
                        'ganador_id': None
                    },
                    ...
                ]
            }
        """
        partidos = self.db.obtener_partidos_por_torneo(torneo_id)
        
        # Agrupar partidos por ronda
        bracket = {}
        
        for partido in partidos:
            ronda = partido['ronda']
            
            if ronda not in bracket:
                bracket[ronda] = []
                
            # Construir información del partido
            info_partido = {
                'partido_id': partido['id'],
                'numero_partido': partido['numero_partido'],
                'equipo_a': {
                    'id': partido['equipo_a_id'],
                    'nombre': partido['equipo_a_nombre'],
                    'escudo': partido['equipo_a_escudo']
                } if partido['equipo_a_id'] else None,
                'equipo_b': {
                    'id': partido['equipo_b_id'],
                    'nombre': partido['equipo_b_nombre'],
                    'escudo': partido['equipo_b_escudo']
                } if partido['equipo_b_id'] else None,
                'fecha': partido['fecha'],
                'hora': partido['hora'],
                'estado': partido['estado'],
                'ganador_id': partido['ganador_id']
            }
            
            bracket[ronda].append(info_partido)
            
        # Ordenar rondas en secuencia lógica
        orden_rondas = ['dieciseisavos', 'octavos', 'cuartos', 'semifinal', 'final']
        bracket_ordenado = {}
        
        for ronda in orden_rondas:
            if ronda in bracket:
                # Ordenar partidos por número dentro de cada ronda
                bracket_ordenado[ronda] = sorted(bracket[ronda], key=lambda x: x['numero_partido'])
                
        return bracket_ordenado
        
    def finalizar_torneo_manual(self, torneo_id: int):
        """
        Finaliza un torneo manualmente.
        
        Args:
            torneo_id: ID del torneo a finalizar
        """
        self.db.finalizar_torneo_manual(torneo_id)
        
    def obtener_ganador_torneo(self, torneo_id: int) -> Optional[Dict]:
        """
        Obtiene el equipo ganador del torneo (ganador de la final).
        
        Args:
            torneo_id: ID del torneo
            
        Returns:
            Diccionario con información del equipo ganador o None
        """
        self.db.conectar()
        cursor = self.db.conn.cursor()
        
        # Buscar el partido final
        cursor.execute("""
            SELECT ganador_id
            FROM Partidos
            WHERE torneo_id = ? AND ronda = 'final' AND estado = 'finalizado'
        """, (torneo_id,))
        
        resultado = cursor.fetchone()
        self.db.desconectar()
        
        if resultado and resultado['ganador_id']:
            return self.db.obtener_equipo_por_id(resultado['ganador_id'])
            
        return None
        
    def verificar_torneo_completo(self, torneo_id: int) -> bool:
        """
        Verifica si todos los partidos del torneo han sido finalizados.
        
        Args:
            torneo_id: ID del torneo
            
        Returns:
            True si todos los partidos están finalizados
        """
        self.db.conectar()
        cursor = self.db.conn.cursor()
        
        cursor.execute("""
            SELECT COUNT(*) as pendientes
            FROM Partidos
            WHERE torneo_id = ? AND estado = 'pendiente'
        """, (torneo_id,))
        
        resultado = cursor.fetchone()
        self.db.desconectar()
        
        return resultado['pendientes'] == 0
        
    def obtener_estadisticas_torneo(self, torneo_id: int) -> Dict:
        """
        Obtiene estadísticas generales del torneo.
        
        Args:
            torneo_id: ID del torneo
            
        Returns:
            Diccionario con estadísticas (partidos jugados, goles totales, etc.)
        """
        self.db.conectar()
        cursor = self.db.conn.cursor()
        
        # Partidos jugados
        cursor.execute("""
            SELECT COUNT(*) as total
            FROM Partidos
            WHERE torneo_id = ? AND estado = 'finalizado'
        """, (torneo_id,))
        partidos_jugados = cursor.fetchone()['total']
        
        # Goles totales
        cursor.execute("""
            SELECT SUM(r.goles_equipo_a + r.goles_equipo_b) as total_goles
            FROM Resultados r
            JOIN Partidos p ON r.partido_id = p.id
            WHERE p.torneo_id = ?
        """, (torneo_id,))
        total_goles = cursor.fetchone()['total_goles'] or 0
        
        # Tarjetas amarillas
        cursor.execute("""
            SELECT COUNT(*) as total
            FROM Eventos e
            JOIN Partidos p ON e.partido_id = p.id
            WHERE p.torneo_id = ? AND e.tipo_evento = 'tarjeta_amarilla'
        """, (torneo_id,))
        tarjetas_amarillas = cursor.fetchone()['total']
        
        # Tarjetas rojas
        cursor.execute("""
            SELECT COUNT(*) as total
            FROM Eventos e
            JOIN Partidos p ON e.partido_id = p.id
            WHERE p.torneo_id = ? AND e.tipo_evento = 'tarjeta_roja'
        """, (torneo_id,))
        tarjetas_rojas = cursor.fetchone()['total']
        
        self.db.desconectar()
        
        return {
            'partidos_jugados': partidos_jugados,
            'total_goles': total_goles,
            'tarjetas_amarillas': tarjetas_amarillas,
            'tarjetas_rojas': tarjetas_rojas
        }
