"""
Vista para la gestión del calendario y partidos.
Crea la interfaz de calendario dinámicamente.
"""

from PySide6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QFrame,
                               QLabel, QPushButton, QTreeWidget, QTreeWidgetItem,
                               QHeaderView)
from PySide6.QtCore import Qt
from Views.components.reloj_widget import RelojDigital

def crear_vista_calendario():
    """
    Crea y retorna la vista de calendario y partidos.
    
    Returns:
        tuple: (QWidget, RelojDigital) - Widget con la interfaz de calendario y el reloj
    """
    widget = QWidget()
    widget.setObjectName("pagina_calendario")
    
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
    
    # Título
    lblTitulo = QLabel("Gestión del Calendario")
    lblTitulo.setStyleSheet("font-size: 20px; font-weight: bold; color: #FFD700;")
    lblTitulo.setAlignment(Qt.AlignCenter)
    layout_titulo_reloj.addWidget(lblTitulo)
    
    # Spacer para empujar el reloj a la derecha
    layout_titulo_reloj.addStretch()
    
    # Reloj digital en la esquina superior derecha
    reloj = RelojDigital()
    reloj.setObjectName("relojDigital")
    reloj.setMaximumWidth(400)
    reloj.mode = "clock"  # Iniciar en modo reloj
    layout_titulo_reloj.addWidget(reloj)
    
    layout_principal.addLayout(layout_titulo_reloj)
    
    # Layout horizontal: Formulario | Lista de partidos
    layout_contenido = QHBoxLayout()
    layout_contenido.setSpacing(20)
    
    # === FORMULARIO (Izquierda) ===
    frame_formulario = QFrame()
    frame_formulario.setObjectName("frameFormulario")
    frame_formulario.setMaximumWidth(400)
    
    layout_formulario = QVBoxLayout(frame_formulario)
    layout_formulario.setSpacing(15)
    
    # Título del formulario
    lblTituloForm = QLabel("Programar Partido")
    lblTituloForm.setStyleSheet("font-size: 16px; font-weight: bold;")
    lblTituloForm.setAlignment(Qt.AlignCenter)
    layout_formulario.addWidget(lblTituloForm)
    
    # Importar widgets para el formulario
    from PySide6.QtWidgets import QComboBox, QDateEdit, QTimeEdit
    from PySide6.QtCore import QDate, QTime
    
    # Equipo A
    lblEquipoA = QLabel("Equipo A:")
    comboEquipoA = QComboBox()
    comboEquipoA.setObjectName("comboEquipoA")
    layout_formulario.addWidget(lblEquipoA)
    layout_formulario.addWidget(comboEquipoA)
    
    # Equipo B
    lblEquipoB = QLabel("Equipo B:")
    comboEquipoB = QComboBox()
    comboEquipoB.setObjectName("comboEquipoB")
    layout_formulario.addWidget(lblEquipoB)
    layout_formulario.addWidget(comboEquipoB)
    
    # Fecha
    lblFecha = QLabel("Fecha:")
    dateFecha = QDateEdit()
    dateFecha.setObjectName("dateFecha")
    dateFecha.setCalendarPopup(True)
    dateFecha.setDate(QDate.currentDate())
    dateFecha.setDisplayFormat("dd/MM/yyyy")
    layout_formulario.addWidget(lblFecha)
    layout_formulario.addWidget(dateFecha)
    
    # Hora
    lblHora = QLabel("Hora:")
    timeHora = QTimeEdit()
    timeHora.setObjectName("timeHora")
    timeHora.setTime(QTime(18, 0))
    timeHora.setDisplayFormat("HH:mm")
    layout_formulario.addWidget(lblHora)
    layout_formulario.addWidget(timeHora)
    
    # Árbitro
    lblArbitro = QLabel("Árbitro:")
    comboArbitro = QComboBox()
    comboArbitro.setObjectName("comboArbitro")
    layout_formulario.addWidget(lblArbitro)
    layout_formulario.addWidget(comboArbitro)
    
    # Eliminatoria
    lblEliminatoria = QLabel("Eliminatoria:")
    comboEliminatoria = QComboBox()
    comboEliminatoria.setObjectName("comboEliminatoria")
    comboEliminatoria.addItems([
        "Previa",
        "Dieciseisavos",
        "Octavos",
        "Cuartos",
        "Semifinal",
        "Final"
    ])
    comboEliminatoria.setCurrentIndex(2)  # Octavos por defecto
    layout_formulario.addWidget(lblEliminatoria)
    layout_formulario.addWidget(comboEliminatoria)
    
    # Botones
    layout_botones = QHBoxLayout()
    btnGuardar = QPushButton("GUARDAR")
    btnGuardar.setObjectName("btnGuardar")
    btnLimpiar = QPushButton("LIMPIAR")
    btnLimpiar.setObjectName("btnLimpiar")
    layout_botones.addWidget(btnGuardar)
    layout_botones.addWidget(btnLimpiar)
    layout_formulario.addLayout(layout_botones)
    
    layout_formulario.addStretch()
    layout_contenido.addWidget(frame_formulario)
    
    # === LISTA DE PARTIDOS (Derecha) ===
    frame_lista = QFrame()
    frame_lista.setObjectName("frameLista")
    
    layout_lista = QVBoxLayout(frame_lista)
    layout_lista.setSpacing(15)
    
    # Título
    lblTituloLista = QLabel("Partidos Programados")
    lblTituloLista.setStyleSheet("font-size: 18px; font-weight: bold; color: #2E7D32;")
    lblTituloLista.setAlignment(Qt.AlignCenter)
    layout_lista.addWidget(lblTituloLista)
    
    # Árbol de partidos (agrupados por eliminatoria)
    treePartidos = QTreeWidget()
    treePartidos.setObjectName("treePartidos")
    treePartidos.setHeaderLabels(["Partido", "Fecha/Hora", "Árbitro"])
    treePartidos.header().setSectionResizeMode(0, QHeaderView.Stretch)
    treePartidos.header().setSectionResizeMode(1, QHeaderView.ResizeToContents)
    treePartidos.header().setSectionResizeMode(2, QHeaderView.ResizeToContents)
    layout_lista.addWidget(treePartidos)
    
    # Botones de acción para el partido seleccionado
    layout_acciones = QHBoxLayout()
    btnEditar = QPushButton("EDITAR")
    btnEditar.setObjectName("btnEditar")
    btnEliminar = QPushButton("ELIMINAR")
    btnEliminar.setObjectName("btnEliminar")
    layout_acciones.addWidget(btnEditar)
    layout_acciones.addWidget(btnEliminar)
    layout_lista.addLayout(layout_acciones)
    
    layout_contenido.addWidget(frame_lista)
    
    layout_principal.addLayout(layout_contenido)
    
    return widget, reloj
