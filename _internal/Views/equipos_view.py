"""
Vista para la gestión de equipos.
Crea la interfaz de gestión de equipos dinámicamente.
"""

from PySide6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QFrame,
                               QLabel, QLineEdit, QPushButton, QComboBox,
                               QListWidget, QScrollArea)
from PySide6.QtCore import Qt, QSize


def crear_vista_equipos():
    """
    Crea y retorna la vista de gestión de equipos.
    
    Returns:
        QWidget: Widget con la interfaz de equipos
    """
    widget = QWidget()
    widget.setObjectName("pagina_equipos")
    
    # Layout principal
    layout_principal = QVBoxLayout(widget)
    layout_principal.setContentsMargins(20, 20, 20, 20)
    
    # Botón volver
    btnVolver = QPushButton("← VOLVER")
    btnVolver.setObjectName("btnVolver")
    btnVolver.setMaximumWidth(150)
    layout_principal.addWidget(btnVolver)
    
    # Layout horizontal: formulario | lista
    layout_contenido = QHBoxLayout()
    layout_contenido.setSpacing(20)
    
    # === FORMULARIO (Izquierda) ===
    frame_formulario = QFrame()
    frame_formulario.setObjectName("frameFormulario")
    frame_formulario.setMaximumWidth(400)
    
    layout_formulario = QVBoxLayout(frame_formulario)
    layout_formulario.setSpacing(15)
    
    # Título
    lblTitulo = QLabel("Gestión de equipos")
    lblTitulo.setStyleSheet("font-size: 20px; font-weight: bold; color: #FFD700;")
    lblTitulo.setAlignment(Qt.AlignCenter)
    layout_formulario.addWidget(lblTitulo)
    
    # Nombre
    lblNombre = QLabel("Nombre del equipo:")
    lblNombre.setStyleSheet("color: #FFD700;")
    txtNombre = QLineEdit()
    txtNombre.setObjectName("txtNombre")
    txtNombre.setPlaceholderText("Ej: Real Madrid")
    layout_formulario.addWidget(lblNombre)
    layout_formulario.addWidget(txtNombre)
    
    # Curso
    lblCurso = QLabel("Curso:")
    lblCurso.setStyleSheet("color: #FFD700;")
    txtCurso = QLineEdit()
    txtCurso.setObjectName("txtCurso")
    txtCurso.setPlaceholderText("Ej: 1º ESO, 2º DAM")
    layout_formulario.addWidget(lblCurso)
    layout_formulario.addWidget(txtCurso)
    
    # Color
    lblColor = QLabel("Color del equipo:")
    lblColor.setStyleSheet("color: #FFD700;")
    btnSeleccionarColor = QPushButton("Seleccionar color")
    btnSeleccionarColor.setObjectName("btnSeleccionarColor")
    btnSeleccionarColor.setStyleSheet("color: #1E1E1E;")
    layout_formulario.addWidget(lblColor)
    layout_formulario.addWidget(btnSeleccionarColor)
    
    # Escudo
    lblEscudo = QLabel("Escudo:")
    lblEscudo.setStyleSheet("color: #FFD700;")
    comboEscudos = QComboBox()
    comboEscudos.setObjectName("comboEscudos")
    comboEscudos.setIconSize(QSize(48, 48))
    comboEscudos.setMinimumHeight(60)
    layout_formulario.addWidget(lblEscudo)
    layout_formulario.addWidget(comboEscudos)
    
    # Vista previa del escudo
    lblVistaPrevia = QLabel()
    lblVistaPrevia.setObjectName("lblVistaPrevia")
    lblVistaPrevia.setFixedSize(80, 80)
    lblVistaPrevia.setAlignment(Qt.AlignCenter)
    lblVistaPrevia.setStyleSheet("border: 2px dashed #4A5F7F; border-radius: 10px;")
    layout_formulario.addWidget(lblVistaPrevia)
    
    # Botones
    layout_botones = QHBoxLayout()
    btnGuardar = QPushButton("GUARDAR")
    btnGuardar.setObjectName("btnGuardar")
    btnGuardar.setStyleSheet("""color: #1E1E1E;""")
    btnLimpiar = QPushButton("LIMPIAR")
    btnLimpiar.setObjectName("btnLimpiar")
    btnLimpiar.setStyleSheet("""color: #000000;""")
    layout_botones.addWidget(btnGuardar)
    layout_botones.addWidget(btnLimpiar)
    layout_formulario.addLayout(layout_botones)
    
    layout_formulario.addStretch()
    
    layout_contenido.addWidget(frame_formulario)
    
    # === LISTA (Derecha) ===
    frame_lista = QFrame()
    frame_lista.setObjectName("frameLista")
    
    layout_lista = QVBoxLayout(frame_lista)
    layout_lista.setSpacing(15)
    
    # Título
    lblTituloLista = QLabel("Equipos registrados")
    lblTituloLista.setStyleSheet("font-size: 18px; font-weight: bold; color: #FFFFFF;")
    lblTituloLista.setAlignment(Qt.AlignCenter)
    layout_lista.addWidget(lblTituloLista)
    
    # Buscador
    txtBuscar = QLineEdit()
    txtBuscar.setObjectName("txtBuscar")
    txtBuscar.setPlaceholderText("🔍 Buscar por nombre o curso...")
    layout_lista.addWidget(txtBuscar)
    
    # Lista de equipos
    scroll_area = QScrollArea()
    scroll_area.setWidgetResizable(True)
    scroll_area.setFrameShape(QFrame.NoFrame)
    
    listEquipos = QListWidget()
    listEquipos.setObjectName("listEquipos")
    scroll_area.setWidget(listEquipos)
    
    layout_lista.addWidget(scroll_area)
    
    # Botón para ver jugadores del equipo seleccionado
    btnVerJugadores = QPushButton("VER JUGADORES DEL EQUIPO")
    btnVerJugadores.setObjectName("btnVerJugadores")
    layout_lista.addWidget(btnVerJugadores)
    
    # Botones de edición/eliminación
    layout_acciones = QHBoxLayout()
    btnEditar = QPushButton("EDITAR")
    btnEditar.setStyleSheet("""color: #000000;
    background-color: #4CAF50;
    border-radius: 5px;
    padding: 10px;
    font-weight: bold;""")
    btnEditar.setObjectName("btnEditar")
    btnEliminar = QPushButton("ELIMINAR")
    btnEliminar.setStyleSheet("""color: #000000;
    background-color: #4CAF50;
    border-radius: 5px;
    padding: 10px;
    font-weight: bold;""")
    btnEliminar.setObjectName("btnEliminar")
    layout_acciones.addWidget(btnEditar)
    layout_acciones.addWidget(btnEliminar)
    layout_lista.addLayout(layout_acciones)
    
    layout_contenido.addWidget(frame_lista)
    
    layout_principal.addLayout(layout_contenido)
    
    return widget
