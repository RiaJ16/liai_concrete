from PySide6.QtWidgets import QWidget, QGridLayout, QVBoxLayout, QLabel

from concrete import conector
from concrete.data import DataWidget
from concrete.sensor_widget import SensorWidget
from ui.ui_board import Ui_board


class BoardWidget(QWidget, Ui_board):

    def __init__(self, tarjeta, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.show()
        self.sensor_widget = SensorWidget()
        self.data_widget = DataWidget()
        self.tarjeta = tarjeta
        self.set_ui(tarjeta)
        self.sensores = conector.consultar_sensores_por_tarjeta(self.tarjeta.tarjeta_id)
        self.populate_board()
        self.btn_historial.setVisible(False)
        self.__signals()

    def __signals(self):
        self.card_frame.mouseReleaseEvent = self.mostrar_datos

    def populate_board(self):
        layout = QVBoxLayout()
        sensor_widget = SensorWidget()
        for sensor in self.sensores:
            sensor_widget.add_sensor(sensor)
        layout.addWidget(sensor_widget)
        self.widget_sensores.setLayout(layout)

    def set_ui(self, tarjeta):
        self.lbl_nombre.setText(tarjeta.nombre)
        layout = self.widget_tags.layout()
        for tag in tarjeta.tags:
            layout.insertWidget(layout.count()-1, QLabel(tag))

    def mostrar_datos(self, event):
        self.data_widget.mostrar_datos(self.tarjeta, self.sensores)
        event.accept()
