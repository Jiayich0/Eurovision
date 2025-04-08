import os
from dotenv import load_dotenv

load_dotenv(override=True)


class ConfiguracionFlask:
    """
    Clase con todas las variables de configuraciones de Flask
    """

    # Secret key: string largo para configurar la proteccion
    # de ciertos componentes de la app
    SECRET_KEY = os.environ.get('SECRET_KEY')

    # Si ponemos el flag DEBUG a true, Flask se ejecutará en modo 'debug'.
    # En este modo, se muestra el log de los errores que se produzcan.
    # NO USAR EN PRODUCCION
    DEBUG = True

    # URI de conexion a la base de datos de Mongo
    MONGO_URI = f"mongodb://{os.environ.get('HOST')}:{os.environ.get('PORT')}/{os.environ.get('DATABASE')}"
