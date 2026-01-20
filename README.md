# Configuración de la base de datos

Para configurar la base de datos para poder hacer uso de este software, es necesario hacer 2 cosas:

1. Utilizar el archivo /database/liai_database.py para crear una base de datos.
2. Crear el archivo en private/database.py con la siguiente estructura:

	# -*- coding: utf-8 -*-
	
	login = {
		'dbuser': '',
		'dbpassword': '',
		'host': '',
		'database': '',
	}
