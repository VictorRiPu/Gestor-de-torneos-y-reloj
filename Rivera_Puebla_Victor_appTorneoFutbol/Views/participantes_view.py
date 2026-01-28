"""
Vista para la gestión de participantes (jugadores y árbitros).
Crea la interfaz de gestión de participantes dinámicamente.
"""

from PySide6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QFrame,
                               QLabel, QLineEdit, QPushButton, QComboBox,
                               QListWidget, QScrollArea, QRadioButton, QButtonGroup,
                               QDateEdit, QCheckBox, QSpinBox, QTableWidget,
                               QHeaderView, QGroupBox)
from PySide6.QtCore import Qt, QDate


def crear_vista_participantes():
    """
    Crea y retorna la vista de gestión de participantes.
    
    Returns:
        QWidget: Widget con la interfaz de participantes
    """
    widget = QWidget()
    widget.setObjectName("pagina_participantes")
    
    # Layout principal horizontal (3 columnas)
    layout_principal = QHBoxLayout(widget)
    layout_principal.setContentsMargins(10, 10, 10, 10)
    layout_principal.setSpacing(10)
    layout_principal.setStretch(0, 30)  # Columna 1: 30%
    layout_principal.setStretch(1, 35)  # Columna 2: 35%
    layout_principal.setStretch(2, 35)  # Columna 3: 35%
    
    # ========== COLUMNA 1: FORMULARIO DE REGISTRO (30%) ==========
    frame_formulario = QFrame()
    frame_formulario.setObjectName("frameFormulario")
    frame_formulario.setFrameShape(QFrame.StyledPanel)
    frame_formulario.setStyleSheet("""
        QFrame#frameFormulario { 
            background: rgba(30, 40, 60, 0.9); 
        } 
        QGroupBox {
            background: rgba(30, 40, 60, 0.9);
            color: #FFD700;
            border: 1px solid #4A5F7F;
            border-radius: 5px;
            margin-top: 5px;
            padding-top: 5px;
        }
        QGroupBox::title {
            color: #FFD700;
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px;
        }
        QLabel { 
            color: #FFD700; 
        } 
        QLineEdit, QDateEdit, QSpinBox { 
            color: #1E1E1E; 
            background: rgba(230, 230, 230, 0.95);
        }
        QRadioButton, QCheckBox {
            color: #FFD700;
        }
    """)
    layout_formulario = QVBoxLayout(frame_formulario)
    layout_formulario.setSpacing(5)
    
    # Botón volver
    btnVolver = QPushButton("⬅ VOLVER")
    btnVolver.setObjectName("btnVolver")
    btnVolver.setMinimumHeight(30)
    btnVolver.setMaximumHeight(30)
    layout_formulario.addWidget(btnVolver)
    
    # Título
    titulo = QLabel("REGISTRAR PARTICIPANTE")
    titulo.setObjectName("tituloParticipantes")
    titulo.setStyleSheet("font-size: 14px; font-weight: bold; padding: 5px; color: #FFD700;")
    titulo.setAlignment(Qt.AlignCenter)
    layout_formulario.addWidget(titulo)
    
    # Área de scroll para el formulario
    scroll_form = QScrollArea()
    scroll_form.setWidgetResizable(True)
    scroll_form.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    scroll_form.setStyleSheet("QScrollArea { background: rgba(30, 40, 60, 0.9); border: none; }")
    
    widget_form_content = QWidget()
    widget_form_content.setStyleSheet("QWidget { background: rgba(30, 40, 60, 0.9); }")
    layout_form_content = QVBoxLayout(widget_form_content)
    layout_form_content.setSpacing(5)
    layout_form_content.setContentsMargins(5, 5, 5, 5)
    
    # === DATOS PERSONALES ===
    group_personal = QGroupBox("Datos Personales")
    layout_personal = QVBoxLayout(group_personal)
    
    # Nombre
    lblNombre = QLabel("Nombre *:")
    txtNombre = QLineEdit()
    txtNombre.setObjectName("txtNombre")
    txtNombre.setPlaceholderText("Nombre del participante")
    layout_personal.addWidget(lblNombre)
    layout_personal.addWidget(txtNombre)
    
    # Apellidos
    lblApellidos = QLabel("Apellidos *:")
    txtApellidos = QLineEdit()
    txtApellidos.setObjectName("txtApellidos")
    txtApellidos.setPlaceholderText("Apellidos")
    layout_personal.addWidget(lblApellidos)
    layout_personal.addWidget(txtApellidos)
    
    # Fecha de nacimiento
    lblFechaNacimiento = QLabel("Fecha de Nacimiento *:")
    dateFechaNacimiento = QDateEdit()
    dateFechaNacimiento.setObjectName("dateFechaNacimiento")
    dateFechaNacimiento.setCalendarPopup(True)
    dateFechaNacimiento.setDate(QDate(2005, 1, 1))
    dateFechaNacimiento.setDisplayFormat("dd/MM/yyyy")
    layout_personal.addWidget(lblFechaNacimiento)
    layout_personal.addWidget(dateFechaNacimiento)
    
    # Curso
    lblCurso = QLabel("Curso *:")
    txtCurso = QLineEdit()
    txtCurso.setObjectName("txtCurso")
    txtCurso.setPlaceholderText("Ej: 2ºDAM, 1ºBachillerato")
    layout_personal.addWidget(lblCurso)
    layout_personal.addWidget(txtCurso)
    
    layout_form_content.addWidget(group_personal)
    
    # === TIPO DE PARTICIPANTE ===
    group_tipo = QGroupBox("Tipo de Participante *")
    layout_tipo_group = QVBoxLayout(group_tipo)
    
    layout_tipo = QHBoxLayout()
    
    radioJugador = QRadioButton("Jugador")
    radioJugador.setObjectName("radioJugador")
    radioJugador.setChecked(True)
    
    radioArbitro = QRadioButton("Árbitro")
    radioArbitro.setObjectName("radioArbitro")
    
    radioAmbos = QRadioButton("Ambos")
    radioAmbos.setObjectName("radioAmbos")
    
    grupoTipo = QButtonGroup()
    grupoTipo.addButton(radioJugador)
    grupoTipo.addButton(radioArbitro)
    grupoTipo.addButton(radioAmbos)
    
    layout_tipo.addWidget(radioJugador)
    layout_tipo.addWidget(radioArbitro)
    layout_tipo.addWidget(radioAmbos)
    layout_tipo_group.addLayout(layout_tipo)
    
    
    # === DATOS DE JUGADOR (si aplica) ===
    group_jugador = QGroupBox("Datos de Jugador")
    group_jugador.setObjectName("groupJugador")
    layout_jugador = QVBoxLayout(group_jugador)
    
    # Equipo
    lblEquipo = QLabel("Equipo:")
    comboEquipo = QComboBox()
    comboEquipo.setObjectName("comboEquipo")
    comboEquipo.setStyleSheet("QComboBox { color: #1E1E1E; background-color: rgba(230, 230, 230, 0.95); } QComboBox QAbstractItemView { color: #1E1E1E; background-color: rgba(230, 230, 230, 0.95); }")
    comboEquipo.addItem("Sin asignar", None)
    layout_jugador.addWidget(lblEquipo)
    layout_jugador.addWidget(comboEquipo)
    
    # Posición
    lblPosicion = QLabel("Posición *:")
    comboPosicion = QComboBox()
    comboPosicion.setObjectName("comboPosicion")
    comboPosicion.setStyleSheet("QComboBox { color: #1E1E1E; background-color: rgba(230, 230, 230, 0.95); } QComboBox QAbstractItemView { color: #1E1E1E; background-color: rgba(230, 230, 230, 0.95); }")
    comboPosicion.addItems(["Portero", "Defensa", "Centrocampista", "Delantero"])
    layout_jugador.addWidget(lblPosicion)
    layout_jugador.addWidget(comboPosicion)
    
    # Dorsal
    lblDorsal = QLabel("Dorsal:")
    spinDorsal = QSpinBox()
    spinDorsal.setObjectName("spinDorsal")
    spinDorsal.setMinimum(1)
    spinDorsal.setMaximum(99)
    spinDorsal.setValue(1)
    layout_jugador.addWidget(lblDorsal)
    layout_jugador.addWidget(spinDorsal)
    
    # Capitán
    checkCapitan = QCheckBox("Capitán del equipo")
    checkCapitan.setObjectName("checkCapitan")
    layout_jugador.addWidget(checkCapitan)
    
    # Estadísticas (editables manualmente)
    lblStats = QLabel("Estadísticas:")
    lblStats.setStyleSheet("font-style: italic; color: #FFA500;")
    layout_jugador.addWidget(lblStats)
    
    layout_stats = QHBoxLayout()
    
    lblGoles = QLabel("Goles:")
    spinGoles = QSpinBox()
    spinGoles.setObjectName("spinGoles")
    spinGoles.setMinimum(0)
    spinGoles.setMaximum(999)
    layout_stats.addWidget(lblGoles)
    layout_stats.addWidget(spinGoles)
    
    lblAmarillas = QLabel("T.A:")
    spinAmarillas = QSpinBox()
    spinAmarillas.setObjectName("spinAmarillas")
    spinAmarillas.setMinimum(0)
    spinAmarillas.setMaximum(99)
    layout_stats.addWidget(lblAmarillas)
    layout_stats.addWidget(spinAmarillas)
    
    lblRojas = QLabel("T.R:")
    spinRojas = QSpinBox()
    spinRojas.setObjectName("spinRojas")
    spinRojas.setMinimum(0)
    spinRojas.setMaximum(99)
    layout_stats.addWidget(lblRojas)
    layout_stats.addWidget(spinRojas)
    
    layout_jugador.addLayout(layout_stats)
    
    layout_form_content.addWidget(group_jugador)
    
    # === DATOS DE ÁRBITRO (si aplica) ===
    group_arbitro = QGroupBox("Datos de Árbitro")
    group_arbitro.setObjectName("groupArbitro")
    group_arbitro.setVisible(False)
    layout_arbitro = QVBoxLayout(group_arbitro)
    
    # Experiencia
    lblExperiencia = QLabel("Años de Experiencia:")
    spinExperiencia = QSpinBox()
    spinExperiencia.setObjectName("spinExperiencia")
    spinExperiencia.setMinimum(0)
    spinExperiencia.setMaximum(50)
    layout_arbitro.addWidget(lblExperiencia)
    layout_arbitro.addWidget(spinExperiencia)
    
    # Categoría
    lblCategoria = QLabel("Categoría:")
    comboCategoria = QComboBox()
    comboCategoria.setObjectName("comboCategoria")
    comboCategoria.setStyleSheet("QComboBox { color: #1E1E1E; background-color: rgba(230, 230, 230, 0.95); } QComboBox QAbstractItemView { color: #1E1E1E; background-color: rgba(230, 230, 230, 0.95); }")
    comboCategoria.addItems(["Regional", "Nacional", "Internacional"])
    layout_arbitro.addWidget(lblCategoria)
    layout_arbitro.addWidget(comboCategoria)
    
    layout_form_content.addWidget(group_arbitro)
    
    # Botones de acción
    layout_botones_form = QHBoxLayout()
    layout_botones_form.setSpacing(5)
    
    btnGuardar = QPushButton("💾 GUARDAR")
    btnGuardar.setObjectName("btnGuardar")
    btnGuardar.setMinimumHeight(35)
    btnGuardar.setMaximumHeight(35)
    btnGuardar.setSizePolicy(btnGuardar.sizePolicy().horizontalPolicy(), btnGuardar.sizePolicy().verticalPolicy())
    btnGuardar.setStyleSheet("QPushButton { background-color: rgba(60, 80, 120, 0.9); color: #FFD700; font-weight: bold; padding: 5px; border: 2px solid #4A5F7F; }")
    
    btnLimpiar = QPushButton("🗑 LIMPIAR")
    btnLimpiar.setObjectName("btnLimpiar")
    btnLimpiar.setMinimumHeight(35)
    btnLimpiar.setMaximumHeight(35)
    btnLimpiar.setSizePolicy(btnLimpiar.sizePolicy().horizontalPolicy(), btnLimpiar.sizePolicy().verticalPolicy())
    btnLimpiar.setStyleSheet("QPushButton { padding: 5px; }")
    
    layout_botones_form.addWidget(btnGuardar)
    layout_botones_form.addWidget(btnLimpiar)
    layout_form_content.addLayout(layout_botones_form)
    
    layout_form_content.addStretch()
    
    scroll_form.setWidget(widget_form_content)
    layout_formulario.addWidget(scroll_form)
    
    layout_principal.addWidget(frame_formulario)
    
    # ========== COLUMNA 2: LISTA DE PARTICIPANTES (35%) ==========
    frame_lista = QFrame()
    frame_lista.setObjectName("frameLista")
    frame_lista.setFrameShape(QFrame.StyledPanel)
    layout_lista = QVBoxLayout(frame_lista)
    
    lblTituloLista = QLabel("PARTICIPANTES REGISTRADOS")
    lblTituloLista.setStyleSheet("font-size: 14px; font-weight: bold; padding: 5px;")
    lblTituloLista.setAlignment(Qt.AlignCenter)
    layout_lista.addWidget(lblTituloLista)
    
    # Búsqueda
    txtBuscar = QLineEdit()
    txtBuscar.setObjectName("txtBuscar")
    txtBuscar.setPlaceholderText("🔍 Buscar participante...")
    txtBuscar.setStyleSheet("QLineEdit { color: black; }")
    layout_lista.addWidget(txtBuscar)
    
    # Filtros
    layout_filtros = QHBoxLayout()
    radioFiltroTodos = QRadioButton("Todos")
    radioFiltroTodos.setObjectName("radioFiltroTodos")
    radioFiltroTodos.setChecked(True)
    
    radioFiltroJugadores = QRadioButton("Jugadores")
    radioFiltroJugadores.setObjectName("radioFiltroJugadores")
    
    radioFiltroArbitros = QRadioButton("Árbitros")
    radioFiltroArbitros.setObjectName("radioFiltroArbitros")
    
    grupoFiltros = QButtonGroup()
    grupoFiltros.addButton(radioFiltroTodos)
    grupoFiltros.addButton(radioFiltroJugadores)
    grupoFiltros.addButton(radioFiltroArbitros)
    
    layout_filtros.addWidget(radioFiltroTodos)
    layout_filtros.addWidget(radioFiltroJugadores)
    layout_filtros.addWidget(radioFiltroArbitros)
    layout_lista.addLayout(layout_filtros)
    
    # Lista de participantes
    listParticipantes = QListWidget()
    listParticipantes.setObjectName("listParticipantes")
    listParticipantes.setStyleSheet("QListWidget { color: black; }")
    layout_lista.addWidget(listParticipantes)
    
    # Botones de gestión
    layout_botones_lista = QHBoxLayout()
    layout_botones_lista.setSpacing(5)
    
    btnEditar = QPushButton("✏ EDITAR")
    btnEditar.setObjectName("btnEditar")
    btnEditar.setMinimumHeight(35)
    btnEditar.setMaximumHeight(35)
    btnEditar.setStyleSheet("QPushButton { padding: 5px; }")
    
    btnEliminar = QPushButton("🗑 ELIMINAR")
    btnEliminar.setObjectName("btnEliminar")
    btnEliminar.setMinimumHeight(35)
    btnEliminar.setMaximumHeight(35)
    btnEliminar.setStyleSheet("QPushButton { background-color: rgba(180, 50, 50, 0.9); color: #FFD700; padding: 5px; border: 2px solid #4A5F7F; }")
    
    layout_botones_lista.addWidget(btnEditar)
    layout_botones_lista.addWidget(btnEliminar)
    layout_lista.addLayout(layout_botones_lista)
    
    layout_principal.addWidget(frame_lista)
    
    # ========== COLUMNA 3: ASIGNACIÓN A EQUIPOS (30%) ==========
    frame_asignacion = QFrame()
    frame_asignacion.setObjectName("frameAsignacion")
    frame_asignacion.setFrameShape(QFrame.StyledPanel)
    layout_asignacion = QVBoxLayout(frame_asignacion)
    
    lblTituloAsignacion = QLabel("ASIGNAR JUGADOR A EQUIPO")
    lblTituloAsignacion.setStyleSheet("font-size: 14px; font-weight: bold; padding: 5px;")
    lblTituloAsignacion.setAlignment(Qt.AlignCenter)
    layout_asignacion.addWidget(lblTituloAsignacion)
    
    # Selección de equipo para asignación
    lblEquipoAsignar = QLabel("Seleccionar Equipo:")
    comboEquipoAsignar = QComboBox()
    comboEquipoAsignar.setObjectName("comboEquipoAsignar")
    comboEquipoAsignar.setStyleSheet("QComboBox { color: #1E1E1E; background-color: rgba(230, 230, 230, 0.95); }")
    layout_asignacion.addWidget(lblEquipoAsignar)
    layout_asignacion.addWidget(comboEquipoAsignar)
    
    btnCargarJugadores = QPushButton("📋 CARGAR JUGADORES DEL EQUIPO")
    btnCargarJugadores.setObjectName("btnCargarJugadores")
    btnCargarJugadores.setMinimumHeight(35)
    btnCargarJugadores.setMaximumHeight(35)
    btnCargarJugadores.setStyleSheet("QPushButton { padding: 5px; }")
    layout_asignacion.addWidget(btnCargarJugadores)
    
    # Tabla de jugadores del equipo
    lblJugadoresEquipo = QLabel("Jugadores en el equipo:")
    layout_asignacion.addWidget(lblJugadoresEquipo)
    
    tableJugadoresEquipo = QTableWidget()
    tableJugadoresEquipo.setObjectName("tableJugadoresEquipo")
    tableJugadoresEquipo.setColumnCount(4)
    tableJugadoresEquipo.setHorizontalHeaderLabels(["Nombre", "Posición", "Dorsal", "Cap."])
    tableJugadoresEquipo.horizontalHeader().setStretchLastSection(True)
    tableJugadoresEquipo.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
    tableJugadoresEquipo.setSelectionBehavior(QTableWidget.SelectRows)
    layout_asignacion.addWidget(tableJugadoresEquipo)
    
    # Opciones de asignación
    lblJugadorAsignar = QLabel("Seleccionar jugador SIN equipo:")
    comboJugadorAsignar = QComboBox()
    comboJugadorAsignar.setObjectName("comboJugadorAsignar")
    comboJugadorAsignar.setStyleSheet("QComboBox { color: #1E1E1E; background-color: rgba(230, 230, 230, 0.95); }")
    layout_asignacion.addWidget(lblJugadorAsignar)
    layout_asignacion.addWidget(comboJugadorAsignar)
    
    btnAsignarEquipo = QPushButton("➕ ASIGNAR AL EQUIPO")
    btnAsignarEquipo.setObjectName("btnAsignarEquipo")
    btnAsignarEquipo.setMinimumHeight(35)
    btnAsignarEquipo.setMaximumHeight(35)
    btnAsignarEquipo.setStyleSheet("QPushButton { background-color: rgba(60, 80, 120, 0.9); color: #FFD700; font-weight: bold; padding: 5px; border: 2px solid #4A5F7F; }")
    layout_asignacion.addWidget(btnAsignarEquipo)
    
    btnDesasignarEquipo = QPushButton("➖ QUITAR DEL EQUIPO")
    btnDesasignarEquipo.setObjectName("btnDesasignarEquipo")
    btnDesasignarEquipo.setMinimumHeight(35)
    btnDesasignarEquipo.setMaximumHeight(35)
    btnDesasignarEquipo.setStyleSheet("QPushButton { background-color: rgba(180, 120, 50, 0.9); color: #1E1E1E; padding: 5px; border: 2px solid #4A5F7F; }")
    layout_asignacion.addWidget(btnDesasignarEquipo)
    
    layout_asignacion.addStretch()
    
    layout_principal.addWidget(frame_asignacion)
    
    return widget
