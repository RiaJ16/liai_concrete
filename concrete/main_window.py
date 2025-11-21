from PySide6.QtWidgets import QMainWindow, QGridLayout, QVBoxLayout, \
    QSpacerItem, QSizePolicy, QWidget

from concrete import conector
from concrete.board_widget import BoardMiniWidget
from concrete.board_widget import BoardWidget
from concrete.sensor_widget import SensorWidget
from ui.ui_main import Ui_main


class MainWindow(QMainWindow, Ui_main):

    def __init__(self, parent=None):
        super().__init__(parent)
        super().setupUi(self)
        self.show()
        self.widget_boards = QWidget()
        self.widget_mini_boards = QWidget()
        self.populate_dashboard()
        self.populate_with_mini()
        self.set_main_layout()
        self.__signals__()

    def __signals__(self):
        self.btn_grafico.toggled.connect(self.swap_layout)

    def set_main_layout(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.widget_boards)
        layout.addWidget(self.widget_mini_boards)
        self.scroll_area_contents.setLayout(layout)
        self.widget_mini_boards.setVisible(False)

    def swap_layout(self):
        self.widget_boards.setVisible(not self.widget_boards.isVisible())
        self.widget_mini_boards.setVisible(not self.widget_mini_boards.isVisible())

    def populate_dashboard(self):
        tarjetas = conector.consultar_tarjetas()
        num_tarjetas = len(tarjetas)
        layout = QGridLayout()
        for i in range(num_tarjetas):
            layout.addWidget(BoardWidget(tarjetas[i]), 0, i)
        self.widget_boards.setLayout(layout)

    def populate_with_mini(self):
        tarjetas = conector.consultar_tarjetas()
        layout = QVBoxLayout()
        layout.setSpacing(1)
        for tarjeta in tarjetas:
            layout.addWidget(BoardMiniWidget(tarjeta))
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Expanding, QSizePolicy.Expanding))
        self.widget_mini_boards.setLayout(layout)
