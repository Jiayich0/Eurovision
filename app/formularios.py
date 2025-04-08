"""
Modulo en el que definimos los formularios de nuestra aplicacion
"""
from typing import List
from . import mongo
from wtforms import StringField, SubmitField, ValidationError
from .render_utils import MultiCheckboxField
from flask_wtf import FlaskForm

class GenerarQuizForm(FlaskForm):
    """
    Formulario para generar un Quiz
    """
    nombre = StringField(
        'Introduce el nombre del Quiz (por si luego te apetece publicarlo 😉)',
    )

    seleccion_anyos = MultiCheckboxField(
        'Selecciona todos los festivales que quieres incluir en el Quiz:',
    )

    seleccion_paises = MultiCheckboxField(
        'Selecciona los países que quieres incluir en el Quiz:',
    )

    submit = SubmitField('Confirmar')

    def __init__(self, anyos: List[str], paises: List[str], **kwargs):
        super().__init__(**kwargs)

        # Asignamos todas las opciones de forma dinamica. Es una lista de tuplas, porque
        # la tupla indica que valor se muestra y que valor se recibe desde el formulario
        # (en este caso, coinciden). Hay que convertirlo en strings
        self.seleccion_anyos.choices = [(str(anyo), str(anyo)) for anyo in anyos]

        self.seleccion_anyos.elementos_por_fila = 4

        # Repetimos la misma idea para "GenerarQuizForm"
        self.seleccion_paises.choices = [(pais, pais) for pais in paises]
        self.seleccion_paises.elementos_por_fila = 3

    def validate_nombre(self, field):
        """
        Validador que comprueba si existe ya un quiz con el nombre asociado
        """
        if mongo.db["quizzes"].find_one({"_id": field.data}, {"_id": 1}):
            raise ValidationError("Ya existe un quizz con ese nombre")

    def validate_seleccion_anyos(self, field):
        # Se deben seleccionar al menos 4 años (para tener respuestas)
        if len(field.data) < 4:
            raise ValidationError("Selecciona al menos cuatro años")

    def validate_seleccion_paises(self, field):
        # Se deben seleccionar al menos 4 paises (para tener respuestas)
        if len(field.data) < 4:
            raise ValidationError("Selecciona al menos cuatro paises")
