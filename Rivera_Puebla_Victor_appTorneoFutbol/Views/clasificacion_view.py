"""
Vista para mostrar el cuadro de eliminatorias del torneo.
Muestra el bracket completo con todos los emparejamientos.
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QScrollArea, QFrame, QGridLayout,
                               QGroupBox, QGraphicsView)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


def crear_vista_clasificacion():
    """
    Crea la vista de clasificación/brackets.
    
    Returns:
        QWidget con la interfaz de clasificación
    """
    widget = QWidget()
    widget.setObjectName("widgetClasificacion")
    widget.setStyleSheet("QWidget#widgetClasificacion { background-color: transparent; }")
    
    layout_principal = QVBoxLayout(widget)
    layout_principal.setContentsMargins(20, 20, 20, 20)
    layout_principal.setSpacing(15)
    
    # Título
    lbl_titulo = QLabel("CUADRO DE ELIMINATORIAS")
    lbl_titulo.setObjectName("lblTitulo")
    lbl_titulo.setStyleSheet("QLabel { color: #FFD700; }")
    font_titulo = QFont()
    font_titulo.setPointSize(18)
    font_titulo.setBold(True)
    lbl_titulo.setFont(font_titulo)
    lbl_titulo.setAlignment(Qt.AlignCenter)
    layout_principal.addWidget(lbl_titulo)
    
    # Botones superiores
    layout_botones = QHBoxLayout()
    
    btn_actualizar = QPushButton("↻ ACTUALIZAR BRACKET")
    btn_actualizar.setObjectName("btnActualizar")
    btn_actualizar.setMinimumHeight(40)
    layout_botones.addWidget(btn_actualizar)
    
    btn_generar_siguiente = QPushButton("⚡ GENERAR SIGUIENTE RONDA")
    btn_generar_siguiente.setObjectName("btnGenerarSiguiente")
    btn_generar_siguiente.setMinimumHeight(40)
    layout_botones.addWidget(btn_generar_siguiente)
    
    btn_volver = QPushButton("← VOLVER")
    btn_volver.setObjectName("btnVolver")
    btn_volver.setMinimumHeight(40)
    layout_botones.addWidget(btn_volver)
    
    layout_principal.addLayout(layout_botones)
    
    # QGraphicsView para mostrar los brackets
    graphics_view = QGraphicsView()
    graphics_view.setObjectName("graphicsViewBrackets")
    graphics_view.setStyleSheet("QGraphicsView { background-color: rgba(230, 230, 230, 0.95); border: 1px solid #4A5F7F; }")
    graphics_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
    graphics_view.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
    layout_principal.addWidget(graphics_view)
    
    # Etiqueta de estadísticas
    lbl_estadisticas = QLabel("")
    lbl_estadisticas.setObjectName("lblEstadisticas")
    lbl_estadisticas.setStyleSheet("QLabel { color: #FFD700; font-style: italic; padding: 10px; }")
    lbl_estadisticas.setWordWrap(True)
    lbl_estadisticas.setAlignment(Qt.AlignCenter)
    layout_principal.addWidget(lbl_estadisticas)
    
    # Información adicional
    lbl_info = QLabel("Haz clic en 'GENERAR SIGUIENTE RONDA' para crear automáticamente los partidos de la siguiente fase según los ganadores.")
    lbl_info.setObjectName("lblInfo")
    lbl_info.setStyleSheet("QLabel { color: #FFA500; font-style: italic; padding: 10px; }")
    lbl_info.setWordWrap(True)
    lbl_info.setAlignment(Qt.AlignCenter)
    layout_principal.addWidget(lbl_info)
    layout_principal.addWidget(lbl_info)
    
    widget.setLayout(layout_principal)
    return widget


def crear_widget_partido(equipo_a_nombre, equipo_b_nombre, goles_a=None, goles_b=None, ganador=None):
    """
    Crea un widget para mostrar un partido del bracket.
    
    Args:
        equipo_a_nombre: Nombre del primer equipo
        equipo_b_nombre: Nombre del segundo equipo
        goles_a: Goles del equipo A (None si no hay resultado)
        goles_b: Goles del equipo B (None si no hay resultado)
        ganador: 'A', 'B' o None
        
    Returns:
        QFrame con el widget del partido
    """
    frame_partido = QFrame()
    frame_partido.setFrameShape(QFrame.Box)
    frame_partido.setLineWidth(1)
    frame_partido.setMinimumWidth(200)
    frame_partido.setMaximumWidth(250)
    
    layout = QVBoxLayout(frame_partido)
    layout.setContentsMargins(10, 5, 10, 5)
    layout.setSpacing(2)
    
    # Equipo A
    layout_equipo_a = QHBoxLayout()
    lbl_equipo_a = QLabel(equipo_a_nombre)
    lbl_equipo_a.setStyleSheet("QLabel { font-weight: bold; }" if ganador == 'A' else "")
    layout_equipo_a.addWidget(lbl_equipo_a)
    layout_equipo_a.addStretch()
    
    if goles_a is not None:
        lbl_goles_a = QLabel(str(goles_a))
        lbl_goles_a.setMinimumWidth(30)
        lbl_goles_a.setAlignment(Qt.AlignCenter)
        lbl_goles_a.setStyleSheet("QLabel { font-weight: bold; font-size: 14px; }")
        layout_equipo_a.addWidget(lbl_goles_a)
    
    layout.addLayout(layout_equipo_a)
    
    # Separador
    separador = QFrame()
    separador.setFrameShape(QFrame.HLine)
    separador.setFrameShadow(QFrame.Sunken)
    layout.addWidget(separador)
    
    # Equipo B
    layout_equipo_b = QHBoxLayout()
    lbl_equipo_b = QLabel(equipo_b_nombre)
    lbl_equipo_b.setStyleSheet("QLabel { font-weight: bold; }" if ganador == 'B' else "")
    layout_equipo_b.addWidget(lbl_equipo_b)
    layout_equipo_b.addStretch()
    
    if goles_b is not None:
        lbl_goles_b = QLabel(str(goles_b))
        lbl_goles_b.setMinimumWidth(30)
        lbl_goles_b.setAlignment(Qt.AlignCenter)
        lbl_goles_b.setStyleSheet("QLabel { font-weight: bold; font-size: 14px; }")
        layout_equipo_b.addWidget(lbl_goles_b)
    
    layout.addLayout(layout_equipo_b)
    
    # Estilo según estado
    if ganador:
        frame_partido.setStyleSheet("QFrame { background-color: #d4edda; border: 2px solid #28a745; }")
    elif goles_a is not None and goles_b is not None:
        frame_partido.setStyleSheet("QFrame { background-color: #fff3cd; border: 2px solid #ffc107; }")
    else:
        frame_partido.setStyleSheet("QFrame { background-color: #f8f9fa; border: 1px solid #dee2e6; }")
    
    frame_partido.setLayout(layout)
    return frame_partido
