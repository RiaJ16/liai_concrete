# Changelog

Todos los cambios relevantes de **LIAI Concreto** se documentan aquí.

## [2.1.0] - 2026-06-09

Monitoreo en tiempo real, alertas de curado, exportación a CSV y una
optimización de rendimiento que elimina los congelamientos de la interfaz.

### Added
- **Alertas de humedad** por debajo del umbral (`UMBRAL_HUM_MIN = 85.0`): el
  valor se resalta en rojo y negrita en la **tarjeta** y en la **vista mini**, y
  las **filas del historial** por debajo del umbral salen con fondo rojo claro.
- **Estado "última vez visto"** en la tarjeta: *hace X min/h/d* en verde, o en
  rojo si el sensor lleva más de 90 min sin reportar
  (`UMBRAL_SIN_REPORTAR_MIN = 90`).
- **Auto-refresco cada 30 s** (`INTERVALO_REFRESCO_MS`) conservando la posición
  del scroll y el filtro activo.
- **Exportación a CSV** para reportes y entrenamiento de ML:
  - Historial → botón "Exportar CSV": lecturas del sensor abierto en el rango
    visible.
  - Menú → "Exportar todo a CSV": toda la base con columnas completas
    (`lectura_id, nodo_id, mac, nodo_nombre, sensor_id, sensor_nombre, alias,
    numero_lectura, fecha_utc, fecha_local, temp, hum, manual`).
  - Codificación `utf-8-sig` y fecha en UTC + hora local.
- **Carga de datos en segundo plano** con `QThreadPool`; nuevo
  `concrete/workers.py`.
- Consulta única `DISTINCT ON (sensor_id)` para traer la última lectura de todos
  los sensores en un solo viaje (aprovecha el índice `(sensor_id, fecha DESC)`).

### Changed
- Las consultas a Supabase ya **no corren en el hilo de la interfaz**: se
  ejecutan en segundo plano y el resultado se entrega por señales.
- **Una sola consulta por refresco** en lugar de `2N+3`: las tarjetas ya no
  consultan la nube en su constructor (leen la última lectura adjunta).
- La **búsqueda por texto** y el **cambio de vista** (grande/mini) filtran la
  caché en memoria; ya no vuelven a consultar la nube (respuesta instantánea).
- Se evita el solapamiento de cargas (guarda `self._cargando`) para no saturar
  el *pooler* de Supabase.
- `sembrar_datos.py` reescrito como **inyector de lecturas en tiempo real**
  (para probar el flujo en vivo).
- La ventana de historial es **única y reutilizable**; si está abierta, también
  se refresca con los datos nuevos.

### Fixed
- **Ventana en blanco al arrancar** y **congelamiento durante la operación**,
  causados por las consultas de red en el hilo de la interfaz.

## [2.0.0] - 2026-06-06

Migración completa de la persistencia de **MySQL local** a **PostgreSQL en la
nube (Supabase)**, con rediseño del modelo de datos. Incluye cambios
incompatibles respecto a la versión basada en MySQL.

### Added
- **Nuevo modelo** `nodo → sensor → lectura`. El nodo es el receptor que agrupa
  sensores; cada lectura trae temperatura y humedad juntas.
- `TIMESTAMPTZ` para las fechas e **índice compuesto** `(sensor_id, fecha DESC)`
  para consultas por rango (gráficas) rápidas.
- Columna **`alias`** en `sensor` (nombre amigable, sin afectar el nombre de
  hardware con el que se emparejan las lecturas).
- **RLS activado** + función **RPC `registrar_lectura`** para la ingesta del
  hardware (autocrea nodo/sensor por MAC y nombre).
- Nueva **capa de datos** en `concrete/db/`: `engine.py` (conexión desde
  `DATABASE_URL`), `models.py` (ORM con SQLAlchemy 2.0), `repositories.py`
  (patrón Repositorio) y `__init__.py`.
- `load_dotenv()` al inicio de `main.py` (carga la cadena de conexión antes de
  tocar la base).
- Serializadores `Nodo`, `Sensor` (nuevo) y `Lectura`.
- `GUIA_HARDWARE.md` (integración: endpoint, llave publishable, JSON, ejemplo
  ESP32/Arduino).
- Archivos auxiliares: `schema_reset.sql`, `migracion_alias.sql`,
  `rpc_hardware.sql`, `requirements.txt`, `.env.example`, y scripts de prueba
  `test_conexion.py`, `test_rpc.py`, `sembrar_datos.py`.

### Changed
- `conector.py` **reescrito** como *facade* sobre SQLAlchemy/PostgreSQL,
  conservando la API que usa la interfaz para no reescribir los widgets.
- El **dashboard** muestra una tarjeta por sensor; el nodo aparece como
  agrupación (etiqueta).
- **Filtro por nodo** + **búsqueda por texto**.
- Menú simplificado: "Administrar sensores" (antes "Dispositivo").
- **Ventana de tamaño fijo**, 2 columnas y **scroll vertical**.
- `data.py` **reescrito**: historial con dos series (temperatura y humedad) de
  una sola consulta; manejo de **zona horaria** (se guarda en UTC, se muestra en
  hora local); **rango de fechas automático**; **filtrado en memoria**; cursor
  de "cargando"; columna **No. señal**; tabla ajustada al contenido.
- `registro.py` **reescrito**: de "agregar dispositivo/grupo" a **administrar
  sensores** (etiquetar alias, nombrar el nodo, eliminar sensores o nodos).

### Fixed
- **Parpadeo** de la interfaz al arrancar (la ventana se muestra ya armada).

### Removed
- Modelo de grupos (tablas `grupo`, `tarjeta`, `tipo`, `registro`).
- Funciones `consultar_grupos`, `agregar_tarjeta`, `agregar_sensor`.
- Acción de menú "Grupo".
- Clases `Grupo` y `Registro` en `serializers.py` (quedan obsoletas).