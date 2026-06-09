"""
Carga de datos en segundo plano para no bloquear la interfaz.

Las consultas a Supabase pueden tardar cientos de milisegundos; si corren en el
hilo de la GUI, la ventana se congela. Aquí se ejecutan en un QThreadPool y el
resultado se entrega a la UI mediante señales (que sí cruzan al hilo principal).

Seguridad de hilos: cada función de `conector` abre su propia Session
(session_scope) sobre el pool de conexiones de SQLAlchemy, que es seguro entre
hilos. Los objetos devueltos son serializadores desacoplados, seguros de emitir.
"""

from PySide6.QtCore import QObject, QRunnable, Signal, Slot

from concrete import conector


class _Senales(QObject):
    # (nodos, tarjetas) cuando la carga termina bien; mensaje de error si falla.
    listo = Signal(object, object)
    error = Signal(str)


class TareaCargarPanel(QRunnable):
    """Trae, en segundo plano, los nodos (para el filtro) y las tarjetas del
    nodo seleccionado (con su última lectura ya incluida)."""

    def __init__(self, nodo_id=None):
        super().__init__()
        self._nodo_id = nodo_id
        self.senales = _Senales()

    @Slot()
    def run(self):
        try:
            nodos = conector.consultar_nodos()
            tarjetas = conector.consultar_tarjetas_con_ultima(self._nodo_id)
            self.senales.listo.emit(nodos, tarjetas)
        except Exception as e:        # noqa: BLE001 (se reporta a la UI)
            self.senales.error.emit(str(e))