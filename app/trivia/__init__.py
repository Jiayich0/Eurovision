"""
Solo se "exponen" aquellos metodos que queremos que se utilicen.
"""
import random
from typing import List
from .operaciones_coleccion import OperacionesEurovision
from .videos import PaisActuacion, NombreCancion, InterpreteCancion
from .preguntas import CancionPais, Trivia, PrimerAnyoParticipacion, MejorClasificacion, MejorMediaPuntos

# Esta es la lista de preguntas posibles de trivia. Segun vayais resolviendolas,
# id incluyendolas en esta lista.
_preguntas_posibles = [] # [PrimerAnyoParticipacion, CancionPais, MejorClasificacion, MejorMediaPuntos,
                         #  PaisActuacion, NombreCancion, InterpreteCancion ]


def generar_n_preguntas_aleatoriamente(n: int, anyos: List[int],
                                       paises: List[str], coleccion_eurovision) -> List[Trivia]:
    """
    Genera n preguntas aleatoriamente entre la lista de preguntas posibles.
    """
    operaciones = OperacionesEurovision(coleccion_eurovision, anyos, paises)
    return [random.choice(_preguntas_posibles)(operaciones) for _ in range(n)]
