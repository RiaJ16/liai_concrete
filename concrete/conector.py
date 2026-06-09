# conector.py
"""
Capa de acceso a datos sobre PostgreSQL/Supabase.

Modelo: nodo (receptor, agrupa) -> sensor (unidad monitoreada) -> lectura.
El dashboard muestra UNA tarjeta por SENSOR; el nodo es la agrupación.
"""

from types import SimpleNamespace

# La humedad no debe bajar de este valor (alerta en rojo en la tarjeta).
UMBRAL_HUM_MIN = 85.0

from concrete.serializers import Tarjeta, Nodo, Sensor, Lectura
from concrete.db import (
    session_scope,
    NodoRepository,
    SensorRepository,
    LecturaRepository,
)


def _renglon(tipo, dato, unidades, sensor_id, campo, alerta=False):
    return SimpleNamespace(tipo=tipo, dato=dato, unidades=unidades,
                           sensor_id=sensor_id, campo=campo, alerta=alerta)


# =====================================================================
#  API que consume tu UI
# =====================================================================

def consultar_tarjetas(nodo_id=None):
    """
    Cada SENSOR es una tarjeta. El nodo va como etiqueta de agrupación.
    Si nodo_id se da, sólo devuelve los sensores de ese nodo (filtro).
    """
    with session_scope() as s:
        filas = SensorRepository(s).listar_con_nodo_y_ultima(nodo_id)
        tarjetas = []
        for sensor, nodo, ultima in filas:
            etiqueta_nodo = nodo.nombre or nodo.mac
            nombre = sensor.alias or sensor.nombre
            t = Tarjeta(
                tarjeta_id=sensor.sensor_id,
                id_fisico=nodo.mac,
                nombre=nombre,
                grupo_id=nodo.nodo_id,
                tags=[etiqueta_nodo],
            )
            t.ultima_fecha = ultima   # fecha (UTC) de la última lectura, o None
            tarjetas.append(t)
        return tarjetas


def consultar_tarjetas_con_ultima(nodo_id=None):
    """
    Igual que consultar_tarjetas, pero en UNA sola consulta trae también la
    última lectura (temp/hum/fecha) de cada sensor y deja listos los renglones
    Temperatura/Humedad en t.sensores. Así las tarjetas del panel NO consultan
    la nube en su constructor (clave para no bloquear la interfaz).
    """
    with session_scope() as s:
        filas = SensorRepository(s).listar_con_nodo_y_ultima_lectura(nodo_id)
        tarjetas = []
        for sensor, nodo, ultima in filas:
            etiqueta_nodo = nodo.nombre or nodo.mac
            nombre = sensor.alias or sensor.nombre
            temp = ultima.temp if ultima else None
            hum = ultima.hum if ultima else None
            hum_alerta = hum is not None and hum < UMBRAL_HUM_MIN
            t = Tarjeta(
                tarjeta_id=sensor.sensor_id,
                id_fisico=nodo.mac,
                nombre=nombre,
                grupo_id=nodo.nodo_id,
                tags=[etiqueta_nodo],
            )
            t.ultima_fecha = ultima.fecha if ultima else None
            t.sensores = [
                _renglon('Temperatura', temp, '°C', sensor.sensor_id, 'temp'),
                _renglon('Humedad', hum, '%', sensor.sensor_id, 'hum', alerta=hum_alerta),
            ]
            tarjetas.append(t)
        return tarjetas


def consultar_sensores_por_tarjeta(sensor_id):
    """Renglones Temperatura/Humedad con el último valor de ese sensor."""
    with session_scope() as s:
        ultima = LecturaRepository(s).ultima(sensor_id)
        temp = ultima.temp if ultima else None
        hum = ultima.hum if ultima else None
        hum_alerta = hum is not None and hum < UMBRAL_HUM_MIN
        return [
            _renglon('Temperatura', temp, '°C', sensor_id, 'temp'),
            _renglon('Humedad', hum, '%', sensor_id, 'hum', alerta=hum_alerta),
        ]


# =====================================================================
#  Gestión / etiquetado / eliminación (diálogo)
# =====================================================================

