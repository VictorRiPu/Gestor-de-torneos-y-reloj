"""
Vista para la gestión de resultados de partidos.
Crea la interfaz de resultados dinámicamente.
"""

from PySide6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QFrame,
                               QLabel, QPushButton, QListWidget, QTableWidget,
                               QTableWidgetItem, QHeaderView, QScrollArea,
                               QSpinBox, QCheckBox, QGroupBox, QComboBox)
from PySide6.QtCore import Qt
from Views.components.reloj_widget import RelojDigital


def crear_vista_resultados():
    """
    Crea y retorna la vista de gestión de resultados.
    
    Returns:
        QWidget: Widget con la interfaz de resultados
    """
    widget = QWidget()
    widget.setObjectName("pagina_resultados")
    
    # Layout principal
    layout_principal = QVBoxLayout(widget)
    layout_principal.setContentsMargins(20, 20, 20, 20)
    
    # Botón volver
    btnVolver = QPushButton("← VOLVER")
    btnVolver.setObjectName("btnVolver")
    btnVolver.setMaximumWidth(150)
    layout_principal.addWidget(btnVolver)
    
    # Layout horizontal para título y reloj
    layout_titulo_reloj = QHBoxLayout()
    layout_titulo_reloj.setSpacing(20)
    
    # Spacer izquierdo para centrar titulo
    layout_titulo_reloj.addStretch()
    
    # Título
    lblTitulo = QLabel("Registro de Resultados")
    lblTitulo.setStyleSheet("font-size: 20px; font-weight: bold; color: #FFD700;")
    lblTitulo.setAlignment(Qt.AlignCenter)
    layout_titulo_reloj.addWidget(lblTitulo)
    
    # Spacer central para empujar el reloj a la derecha
    layout_titulo_reloj.addStretch()
    
    # Reloj digital en la esquina superior derecha
    reloj = RelojDigital()
    reloj.setObjectName("relojPartido")
    reloj.setMaximumWidth(400)
    reloj.mode = "timer"
    layout_titulo_reloj.addWidget(reloj)
    
    layout_principal.addLayout(layout_titulo_reloj)
    
    # Layout horizontal: Lista partidos (1/3) | Registro de jugadores (2/3)
    layout_contenido = QHBoxLayout()
    layout_contenido.setSpacing(20)
    
    # === PANEL IZQUIERDO: LISTA DE PARTIDOS (1/3) ===
    panel_izquierdo = QFrame()
    panel_izquierdo.setObjectName("panelIzquierdo")
    panel_izquierdo.setMaximumWidth(400)
    panel_izquierdo.setStyleSheet("""
        QFrame#panelIzquierdo {
            background-color: rgba(30, 40, 60, 0.9);
            border-radius: 10px;
            padding: 10px;
        }
    """)
    
    layout_izquierdo = QVBoxLayout(panel_izquierdo)
    layout_izquierdo.setSpacing(15)
    
    # Título
    lblTituloPartidos = QLabel("Partidos")
    lblTituloPartidos.setStyleSheet("font-size: 16px; font-weight: bold; color: #FFD700;")
    lblTituloPartidos.setAlignment(Qt.AlignCenter)
    layout_izquierdo.addWidget(lblTituloPartidos)
    
    # Filtro de estado
    layout_filtro = QHBoxLayout()
    lblFiltro = QLabel("Filtrar:")
    lblFiltro.setStyleSheet("color: #FFD700; font-weight: bold;")
    layout_filtro.addWidget(lblFiltro)
    
    comboFiltroEstado = QComboBox()
    comboFiltroEstado.setObjectName("comboFiltroEstado")
    comboFiltroEstado.addItem("Todos", "todos")
    comboFiltroEstado.addItem("Pendientes", "pendiente")
    comboFiltroEstado.addItem("En Curso", "en_curso")
    comboFiltroEstado.addItem("Finalizados", "finalizado")
    comboFiltroEstado.addItem("Cancelados", "cancelado")
    comboFiltroEstado.setStyleSheet("""
        QComboBox {
            background-color: #E6E6E6;
            color: #1E1E1E;
            border: 1px solid #4A5F7F;
            border-radius: 5px;
            padding: 5px;
            min-height: 25px;
        }
        QComboBox::drop-down {
            border: none;
            width: 20px;
        }
        QComboBox::down-arrow {
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 5px solid #1E1E1E;
            margin-right: 5px;
        }
        QComboBox QAbstractItemView {
            background-color: #E6E6E6;
            color: #1E1E1E;
            selection-background-color: #4A5F7F;
            selection-color: black;
        }
    """)
    layout_filtro.addWidget(comboFiltroEstado)
    layout_filtro.addStretch()
    
    layout_izquierdo.addLayout(layout_filtro)
    
    # Lista de partidos
    listPartidos = QListWidget()
    listPartidos.setObjectName("listPartidos")
    listPartidos.setStyleSheet("""
        QListWidget {
            background-color: white;
            color: black;
            border: 1px solid #CCCCCC;
            border-radius: 5px;
            padding: 5px;
        }
        QListWidget::item {
            color: black;
            padding: 10px;
            border-bottom: 1px solid #EEEEEE;
        }
        QListWidget::item:selected {
            background-color: #E8F5E9;
            color: black;
        }
        QListWidget::item:hover {
            background-color: #F1F8F4;
        }
    """)
    layout_izquierdo.addWidget(listPartidos)
    
    # Resumen del resultado
    frameResumen = QFrame()
    frameResumen.setObjectName("frameResumen")
    frameResumen.setMaximumHeight(150)
    frameResumen.setStyleSheet("""
        QFrame#frameResumen {
            background-color: rgba(255, 255, 255, 180);
            border: 2px solid #4CAF50;
            border-radius: 8px;
            padding: 10px;
        }
    """)
    layoutResumen = QVBoxLayout(frameResumen)
    
    lblResumenTitulo = QLabel("Resumen del Resultado")
    lblResumenTitulo.setStyleSheet("font-weight: bold; font-size: 14px; color: #000000;")
    lblResumenTitulo.setAlignment(Qt.AlignCenter)
    layoutResumen.addWidget(lblResumenTitulo)
    
    lblResumen = QLabel("")
    lblResumen.setObjectName("lblResumen")
    lblResumen.setWordWrap(True)
    lblResumen.setAlignment(Qt.AlignCenter)
    lblResumen.setStyleSheet("color: #000000; font-size: 13px; font-weight: bold;")
    layoutResumen.addWidget(lblResumen)
    
    layout_izquierdo.addWidget(frameResumen)
    
    layout_contenido.addWidget(panel_izquierdo, 1)
    
    # === PANEL DERECHO: REGISTRO DE JUGADORES (2/3) ===
    panel_derecho = QFrame()
    panel_derecho.setObjectName("panelDerecho")
    panel_derecho.setStyleSheet("""
        QFrame#panelDerecho {
            background-color: rgba(255, 255, 255, 200);
            border-radius: 10px;
            padding: 10px;
        }
    """)
    
    layout_derecho = QVBoxLayout(panel_derecho)
    layout_derecho.setSpacing(15)
    
    # Información del partido seleccionado
    lblPartidoSeleccionado = QLabel("Selecciona un partido para registrar el resultado")
    lblPartidoSeleccionado.setObjectName("lblPartidoSeleccionado")
    lblPartidoSeleccionado.setStyleSheet("font-size: 16px; font-weight: bold; color: #000000;")
    lblPartidoSeleccionado.setAlignment(Qt.AlignCenter)
    layout_derecho.addWidget(lblPartidoSeleccionado)
    
    # Layout horizontal para los dos equipos
    layout_equipos = QHBoxLayout()
    layout_equipos.setSpacing(10)
    
    # === EQUIPO A ===
    groupEquipoA = QGroupBox()
    groupEquipoA.setObjectName("groupEquipoA")
    groupEquipoA.setTitle("Equipo A")
    groupEquipoA.setStyleSheet("""
        QGroupBox {
            font-weight: bold;
            color: black;
            border: 2px solid #4CAF50;
            border-radius: 8px;
            margin-top: 10px;
            padding: 10px;
            background-color: rgba(255, 255, 255, 150);
        }
        QGroupBox::title {
            color: black;
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px;
        }
    """)
    layoutEquipoA = QVBoxLayout(groupEquipoA)
    
    # Nombre del equipo A
    lblNombreEquipoA = QLabel("")
    lblNombreEquipoA.setObjectName("lblNombreEquipoA")
    lblNombreEquipoA.setStyleSheet("font-size: 18px; font-weight: bold; color: #000000;")
    lblNombreEquipoA.setAlignment(Qt.AlignCenter)
    layoutEquipoA.addWidget(lblNombreEquipoA)
    
    # Tabla de jugadores del equipo A
    tableJugadoresA = QTableWidget()
    tableJugadoresA.setObjectName("tableJugadoresA")
    tableJugadoresA.setColumnCount(4)
    tableJugadoresA.setHorizontalHeaderLabels(["Jugador", "Goles", "T. Amarillas", "T. Rojas"])
    tableJugadoresA.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
    tableJugadoresA.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
    tableJugadoresA.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
    tableJugadoresA.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
    tableJugadoresA.setEditTriggers(QTableWidget.DoubleClicked)
    tableJugadoresA.setSelectionBehavior(QTableWidget.SelectRows)
    tableJugadoresA.setSelectionMode(QTableWidget.SingleSelection)
    tableJugadoresA.setStyleSheet("""
        QTableWidget {
            background-color: white;
            color: black;
            gridline-color: #DDDDDD;
            border: 1px solid #CCCCCC;
        }
        QTableWidget::item {
            color: black;
            padding: 5px;
        }
        QHeaderView::section {
            background-color: #4CAF50;
            color: white;
            font-weight: bold;
            padding: 5px;
            border: none;
        }
    """)
    layoutEquipoA.addWidget(tableJugadoresA)
    
    # Total goles equipo A
    layoutTotalA = QHBoxLayout()
    lblTotalGolesA = QLabel("Total Goles:")
    lblTotalGolesA.setStyleSheet("font-weight: bold; color: #000000; font-size: 14px;")
    layoutTotalA.addWidget(lblTotalGolesA)
    
    spinTotalGolesA = QSpinBox()
    spinTotalGolesA.setObjectName("spinTotalGolesA")
    spinTotalGolesA.setMinimum(0)
    spinTotalGolesA.setMaximum(99)
    spinTotalGolesA.setReadOnly(True)
    layoutTotalA.addWidget(spinTotalGolesA)
    layoutTotalA.addStretch()
    
    layoutEquipoA.addLayout(layoutTotalA)
    
    layout_equipos.addWidget(groupEquipoA)
    
    # === EQUIPO B ===
    groupEquipoB = QGroupBox()
    groupEquipoB.setObjectName("groupEquipoB")
    groupEquipoB.setTitle("Equipo B")
    groupEquipoB.setStyleSheet("""
        QGroupBox {
            font-weight: bold;
            color: black;
            border: 2px solid #2196F3;
            border-radius: 8px;
            margin-top: 10px;
            padding: 10px;
            background-color: rgba(255, 255, 255, 150);
        }
        QGroupBox::title {
            color: black;
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px;
        }
    """)
    layoutEquipoB = QVBoxLayout(groupEquipoB)
    
    # Nombre del equipo B
    lblNombreEquipoB = QLabel("")
    lblNombreEquipoB.setObjectName("lblNombreEquipoB")
    lblNombreEquipoB.setStyleSheet("font-size: 18px; font-weight: bold; color: #000000;")
    lblNombreEquipoB.setAlignment(Qt.AlignCenter)
    layoutEquipoB.addWidget(lblNombreEquipoB)
    
    # Tabla de jugadores del equipo B
    tableJugadoresB = QTableWidget()
    tableJugadoresB.setObjectName("tableJugadoresB")
    tableJugadoresB.setColumnCount(4)
    tableJugadoresB.setHorizontalHeaderLabels(["Jugador", "Goles", "T. Amarillas", "T. Rojas"])
    tableJugadoresB.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
    tableJugadoresB.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
    tableJugadoresB.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
    tableJugadoresB.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
    tableJugadoresB.setEditTriggers(QTableWidget.DoubleClicked)
    tableJugadoresB.setSelectionBehavior(QTableWidget.SelectRows)
    tableJugadoresB.setSelectionMode(QTableWidget.SingleSelection)
    tableJugadoresB.setStyleSheet("""
        QTableWidget {
            background-color: white;
            color: black;
            gridline-color: #DDDDDD;
            border: 1px solid #CCCCCC;
        }
        QTableWidget::item {
            color: black;
            padding: 5px;
        }
        QHeaderView::section {
            background-color: #2196F3;
            color: white;
            font-weight: bold;
            padding: 5px;
            border: none;
        }
    """)
    layoutEquipoB.addWidget(tableJugadoresB)
    
    # Total goles equipo B
    layoutTotalB = QHBoxLayout()
    lblTotalGolesB = QLabel("Total Goles:")
    lblTotalGolesB.setStyleSheet("font-weight: bold; color: #000000; font-size: 14px;")
    layoutTotalB.addWidget(lblTotalGolesB)
    
    spinTotalGolesB = QSpinBox()
    spinTotalGolesB.setObjectName("spinTotalGolesB")
    spinTotalGolesB.setMinimum(0)
    spinTotalGolesB.setMaximum(99)
    spinTotalGolesB.setReadOnly(True)
    layoutTotalB.addWidget(spinTotalGolesB)
    layoutTotalB.addStretch()
    
    layoutEquipoB.addLayout(layoutTotalB)
    
    layout_equipos.addWidget(groupEquipoB)
    
    layout_derecho.addLayout(layout_equipos)
    
    # Botones de gestión de estado
    layout_botones_estado = QHBoxLayout()
    
    btnIniciarPartido = QPushButton("INICIAR PARTIDO")
    btnIniciarPartido.setObjectName("btnIniciarPartido")
    btnIniciarPartido.setMinimumHeight(40)
    btnIniciarPartido.setStyleSheet("""
        QPushButton {
            background-color: #FFA726;
            color: white;
            font-weight: bold;
            border-radius: 5px;
            border: none;
        }
        QPushButton:hover {
            background-color: #FB8C00;
        }
        QPushButton:disabled {
            background-color: #CCCCCC;
            color: #666666;
        }
    """)
    layout_botones_estado.addWidget(btnIniciarPartido)
    
    btnFinalizarPartido = QPushButton("FINALIZAR PARTIDO")
    btnFinalizarPartido.setObjectName("btnFinalizarPartido")
    btnFinalizarPartido.setMinimumHeight(40)
    btnFinalizarPartido.setStyleSheet("""
        QPushButton {
            background-color: #66BB6A;
            color: white;
            font-weight: bold;
            border-radius: 5px;
            border: none;
        }
        QPushButton:hover {
            background-color: #4CAF50;
        }
        QPushButton:disabled {
            background-color: #CCCCCC;
            color: #666666;
        }
    """)
    layout_botones_estado.addWidget(btnFinalizarPartido)
    
    btnCancelarPartido = QPushButton("CANCELAR PARTIDO")
    btnCancelarPartido.setObjectName("btnCancelarPartido")
    btnCancelarPartido.setMinimumHeight(40)
    btnCancelarPartido.setStyleSheet("""
        QPushButton {
            background-color: #EF5350;
            color: white;
            font-weight: bold;
            border-radius: 5px;
            border: none;
        }
        QPushButton:hover {
            background-color: #E53935;
        }
        QPushButton:disabled {
            background-color: #CCCCCC;
            color: #666666;
        }
    """)
    layout_botones_estado.addWidget(btnCancelarPartido)
    
    btnReabrirPartido = QPushButton("REABRIR PARTIDO")
    btnReabrirPartido.setObjectName("btnReabrirPartido")
    btnReabrirPartido.setMinimumHeight(40)
    btnReabrirPartido.setStyleSheet("""
        QPushButton {
            background-color: #42A5F5;
            color: white;
            font-weight: bold;
            border-radius: 5px;
            border: none;
        }
        QPushButton:hover {
            background-color: #2196F3;
        }
        QPushButton:disabled {
            background-color: #CCCCCC;
            color: #666666;
        }
    """)
    layout_botones_estado.addWidget(btnReabrirPartido)
    
    layout_derecho.addLayout(layout_botones_estado)
    
    # Botones de acción
    layout_botones = QHBoxLayout()
    
    btnRegistrarResultado = QPushButton("REGISTRAR RESULTADO")
    btnRegistrarResultado.setObjectName("btnRegistrarResultado")
    btnRegistrarResultado.setMinimumHeight(50)
    btnRegistrarResultado.setStyleSheet("""
        QPushButton {
            background-color: #4CAF50;
            color: white;
            font-weight: bold;
            font-size: 14px;
            border-radius: 5px;
            border: none;
        }
        QPushButton:hover {
            background-color: #45A049;
        }
        QPushButton:disabled {
            background-color: #CCCCCC;
            color: #666666;
        }
    """)
    layout_botones.addWidget(btnRegistrarResultado)
    
    btnLimpiar = QPushButton("LIMPIAR")
    btnLimpiar.setObjectName("btnLimpiar")
    btnLimpiar.setMinimumHeight(50)
    btnLimpiar.setStyleSheet("""
        QPushButton {
            background-color: #9E9E9E;
            color: white;
            font-weight: bold;
            font-size: 14px;
            border-radius: 5px;
            border: none;
        }
        QPushButton:hover {
            background-color: #757575;
        }
    """)
    layout_botones.addWidget(btnLimpiar)
    
    layout_derecho.addLayout(layout_botones)
    
    layout_contenido.addWidget(panel_derecho, 2)
    
    layout_principal.addLayout(layout_contenido)
    
    return widget
