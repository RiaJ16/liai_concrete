import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, \
    QFileDialog, QMessageBox
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# --- Ajustes de la gráfica ---
MOSTRAR_REJILLA = True
ALPHA_REJILLA = 0.3

# Umbral mínimo de humedad para el curado. Se importa de conector (fuente única):
# cambiarlo ahí actualiza tarjeta, mini, lista y gráfica a la vez.
from concrete.conector import UMBRAL_HUM_MIN as UMBRAL_HUMEDAD  # fuente única
MOSTRAR_UMBRAL = True
MOSTRAR_BANDA_IDEAL = True
HUMEDAD_MAX = 100.0            # tope de la banda de curado ideal

# El formato de fecha del eje X lo elige AutoDateFormatter según la escala de
# las marcas (segundos, minutos, horas o días), evitando etiquetas repetidas.
MAX_TICKS_X = 8            # máximo de marcas de fecha para que no se amontonen

# Config por tipo de serie. La subcadena se busca en el nombre de la serie
# ('Temperatura', 'Humedad'); define su etiqueta de eje, color y en qué eje Y va.
#   'izq' = eje Y izquierdo, 'der' = eje Y derecho.
CONFIG_SERIES = {
    "temp": {"eje_label": "Temperatura (°C)", "color": "#e74c3c", "lado": "izq"},
    "hum":  {"eje_label": "Humedad (%)",      "color": "#2980b9", "lado": "der"},
}


class ChartWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        self.fig = Figure()
        self.canvas = FigureCanvas(self.fig)
        layout.addWidget(self.canvas)

        # Barra inferior con el botón de exportar la gráfica a imagen.
        barra = QHBoxLayout()
        barra.addStretch(1)
        self.btn_guardar = QPushButton("Guardar imagen")
        self.btn_guardar.clicked.connect(self._guardar_imagen)
        barra.addWidget(self.btn_guardar)
        layout.addLayout(barra)

        self._titulo = ""        # nombre del sensor (título + nombre de archivo)
        self._tiene_datos = False

    def _config_para(self, nombre):
        clave = nombre.lower()
        for sub, cfg in CONFIG_SERIES.items():
            if sub in clave:
                return cfg
        return None

    def plot_data(self, fechas, series, titulo=None):
        self._titulo = titulo or ""
        self._tiene_datos = bool(fechas)

        self.fig.clear()
        ax_izq = self.fig.add_subplot(111)
        ax_der = None
        lineas = []   # para armar una leyenda combinada de ambos ejes

        for nombre, valores in series.items():
            cfg = self._config_para(nombre)
            color = cfg["color"] if cfg else None
            # Elegir eje: humedad al derecho, temperatura (o desconocido) al izquierdo.
            if cfg and cfg["lado"] == "der":
                if ax_der is None:
                    ax_der = ax_izq.twinx()
                destino = ax_der
            else:
                destino = ax_izq
            (linea,) = destino.plot(fechas, valores, label=nombre, color=color)
            lineas.append(linea)
            # Cada eje Y muestra su TIPO y unidad, en el color de su línea.
            if cfg:
                destino.set_ylabel(cfg["eje_label"], color=color)
                destino.tick_params(axis="y", labelcolor=color)

        # Umbral de humedad + banda de zona de curado ideal (sobre el eje de humedad).
        if ax_der is not None:
            if MOSTRAR_BANDA_IDEAL:
                ax_der.axhspan(UMBRAL_HUMEDAD, HUMEDAD_MAX,
                               color="#2ecc71", alpha=0.08, zorder=0)
            if MOSTRAR_UMBRAL:
                ax_der.axhline(UMBRAL_HUMEDAD, color="#27ae60", linestyle="--",
                               linewidth=1, label=f"Umbral {UMBRAL_HUMEDAD:.0f}%")
                # incluir la línea de umbral en la leyenda
                lineas.append(ax_der.lines[-1])

        # Título con el nombre del sensor.
        if self._titulo:
            ax_izq.set_title(self._titulo)

        ax_izq.set_xlabel("Fecha")
        if MOSTRAR_REJILLA:
            ax_izq.grid(True, alpha=ALPHA_REJILLA)

        # Formato de fecha del eje X. AutoDateFormatter elige el formato según
        # la escala de las marcas (segundos/minutos/horas/días), así nunca quedan
        # etiquetas repetidas ni con más detalle del necesario.
        if fechas:
            locator = mdates.AutoDateLocator(maxticks=MAX_TICKS_X)
            formatter = mdates.AutoDateFormatter(locator)
            formatter.scaled[1 / (24 * 3600)] = "%H:%M:%S"   # marcas de segundos
            formatter.scaled[1 / (24 * 60)] = "%H:%M"         # marcas de minutos
            formatter.scaled[1 / 24] = "%d/%m %H:%M"          # marcas de horas
            formatter.scaled[1.0] = "%d/%m %H:%M"             # marcas de días
            formatter.scaled[30.0] = "%d/%m/%Y"               # marcas de meses
            ax_izq.xaxis.set_major_locator(locator)
            ax_izq.xaxis.set_major_formatter(formatter)
            for etiqueta in ax_izq.get_xticklabels():
                etiqueta.set_rotation(30)
                etiqueta.set_ha("right")

        # Leyenda combinada (líneas de ambos ejes + umbral en un solo recuadro).
        if lineas:
            ax_izq.legend(lineas, [l.get_label() for l in lineas], loc="best")

        self.fig.tight_layout()
        self.canvas.draw()

    def _guardar_imagen(self):
        if not self._tiene_datos:
            QMessageBox.information(self, "Gráfica", "No hay datos para guardar.")
            return
        base = f"grafica_{self._titulo}".strip().replace(" ", "_") if self._titulo else "grafica"
        ruta, _ = QFileDialog.getSaveFileName(
            self, "Guardar gráfica", f"{base}.png", "PNG (*.png)")
        if not ruta:
            return
        try:
            self.fig.savefig(ruta, dpi=150, bbox_inches="tight")
            QMessageBox.information(self, "Gráfica", f"Imagen guardada en:\n{ruta}")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"No se pudo guardar: {e}")