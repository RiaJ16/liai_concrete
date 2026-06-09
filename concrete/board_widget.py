from datetime import datetime, timezone

from PySide6.QtWidgets import QWidget, QGridLayout, QVBoxLayout, QLabel, \
    QSizePolicy, QHBoxLayout

from concrete import conector
from concrete.sensor_mini_widget import SensorMiniWidget
from concrete.sensor_widget import SensorWidget
from ui.ui_board import Ui_board
from ui.ui_board_mini import Ui_board_mini

# Minutos sin reportar tras los cuales el sensor se marca como "caído" (rojo).
UMBRAL_SIN_REPORTAR_MIN = 90


class BaseBoardWidget(QWidget):

    def __init__(self, tarjeta, abrir_historial=None, parent=None):
        super().__init__(parent)
        self.tarjeta = tarjeta
        self.abrir_historial = abrir_historial
        # Los renglones (Temperatura/Humedad) ya vienen en la tarjeta, calculados
        # en una sola consulta. NO se consulta la nube aquí (no bloquea la UI).
        self.sensores = getattr(tarjeta, "sensores", None) or []

    def mostrar_datos(self, event):
        if self.abrir_historial is not None:
            self.abrir_historial(self.tarjeta, self.sensores)
        event.accept()

    def set_common_ui(self, lbl_nombre, widget_tags):
        lbl_nombre.setText(self.tarjeta.nombre)
        layout = widget_tags.layout()
        for tag in self.tarjeta.tags:
            label = QLabel(tag)
            self.customize_tag_label(label)   # hook
            layout.insertWidget(layout.count() - 1, label)
        # Indicador "última vez visto" con color de alerta.
        texto, alerta = self._estado_ultima()
        estado = QLabel(texto)
        self.customize_tag_label(estado)
        color = "#e74c3c" if alerta else "#2ecc71"
        peso = "bold" if alerta else "normal"
        estado.setStyleSheet(f"color: {color}; font-weight: {peso};")
        layout.insertWidget(layout.count() - 1, estado)

    def _estado_ultima(self):
        """Devuelve (texto, alerta) según hace cuánto reportó el sensor."""
        ult = getattr(self.tarjeta, "ultima_fecha", None)
        if ult is None:
            return "sin datos", True
        minutos = (datetime.now(timezone.utc) - ult).total_seconds() / 60
        alerta = minutos > UMBRAL_SIN_REPORTAR_MIN
        if minutos < 1:
            texto = "hace <1 min"
        elif minutos < 60:
            texto = f"hace {int(minutos)} min"
        elif minutos < 60 * 24:
            texto = f"hace {int(minutos // 60)} h"
        else:
            texto = f"hace {int(minutos // (60 * 24))} d"
        return texto, alerta

    # Hook for subclasses
    def customize_tag_label(self, label):
        pass

    # Shared helper
    def populate_common_board(self, widget_sensores):
        layout = self.make_layout()                # hook
        sensor_widget = self.make_sensor_widget()  # hook
        for sensor in self.sensores:
            sensor_widget.add_sensor(sensor)
        layout.addWidget(sensor_widget)
        widget_sensores.setLayout(layout)

    # Hooks
    def make_layout(self):
        raise NotImplementedError()

    def make_sensor_widget(self):
        raise NotImplementedError()


class BoardWidget(BaseBoardWidget, Ui_board):

    def __init__(self, tarjeta, abrir_historial=None, parent=None):
        super().__init__(tarjeta, abrir_historial, parent)
        self.setupUi(self)
        self.set_common_ui(self.lbl_nombre, self.widget_tags)
        self.populate_common_board(self.widget_sensores)
        self.btn_historial.setVisible(False)
        self.__signals()

    def __signals(self):
        self.card_frame.mouseReleaseEvent = self.mostrar_datos

    def make_layout(self):
        return QVBoxLayout()

    def make_sensor_widget(self):
        return SensorWidget()


class BoardMiniWidget(BaseBoardWidget, Ui_board_mini):

    def __init__(self, tarjeta, abrir_historial=None, parent=None):
        super().__init__(tarjeta, abrir_historial, parent)
        self.setupUi(self)
        self.set_common_ui(self.lbl_nombre, self.widget_tags)
        self.populate_common_board(self.widget_sensores)
        self.__signals()

    def __signals(self):
        self.mini_frame.mouseReleaseEvent = self.mostrar_datos

    def customize_tag_label(self, label):
        label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

    def make_layout(self):
        return QHBoxLayout()

    def make_sensor_widget(self):
        return SensorMiniWidget()