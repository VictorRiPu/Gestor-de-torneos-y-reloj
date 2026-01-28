"""
Controlador del diálogo de onboarding (ayuda).
Gestiona la navegación entre los pasos del tutorial.
"""

from PySide6.QtWidgets import QDialog, QStackedWidget, QPushButton, QLabel


class OnboardingController:
    """
    Controlador para el diálogo de onboarding que muestra
    los pasos para usar la aplicación.
    """
    
    def __init__(self, dialog: QDialog):
        """
        Inicializa el controlador del onboarding.
        
        Args:
            dialog: Diálogo del onboarding cargado desde .ui
        """
        self.dialog = dialog
        self.paso_actual = 0
        self.total_pasos = 4
        
        # Obtener widgets
        self.stacked_pasos = self.dialog.findChild(QStackedWidget, "stackedPasos")
        self.btn_anterior = self.dialog.findChild(QPushButton, "btnAnterior")
        self.btn_siguiente = self.dialog.findChild(QPushButton, "btnSiguiente")
        self.btn_cerrar = self.dialog.findChild(QPushButton, "btnCerrar")
        self.lbl_progreso = self.dialog.findChild(QLabel, "lblProgreso")
        
        # Conectar señales
        self._conectar_senales()
        
        # Actualizar UI inicial
        self._actualizar_ui()
        
    def _conectar_senales(self):
        """Conecta las señales de los botones."""
        if self.btn_anterior:
            self.btn_anterior.clicked.connect(self.ir_anterior)
            
        if self.btn_siguiente:
            self.btn_siguiente.clicked.connect(self.ir_siguiente)
            
        if self.btn_cerrar:
            self.btn_cerrar.clicked.connect(self.dialog.accept)
            
    def ir_anterior(self):
        """Navega al paso anterior."""
        if self.paso_actual > 0:
            self.paso_actual -= 1
            self._actualizar_ui()
            
    def ir_siguiente(self):
        """Navega al paso siguiente."""
        if self.paso_actual < self.total_pasos - 1:
            self.paso_actual += 1
            self._actualizar_ui()
            
    def _actualizar_ui(self):
        """Actualiza la interfaz según el paso actual."""
        # Cambiar página del stacked widget
        if self.stacked_pasos:
            self.stacked_pasos.setCurrentIndex(self.paso_actual)
            
        # Actualizar texto de progreso
        if self.lbl_progreso:
            self.lbl_progreso.setText(f"Paso {self.paso_actual + 1} de {self.total_pasos}")
            
        # Habilitar/deshabilitar botón anterior
        if self.btn_anterior:
            self.btn_anterior.setEnabled(self.paso_actual > 0)
            
        # Cambiar texto del botón siguiente en el último paso
        if self.btn_siguiente:
            if self.paso_actual == self.total_pasos - 1:
                self.btn_siguiente.setVisible(False)
            else:
                self.btn_siguiente.setVisible(True)
                self.btn_siguiente.setText("Siguiente")
