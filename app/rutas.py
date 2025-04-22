"""
Módulo de Python que contiene las rutas
"""
import datetime
from flask import current_app as app, render_template, redirect, url_for, flash, abort, request
from .formularios import GenerarQuizForm
from . import mongo
from .trivia import generar_n_preguntas_aleatoriamente
from .render_utils import render_pagination


@app.route("/")
@app.route("/ediciones")
def mostrar_ediciones():
    # Muestra la lista de ediciones, utilizando una paginacion.
    # Os proporciono los metodos para cargar la pagina actual y
    # renderizar la respuesta (con el elemento pagination). Vosotros teneis que hacer
    # la carga de informacion la base de datos. En particular, debeis cuantos documentos
    # hay en total para computar "total_elementos" (podeis utilizar el metodo "count_documents").

    # Pagina actual de resultados
    pagina = int(request.args.get('page', 1))

    # Numero de elementos por pagina
    elementos_por_pagina = 5

    # AQUI VA VUESTRO CODIGO
    # Nota importante:
    #   en find({}, {})
    #       el primer {} es el filtro, WHERE en SQL
    #       el segundo {} son las columnas/campos que quieres o no traer, SELECT en SQL
    #           {"x":1, "y":1} : obtienes los campos x e y (+ campo id, por defecto)
    #           {"x":0, "y":0} : obtienes todos los campos excepto x e y
    #           {"x":1, "y":0} : error, no se pueden mezclar 1 y 0 (excepto id que puede ser 0)
    total_elementos = mongo.db["festivales"].count_documents({})
    skip = (pagina - 1) * elementos_por_pagina # Paginacion: empeiza en el 0, 5, 10, etc
    festivales = list(
        mongo.db["festivales"]
        .find({}, {"anyo":1, "ciudad":1, "pais":1, "fecha":1, "concursantes":1})
        .skip(skip)                     # Empiezan desde x pagina, cada 5 (paginate)
        .limit(elementos_por_pagina)    # 5 por pagina (paginate)
        .sort("anyo", -1)               # Aunque esté el útlimo, pyhton primero hace el sort y luego el skip y limit
    )

    # Descomentad cuando cargueis la informacion
    paginacion = render_pagination(pagina, elementos_por_pagina, total_elementos, 'mostrar_ediciones')

    return render_template("mostrar_ediciones.html", festivales=festivales,
                            pagination=paginacion, pagina=pagina)


@app.route("/edicion/<int:anyo>")
def mostrar_festival(anyo: int):
    # Mostrar la lista de participaciones, dado un anyo.
    # Devuelve un error 404 si no se encuentra presente ese anyo.
    # Como respuesta, renderiza el template "mostrar_actuaciones_edicion.html"
    festival = mongo.db["festivales"].find_one({"anyo": anyo}, {"_id":0, "fecha":0, "anyo":0})

    if not festival:
        abort(404)

    return render_template(
        "mostrar_actuaciones_edicion.html",
        anyo=festival["anyo"],
        ciudad=festival["ciudad"],
        pais_organizador=festival["pais"],
        participaciones=festival["concursantes"]
    )


@app.route('/jugar')
def jugar_quiz():
    # Jugar a un quiz. Esta funcion NO la teneis que modificar
    # (salvo probar diferentes num_preguntas si quereis un quiz mas largo).
    # Hay dos opciones: si no venimos de 'generar_quiz',
    # la lista de anyos y paises es vacia. Este caso se procesa en "OperacionesEurovision",
    # ya que si las listas son vacias, se asume que no hay ninguna restriccion.
    # Esta informacion se la proporcionamos al metodo "generar_n_preguntas_aleatoriamente", el cual devuelve
    # "n" preguntas que extienden a Trivia. Hay que proporcionar estas preguntas con el metodo "to_dict()" (para
    # convertir en diccionario) a la funcion "funcion_quiz_json"
    anyos = request.args.getlist("anyos", type=int)
    paises = request.args.getlist("paises")
    nombre = request.args.get("nombre", None)
    num_preguntas = 1

    preguntas_aleatorias = generar_n_preguntas_aleatoriamente(num_preguntas, anyos, paises, mongo.db["festivales"])

    preguntas = {"preguntas": [pregunta.to_dict() for pregunta in preguntas_aleatorias]}

    # Solo guardamos un nombre si no es nulo ni vacio
    if nombre:
        preguntas["_id"] = nombre

    return render_template("juego.html", preguntas=preguntas, guardable=nombre is not None)

# TODO
@app.route('/quiz', methods=['GET', 'POST'])
def generar_quiz():
    # Generacion de un quiz personalizado.
    # Para crear un Quiz, tenemos que crear un formulario "GenerarQuizForm", el cual
    # debe recibir la lista de anyos y la lista de paises disponibles en la base de datos en su constructor.
    # La lista de anyos debe ir ordenada de forma descendente, y la lista de paises de forma ascendente.
    # El formulario se debe renderizar con "crear_quiz.html"
    # Una vez el formulario se valide correctamente, debemos redireccionar a la funcion de vista
    # 'jugar_quiz', que debe recibir la lista de anyos (variable "anyos"), la lista de paises (variable "paises")
    # y el nombre del formulario (variable "nombre"). Estas variables se leen con request.args.get
    abort(404)


