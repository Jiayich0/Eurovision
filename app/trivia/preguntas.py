"""
Modulo que contiene diferentes modelos de consulta para la seccion de "trivia".
"""
import random
from typing import List
from abc import ABC, abstractmethod
from .operaciones_coleccion import OperacionesEurovision


# Clases para encapsular las preguntas y respuestas generadas aleatoriamente
class Trivia(ABC):
    """
    Clase abstracta con los metodos que deben implementar todas las preguntas de trivia.
    """
    @abstractmethod
    def __init__(self, parametros: OperacionesEurovision):
        # Obligamos a que todos los constructores les pasen un objeto con los parametros aleatorios
        pass

    @property
    @abstractmethod
    def pregunta(self) -> str:
        """
        Pregunta que se debe mostrar
        """
        pass

    @property
    @abstractmethod
    def opciones_invalidas(self) -> List[str]:
        """
        Lista de opciones invalidas. Deben ser exactamente 3
        """
        pass

    @property
    @abstractmethod
    def respuesta(self) -> str:
        """
        Respuesta correcta
        """
        pass

    @property
    @abstractmethod
    def puntuacion(self) -> int:
        """
        Puntuacion asociada a la pregunta
        """
        pass

    def to_dict(self):
        # Sorteamos aleatoriamente las respuestas
        respuestas = [self.respuesta, *self.opciones_invalidas]
        random.shuffle(respuestas)

        # Funcion que genera la informacion que pasamos al script de trivia en el formato adecuado
        return {"pregunta": self.pregunta,
                "correcta": respuestas.index(self.respuesta),
                "respuestas": respuestas,
                "puntuacion": self.puntuacion,
                "tipo": "pregunta"}


class PrimerAnyoParticipacion(Trivia):
    """
    Pregunta que anyo fue el primero en el que participo un pais seleccionado aleatoriamente
    """

    def __init__(self, parametros: OperacionesEurovision):
        """
        Dada una <participacion>, se extrae el pais y se saca todas las <participaciones> de ese pais. Es un map/diccionario
        {anyo:1999, anyo:...}, pero para ordenar necesito una lista: extraigo los años en una lista <anyos> [1999, ...] y
        obtengo el año pillando el primero (sort: menor a mayor) de la lista. Importante, es un string no un int
        """
        participacion = parametros.participacion_aleatoria(1)[0]
        # como devulve una lista de n elementos (n=1 en este caso) yo solo quiero el primer elemento, el 0, por eso [0]
        # es equivalente a sacar la lista, y de al lista sacar el [0], pero python me deja hacerlo directamente

        """ PAIS """
        self.pais = participacion["pais"]

        """ RESPUESTA CORRECTA """
        participaciones = parametros.consulta(
            {"concursantes.pais": self.pais},
            {"anyo":1, "_id":0}
        )

        anyos = sorted(p["anyo"] for p in participaciones)  # más pythonic
        """anyos = []
        for p in participaciones:
            anyos.append(p["anyo"])
        anyos.sort()"""

        self._respuesta = str(anyos[0])

        """ RESPUESTAS INCORRECTAS """
        condicion = [{"$match": {"anyo": {"$ne": anyos[0]}}}]     # = where anyo != anyos[0]
        invalidos = parametros.anyo_aleatorio(3, condicion)

        self._opciones_invalidas = [str(inv) for inv in invalidos]


    @property
    def pregunta(self) -> str:
        return f"¿En qué año participó por primera vez {self.pais}?"

    @property
    def opciones_invalidas(self) -> List[str]:
        return self._opciones_invalidas

    @property
    def respuesta(self) -> str:
        return self._respuesta

    @property
    def puntuacion(self) -> int:
        """
        Puntuacion asociada a la pregunta
        """
        return 2


