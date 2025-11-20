import json

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime


#Turns the object into a dictionary and JSON
class JsonMixin:

    @property
    def diccionario(self):
        diccionario = {}
        for key, value in self.__dict__.items():

            if isinstance(value, JsonMixin):
                value = value.diccionario

            elif isinstance(value, datetime):
                value = value.isoformat(sep=' ', timespec='seconds')

            diccionario[key.lstrip('_')] = value

        return diccionario

#Llena el objeto desde un diccionario
class MapperMixin(ABC):

    # Override this per model if needed
    @staticmethod
    def special_fields():
        return {}  # db_key -> converter_function

    def update_from_dict(self, data):
        for db_key, python_attr in self.map_to_db_fields().items():
            if db_key not in data:
                continue

            value = data[db_key]

            converters = self.special_fields()
            if db_key in converters:
                try:
                    value = converters[db_key](value)
                except Exception:
                    pass

            # Convert ISO timestamps
            if isinstance(value, str):
                try:
                    from datetime import datetime
                    value = datetime.fromisoformat(value)
                except ValueError:
                    pass

            setattr(self, python_attr, value)

    @staticmethod
    @abstractmethod
    def map_to_db_fields():
        """Subclasses must implement this method to provide field mappings."""
        pass


@dataclass
class Tarjeta(JsonMixin, MapperMixin):

    tarjeta_id: int = 0
    nombre: str = ''
    id_fisico: str = ''
    grupo_id: int = None
    tags: list = None

    def __init__(self, tarjeta_id=0, id_fisico='', nombre="", grupo_id=None, tags=None):
        self.tarjeta_id = tarjeta_id
        self.id_fisico = id_fisico
        self.nombre = nombre
        self.grupo_id = grupo_id
        self.tags = tags

    @staticmethod
    def map_to_db_fields():
        return {
            'tarjeta_id': 'tarjeta_id',
            'id_fisico': 'id_fisico',
            'nombre': 'nombre',
            'grupo_id': 'grupo_id',
            'tags': 'tags',
        }

    @staticmethod
    def special_fields():
        return {
            'tags': lambda t: [s.strip() for s in t.split(',')] if t else []
        }


@dataclass
class Sensor(JsonMixin, MapperMixin):

    sensor_id: int = 0
    tarjeta_id: int = None
    tipo: str = ''
    dato: float = None
    fecha_dato: datetime = None
    unidades: str = ''

    def __init__(self, sensor_id=0, tarjeta_id=None, tipo='', dato=None, fecha_dato=None, unidades=''):
        self.sensor_id = sensor_id
        self.tarjeta_id = tarjeta_id
        self.tipo = tipo
        self.dato = dato
        self.fecha_dato = fecha_dato
        self.unidades = unidades

    @staticmethod
    def map_to_db_fields():
        return {
            'sensor_id': 'sensor_id',
            'tarjeta_id': 'tarjeta_id',
            'tipo': 'tipo',
            'dato': 'dato',
            'fecha_dato': 'fecha_dato',
            'unidades': 'unidades',
        }

@dataclass
class Registro(JsonMixin, MapperMixin):

    registro_id: int = 0
    sensor_id: int = None
    fecha: datetime = None
    dato: float = None

    def __init__(self, registro_id=0, sensor_id=None, fecha=None, dato=None):
        self.registro_id = registro_id
        self.sensor_id = sensor_id
        self.fecha = fecha
        self.dato = dato

    @staticmethod
    def map_to_db_fields():
        return {
            'registro_id': 'registro_id',
            'sensor_id': 'sensor_id',
            'fecha': 'fecha',
            'dato': 'dato',
        }

@dataclass
class Grupo(JsonMixin, MapperMixin):

    grupo_id: int = 0
    grupo_nombre: str = ''

    def __init__(self, grupo_id=0, grupo_nombre=''):
        self.grupo_id = grupo_id
        self.grupo_nombre = grupo_nombre

    @staticmethod
    def map_to_db_fields():
        return {
            'grupo_id': 'grupo_id',
            'grupo_nombre': 'grupo_nombre',
        }
