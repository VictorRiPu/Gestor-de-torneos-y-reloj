"""
Controlador para la pantalla de clasificación y brackets.
Gestiona el cuadro de eliminatorias del torneo con visualización gráfica.
"""

from PySide6.QtWidgets import (QWidget, QPushButton, QLabel,
                               QGraphicsView, QGraphicsScene, QGraphicsRectItem,
                               QGraphicsTextItem, QGraphicsLineItem)
from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPen, QBrush, QColor, QFont, QPainter

from Models.database import DatabaseManager


class ClasificacionController:
    """Controlador para visualización de brackets y clasificación."""
    
    def __init__(self, widget: QWidget, main_controller):
        """
        Inicializa el controlador.
        
        Args:
            widget: Widget de la vista de clasificación
            main_controller: Controlador principal para navegación
        """
        self.widget = widget
        self.main_controller = main_controller
        self.db = DatabaseManager()
        
        # Obtener widgets
        self._obtener_widgets()
        
        # Crear escena para el bracket
        self.scene = QGraphicsScene()
        self.scene.setBackgroundBrush(QBrush(QColor(255, 255, 255)))  # Fondo blanco
        
        if self.graphics_view:
            self.graphics_view.setScene(self.scene)
            self.graphics_view.setRenderHint(QPainter.Antialiasing)
            self.graphics_view.setStyleSheet("background: white; border: 1px solid #ccc;")
        
        # Conectar señales
        self._conectar_senales()
        
        # Cargar brackets al inicio
        self.cargar_brackets()
        
    def _obtener_widgets(self):
        """Obtiene referencias a los widgets de la UI."""
        self.btn_volver = self.widget.findChild(QPushButton, "btnVolver")
        self.graphics_view = self.widget.findChild(QGraphicsView, "graphicsViewBrackets")
        self.lbl_estadisticas = self.widget.findChild(QLabel, "lblEstadisticas")
        
    def _conectar_senales(self):
        """Conecta las señales de los widgets."""
        if self.btn_volver:
            self.btn_volver.clicked.connect(self.main_controller.volver_a_principal)
                    
    def cargar_brackets(self):
        """Carga y muestra todos los brackets del torneo en visualización gráfica."""
        try:
            # Verificar torneo activo
            torneo = self.db.torneo_activo_existe()
            if not torneo:
                if self.lbl_estadisticas:
                    self.lbl_estadisticas.setText("No hay torneo activo")
                return
                
            torneo_id = torneo['id']
            
            # Limpiar escena
            self.scene.clear()
            
            # Obtener todas las rondas del torneo
            rondas_data = self._obtener_datos_rondas(torneo_id)
            
            if not rondas_data:
                if self.lbl_estadisticas:
                    self.lbl_estadisticas.setText("No hay partidos en el torneo aún")
                return
            
            # Dibujar bracket
            self._dibujar_bracket(rondas_data)
            
            # Actualizar estadísticas
            self._actualizar_estadisticas(torneo, rondas_data)
        except Exception as e:
            print(f"❌ Error al cargar brackets: {e}")
            import traceback
            traceback.print_exc()
        
    def _obtener_datos_rondas(self, torneo_id: int):
        """
        Obtiene los datos de todas las rondas del torneo organizados.
        
        Returns:
            Dict con estructura {ronda: [partidos]}
        """
        # Orden de todas las posibles rondas
        rondas_orden = ['dieciseisavos', 'octavos', 'cuartos', 'semifinal', 'final']
        rondas_data = {}
        
        # Intentar obtener partidos de cada ronda, solo agregar las que tengan partidos
        for ronda in rondas_orden:
            partidos = self.db.obtener_partidos_por_ronda(torneo_id, ronda)
            if partidos:  # Solo agregar si hay partidos en esta ronda
                rondas_data[ronda] = partidos
                
        return rondas_data
        
    def _dibujar_bracket(self, rondas_data):
        """
        Dibuja el bracket completo en la escena gráfica.
        
        Args:
            rondas_data: Diccionario con datos de rondas
        """
        if not rondas_data:
            return
            
        # Cargar todos los resultados de una vez para evitar múltiples conexiones
        resultados_cache = {}
        for partidos in rondas_data.values():
            for partido in partidos:
                resultado = self.db.obtener_resultado_partido(partido['id'])
                if resultado:
                    resultados_cache[partido['id']] = resultado
        
        # Configuración de diseño
        partido_width = 200
        partido_height = 80
        espacio_vertical = 30
        espacio_horizontal = 100
        margen_inicial = 50
        
        # Determinar número de rondas y altura total
        num_rondas = len(rondas_data)
        rondas_list = list(rondas_data.keys())
        
        # Calcular altura inicial basada en la primera ronda
        primera_ronda = rondas_list[0]
        num_partidos_primera = len(rondas_data[primera_ronda])
        
        # Dibujar cada ronda
        x_actual = margen_inicial
        y_base = margen_inicial
        
        for idx_ronda, ronda_nombre in enumerate(rondas_list):
            partidos = rondas_data[ronda_nombre]
            
            # Calcular espaciado vertical para esta ronda
            multiplicador = 2 ** idx_ronda
            espacio_entre_partidos = (partido_height + espacio_vertical) * multiplicador
            
            # Título de la ronda
            self._dibujar_titulo_ronda(ronda_nombre.capitalize(), x_actual, y_base - 30, partido_width)
            
            # Dibujar partidos de esta ronda
            for idx_partido, partido in enumerate(partidos):
                y_pos = y_base + (idx_partido * espacio_entre_partidos)
                
                # Dibujar el partido (pasar resultado desde cache)
                resultado = resultados_cache.get(partido['id'])
                self._dibujar_partido(
                    partido, 
                    resultado,
                    x_actual, 
                    y_pos, 
                    partido_width, 
                    partido_height
                )
                
                # Dibujar líneas conectoras a la siguiente ronda
                if idx_ronda < num_rondas - 1:
                    siguiente_y = y_base + ((idx_partido // 2) * espacio_entre_partidos * 2) + (espacio_entre_partidos)
                    self._dibujar_conector(
                        x_actual + partido_width,
                        y_pos + partido_height // 2,
                        x_actual + partido_width + espacio_horizontal,
                        siguiente_y + partido_height // 2 - espacio_entre_partidos // 2,
                        idx_partido % 2 == 0
                    )
            
            # Avanzar a la siguiente columna
            x_actual += partido_width + espacio_horizontal
            y_base += espacio_entre_partidos // 2
        
        # Ajustar tamaño de la escena
        self.scene.setSceneRect(self.scene.itemsBoundingRect())
        
    def _dibujar_titulo_ronda(self, nombre_ronda: str, x: float, y: float, width: float):
        """Dibuja el título de una ronda."""
        texto = QGraphicsTextItem(nombre_ronda.upper())
        font = QFont("Arial", 14, QFont.Bold)
        texto.setFont(font)
        texto.setDefaultTextColor(QColor(0, 0, 0))  # Negro
        
        # Centrar texto
        texto_width = texto.boundingRect().width()
        texto.setPos(x + (width - texto_width) / 2, y)
        
        self.scene.addItem(texto)
        
    def _dibujar_partido(self, partido, resultado, x: float, y: float, width: float, height: float):
        """
        Dibuja un partido en el bracket.
        
        Args:
            partido: Datos del partido
            resultado: Resultado del partido (pre-cargado)
            x, y: Posición
            width, height: Dimensiones
        """
        # Determinar estado y colores
        estado = partido.get('estado', 'pendiente')
        tiene_equipos = partido.get('equipo_a_id') and partido.get('equipo_b_id')
        
        if not tiene_equipos:
            # Partido pendiente de definir equipos
            color_fondo = QColor(245, 245, 245)
            color_borde = QColor(200, 200, 200)
        elif estado == 'finalizado':
            color_fondo = QColor(200, 230, 201)  # Verde claro
            color_borde = QColor(76, 175, 80)
        elif estado == 'en_curso':
            color_fondo = QColor(255, 224, 178)  # Naranja claro
            color_borde = QColor(255, 152, 0)
        else:  # pendiente
            color_fondo = QColor(255, 255, 255)
            color_borde = QColor(150, 150, 150)
        
        # Dibujar rectángulo del partido
        rect = QGraphicsRectItem(x, y, width, height)
        rect.setBrush(QBrush(color_fondo))
        rect.setPen(QPen(color_borde, 2))
        self.scene.addItem(rect)
        
        # Usar resultado pre-cargado
        ganador_id = partido.get('ganador_id')
        
        # Nombres y goles
        equipo_a = partido.get('equipo_a_nombre', 'Por definir')
        equipo_b = partido.get('equipo_b_nombre', 'Por definir')
        
        goles_a = resultado['goles_equipo_a'] if resultado else '-'
        goles_b = resultado['goles_equipo_b'] if resultado else '-'
        
        # Dibujar equipo A
        self._dibujar_equipo(
            equipo_a, goles_a,
            x + 10, y + 15,
            width - 20,
            es_ganador=(ganador_id == partido.get('equipo_a_id')) if ganador_id else False
        )
        
        # Línea divisoria
        linea = self.scene.addLine(x + 10, y + height/2, x + width - 10, y + height/2,
                                    QPen(color_borde, 1))
        
        # Dibujar equipo B
        self._dibujar_equipo(
            equipo_b, goles_b,
            x + 10, y + height/2 + 10,
            width - 20,
            es_ganador=(ganador_id == partido.get('equipo_b_id')) if ganador_id else False
        )
        
    def _dibujar_equipo(self, nombre: str, goles, x: float, y: float, width: float, es_ganador: bool):
        """Dibuja la información de un equipo en un partido."""
        # Formatear texto
        if goles != '-':
            texto = f"{nombre}  [{goles}]"
        else:
            texto = nombre
            
        item_texto = QGraphicsTextItem(texto)
        item_texto.setPos(x, y)
        
        # Estilo según si es ganador - SIEMPRE TEXTO NEGRO
        font = QFont("Arial", 10)
        if es_ganador:
            font.setBold(True)
            item_texto.setDefaultTextColor(QColor(0, 0, 0))  # Negro
        else:
            item_texto.setDefaultTextColor(QColor(0, 0, 0))  # Negro
            
        item_texto.setFont(font)
        
        # Truncar nombre si es muy largo
        if item_texto.boundingRect().width() > width:
            nombre_corto = nombre[:12] + "..."
            if goles != '-':
                texto_truncado = f"{nombre_corto} [{goles}]"
            else:
                texto_truncado = nombre_corto
            item_texto.setPlainText(texto_truncado)
        
        self.scene.addItem(item_texto)
        
    def _dibujar_conector(self, x1: float, y1: float, x2: float, y2: float, es_superior: bool):
        """
        Dibuja líneas conectoras entre partidos.
        
        Args:
            x1, y1: Punto inicial (salida del partido)
            x2, y2: Punto final (entrada del siguiente partido)
            es_superior: True si es el partido superior del par
        """
        color_linea = QColor(180, 180, 180)
        pen = QPen(color_linea, 2)
        
        # Punto medio horizontal
        x_medio = (x1 + x2) / 2
        
        # Línea horizontal desde el partido
        self.scene.addLine(x1, y1, x_medio, y1, pen)
        
        # Línea vertical
        self.scene.addLine(x_medio, y1, x_medio, y2, pen)
        
        # Línea horizontal hacia el siguiente partido
        self.scene.addLine(x_medio, y2, x2, y2, pen)
        
    def _actualizar_estadisticas(self, torneo, rondas_data):
        """Actualiza el label de estadísticas con información del torneo."""
        if not self.lbl_estadisticas:
            return
            
        total_partidos = sum(len(partidos) for partidos in rondas_data.values())
        partidos_finalizados = 0
        partidos_pendientes = 0
        
        for partidos in rondas_data.values():
            for partido in partidos:
                estado = partido.get('estado', 'pendiente')
                if estado == 'finalizado':
                    partidos_finalizados += 1
                elif estado == 'pendiente' and partido.get('equipo_a_id') and partido.get('equipo_b_id'):
                    partidos_pendientes += 1
        
        # Buscar campeón
        campeon = None
        if 'final' in rondas_data:
            partidos_final = rondas_data['final']
            if partidos_final:
                partido_final = partidos_final[0]
                if partido_final.get('estado') == 'finalizado' and partido_final.get('ganador_id'):
                    if partido_final['ganador_id'] == partido_final.get('equipo_a_id'):
                        campeon = partido_final.get('equipo_a_nombre')
                    else:
                        campeon = partido_final.get('equipo_b_nombre')
        
        # Construir mensaje
        mensaje = f"📊 Torneo: {torneo['nombre']} | "
        mensaje += f"Equipos: {torneo['num_equipos']} | "
        mensaje += f"Partidos: {partidos_finalizados}/{total_partidos} finalizados"
        
        if campeon:
            mensaje += f" | 🏆 CAMPEÓN: {campeon}"
        
        self.lbl_estadisticas.setText(mensaje)
