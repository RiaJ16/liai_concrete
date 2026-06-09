import csv

from PySide6.QtCore import Qt, QTimer, QThreadPool
from PySide6.QtWidgets import (
    QMainWindow, QGridLayout, QVBoxLayout, QSpacerItem, QSizePolicy,
    QWidget, QComboBox, QFileDialog, QMessageBox,
)

from concrete import conector
from concrete.board_widget import BoardMiniWidget
from concrete.board_widget import BoardWidget
from concrete.data import DataWidget
from concrete.registro import Registro
from concrete.workers import TareaCargarPanel
from ui.ui_main import Ui_main

# --- Ajustes de presentación ---
ANCHO_VENTANA = 820
ALTO_VENTANA = 640
COLUMNAS = 2
INTERVALO_REFRESCO_MS = 30000   # 30 segundos


class MainWindow(QMainWindow, Ui_main):

    def __init__(self, parent=None):
        super().__init__(parent)
        super().setupUi(self)
        self.widget_boards = QWidget()
        self.widget_mini_boards = QWidget()
        self.historial = DataWidget()        # ventana de historial ÚNICA y reutilizable

        # Estado en memoria: los datos se cargan en segundo plano y se cachean.
        self._pool = QThreadPool.globalInstance()
        self._nodos = []
        self._tarjetas = []      # caché de la última carga (se filtra sin red)
        self._cargando = False   # evita solapar cargas

        self._ajustar_menu()
        self._configurar_ventana()
        self._crear_filtro()
        self.set_main_layout()
        self.__signals__()
        self.show()                  # la ventana aparece de inmediato (no en blanco)
        self._recargar()             # primera carga, en segundo plano
        self._iniciar_auto_refresco()

    def __signals__(self):
        self.btn_grafico.toggled.connect(self.swap_layout)
        self.accion_dispositivo.triggered.connect(self.register_new)
        # El filtro de texto NO consulta la nube: re-filtra la caché y repinta.
        self.le_filtrar.textChanged.connect(self._repintar)

    # ----- Carga en segundo plano -----
    def _recargar(self):
        """Lanza la carga de nodos + tarjetas en un hilo aparte (no bloquea)."""
        if self._cargando:
            return
        self._cargando = True
        tarea = TareaCargarPanel(self._nodo_seleccionado())
        tarea.senales.listo.connect(self._on_datos)
        tarea.senales.error.connect(self._on_error)
        self._pool.start(tarea)

    def _on_datos(self, nodos, tarjetas):
        """Llega en el hilo de la GUI cuando termina la carga: cachea y repinta."""
        self._cargando = False
        self._nodos = nodos
        self._tarjetas = tarjetas
        self._refrescar_filtro()
        self._repintar()

    def _on_error(self, mensaje):
        # En auto-refresco no interrumpimos con popups; sólo en la primera carga.
        self._cargando = False
        if not self._tarjetas:
            QMessageBox.warning(self, "Conexión",
                                f"No se pudieron cargar los datos:\n{mensaje}")

    # ----- Auto-refresco cada 30 s -----
    def _iniciar_auto_refresco(self):
        self._timer = QTimer(self)
        self._timer.setInterval(INTERVALO_REFRESCO_MS)
        self._timer.timeout.connect(self._recargar)   # en segundo plano
        self._timer.start()

    # ----- Repintado (usa SÓLO la caché, sin red) -----
    def _repintar(self):
        barra = self.scroll_area.verticalScrollBar()
        pos = barra.value()
        self.scroll_area_contents.setUpdatesEnabled(False)   # evita parpadeo
        if self.widget_mini_boards.isVisible():
            self.populate_with_mini()
        else:
            self.populate_dashboard()
        self.scroll_area_contents.setUpdatesEnabled(True)
        barra.setValue(pos)
        # Si el historial está abierto, también se actualiza.
        if self.historial.isVisible():
            self.historial.refrescar()

    # ----- Exportar toda la base a CSV -----
    def _exportar_todo_csv(self):
        ruta, _ = QFileDialog.getSaveFileName(
            self, "Exportar todo a CSV", "lecturas.csv", "CSV (*.csv)")
        if not ruta:
            return
        columnas = ["lectura_id", "nodo_id", "mac", "nodo_nombre", "sensor_id",
                    "sensor_nombre", "alias", "numero_lectura", "fecha_utc",
                    "fecha_local", "temp", "hum", "manual"]
        try:
            datos = conector.exportar_todo()
            with open(ruta, "w", newline="", encoding="utf-8-sig") as f:
                escritor = csv.DictWriter(f, fieldnames=columnas)
                escritor.writeheader()
                escritor.writerows(datos)
            QMessageBox.information(self, "Exportación",
                                   f"Se exportaron {len(datos)} lecturas a:\n{ruta}")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"No se pudo exportar: {e}")

    # ----- Abrir historial (ventana única) -----
    def _abrir_historial(self, tarjeta, sensores):
        self.historial.mostrar_datos(tarjeta, sensores)

    # ----- Tamaño fijo + scroll vertical -----
    def _configurar_ventana(self):
        self.setFixedSize(ANCHO_VENTANA, ALTO_VENTANA)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

    # ----- Limpieza del menú -----
    def _ajustar_menu(self):
        self.menuAgregar.setTitle("Sensores")
        self.accion_dispositivo.setText("Administrar sensores")
        self.menuAgregar.removeAction(self.accion_grupo)
        self.le_filtrar.setPlaceholderText("Buscar por nombre…")
        # Exportar toda la base a CSV (para reportes / entrenamiento de ML).
        self.menuAgregar.addSeparator()
        accion_exportar = self.menuAgregar.addAction("Exportar todo a CSV")
        accion_exportar.triggered.connect(self._exportar_todo_csv)

    # ----- Filtro por nodo -----
    def _crear_filtro(self):
        self.cb_filtro = QComboBox()
        self.cb_filtro.setMinimumSize(0, 30)
        self.cb_filtro.setStyleSheet("background-color: white; color: black;")
        self.horizontalLayout.insertWidget(1, self.cb_filtro)
        # Cambiar de nodo SÍ requiere nueva consulta (otro subconjunto).
        self.cb_filtro.currentIndexChanged.connect(self._recargar)

    def _refrescar_filtro(self):
        """Repuebla el combo de nodos desde la caché, conservando la selección."""
        anterior = self.cb_filtro.currentData() if self.cb_filtro.count() else None
        self.cb_filtro.blockSignals(True)
        self.cb_filtro.clear()
        self.cb_filtro.addItem("Nodos", None)
        for nodo in self._nodos:
            self.cb_filtro.addItem(nodo.nombre or nodo.mac, nodo.nodo_id)
        idx = self.cb_filtro.findData(anterior)
        self.cb_filtro.setCurrentIndex(idx if idx >= 0 else 0)
        self.cb_filtro.blockSignals(False)

    def _nodo_seleccionado(self):
        return self.cb_filtro.currentData() if hasattr(self, "cb_filtro") else None

    def _tarjetas_filtradas(self):
        """Filtra la CACHÉ por el texto de búsqueda (sin red). El filtro por
        nodo ya se aplicó en la consulta."""
        texto = self.le_filtrar.text().strip().lower()
        tarjetas = self._tarjetas
        if texto:
            tarjetas = [
                t for t in tarjetas
                if texto in (t.nombre or "").lower()
                or any(texto in (tag or "").lower() for tag in (t.tags or []))
            ]
        return tarjetas

    # ----- Layout -----
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
        self._repintar()   # construye, desde la caché, el panel que quedó visible

    def populate_dashboard(self):
        layout = self.widget_boards.layout()
        if layout is None:
            layout = QGridLayout(self.widget_boards)
            self.widget_boards.setLayout(layout)
        self.clear_layout(layout)
        tarjetas = self._tarjetas_filtradas()
        for i, tarjeta in enumerate(tarjetas):
            row = i // COLUMNAS
            col = i % COLUMNAS
            layout.addWidget(BoardWidget(tarjeta, self._abrir_historial), row, col)
        layout.setRowStretch(layout.rowCount(), 1)

    @staticmethod
    def clear_layout(layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def populate_with_mini(self):
        layout = self.widget_mini_boards.layout()
        if layout is None:
            layout = QVBoxLayout(self.widget_mini_boards)
            layout.setSpacing(1)
            self.widget_mini_boards.setLayout(layout)
        self.clear_layout(layout)
        tarjetas = self._tarjetas_filtradas()
        for tarjeta in tarjetas:
            layout.addWidget(BoardMiniWidget(tarjeta, self._abrir_historial))
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Expanding, QSizePolicy.Expanding))

    def register_new(self):
        Registro().exec()
        self._recargar()   # recarga en segundo plano tras administrar sensores