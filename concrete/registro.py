from PySide6.QtCore import Signal
from PySide6.QtWidgets import QDialog, QMessageBox

import qtawesome as qta

from concrete import conector
from concrete.serializers import Tarjeta
from ui.ui_registro import Ui_registro


class Registro(QDialog, Ui_registro):

    signal_nueva_tarjeta = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.init_gui()
        self.success = self.cargar_nodos()
        self.__signals()

    def init_gui(self):
        self.tb_errores.setVisible(False)
        icons = {
            self.icon_nombre: 'fa5s.id-card',
            self.icon_id: 'fa5s.microchip',
            self.icon_nodo: 'fa5s.users',
            self.icon_tags: 'fa5s.tags',
            self.icon_sensores: 'fa5s.thermometer-half',
        }
        for widget, icon in icons.items():
            widget.setPixmap(qta.icon(icon, color='#42a2f3').pixmap(24, 24))
        self.adjustSize()

    def __signals(self):
        self.btn_registrar.clicked.connect(self.registrar_nuevo)

    def exec(self):
        if not self.success:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("No se encontraron nodos")
            msg.setText("Crea al menos un nodo antes de continuar")
            msg.setStyleSheet("color: black")
            msg.exec()
            return QDialog.Rejected
        return super().exec()

    def registrar_nuevo(self):
        tarjeta = Tarjeta()
        tarjeta.id_fisico = self.le_id.text()
        tarjeta.nombre = self.le_nombre.text()
        nodo = self.cb_nodo.currentData()
        if nodo:
            tarjeta.nodo_id = nodo.nodo_id
        tarjeta.tags = self.le_etiquetas.text()
        tipo_sensores = []
        if self.chkb_temperatura.isChecked():
            tipo_sensores.append(1)
        if self.chkb_humedad.isChecked():
            tipo_sensores.append(2)
        if self.validar_registro():
            conector.agregar_tarjeta(tarjeta, tipo_sensores)
            self.accept()

    def cargar_nodos(self):
        self.cb_nodo.clear()
        nodos = conector.consultar_nodos()
        for nodo in nodos:
            self.cb_nodo.addItem(nodo.nombre, nodo)
        hay_nodos = bool(len(nodos))
        return hay_nodos

    def validar_registro(self):
        errores = []
        if not self.le_nombre.text().strip():
            errores.append("• Escribe un nombre para la tarjeta.")
        if not self.le_id.text().strip():
            errores.append("• Escribe un ID válido.")
        if self.cb_nodo.currentData() is None:
            errores.append("• Selecciona un nodo.")
        if not (
            self.chkb_temperatura.isChecked()
            or self.chkb_humedad.isChecked()
        ):
            errores.append("• Selecciona al menos un sensor.")
        valido = len(errores) == 0
        if not valido:
            self.tb_errores.setText("\n".join(errores))
            self.tb_errores.setVisible(True)
        return valido
