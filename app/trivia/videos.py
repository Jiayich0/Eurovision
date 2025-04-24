"""
Modulo para hacer cuestiones de trivia relacionadas con videos de Youtube. Creamos una clase TriviaVideo que extiende
a Trivia y almacena el id de reproduccion de video
"""
import random
from abc import ABC, abstractmethod
from typing import List
from pathlib import Path

from.operaciones_coleccion import OperacionesEurovision
from .preguntas import Trivia


def extraer_id_url(url) -> str:
    """
    Para renderizar el juego, necesitamos extraer el id desde la url del video.
    Utilizamos expresiones regulares
    """
    try:
        return Path(url).name
    except:
        # Return id for Rick Roll
        return "dQw4w9WgXcQ"


class TriviaVideo(Trivia, ABC):
    """
    Clase abstracta que contiene los metodos que deben incorporar las preguntas asociadas a videos.
    """
    @property
    @abstractmethod
    def url(self) -> str:
        pass

    def to_dict(self):
        # Modifica el diccionario de Trivia con la url del video
        # y el tipo "video"
        super_dict = super().to_dict()
        super_dict["url"] = self.url
        # Extraemos el id de la URL
        super_dict["url_id"] = extraer_id_url(self.url)
        super_dict["tipo"] = "video"
        return super_dict


class PaisActuacion(TriviaVideo):
    """
    ¿Que pais represento la cancion?
    """
    def __init__(self, parametros: OperacionesEurovision):
        participacion = parametros.participacion_aleatoria(1)[0]

        """ URL """
        self._url = participacion["url_youtube"]

        """ RESPUESTA CORRECTA """
        self._respuesta = participacion["pais"]

        """ RESPUESTAS INCORRECTAS """
        condicion = [{"$match": {"concursantes.pais": {"$ne": self._respuesta}}}]
        self._opciones_invalidas = parametros.paises_participantes_aleatorios(3, condicion)

    @property
    def url(self) -> str:
        return self._url

    @property
    def pregunta(self) -> str:
        return "¿A qué país representó esta canción?"

    @property
    def opciones_invalidas(self) -> List[str]:
        return self._opciones_invalidas

    @property
    def respuesta(self) -> str:
        return self._respuesta

    @property
    def puntuacion(self) -> float:
        return 3


class NombreCancion(TriviaVideo):
    """
    ¿Cual es el titulo de esta cancion?

    NOTA: para dificultar la respuesta, se deben seleccionar canciones del mismo pais.
    """
    def __init__(self, parametros: OperacionesEurovision):
        participacion = parametros.participacion_aleatoria(1)[0]

        """ URL """
        self._url = participacion["url_youtube"]

        """ RESPUESTA CORRECTA """
        self._respuesta = participacion["cancion"]

        """ RESPUESTAS INCORRECTAS """
        pipeline = [
            {"$unwind": "$concursantes"},
            {"$match": {
                "concursantes.pais": participacion["pais"],
                "concursantes.cancion":{"$ne": self._respuesta}}
            },
            {"$sample": {"size": 3}},
            {"$project": {"concursantes.cancion":1, "_id":0}}
        ]
        canciones_agregacion = list(parametros.agregacion(pipeline))
        canciones = [c["concursantes"]["cancion"] for c in canciones_agregacion]

        self._opciones_invalidas = canciones
        # FIXME preguntar
        """
        He pensado en varias opciones para las respuestas invalidas de cara a la eficiencia:
            1. Agregación, O(n), devolviendo una lista de dict. Transformo 'list de dict' en 'list de string', O(n).
               Random.sample de O(k) (k=3). Conversion a String O(k)
            2. Agregacion con {"$sample": {"size": 3}}, devolviendo una lista de dict de solo 3, O(k). Conversion a String O(k)
               Sample documentacion: https://www.mongodb.com/docs/manual/reference/operator/aggregation/sample/ 
               (no sale en la teoria, no se si puedo usarlo, preguntar al profe)
            3. Incluso se podria hacer con un sort + rand + limit:3 (no se que eficiencia tendría)
        """

    @property
    def url(self) -> str:
        return self._url

    @property
    def pregunta(self) -> str:
        return "¿Cual es el titulo de esta cancion?"

    @property
    def opciones_invalidas(self) -> List[str]:
        return self._opciones_invalidas

    @property
    def respuesta(self) -> str:
        return self._respuesta

    @property
    def puntuacion(self) -> float:
        return 2


class InterpreteCancion(TriviaVideo):
    """
    ¿Quien interpreto esta cancion?

    NOTA: para dificultar la respuesta, se deben seleccionar interpretes del mismo pais.
    """
    def __init__(self, parametros: OperacionesEurovision):
        participacion = parametros.participacion_aleatoria(1)[0]

        """ URL """
        self._url = participacion["url_youtube"]

        """ RESPUESTA CORRECTA """
        self._respuesta = participacion["artista"]

        """ RESPUESTAS INCORRECTAS """
        pipeline = [
            {"$unwind": "$concursantes"},
            {"$match": {
                "concursantes.pais": participacion["pais"],
                "concursantes.artista": {"$ne": self._respuesta}}
            },
            {"$sample": {"size": 3}},
            {"$project": {"concursantes.artista": 1, "_id": 0}}
        ]
        canciones_agregacion = list(parametros.agregacion(pipeline))
        canciones = [c["concursantes"]["artista"] for c in canciones_agregacion]

        self._opciones_invalidas = canciones


    @property
    def url(self) -> str:
        return self._url

    @property
    def pregunta(self) -> str:
        return f"¿Qué artista interpretó esta canción?"

    @property
    def opciones_invalidas(self) -> List[str]:
        return self._opciones_invalidas

    @property
    def respuesta(self) -> str:
        return self._respuesta

    @property
    def puntuacion(self) -> float:
        return 4
