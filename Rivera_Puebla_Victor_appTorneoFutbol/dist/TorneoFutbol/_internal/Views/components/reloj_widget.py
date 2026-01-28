from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Dict, Optional, Tuple

from PySide6.QtCore import QCoreApplication, QDateTime, QEvent, QFile, QTime, QTimer, QTranslator, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QAbstractSpinBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QLabel,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QTimeEdit,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtUiTools import QUiLoader


_ES_TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "RelojDigital": {
        "UI file not found: {path}": "No se encontró el archivo de interfaz: {path}",
        "Unable to open {path}": "No se puede abrir {path}",
        "Could not load UI from {path}": "No se pudo cargar la interfaz desde {path}",
        "Missing widget {name} in UI": "Falta el widget {name} en la interfaz",
        "Alarm": "Alarma",
        "Reset": "Reiniciar",
        "Clock": "Reloj",
        "Timer": "Temporizador",
        "Mode: {mode}": "Modo: {mode}",
        "Timer ({behavior})": "Temporizador ({behavior})",
        "Switch to Timer": "Cambiar a temporizador",
        "Switch to Clock": "Cambiar a reloj",
        "Switch to Alarm": "Cambiar a alarma",
        "Pause": "Pausa",
        "Start": "Iniciar",
        "Digital Clock": "Reloj digital",
        "Language": "Idioma",
        "English": "Inglés",
        "Spanish": "Español",
        "Use Stopwatch": "Usar cronómetro",
        "Use Countdown": "Usar cuenta atrás",
        "Countdown": "Cuenta atrás",
        "Stopwatch": "Cronómetro",
        "Alarm disabled": "Alarma desactivada",
        "Next alarm at {time} ({countdown})": "Próxima alarma a las {time} ({countdown})",
        "Set Alarm": "Configurar alarma",
        "Alarm time (HH:MM)": "Hora de la alarma (HH:MM)",
        "Invalid time format": "Formato de hora no válido",
        "Timer finished": "El temporizador ha finalizado",
    }
}


class InlineTranslator(QTranslator):
    def __init__(self, translations: Dict[str, Dict[str, str]]) -> None:
        super().__init__()
        self._translations = translations

    def translate(self, context, sourceText, disambiguation=None, n=-1):  # type: ignore[override]
        context_key = context or ""
        context_map = self._translations.get(context_key, {})
        text = context_map.get(sourceText)
        return text if text is not None else sourceText