class CancionPais(Trivia):
    """
    Pregunta de que pais es el interprete de una cancion, dada el titulo de la cancion
    """

    def __init__(self, parametros: OperacionesEurovision):
        # Obtenemos una participacion para la respuesta
        participacion = parametros.participacion_aleatoria(1)[0]

        """ CANCION """
        self._cancion = participacion["cancion"]

        """ RESPUESTA CORRECTA """
        self._respuesta = participacion["pais"]

        """ RESPUESTAS INCORRECTAS """
        condicion = [{"$match": {"concursantes.pais": {"$ne": self._respuesta}}}]
        invalidos = parametros.paises_participantes_aleatorios(3, condicion)

        self._opciones_invalidas = invalidos

    @property
    def pregunta(self) -> str:
        return f"¿De que país es el intérprete de la canción '{self._cancion}'?"

    @property
    def opciones_invalidas(self) -> List[str]:
        return self._opciones_invalidas

    @property
    def respuesta(self) -> str:
        return self._respuesta

    @property
    def puntuacion(self) -> int:
        """
        Puntuacion asociada a la pregunta
        """
        return 3


class MejorClasificacion(Trivia):
    """
    Pregunta: ¿Que cancion/pais obtuvo la mejor posicion en un anyo dado?

    Respuesta: las respuestas deben ser de la forma cancion/pais.

    IMPORTANTE: la solucion debe ser unica. Ademas, todos las opciones
    deben haber participado el mismo anyo.
    """
    def __init__(self, parametros: OperacionesEurovision):
        participacion = parametros.participacion_aleatoria(1)[0]

        """ AÑO """
        anyo = parametros.consulta(
            {"concursantes": participacion},
            {"anyo": 1, "_id": 0}
        ).next()

        self._anyo = anyo["anyo"]   # creoq ue esto se puede hacer con agregate FIXME preguntar al profe

        """ RESPUESTA CORRECTA """
        edicion = parametros.consulta(
            {"anyo": self._anyo},
            {"concursantes.pais": 1, "concursantes.cancion": 1, "concursantes.resultado": 1, "_id":0}
            # mas eficiente solo devuelvo los tres datos que quiero
        ).next()    # devuelve un cursor, itera, pero queremos el primero y se hace .next (aunque solo haya uno)

        concursantes = edicion["concursantes"]
        concursantes.sort(key=lambda c: c["resultado"])
        ganador = concursantes[0]

        self._respuesta = ganador["cancion"] + "/" + ganador["pais"]

        """ RESPUESTAS INCORRECTAS """
        opciones = random.sample(concursantes[1:],3)
        # sample genera unicos al azar (evita duplicados) y con concursantes[1:] exlcuye al primero (ganador)
        invalidos = [f"{c['cancion']}/{c['pais']}" for c in opciones]
        # moderno + pythonic. Mejor que [c["cancion"] + "/" + c["pais"] for c in opciones]
        # al parecer es lo mismo c["pais"] que c['pais']. Comillas dobles o simples son iguales

        self._opciones_invalidas = invalidos

    @property
    def pregunta(self) -> str:
        return f"¿Que canción/país obtuvo la mejor posición en {self._anyo}?"

    @property
    def opciones_invalidas(self) -> List[str]:
        return self._opciones_invalidas

    @property
    def respuesta(self) -> str:
        return self._respuesta

    @property
    def puntuacion(self) -> int:
        return 1


class MejorMediaPuntos(Trivia):
    """
    Pregunta que pais ha tenido mejor media de resultados en un periodo determinado.

    IMPORTANTE: la solucion debe ser unica.
    """
    def __init__(self, parametros: OperacionesEurovision):
        self._anyo_inicial = None
        self._anyo_final = None
        self._opciones_invalidas = None
        self._respuesta = None

    @property
    def pregunta(self) -> str:
        return f"¿Qué país quedó mejor posicionado de media entre los años {self._anyo_inicial} y {self._anyo_final}?"

    @property
    def opciones_invalidas(self) -> List[str]:
        return self._opciones_invalidas

    @property
    def respuesta(self) -> str:
        return self._respuesta

    @property
    def puntuacion(self) -> int:
        return 4
