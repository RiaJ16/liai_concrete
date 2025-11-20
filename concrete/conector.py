# conector.py

from mysql.connector import pooling

from concrete.serializers import Tarjeta, Sensor, Registro
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
