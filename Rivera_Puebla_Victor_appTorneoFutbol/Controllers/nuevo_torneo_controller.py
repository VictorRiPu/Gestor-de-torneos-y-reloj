"""
Controlador para el diálogo de creación de nuevo torneo.
Gestiona la selección de equipos y validación para iniciar un torneo.
"""

from PySide6.QtWidgets import QMessageBox, QListWidgetItem, QListWidget, QLabel, QPushButton, QLineEdit
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QColor

from Models.database import DatabaseManager, obtener_ruta_recurso
from Models.torneo_logic import TorneoLogic


class NuevoTorneoController:
    """Controlador para creación de nuevo torneo."""
    
    def __init__(self, dialog, main_controller=None):
        """
        Inicializa el controlador.
        
        Args:
            dialog: Diálogo cargado con QUiLoader
            main_controller: Controlador principal (opcional)
        """
        self.dialog = dialog
        self.main_controller = main_controller
        self.db = DatabaseManager()
        self.torneo_logic = TorneoLogic()
        
        # Referencias a widgets
        self.txtNombreTorneo = self.dialog.findChild(QLineEdit, "txtNombreTorneo")
        self.listEquiposDisponibles = self.dialog.findChild(QListWidget, "listEquiposDisponibles")
        self.lblEquiposSeleccionados = self.dialog.findChild(QLabel, "lblEquiposSeleccionados")
        self.lblAdvertencia = self.dialog.findChild(QLabel, "lblAdvertencia")
        self.btnCrearTorneo = self.dialog.findChild(QPushButton, "btnCrearTorneo")
        self.btnCancelar = self.dialog.findChild(QPushButton, "btnCancelar")
        
        # Conectar señales
        self._conectar_senales()
        
        # Cargar equipos disponibles
        self.cargar_equipos_disponibles()
        
    def _conectar_senales(self):
        """Conecta las señales de los widgets."""
        if self.listEquiposDisponibles:
            self.listEquiposDisponibles.itemSelectionChanged.connect(self.actualizar_contador)
            
        if self.btnCrearTorneo:
            self.btnCrearTorneo.clicked.connect(self.crear_torneo)
            
        if self.btnCancelar:
            self.btnCancelar.clicked.connect(self.dialog.reject)
            
    def cargar_equipos_disponibles(self):
        """Carga todos los equipos disponibles en la lista."""
        if not self.listEquiposDisponibles:
            return
            
        self.listEquiposDisponibles.clear()
        
        # Obtener todos los equipos
        equipos = self.db.obtener_todos_equipos()
        
        for equipo in equipos:
            equipo_id = equipo['id']
            nombre = equipo['nombre']
            curso = equipo.get('curso', '')
            escudo_path = equipo.get('escudo', '')
            
            # Contar jugadores del equipo
            cantidad_jugadores = self.db.contar_jugadores_por_equipo(equipo_id)
            
            # Crear texto del item
            texto = f"{nombre} ({curso})" if curso else nombre
            if cantidad_jugadores < 7:
                texto += f" - ⚠️ {cantidad_jugadores} jugadores"
            else:
                texto += f" - ✓ {cantidad_jugadores} jugadores"
                
            # Crear item
            item = QListWidgetItem(texto)
            item.setData(Qt.UserRole, equipo_id)
            
            # Agregar icono del escudo
            if escudo_path:
                ruta_escudo = obtener_ruta_recurso(f"Resources/img/{escudo_path}")
                icon = QIcon(ruta_escudo)
                item.setIcon(icon)
                
            # Marcar en rojo si no tiene suficientes jugadores
            if cantidad_jugadores < 7:
                item.setForeground(QColor(200, 50, 50))
                
            self.listEquiposDisponibles.addItem(item)
            
    def actualizar_contador(self):
        """Actualiza el contador de equipos seleccionados."""
        if not self.listEquiposDisponibles or not self.lblEquiposSeleccionados:
            return
            
        cantidad = len(self.listEquiposDisponibles.selectedItems())
        self.lblEquiposSeleccionados.setText(f"Equipos seleccionados: {cantidad}")
        
        # Validar si es un número válido (8, 16 o 32)
        if cantidad not in [8, 16, 32]:
            if self.lblAdvertencia:
                self.lblAdvertencia.setStyleSheet("color: #f44336;")
                self.lblAdvertencia.setText("⚠️ Debes seleccionar 8, 16 o 32 equipos")
        else:
            if self.lblAdvertencia:
                self.lblAdvertencia.setStyleSheet("color: #4CAF50;")
                self.lblAdvertencia.setText("✓ Cantidad de equipos válida")
                
    def crear_torneo(self):
        """Crea un nuevo torneo con los equipos seleccionados."""
        # Validar nombre del torneo
        if not self.txtNombreTorneo:
            return
            
        nombre_torneo = self.txtNombreTorneo.text().strip()
        if not nombre_torneo:
            QMessageBox.warning(
                self.dialog,
                "Error",
                "Ingresa un nombre para el torneo."
            )
            return
            
        # Obtener equipos seleccionados
        items_seleccionados = self.listEquiposDisponibles.selectedItems()
        equipos_ids = [item.data(Qt.UserRole) for item in items_seleccionados]
        
        # Validar cantidad de equipos
        if len(equipos_ids) not in [8, 16, 32]:
            QMessageBox.warning(
                self.dialog,
                "Error",
                "Debes seleccionar 8, 16 o 32 equipos para el torneo."
            )
            return
            
        # Validar que todos los equipos tengan al menos 7 jugadores
        valido, equipos_invalidos = self.torneo_logic.validar_equipos_para_torneo(equipos_ids)
        
        if not valido:
            # Mostrar mensaje con equipos que necesitan más jugadores
            mensaje = "Los siguientes equipos necesitan más jugadores (mínimo 7):\n\n"
            for nombre_equipo, faltantes in equipos_invalidos.items():
                mensaje += f"• {nombre_equipo}: faltan {faltantes} jugador(es)\n"
                    
            QMessageBox.warning(
                self.dialog,
                "Equipos Inválidos",
                mensaje
            )
            return
            
        # Confirmar creación
        respuesta = QMessageBox.question(
            self.dialog,
            "Confirmar Creación",
            f"¿Crear torneo '{nombre_torneo}' con {len(equipos_ids)} equipos?\n\n"
            "Esto generará automáticamente los emparejamientos.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if respuesta != QMessageBox.Yes:
            return
            
        # Crear torneo
        try:
            exito, mensaje = self.torneo_logic.iniciar_nuevo_torneo(nombre_torneo, equipos_ids)
            
            if exito:
                # Actualizar brackets si existe el controlador de clasificación
                if hasattr(self.main_controller, 'clasificacion_controller') and self.main_controller.clasificacion_controller:
                    self.main_controller.clasificacion_controller.cargar_brackets()
                
                QMessageBox.information(
                    self.dialog,
                    "Éxito",
                    f"Torneo '{nombre_torneo}' creado correctamente.\n\n"
                    f"Se han generado {len(equipos_ids)//2} partidos para la primera ronda."
                )
                self.dialog.accept()
            else:
                QMessageBox.critical(
                    self.dialog,
                    "Error",
                    f"No se pudo crear el torneo:\n{mensaje}"
                )
                
        except Exception as e:
            QMessageBox.critical(
                self.dialog,
                "Error",
                f"Error al crear torneo: {str(e)}"
            )
