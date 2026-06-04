from PySide6.QtWidgets import QDialog

import qtawesome as qta

from concrete import conector
from ui.ui_registro_nodo import Ui_registro_nodo
from concrete.serializers import Nodo


class RegistroNodo(QDialog, Ui_registro_nodo):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.__signals()

    def init_gui(self):
        self.tb_errores.setVisible(False)
        icons = {
            self.icon_nombre: 'fa5s.id-card',
            self.icon_id: 'fa5s.microchip',
        }
        for widget, icon in icons.items():
            widget.setPixmap(qta.icon(icon, color='#42a2f3').pixmap(24, 24))
        self.adjustSize()

    def __signals(self):
        self.btn_registrar.clicked.connect(self.registrar_nodo)

    def registrar_nodo(self):
        nodo = Nodo()
        nodo.nombre = self.le_nombre.text()
        nodo.id_fisico = self.le_id.text()
        if self.validar_registro():
            conector.agregar_nodo(nodo)
            self.accept()

    def validar_registro(self):
        errores = []
        if not self.le_nombre.text().strip():
            errores.append("• Escribe un nombre para el nodo.")
        if not self.le_id.text().strip():
            errores.append("• Escribe un ID válido.")
        valido = len(errores) == 0
        if not valido:
            self.tb_errores.setText("\n".join(errores))
            self.tb_errores.setVisible(True)
        return valido
