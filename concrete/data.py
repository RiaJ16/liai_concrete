import csv
from datetime import timedelta

from PySide6 import QtWidgets
from PySide6.QtCore import QDateTime
from PySide6.QtGui import Qt, QColor, QBrush
from PySide6.QtWidgets import QWidget, QGridLayout, QVBoxLayout, QLabel, \
    QTableWidgetItem, QAbstractItemView, QSplitter, QHBoxLayout, QTableWidget, \
    QApplication, QPushButton, QFileDialog, QMessageBox

from concrete import conector
from concrete.chart_widget import ChartWidget
from ui.ui_data import Ui_data


class DataWidget(QWidget, Ui_data):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.widget_chart = ChartWidget()
        self.splitter = QSplitter()
        self.widget_table = QTableWidget()
        self.splitter.addWidget(self.widget_table)
        self.splitter.addWidget(self.widget_chart)
        self.splitter.setStretchFactor(0, 0)   # tabla: a su contenido
        self.splitter.setStretchFactor(1, 1)   # gráfica: ocupa el resto
        self.layout().insertWidget(0, self.splitter)
        self.resize(1100, 560)
        self.btn_exportar = QPushButton("Exportar CSV")
        self.layout().addWidget(self.btn_exportar)
        self.btn_exportar.clicked.connect(self._exportar_csv)
        self.tarjeta = None
        self.sensores = []
        self._lecturas = []
        self._rango_manual = False
        self.__signals()

    def __signals(self):
        self.fecha_inicial.dateTimeChanged.connect(self._on_rango_cambiado)
        self.fecha_final.dateTimeChanged.connect(self._on_rango_cambiado)

    def _on_rango_cambiado(self):
        # El usuario movió las fechas: respetar su rango en los auto-refrescos.
        self._rango_manual = True
        self.consultar_datos()

    def mostrar_datos(self, tarjeta, sensores):
        self.setWindowTitle(f'Datos de {tarjeta.nombre}')
        self.tarjeta = tarjeta
        self.sensores = sensores
        self._rango_manual = False
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            sensor_id = sensores[0].sensor_id if sensores else None
            self._lecturas = conector.consultar_lecturas_sensor(sensor_id) if sensor_id else []
            self._ajustar_rango_fechas()
            self.consultar_datos()
        finally:
            QApplication.restoreOverrideCursor()
        self.show()

    def refrescar(self):
        """Auto-refresco (cada 30 s) del historial abierto, sin cursor de espera."""
        if not self.sensores:
            return
        sensor_id = self.sensores[0].sensor_id
        self._lecturas = conector.consultar_lecturas_sensor(sensor_id)
        if not self._rango_manual:
            self._ajustar_rango_fechas()   # extiende el rango a los datos nuevos
        self.consultar_datos()

    def _exportar_csv(self):
        if not self.sensores or not self.tarjeta:
            return
        ruta, _ = QFileDialog.getSaveFileName(
            self, "Exportar CSV", f"{self.tarjeta.nombre}.csv", "CSV (*.csv)")
        if not ruta:
            return
        fi = self.fecha_inicial.dateTime().toPython().astimezone()
        ff = self.fecha_final.dateTime().toPython().astimezone()
        lecturas = sorted(
            (l for l in self._lecturas if fi <= l.fecha <= ff),
            key=lambda r: r.fecha,
        )
        mac = self.tarjeta.id_fisico
        nodo_nombre = self.tarjeta.tags[0] if self.tarjeta.tags else ""
        sensor = self.tarjeta.nombre
        columnas = ["mac", "nodo_nombre", "sensor", "numero_lectura",
                    "fecha_utc", "fecha_local", "temp", "hum"]
        try:
            with open(ruta, "w", newline="", encoding="utf-8-sig") as f:
                w = csv.writer(f)
                w.writerow(columnas)
                for l in lecturas:
                    w.writerow([
                        mac, nodo_nombre, sensor, l.numero_lectura,
                        l.fecha.isoformat(),
                        l.fecha.astimezone().strftime("%Y-%m-%d %H:%M:%S"),
                        l.temp, l.hum,
                    ])
            QMessageBox.information(self, "Exportación",
                                   f"Se exportaron {len(lecturas)} lecturas a:\n{ruta}")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"No se pudo exportar: {e}")

    def _ajustar_rango_fechas(self):
        if not self._lecturas:
            return
        fechas = [l.fecha for l in self._lecturas]
        ini = min(fechas).astimezone()
        fin = max(fechas).astimezone() + timedelta(minutes=1)
        self.fecha_inicial.blockSignals(True)
        self.fecha_final.blockSignals(True)
        self.fecha_inicial.setDateTime(
            QDateTime.fromString(ini.strftime("%Y-%m-%d %H:%M:%S"), "yyyy-MM-dd HH:mm:ss"))
        self.fecha_final.setDateTime(
            QDateTime.fromString(fin.strftime("%Y-%m-%d %H:%M:%S"), "yyyy-MM-dd HH:mm:ss"))
        self.fecha_inicial.blockSignals(False)
        self.fecha_final.blockSignals(False)

    def consultar_datos(self):
        self.widget_table.clear()
        self.widget_table.setRowCount(0)
        # Columnas base: No. señal primero, luego Fecha.
        self.widget_table.setColumnCount(2)
        self.widget_table.setHorizontalHeaderLabels(["No. señal", "Fecha"])

        if not self.sensores:
            return

        fecha_inicial = self.fecha_inicial.dateTime().toPython().astimezone()
        fecha_final = self.fecha_final.dateTime().toPython().astimezone()

        lecturas = sorted(
            (l for l in self._lecturas if fecha_inicial <= l.fecha <= fecha_final),
            key=lambda r: r.fecha,
        )
        fechas = [l.fecha.astimezone() for l in lecturas]

        # Una fila por lectura: No. señal + Fecha.
        # La tabla se arma del MAS NUEVO al mas viejo (reversed), mientras que la
        # grafica sigue usando 'lecturas'/'fechas' en orden ascendente (tiempo
        # de izquierda a derecha). Los valores se ubican por clave, asi que el
        # orden de las filas no afecta a que celda va cada dato.
        filas_por_clave = {}
        for reg in reversed(lecturas):
            fecha_local = reg.fecha.astimezone()
            clave = fecha_local.strftime("%Y-%m-%d %H:%M:%S")
            if clave not in filas_por_clave:
                row = self.widget_table.rowCount()
                self.widget_table.insertRow(row)
                num_txt = str(reg.numero_lectura) if reg.numero_lectura is not None else "—"
                it_num = QTableWidgetItem(num_txt)
                it_num.setTextAlignment(Qt.AlignCenter)
                self.widget_table.setItem(row, 0, it_num)                       # No. señal
                self.widget_table.setItem(
                    row, 1, QTableWidgetItem(fecha_local.strftime("%Y-%m-%d %H:%M")))  # Fecha
                filas_por_clave[clave] = row

        # Columnas de valores (Temperatura / Humedad)
        series = {}
        filas_alerta = set()   # humedad por debajo del umbral (rojo)
        filas_ok = set()       # humedad por encima del umbral (verde)
        for sensor in self.sensores:
            col = self.widget_table.columnCount()
            self.widget_table.insertColumn(col)
            self.widget_table.setHorizontalHeaderItem(col, QTableWidgetItem(sensor.tipo))

            valores = []
            for reg in lecturas:
                valor = getattr(reg, sensor.campo)
                valores.append(valor if valor is not None else float('nan'))
                clave = reg.fecha.astimezone().strftime("%Y-%m-%d %H:%M:%S")
                row = filas_por_clave[clave]
                texto = f"{valor:.2f} {sensor.unidades}" if valor is not None else "—"
                item = QTableWidgetItem(texto)
                item.setTextAlignment(Qt.AlignRight)
                self.widget_table.setItem(row, col, item)
                # Humedad: por debajo del umbral -> rojo; por encima -> verde.
                if sensor.campo == "hum" and valor is not None:
                    if valor < conector.UMBRAL_HUM_MIN:
                        filas_alerta.add(row)
                    else:
                        filas_ok.add(row)
            series[sensor.tipo] = valores

        # Resaltar filas por estado de humedad (rojo/verde claro).
        fondo_alerta = QBrush(QColor("#fdecea"))   # rojo claro
        fondo_ok = QBrush(QColor("#eafaf1"))        # verde claro
        for filas, fondo in ((filas_ok, fondo_ok), (filas_alerta, fondo_alerta)):
            for row in filas:
                for col in range(self.widget_table.columnCount()):
                    item = self.widget_table.item(row, col)
                    if item is not None:
                        item.setBackground(fondo)

        if fechas:
            titulo = self.tarjeta.nombre if self.tarjeta else None
            self.widget_chart.plot_data(fechas, series, titulo=titulo)

        self.widget_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.widget_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.widget_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.widget_table.verticalHeader().setVisible(False)
        self.widget_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.widget_table.resizeColumnsToContents()
        self.widget_table.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.ResizeToContents)

        # Ajustar el ancho de la tabla EXACTAMENTE a su contenido:
        # sin margen vacío a la derecha y sin scroll horizontal.
        ancho = self.widget_table.frameWidth() * 2
        for c in range(self.widget_table.columnCount()):
            ancho += self.widget_table.columnWidth(c)
        ancho += self.widget_table.verticalScrollBar().sizeHint().width()
        self.widget_table.setFixedWidth(ancho)