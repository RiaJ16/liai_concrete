# conector.py

from mysql.connector import pooling

from concrete.serializers import Tarjeta, Sensor, Registro, Nodo
from private import database

_pool = pooling.MySQLConnectionPool(
    pool_name="htechpool",
    pool_size=1,
    user=database.login['dbuser'],
    password=database.login['dbpassword'],
    host='localhost',
    database='liai_concrete',
)

def get_connection(autocommit=False):
    cnx = _pool.get_connection()
    cnx.autocommit = autocommit
    return cnx

def consultar(sql, params=None):
    with get_connection() as cnx, cnx.cursor(dictionary=True) as cursor:
        cursor.execute(sql, params)
        return list(cursor)

def insertar(sql, args=None):
    last_row_id = None
    with get_connection(True) as cnx:
        with cnx.cursor() as cursor:
            cursor.execute(sql, args)
            last_row_id = cursor.lastrowid
            cnx.commit()
    return last_row_id

def consultar_tarjetas():
    sql = "SELECT * FROM tarjeta"
    rows = consultar(sql)
    tarjetas = []
    for row in rows:
        tarjeta = Tarjeta()
        tarjeta.update_from_dict(row)
        tarjetas.append(tarjeta)
    return tarjetas

def consultar_sensores_por_tarjeta(tarjeta_id):
    sql = ("SELECT sensor.*, tipo.etiqueta as tipo, tipo.unidades FROM sensor "
           "LEFT JOIN tipo ON sensor.tipo = tipo.tipo_id "
           f"WHERE sensor.tarjeta_id = {tarjeta_id}")
    rows = consultar(sql)
    sensores = []
    for row in rows:
        sensor = Sensor()
        sensor.update_from_dict(row)
        sensores.append(sensor)
    return sensores

def consultar_registros(sensor_id, fecha_inicial, fecha_final):
    sql = ("SELECT * FROM registro WHERE sensor_id = %(sensor_id)s "
           "AND fecha BETWEEN %(fecha_inicial)s AND %(fecha_final)s "
           "ORDER BY fecha DESC")
    args = {
        'sensor_id': sensor_id,
        'fecha_inicial': fecha_inicial,
        'fecha_final': fecha_final,
    }
    rows = consultar(sql, args)
    registros = []
    for row in rows:
        registro = Registro()
        registro.update_from_dict(row)
        registros.append(registro)
    return registros

def consultar_nodos():
    sql = "SELECT * FROM nodo "
    rows = consultar(sql)
    nodos = []
    for row in rows:
        nodo = Nodo()
        nodo.update_from_dict(row)
        nodos.append(nodo)
    return nodos

def agregar_tarjeta(tarjeta, tipo_sensores):
    sql = ("INSERT INTO tarjeta "
           "(id_fisico, nombre, nodo_id, tags) "
           "VALUES (%(id_fisico)s, %(nombre)s, %(nodo_id)s, %(tags)s)")
    args = {
        'id_fisico': tarjeta.id_fisico,
        'nombre': tarjeta.nombre,
        'nodo_id': tarjeta.nodo_id,
        'tags': tarjeta.tags,
    }
    tarjeta_id = insertar(sql, args)
    tarjeta.tarjeta_id = tarjeta_id
    for tipo_sensor in tipo_sensores:
        sensor = Sensor()
        sensor.tipo = tipo_sensor
        sensor.tarjeta_id = tarjeta_id
        agregar_sensor(sensor)
    return tarjeta

def agregar_sensor(sensor):
    sql = ("INSERT INTO sensor "
           "(tarjeta_id, tipo) "
           "VALUES (%(tarjeta_id)s, %(tipo)s)")
    args = {
        'tarjeta_id': sensor.tarjeta_id,
        'tipo': sensor.tipo
    }
    return insertar(sql, args)

def agregar_nodo(nodo):
    sql = ("INSERT INTO nodo "
           "(nombre, id_fisico) "
           "VALUES (%(nombre)s, %(id_fisico)s)")
    args = {
        'nombre': nodo.nombre,
        'id_fisico': nodo.id_fisico
    }
    return insertar(sql, args)