class RelojDigital(QWidget):
    """Widget reutilizable que muestra un reloj digital con temporizador y alarma."""

    alarmTriggered = Signal(str)
    timerFinished = Signal()
    modeChanged = Signal(str)

    class Mode(Enum):
        CLOCK = "clock"
        TIMER = "timer"
        ALARM = "alarm"

    class TimerBehavior(Enum):
        COUNTDOWN = "countdown"
        STOPWATCH = "stopwatch"

    MODE_SEQUENCE: tuple["RelojDigital.Mode", ...] = (
        Mode.CLOCK,
        Mode.TIMER,
        Mode.ALARM,
    )

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._root = self._load_ui()
        self._displayLabel: QLabel = self._require_child("displayLabel", QLabel)
        self._modeLabel: QLabel = self._require_child("modeLabel", QLabel)
        self._startStopButton: QPushButton = self._require_child("startStopButton", QPushButton)
        self._resetButton: QPushButton = self._require_child("resetButton", QPushButton)
        self._modeButton: QPushButton = self._require_child("modeButton", QPushButton)
        self._timerTypeButton: QPushButton = self._require_child("timerTypeButton", QPushButton)
        self._setAlarmButton: QPushButton = self._require_child("setAlarmButton", QPushButton)
        self._languageLabel: QLabel = self._require_child("languageLabel", QLabel)
        self._languageCombo: QComboBox = self._require_child("languageCombo", QComboBox)

        self._mode = RelojDigital.Mode.CLOCK
        self._is24Hour = True
        self._alarmEnabled = False
        self._alarmHour = 7
        self._alarmMinute = 0
        self._alarmMessage = self.tr("Alarm")
        self._alarmMessageCustom = False
        self._timerDuration = 300
        self._timerBehavior = RelojDigital.TimerBehavior.COUNTDOWN
        self._remainingSeconds = self._timerDuration
        self._elapsedSeconds = 0
        self._timerRunning = False
        self._lastAlarmStamp: Optional[Tuple[int, int]] = None
        self._languageCodes = ["es", "en"]
        self._currentLanguage = "es"
        self._translatorMap = {
            "en": None,
            "es": InlineTranslator(_ES_TRANSLATIONS),
        }
        self._activeTranslator: Optional[QTranslator] = None

        self._tick = QTimer(self)
        self._tick.setInterval(1000)
        self._tick.timeout.connect(self._on_tick)
        self._tick.start()

        self._initialize_language_combo()
        self._apply_translator()
        self._configure_responsive_widgets()
        self._connect_signals()
        self._sync_controls()
        self._refresh_clock_display()

    def _load_ui(self) -> QWidget:
        ui_path = Path(__file__).resolve().with_name("reloj.ui")
        if not ui_path.exists():
            raise FileNotFoundError(self.tr("UI file not found: {path}").format(path=ui_path))

        loader = QUiLoader()
        ui_file = QFile(str(ui_path))
        if not ui_file.open(QFile.ReadOnly):
            raise RuntimeError(self.tr("Unable to open {path}").format(path=ui_path))
        widget = loader.load(ui_file, self)
        ui_file.close()
        if widget is None:
            raise RuntimeError(self.tr("Could not load UI from {path}").format(path=ui_path))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(widget)
        return widget

    def _require_child(self, name: str, cls: type):
        widget = self._root.findChild(cls, name)  # type: ignore[arg-type]
        if widget is None:
            raise AttributeError(self.tr("Missing widget {name} in UI").format(name=name))
        return widget

    def _configure_responsive_widgets(self) -> None:
        """Configura los widgets para que sean responsive."""
        # Configurar el label principal (dígitos del reloj) para que sea responsive
        if self._displayLabel:
            self._displayLabel.setWordWrap(True)
            self._displayLabel.setMinimumHeight(40)
            self._displayLabel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self._displayLabel.setScaledContents(False)
        
        # Configurar el label de modo para que tenga wordWrap
        if self._modeLabel:
            self._modeLabel.setWordWrap(True)
            self._modeLabel.setMinimumHeight(20)
            self._modeLabel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        
        # Configurar botones para que puedan reducirse
        for button in [self._startStopButton, self._resetButton, self._modeButton, 
                       self._timerTypeButton, self._setAlarmButton]:
            if button:
                button.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)

    def _connect_signals(self) -> None:
        self._startStopButton.clicked.connect(self._handle_start_stop)
        self._resetButton.clicked.connect(self.reset)
        self._modeButton.clicked.connect(self._toggle_mode)
        self._timerTypeButton.clicked.connect(self._toggle_timer_behavior)
        self._setAlarmButton.clicked.connect(self._prompt_alarm_time)
        self._languageCombo.currentIndexChanged.connect(self._handle_language_combo_change)

    def _initialize_language_combo(self) -> None:
        self._languageCombo.blockSignals(True)
        self._languageCombo.clear()
        for code in self._languageCodes:
            self._languageCombo.addItem("", code)
        self._languageCombo.blockSignals(False)
        self._update_language_combo_texts()
        self._sync_language_selection()

    def resizeEvent(self, event):  # type: ignore[override]
        """Ajusta el tamaño de fuente del display al redimensionar."""
        super().resizeEvent(event)
        if self._displayLabel:
            # Calcular tamaño de fuente basado en el tamaño del widget
            # Usar regla de tres simple: el tamaño de fuente es proporcional al tamaño mínimo
            available_width = self.width()
            available_height = self._displayLabel.height()
            
            # Tomar el mínimo entre ancho y alto para calcular el tamaño de fuente
            min_dimension = min(available_width, available_height * 2)
            
            # Calcular tamaño de fuente: aproximadamente 10-12% del ancho disponible
            font_size = max(12, int(min_dimension * 0.10))  # Mínimo 12pt
            font_size = min(font_size, 72)  # Máximo 72pt para evitar excesos
            
            # Aplicar el nuevo tamaño de fuente
            font = self._displayLabel.font()
            if font.pointSize() != font_size:
                font.setPointSize(font_size)
                self._displayLabel.setFont(font)

    def changeEvent(self, event):  # type: ignore[override]
        super().changeEvent(event)
        if event.type() == QEvent.LanguageChange:
            self._retranslate_ui()

    def _retranslate_ui(self) -> None:
        if not self._alarmMessageCustom:
            self._alarmMessage = self.tr("Alarm")
        self._resetButton.setText(self.tr("Reset"))
        self._languageLabel.setText(self.tr("Language"))
        self._setAlarmButton.setText(self.tr("Set Alarm"))
        self._update_language_combo_texts()
        self._update_mode_label()
        self._update_mode_button()
        self._update_start_button()
        self._update_timer_type_button()

    @property
    def mode(self) -> str:
        return self._mode.value

    @mode.setter
    def mode(self, value: str | Mode) -> None:
        new_mode = self._normalize_mode(value)
        if new_mode == self._mode:
            return
        self._mode = new_mode
        self._timerRunning = False
        self._sync_controls()
        self.modeChanged.emit(self._mode.value)

    @staticmethod
    def _normalize_mode(value: str | Mode) -> Mode:
        if isinstance(value, RelojDigital.Mode):
            return value
        normalized = value.lower()
        return RelojDigital.Mode(normalized)

    @staticmethod
    def _next_mode_value(current: Optional["RelojDigital.Mode"] = None) -> "RelojDigital.Mode":
        sequence = RelojDigital.MODE_SEQUENCE
        active = current or sequence[0]
        try:
            index = sequence.index(active)
        except ValueError:
            index = 0
        return sequence[(index + 1) % len(sequence)]

    @property
    def is24Hour(self) -> bool:
        return self._is24Hour

    @is24Hour.setter
    def is24Hour(self, value: bool) -> None:
        self._is24Hour = bool(value)
        if self._mode == RelojDigital.Mode.CLOCK:
            self._refresh_clock_display()

    @property
    def alarmEnabled(self) -> bool:
        return self._alarmEnabled

    @alarmEnabled.setter
    def alarmEnabled(self, value: bool) -> None:
        self._alarmEnabled = bool(value)

    @property
    def alarmHour(self) -> int:
        return self._alarmHour

    @alarmHour.setter
    def alarmHour(self, value: int) -> None:
        self._alarmHour = max(0, min(23, int(value)))

    @property
    def alarmMinute(self) -> int:
        return self._alarmMinute

    @alarmMinute.setter
    def alarmMinute(self, value: int) -> None:
        self._alarmMinute = max(0, min(59, int(value)))

    @property
    def alarmMessage(self) -> str:
        return self._alarmMessage

    @alarmMessage.setter
    def alarmMessage(self, value: str) -> None:
        self._alarmMessage = str(value)
        self._alarmMessageCustom = True

    @property
    def timerDuration(self) -> int:
        return self._timerDuration

    @timerDuration.setter
    def timerDuration(self, value: int) -> None:
        seconds = max(0, int(value))
        self._timerDuration = seconds
        if self._timerBehavior == RelojDigital.TimerBehavior.COUNTDOWN:
            self._remainingSeconds = seconds
            self._elapsedSeconds = 0
            self._timerRunning = False
            if self._mode == RelojDigital.Mode.TIMER:
                self._refresh_timer_display()
                self._update_start_button()

    def start(self) -> None:
        if self._mode != RelojDigital.Mode.TIMER:
            return
        self._timerRunning = True
        self._update_start_button()

    def stop(self) -> None:
        if self._mode != RelojDigital.Mode.TIMER:
            return
        self._timerRunning = False
        self._update_start_button()

    def reset(self) -> None:
        if self._mode != RelojDigital.Mode.TIMER:
            return
        self._timerRunning = False
        if self._timerBehavior == RelojDigital.TimerBehavior.COUNTDOWN:
            self._remainingSeconds = self._timerDuration
            self._elapsedSeconds = 0
        else:
            self._elapsedSeconds = 0
        self._refresh_timer_display()
        self._update_start_button()

    def _handle_start_stop(self) -> None:
        if self._mode != RelojDigital.Mode.TIMER:
            return
        if self._timerRunning:
            self.stop()
        else:
            self.start()

    def _toggle_mode(self) -> None:
        self.mode = self._next_mode_value(self._mode)

    def _sync_controls(self) -> None:
        is_timer = self._mode == RelojDigital.Mode.TIMER
        self._startStopButton.setEnabled(is_timer)
        self._resetButton.setEnabled(is_timer)
        self._update_mode_label()
        self._update_mode_button()
        if self._mode == RelojDigital.Mode.CLOCK:
            self._refresh_clock_display()
        elif self._mode == RelojDigital.Mode.TIMER:
            self._refresh_timer_display()
        else:
            self._refresh_alarm_display()
        self._update_start_button()
        self._update_timer_type_button()

    def _update_mode_label(self) -> None:
        if self._mode == RelojDigital.Mode.CLOCK:
            mode_text = self.tr("Clock")
        elif self._mode == RelojDigital.Mode.TIMER:
            behavior = self.tr("Countdown") if self._timerBehavior == RelojDigital.TimerBehavior.COUNTDOWN else self.tr("Stopwatch")
            mode_text = self.tr("Timer ({behavior})").format(behavior=behavior)
        else:
            mode_text = self.tr("Alarm")
        self._modeLabel.setText(self.tr("Mode: {mode}").format(mode=mode_text))

    def _update_mode_button(self) -> None:
        next_mode = self._next_mode_value(self._mode)
        if next_mode == RelojDigital.Mode.CLOCK:
            text = self.tr("Switch to Clock")
        elif next_mode == RelojDigital.Mode.TIMER:
            text = self.tr("Switch to Timer")
        else:
            text = self.tr("Switch to Alarm")
        self._modeButton.setText(text)

    def _update_start_button(self) -> None:
        text = self.tr("Pause") if self._timerRunning else self.tr("Start")
        self._startStopButton.setText(text)

    def _update_timer_type_button(self) -> None:
        is_timer = self._mode == RelojDigital.Mode.TIMER
        self._timerTypeButton.setEnabled(is_timer)
        if self._timerBehavior == RelojDigital.TimerBehavior.COUNTDOWN:
            text = self.tr("Use Stopwatch")
        else:
            text = self.tr("Use Countdown")
        self._timerTypeButton.setText(text)

    def _on_tick(self) -> None:
        if self._mode == RelojDigital.Mode.CLOCK:
            self._refresh_clock_display()
        elif self._mode == RelojDigital.Mode.TIMER:
            self._advance_timer()
            self._refresh_timer_display()
        else:
            self._refresh_alarm_display()
        self._check_alarm()

    def _refresh_clock_display(self) -> None:
        now = QDateTime.currentDateTime()
        time = now.time()
        fmt = "hh:mm:ss AP" if not self._is24Hour else "HH:mm:ss"
        text = time.toString(fmt)
        if self._displayLabel.text() != text:
            self._displayLabel.setText(text)

    def _refresh_timer_display(self) -> None:
        seconds = self._remainingSeconds if self._timerBehavior == RelojDigital.TimerBehavior.COUNTDOWN else self._elapsedSeconds
        formatted = self._format_seconds(seconds)
        if self._displayLabel.text() != formatted:
            self._displayLabel.setText(formatted)

    def _refresh_alarm_display(self) -> None:
        if not self._alarmEnabled:
            text = self.tr("Alarm disabled")
        else:
            next_alarm = self._next_alarm_datetime()
            if next_alarm is None:
                text = self.tr("Alarm disabled")
            else:
                fmt = "HH:mm" if self._is24Hour else "hh:mm AP"
                alarm_time = next_alarm.time().toString(fmt)
                seconds = max(0, QDateTime.currentDateTime().secsTo(next_alarm))
                countdown = self._format_seconds(seconds)
                text = self.tr("Next alarm at {time} ({countdown})").format(time=alarm_time, countdown=countdown)
        if self._displayLabel.text() != text:
            self._displayLabel.setText(text)

    def _next_alarm_datetime(self) -> Optional[QDateTime]:
        if not self._alarmEnabled:
            return None
        now = QDateTime.currentDateTime()
        target_time = QTime(self._alarmHour, self._alarmMinute)
        target = QDateTime(now.date(), target_time)
        if target <= now:
            target = target.addDays(1)
        return target

    @staticmethod
    def _format_seconds(seconds: int) -> str:
        seconds = max(0, seconds)
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        remaining = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{remaining:02d}"

    def _advance_timer(self) -> None:
        if not self._timerRunning:
            return
        if self._timerBehavior == RelojDigital.TimerBehavior.COUNTDOWN:
            if self._remainingSeconds > 0:
                self._remainingSeconds -= 1
            if self._remainingSeconds == 0:
                self._timerRunning = False
                self._update_start_button()
                self.timerFinished.emit()
                self._notify_timer_finished()
        else:
            self._elapsedSeconds += 1

    def _check_alarm(self) -> None:
        if not self._alarmEnabled:
            return
        now = QDateTime.currentDateTime()
        time = now.time()
        if time.hour() != self._alarmHour or time.minute() != self._alarmMinute:
            return
        stamp = (now.date().toJulianDay(), time.minute())
        if stamp == self._lastAlarmStamp:
            return
        self._lastAlarmStamp = stamp
        message = self._alarmMessage or self.tr("Alarm")
        self.alarmTriggered.emit(message)
        self._notify_alarm_trigger(message)

    def _notify_alarm_trigger(self, message: str) -> None:
        QMessageBox.information(self, self.tr("Alarm"), message)

    def _notify_timer_finished(self) -> None:
        QMessageBox.information(self, self.tr("Timer"), self.tr("Timer finished"))

    def _toggle_timer_behavior(self) -> None:
        new_behavior = (
            RelojDigital.TimerBehavior.STOPWATCH
            if self._timerBehavior == RelojDigital.TimerBehavior.COUNTDOWN
            else RelojDigital.TimerBehavior.COUNTDOWN
        )
        self.timerBehavior = new_behavior.value

    def _prompt_alarm_time(self) -> None:
        dialog = QDialog(self)
        dialog.setWindowTitle(self.tr("Set Alarm"))
        layout = QVBoxLayout(dialog)
        label = QLabel(self.tr("Alarm time (HH:MM)"), dialog)
        layout.addWidget(label)

        time_edit = QTimeEdit(dialog)
        time_edit.setDisplayFormat("HH:mm")
        time_edit.setTime(QTime(self._alarmHour, self._alarmMinute))
        time_edit.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.UpDownArrows)
        layout.addWidget(time_edit)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, parent=dialog)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        if dialog.exec() != QDialog.Accepted:
            return

        time = time_edit.time()
        self.alarmHour = time.hour()
        self.alarmMinute = time.minute()
        self.alarmEnabled = True
        if self._mode == RelojDigital.Mode.ALARM:
            self._refresh_alarm_display()

    @property
    def timerBehavior(self) -> str:
        return self._timerBehavior.value

    @timerBehavior.setter
    def timerBehavior(self, value: str | TimerBehavior) -> None:
        behavior = self._normalize_timer_behavior(value)
        if behavior == self._timerBehavior:
            return
        self._timerBehavior = behavior
        self._timerRunning = False
        if behavior == RelojDigital.TimerBehavior.COUNTDOWN:
            self._remainingSeconds = self._timerDuration
            self._elapsedSeconds = 0
        else:
            self._elapsedSeconds = 0
            self._remainingSeconds = 0
        self._sync_controls()

    @staticmethod
    def _normalize_timer_behavior(value: str | TimerBehavior) -> TimerBehavior:
        if isinstance(value, RelojDigital.TimerBehavior):
            return value
        normalized = value.lower()
        return RelojDigital.TimerBehavior(normalized)

    def _handle_language_combo_change(self, index: int) -> None:
        code = self._languageCombo.itemData(index)
        if code:
            self.setLanguage(code)

    def _update_language_combo_texts(self) -> None:
        self._languageCombo.blockSignals(True)
        for idx, code in enumerate(self._languageCodes):
            if idx < self._languageCombo.count():
                self._languageCombo.setItemText(idx, self._language_label_text(code))
        self._languageCombo.blockSignals(False)

    def _language_label_text(self, code: str) -> str:
        return self.tr("English") if code == "en" else self.tr("Spanish")

    def _sync_language_selection(self) -> None:
        self._languageCombo.blockSignals(True)
        try:
            index = self._languageCodes.index(self._currentLanguage)
        except ValueError:
            index = 0
        self._languageCombo.setCurrentIndex(index)
        self._languageCombo.blockSignals(False)

    def setLanguage(self, code: Optional[str]) -> None:
        normalized = self._normalize_language(code)
        if normalized == self._currentLanguage:
            return
        self._currentLanguage = normalized
        self._apply_translator()
        self._sync_language_selection()

    def _normalize_language(self, code: Optional[str]) -> str:
        if not code:
            return "es"
        lowered = code.lower()
        return "es" if lowered.startswith("es") else "en"

    def _apply_translator(self) -> None:
        app = QCoreApplication.instance()
        if app is None:
            return
        if self._activeTranslator is not None:
            app.removeTranslator(self._activeTranslator)
        translator = self._translatorMap.get(self._currentLanguage)
        if translator is not None:
            app.installTranslator(translator)
        self._activeTranslator = translator
        self._retranslate_ui()

    @property
    def language(self) -> str:
        return self._currentLanguage

