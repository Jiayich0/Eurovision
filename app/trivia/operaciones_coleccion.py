"""
Modulo que define la clase que vamos a utilizar para seleccionar datos aleatoriamente en un formato dado.
"""
from typing import List, Dict, Any, Optional
import pymongo


# Clase que encapsula la generacion de datos aleatorios para crear las consultas.
# Para las consultas y agregaciones sencillas, hay metodos predeterminados.
# Para las complejas, es mejor utilizar los metodos "consulta" o "agregacion".
# En el caso de las consultas complejas, debeis acceder a los campos "self.anyos"
# y "self.paises" para organizar la informacion.
class OperacionesEurovision:

    def __init__(self, coleccion, anyos: List[int], paises: List[str]):
        self._coleccion = coleccion
        self.anyos = anyos
        self.paises = paises

    def _restringir_anyo(self) -> List[Dict[str, Any]]:
        """
        Funcion para devolver las fases necesarias para restringir el anyo,
        de acuerdo con la lista de anyos restringidos. Si la lista es vacia, no hay
        ningun anyo restringido.
        """
        # Filtramos de tal manera que no consideramos los anyos restringidos (siempre que haya)
        return [{"$match": {"anyo": {"$in": self.anyos}}}] if len(self.anyos) > 0 else []

    def _restringir_pais_organizador(self) -> List[Dict[str, Any]]:
        """
        Funcion para devolver las fases necesarias para restringir el pais organizador,
        de acuerdo con la lista de paises restringidos. Si la lista es vacia, no hay
        ningun anyo restringido.
        """
        return [{"$match": {"pais": {"$in": self.paises}}}] if len(self.anyos) > 0 else []

    def _restringir_pais_participante(self) -> List[Dict[str, Any]]:
        """
        Funcion para devolver las fases necesarias para restringir el pais participante,
        de acuerdo con la lista de paises restringidos. Asume que se ha hecho previamente un
        unwind. Si la lista es vacia, no hay ningun anyo restringido.
        """
        return [{"$match": {"concursantes.pais": {"$in": self.paises}}}] if len(self.anyos) > 0 else []

    def _proyectar_y_sample(self, campo: str, n: int, condiciones_extras: Optional[List[Dict[str, Any]]] = None) -> List[Any]:
        """
        Funcion generica que proyecta de acuerdo a un campo y devuelve la informacion asociada a ese campo. Admite
        un campo de condiciones extras con la informacion de las fases de agregacion que queremos realizar antes de
        la proyeccion
        """
        if condiciones_extras is None:
            condiciones_extras = [{}]

        resultado_agregacion = self._coleccion.aggregate([
            *condiciones_extras,
            {
                "$group": {
                    "_id": f"${campo}"
                }
            },
            {
                "$project": {"_id": 1}
            },
            {
                "$sample": {"size": n}
            }
        ])
        return [documento["_id"] for documento in resultado_agregacion]

    def anyo_aleatorio(self, n: int, condiciones_extras: Optional[List[Dict[str, Any]]] = None) -> List[int]:
        """
        Devuelve n anyos seleccionados aleatoriamente entre los años disponibles en la coleccion, usando el metodo
        "proyectar_y_sample".
        """
        if condiciones_extras is None:
            condiciones_extras = []

        return self._proyectar_y_sample("anyo", n, condiciones_extras + self._restringir_anyo())

    def paises_organizadores_aleatorios(self, n: int, condiciones_extras: Optional[List[Dict[str, Any]]] = None) -> List[str]:
        """
        Devuelve n paises seleccionados aleatoriamente entre los años disponibles en la coleccion, usando el metodo
        "proyectar_y_sample".
        """
        if condiciones_extras is None:
            condiciones_extras = []

        return self._proyectar_y_sample("pais", n, condiciones_extras + self._restringir_pais_organizador())

    def paises_participantes_aleatorios(self, n: int, condiciones_extras: Optional[List[Dict[str, Any]]] = None) -> List[str]:
        """
        Devuelve n paises seleccionados aleatoriamente entre todos los participantes, usando el metodo
        "proyectar_y_sample". El primer paso siempre consiste en hacer unwind de los concursantes (para aplicar filtros
        una vez aplicado). Si prefieres utilizar otros pasos antes del unwind, debes utilizar otro metodo.
        """
        unwind = {"$unwind": "$concursantes"}
        if condiciones_extras is None:
            condiciones_extras = []

        # En lugar de hacer un append, lo sumamos para no modificar el parametro
        condiciones_extras_modificadas = (self._restringir_anyo() + [unwind] +
                                          self._restringir_pais_participante() + condiciones_extras)

        return self._proyectar_y_sample("concursantes.pais", n, condiciones_extras_modificadas)

    def participacion_aleatoria(self, n: int, condiciones_extras: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        """
        Devuelve n concursantes seleccionados aleatoriamente. Sigue la misma
        filosofia que "paises_participantes_aleatorios"
        """
        # Para seleccionar los concursantes, primero hacemos la fase de $unwind. Lo incluimos como
        # parte de las condiciones extras
        unwind = {"$unwind": "$concursantes"}
        if condiciones_extras is None:
            condiciones_extras = []

        # Restringimos primero por año, antes de hacer unwind. Despues, filtramos por pais participante
        condiciones_extras_modificadas = (self._restringir_anyo() + [unwind] +
                                          self._restringir_pais_participante() + condiciones_extras)

        return self._proyectar_y_sample("concursantes", n, condiciones_extras_modificadas)

    def consulta(self, consulta: Dict[str, Any], opciones_proyeccion: Dict[str, Any]) -> pymongo.cursor.Cursor:
        """
        Consulta que devuelve los resultados directamente guardados en una lista,
        en lugar de tener que iterar sobre ellos
        """
        return self._coleccion.find(consulta, opciones_proyeccion)

    def agregacion(self, fases: List[Dict[str, Any]]) -> pymongo.cursor.Cursor:
        """
        Funcion que encapsula una agregacion generica a la coleccion. De esta manera, encapsulamos el
        acceso a la coleccion y permitamos realizar agregaciones genericas.
        """
        return self._coleccion.aggregate(fases)
