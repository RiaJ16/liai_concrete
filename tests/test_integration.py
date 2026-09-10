import datetime as dt
# import random
from zoneinfo import ZoneInfo

from concrete.conector import (
    consultar_lecturas,
    consultar_lecturas_sensor,
    consultar_tarjetas_con_ultima,
    eliminar_nodo,
    registrar_lectura_desde_hardware,
    renombrar_sensor,
)
from concrete.db import session_scope, NodoRepository, SensorRepository
from concrete.db.models import Sensor, Lectura

TEST_SENSOR = "TEST-SENSOR-001"

def test_registrar_y_consultar(test_mac, cleanup_test_node):
    cleanup_test_node(test_mac)
    fecha = dt.datetime.now(ZoneInfo("America/Mexico_City"))
    # temp = round(random.uniform(22, 28), 1)
    # hum = round(random.uniform(18, 79), 1)
    temp = 28.2
    hum = 84.4
    lectura_id = registrar_lectura_desde_hardware(
        mac=test_mac,
        nombre_sensor=TEST_SENSOR,
        fecha=fecha,
        temp=temp,
        hum=hum,
    )

    assert lectura_id is not None

    with session_scope() as session:
        nodo = NodoRepository(session).obtener_por_mac(test_mac)

        assert nodo is not None

        sensor = SensorRepository(session).buscar(
            nodo_id=nodo.nodo_id,
            nombre=TEST_SENSOR,
        )

        assert sensor is not None

        sensor_id = sensor.sensor_id

    lecturas = consultar_lecturas_sensor(sensor_id)
    assert lecturas is not None
    assert lecturas
    lectura = lecturas[-1]

    assert lectura.temp == temp
    assert lectura.hum == hum


def test_consultar_ultima_lectura(test_mac, cleanup_test_node):
    cleanup_test_node(test_mac)

    nombre_sensor = "TEST-SENSOR-T2"

    fecha_1 = dt.datetime(
        2026, 9, 2, 10, 0,
        tzinfo=ZoneInfo("America/Mexico_City")
    )

    fecha_2 = dt.datetime(
        2026, 9, 2, 11, 0,
        tzinfo=ZoneInfo("America/Mexico_City")
    )

    fecha_3 = dt.datetime(
        2026, 9, 2, 12, 0,
        tzinfo=ZoneInfo("America/Mexico_City")
    )

    registrar_lectura_desde_hardware(
        mac=test_mac,
        nombre_sensor=nombre_sensor,
        fecha=fecha_1,
        temp=24.0,
        hum=60.0,
    )

    registrar_lectura_desde_hardware(
        mac=test_mac,
        nombre_sensor=nombre_sensor,
        fecha=fecha_3,
        temp=19.0,
        hum=84.0,
    )

    registrar_lectura_desde_hardware(
        mac=test_mac,
        nombre_sensor=nombre_sensor,
        fecha=fecha_2,
        temp=26.0,
        hum=62.0,
    )

    with session_scope() as session:
        nodo = NodoRepository(session).obtener_por_mac(test_mac)

        assert nodo is not None

    tarjetas = consultar_tarjetas_con_ultima(nodo.nodo_id)
    assert tarjetas is not None
    assert tarjetas
    tarjeta = tarjetas[-1]
    mediciones = {}
    for sensor in tarjeta.sensores:
        mediciones[sensor.tipo] = sensor.dato

    assert mediciones['Temperatura'] == 19.0
    assert mediciones['Humedad'] == 84.0


def test_consultar_multiples_lecturas(test_mac, cleanup_test_node):
    cleanup_test_node(test_mac)

    nombre_sensor = "TEST-SENSOR-T3"

    fecha_1 = dt.datetime(2026, 9, 1, 10, 0, tzinfo=ZoneInfo("America/Mexico_City"))
    fecha_2 = dt.datetime(2026, 9, 1, 11, 0, tzinfo=ZoneInfo("America/Mexico_City"))
    fecha_3 = dt.datetime(2026, 9, 1, 12, 0, tzinfo=ZoneInfo("America/Mexico_City"))

    registrar_lectura_desde_hardware(
        mac=test_mac,
        nombre_sensor=nombre_sensor,
        fecha=fecha_1,
        temp=24.0,
        hum=60.0,
    )

    registrar_lectura_desde_hardware(
        mac=test_mac,
        nombre_sensor=nombre_sensor,
        fecha=fecha_2,
        temp=25.0,
        hum=61.0,
    )

    registrar_lectura_desde_hardware(
        mac=test_mac,
        nombre_sensor=nombre_sensor,
        fecha=fecha_3,
        temp=26.0,
        hum=86.0,
    )

    with session_scope() as session:
        nodo = NodoRepository(session).obtener_por_mac(test_mac)

        assert nodo is not None

        sensor = SensorRepository(session).buscar(
            nodo_id=nodo.nodo_id,
            nombre=nombre_sensor,
        )

        assert sensor is not None

        sensor_id = sensor.sensor_id

    lecturas = consultar_lecturas_sensor(sensor_id)

    assert len(lecturas) == 3

    assert lecturas[0].temp == 24.0
    assert lecturas[0].hum == 60.0

    assert lecturas[1].temp == 25.0
    assert lecturas[1].hum == 61.0

    assert lecturas[2].temp == 26.0
    assert lecturas[2].hum == 86.0


