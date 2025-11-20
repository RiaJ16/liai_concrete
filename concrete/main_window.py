from PySide6.QtWidgets import QMainWindow, QGridLayout

from concrete import conector
from concrete.board_widget import BoardWidget
from concrete.sensor_widget import SensorWidget
from ui.ui_main import Ui_main


class MainWindow(QMainWindow, Ui_main):

    def __init__(self, parent=None):
        super().__init__(parent)
        super().setupUi(self)
        self.show()
        self.populate_dashboard()

    def populate_dashboard(self):
        tarjetas = conector.consultar_tarjetas()
        num_tarjetas = len(tarjetas)
        layout = QGridLayout()
        for i in range(num_tarjetas):
            layout.addWidget(BoardWidget(tarjetas[i]), 0, i)
        self.scroll_area.setLayout(layout)