def consultar_sensores():
    """Detalle de cada sensor + su nodo, para el diálogo."""
    with session_scope() as s:
        filas = SensorRepository(s).listar_con_nodo()
        return [
            SimpleNamespace(
                sensor_id=sensor.sensor_id,
                nombre=sensor.nombre,
                alias=sensor.alias,
                nodo_id=nodo.nodo_id,
                nodo_nombre=nodo.nombre,
                mac=nodo.mac,
            )
            for sensor, nodo in filas
        ]


def renombrar_sensor(sensor_id, alias):
    with session_scope() as s:
        SensorRepository(s).actualizar_alias(sensor_id, alias)


def renombrar_nodo(nodo_id, nombre):
    with session_scope() as s:
        NodoRepository(s).actualizar_nombre(nodo_id, nombre)


def eliminar_sensor(sensor_id):
    """Borra un sensor y todas sus lecturas (cascada)."""
    with session_scope() as s:
        SensorRepository(s).eliminar(sensor_id)


def eliminar_nodo(nodo_id):
    """Borra un nodo con todos sus sensores y lecturas (cascada)."""
    with session_scope() as s:
        NodoRepository(s).eliminar(nodo_id)


# =====================================================================
#  API nueva / hardware
# =====================================================================

def _nodo_to_serializer(n):
    nodo = Nodo()
    nodo.update_from_dict({"nodo_id": n.nodo_id, "mac": n.mac, "nombre": n.nombre})
    return nodo


def _lectura_to_serializer(l):
    lectura = Lectura()
    lectura.update_from_dict({
        "lectura_id": l.lectura_id, "sensor_id": l.sensor_id,
        "numero_lectura": l.numero_lectura, "fecha": l.fecha,
        "temp": l.temp, "hum": l.hum,
    })
    return lectura


def consultar_nodos():
    with session_scope() as s:
        return [_nodo_to_serializer(n) for n in NodoRepository(s).listar()]


def consultar_lecturas(sensor_id, fecha_inicial, fecha_final):
    with session_scope() as s:
        filas = LecturaRepository(s).graficar(sensor_id, fecha_inicial, fecha_final)
        return [_lectura_to_serializer(l) for l in filas]


def rango_fechas_sensor(sensor_id):
    """(fecha_min, fecha_max) de las lecturas del sensor, o (None, None)."""
    with session_scope() as s:
        return LecturaRepository(s).rango_fechas(sensor_id)


def consultar_lecturas_sensor(sensor_id):
    """Todas las lecturas de un sensor (para cargar el historial de una sola vez)."""
    with session_scope() as s:
        return [_lectura_to_serializer(l) for l in LecturaRepository(s).todas(sensor_id)]


def exportar_todo():
    """Todas las lecturas con su sensor y nodo, para exportar a CSV / ML."""
    with session_scope() as s:
        filas = LecturaRepository(s).exportar_todo()
        datos = []
        for lec, sen, nod in filas:
            datos.append({
                "lectura_id": lec.lectura_id,
                "nodo_id": nod.nodo_id,
                "mac": nod.mac,
                "nodo_nombre": nod.nombre or "",
                "sensor_id": sen.sensor_id,
                "sensor_nombre": sen.nombre,
                "alias": sen.alias or "",
                "numero_lectura": lec.numero_lectura,
                "fecha_utc": lec.fecha.isoformat(),
                "fecha_local": lec.fecha.astimezone().strftime("%Y-%m-%d %H:%M:%S"),
                "temp": lec.temp,
                "hum": lec.hum,
                "manual": lec.manual,
            })
        return datos


def registrar_lectura_desde_hardware(mac, nombre_sensor, fecha,
                                     temp=None, hum=None, numero_lectura=None):
    with session_scope() as s:
        nodo = NodoRepository(s).obtener_o_crear(mac=mac)
        sensor = SensorRepository(s).obtener_o_crear(nodo_id=nodo.nodo_id, nombre=nombre_sensor)
        return LecturaRepository(s).crear(
            sensor_id=sensor.sensor_id, fecha=fecha, temp=temp, hum=hum,
            numero_lectura=numero_lectura,
        ).lectura_id