def test_filtrar_sensores_por_nodo(test_mac, cleanup_test_node):
    mac_1 = test_mac
    mac_2 = f"{test_mac}_"

    cleanup_test_node(mac_1)
    cleanup_test_node(mac_2)

    sensor_1 = "TEST-SENSOR-T4-01"
    sensor_2 = "TEST-SENSOR-T4-02"

    registrar_lectura_desde_hardware(
        mac=mac_1,
        nombre_sensor=sensor_1,
        fecha=dt.datetime.now(ZoneInfo("America/Mexico_City")),
        temp=25.6,
        hum=60.2,
    )

    registrar_lectura_desde_hardware(
        mac=mac_2,
        nombre_sensor=sensor_2,
        fecha=dt.datetime.now(ZoneInfo("America/Mexico_City")),
        temp=19.1,
        hum=91.4,
    )

    with session_scope() as session:
        nodo = NodoRepository(session).obtener_por_mac(mac_1)
        assert nodo is not None
        nodo_id = nodo.nodo_id

    with session_scope() as session:
        sensores = SensorRepository(session).listar_con_nodo(nodo_id)

        assert len(sensores) == 1
        sensor, nodo = sensores[0]

        nombre = sensor.nombre

        assert nombre == sensor_1


def test_consultar_lecturas_por_rango(test_mac, cleanup_test_node):
    cleanup_test_node(test_mac)

    nombre_sensor = "TEST-SENSOR-T5"

    tz = ZoneInfo("America/Mexico_City")

    fecha_1 = dt.datetime(2026, 9, 1, 11, 0, tzinfo=tz)
    fecha_2 = dt.datetime(2026, 9, 5, 11, 0, tzinfo=tz)
    fecha_3 = dt.datetime(2026, 9, 7, 11, 0, tzinfo=tz)
    fecha_4 = dt.datetime(2026, 9, 10, 11, 0, tzinfo=tz)

    registrar_lectura_desde_hardware(
        mac=test_mac,
        nombre_sensor=nombre_sensor,
        fecha=fecha_1,
        temp=22.1,
        hum=65.4,
    )

    registrar_lectura_desde_hardware(
        mac=test_mac,
        nombre_sensor=nombre_sensor,
        fecha=fecha_2,
        temp=24.9,
        hum=61.0,
    )

    registrar_lectura_desde_hardware(
        mac=test_mac,
        nombre_sensor=nombre_sensor,
        fecha=fecha_3,
        temp=25.2,
        hum=82.4,
    )

    registrar_lectura_desde_hardware(
        mac=test_mac,
        nombre_sensor=nombre_sensor,
        fecha=fecha_4,
        temp=27.1,
        hum=92.8,
    )

    with session_scope() as session:
        nodo = NodoRepository(session).obtener_por_mac(test_mac)

        assert nodo is not None

        sensor = SensorRepository(session).buscar(
            nodo_id=nodo.nodo_id,
            nombre=nombre_sensor,
        )

        assert sensor is not None

        sensor_id = sensor.sensor_id

    lecturas = consultar_lecturas(
        sensor_id,
        fecha_2,
        fecha_3,
    )

    assert len(lecturas) == 2

    valores = [
        (lectura.temp, lectura.hum)
        for lectura in lecturas
    ]

    assert valores == [
        (25.2, 82.4),
        (24.9, 61.0),
    ]

def test_modificar_nombre_sensor(test_mac, cleanup_test_node):
    cleanup_test_node(test_mac)

    nombre_inicial = "TEST-SENSOR-T6"
    nombre_nuevo = "TEST-SENSOR-T6-NUEVO"

    registrar_lectura_desde_hardware(
        mac=test_mac,
        nombre_sensor=nombre_inicial,
        fecha=dt.datetime.now(ZoneInfo("America/Mexico_City")),
        temp=25.0,
        hum=60.0,
    )

    with session_scope() as session:
        nodo = NodoRepository(session).obtener_por_mac(test_mac)

        assert nodo is not None

        sensor = SensorRepository(session).buscar(
            nodo_id=nodo.nodo_id,
            nombre=nombre_inicial,
        )

        assert sensor is not None

        sensor_id = sensor.sensor_id

    renombrar_sensor(sensor_id, nombre_nuevo)

    with session_scope() as session:
        nodo = NodoRepository(session).obtener_por_mac(test_mac)

        assert nodo is not None

        sensor = SensorRepository(session).buscar(
            nodo_id=nodo.nodo_id,
            nombre=nombre_inicial,
        )

        assert sensor is not None
        assert sensor.alias == nombre_nuevo


def test_eliminar_nodo_y_datos_asociados(test_mac):

    nombre_sensor = "TEST-SENSOR-T7"

    fecha = dt.datetime.now(
        ZoneInfo("America/Mexico_City")
    )

    lectura_id = registrar_lectura_desde_hardware(
        mac=test_mac,
        nombre_sensor=nombre_sensor,
        fecha=fecha,
        temp=24.3,
        hum=69.5,
    )

    with session_scope() as session:
        nodo = NodoRepository(session).obtener_por_mac(test_mac)

        assert nodo is not None

        sensor = SensorRepository(session).buscar(
            nodo_id=nodo.nodo_id,
            nombre=nombre_sensor,
        )

        assert sensor is not None

        nodo_id = nodo.nodo_id
        sensor_id = sensor.sensor_id

    eliminar_nodo(nodo_id)

    with session_scope() as session:
        nodo = NodoRepository(session).obtener_por_mac(test_mac)
        sensor = session.get(Sensor, sensor_id)
        lectura = session.get(Lectura, lectura_id)

        assert nodo is None
        assert sensor is None
        assert lectura is None