@app.route("/pais/<id_pais>")
def mostrar_actuaciones_pais(id_pais: str):
    # Muestra todas las actuaciones de un pais, ordenadas de forma decreciente en funcion del anyo.
    # Si el id del pais no existe, devuelve un error 404.
    # En esta funcion, utilizamos una paginacion para no cargar todos los resultados
    # de golpe. Os proporciono directamente como cargar la pagina correspondiente (con request.args.get)
    # y como generar la paginacion. Vosotros teneis que obtener cuantos elementos hay en total, y
    # filtrar los elementos que se corresponden a la pagina ("pagina") teniendo en cuenta el numero de elementos
    # que hay en cada pagina ("elementos_por_pagina")

    pagina = int(request.args.get('page', 1))
    elementos_por_pagina = 10

    # AQUI VA VUESTRO CODIGO
    if not id_pais:     # el problema es que solo verifca que id no sea ni null ni vacio pero si un pais no existe? -> if not participaciones
        abort(404)

    skip = (pagina - 1) * elementos_por_pagina

    participaciones_agregacion = [                             # para entenderlo es como hacer una version plana de doc
        {"$unwind": {"path": "$concursantes"}},                 # Deconstruyo mi array
        {"$match": {"concursantes.id_pais": id_pais}},          # Wgere id = id
        {"$sort": {"anyo":-1}},                                 # Descendente 2017>1999>1950
        {"$skip": skip},
        {"$limit": elementos_por_pagina},
        {"$project": {
            "_id": 0,                                           # exluey
            "anyo": 1,                                          # incluye
            "pais_organizador": "$pais",                        # se crea un campo para diferenciar e pais concursante
            "ciudad": 1,
            "artista": "$concursantes.artista",                 # se crea un campo para deconstruir el doc
            "cancion": "$concursantes.cancion",
            "resultado": "$concursantes.resultado",
            "puntuacion": "$concursantes.puntuacion",
            "url_youtube": "$concursantes.url_youtube",
            "pais_nombre": "$concursantes.pais"
        }}
    ]
    participaciones = list(mongo.db["festivales"].aggregate(participaciones_agregacion))

    if not participaciones:
        abort(404)

    nombre_pais = participaciones[0]["pais_nombre"]

    conteo_agregacion = [
        {"$unwind": "$concursantes"},
        {"$match": {"concursantes.id_pais": id_pais}},
        {"$count": "total"}
    ]
    conteo = list(mongo.db["festivales"].aggregate(conteo_agregacion))

    total_elementos = conteo[0]["total"]

    # Descomentad cuando cargueis la informacion
    paginacion = render_pagination(pagina, elementos_por_pagina, total_elementos, 'mostrar_actuaciones_pais', id_pais=id_pais)

    return render_template("mostrar_actuaciones_pais.html", pais=nombre_pais, participaciones=participaciones,
                           pagination=paginacion, pagina=pagina)

# TODO
@app.route("/upload_contest", methods=["POST"])
def guardar_concurso():
    # Guarda un concurso personalizado.
    # A esta funcion se le invoca al acabar un quiz, si el usuario
    # decide almacenar las preguntas que se han generado.
    # La informacion "data" se guarda en la coleccion "quizzes".
    # Hay que hacer dos cambios sobre el diccionario "data":
    #
    # * Borrar el campo "seleccionado" de cada pregunta,
    #   ya que no nos interesan las respuestas del usuario.
    #
    # * Añadir la fecha de creacion en el campo "creacion"
    #
    # Una vez se ha almacenado la informacion, se redirige a la lista de quizzes.

    # data es el diccionario con la informacion
    data = request.get_json()

    # AQUI VA VUESTRO CODIGO

    # En este caso, no hacemos un redirect directamente porque desde JS no se reconoce
    # bien. En su lugar, devolvemos la respuesta en un json
    return {'redirect': url_for('mostrar_quizzes')}

# TODO
@app.route("/quizzes")
def mostrar_quizzes():
    # Muestra la lista de quizzes en la aplicacion, utilizando una paginacion.
    # Os proporciono los metodos para cargar la pagina actual y
    # renderizar la respuesta (con el elemento pagination). Vosotros teneis que hacer
    # la carga de informacion la base de datos y renderizar "listar_quizzes.html".
    # La lista de quizzes se debe cargar en orden decreciente segun la fecha de creacion.

    # Pagina actual de resultados
    pagina = int(request.args.get('page', 1))

    # Numero de elementos por pagina
    elementos_por_pagina = 20

    # Descomentad cuando cargueis la informacion
    # paginacion = render_pagination(pagina, elementos_por_pagina, total_elementos, 'mostrar_quizzes')

    # return render_template("listar_quizzes.html", quizzes=quizzes,
    #                        pagination=paginacion, pagina=pagina)
    abort(404)

# TODO
@app.route("/jugar/<nombre_quiz>")
def jugar_quiz_personalizado(nombre_quiz: str):
    # Juega a un quiz que ha sido creado previamente por un usuario
    # Primero, hay que comprobar un quiz con ese nombre en la coleccion
    # "quizzes". En tal caso, cargamos toda la informacion y renderizamos "juego.html".
    # Si no es asi, lanzamos un error 404.
    abort(404)
