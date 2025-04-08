from flask import Flask
from flask_bootstrap import Bootstrap5
from flask_pymongo import PyMongo
from flask_wtf import CSRFProtect
from config import ConfiguracionFlask
from flask_login import LoginManager

# Los distintos objetos de la aplicacion se crean fuera del metodo create_app, para que esten
# disponibles para importar del resto de paquetes.

mongo = PyMongo()
bootstrap = Bootstrap5()
csrf = CSRFProtect()


def create_app() -> Flask:
    """
    Funcion que crea la instancia de la aplicacion de Flask
    """
    # Declaramos la instancia de la app de Flask
    app = Flask(__name__)

    # Configuramos la app utilizando el objeto que hemos declarado previamente
    app.config.from_object(ConfiguracionFlask())

    # Inicializamos los distintos componentes de la app
    bootstrap.init_app(app)
    csrf.init_app(app)
    mongo.init_app(app)

    # Vinculamos las rutas del modulo "rutas"
    with app.app_context():
        from . import rutas
    return app
