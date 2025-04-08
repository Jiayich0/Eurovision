// Cogemos la informacion desde "quiz-data"
const quizData = JSON.parse(document.getElementById("quiz-data").textContent);

// Obtenemos la informacion de los videos
const questions = quizData.preguntas;

let currentIndex = 0;
let player;
let startTime, videoLength;
let countdown;
let duration = 10; // tiempo de reproduccion
let puntuacion_total = 0; // puntuacion acumulada


function loadYouTubeAPI() {
    let tag = document.createElement("script");
    tag.src = "https://www.youtube.com/iframe_api";
    document.body.appendChild(tag);
}

function onYouTubeIframeAPIReady() {
    nextRound();
}

function loadNextVideo() {
    let videoId = questions[currentIndex].url_id;

    if (player) player.destroy(); // Cargarse el anterior player

    showLoading(true);

    player = new YT.Player("player", {
        height: "0",
        width: "0",
        videoId: videoId,
        playerVars: { autoplay: 1, controls: 0 },
        events: {
            onReady: (event) => {
                console.log("YouTube player ready");

                videoLength = event.target.getDuration();
                if (!videoLength || isNaN(videoLength)) {
                    console.error("Failed to retrieve video duration");
                    return;
                }

                startTime = Math.floor(Math.random() * (videoLength - duration));
                console.log("Start Time: " + startTime);

                event.target.seekTo(startTime);
                event.target.playVideo();
            },
            onStateChange: onPlayerStateChange
        }
    });
}


function startTimer(timeLeft) {
    clearInterval(countdown); // cargarse timers anteriores
    document.getElementById("timer").innerText = `Time left: ${timeLeft}s`;

    countdown = setInterval(() => {
        timeLeft--;
        document.getElementById("timer").innerText = `Time left: ${timeLeft}s`;

        if (timeLeft <= 0) {
            clearInterval(countdown);
            document.getElementById("timer").innerText = "";
        }
    }, 1000);
}

function stopVideo() {
    if (player) player.stopVideo();
    changeElementsInCategory("video", "none");
    changeElementsInCategory("pregunta", "block");
    showQuestion();
}

function onPlayerStateChange(event) {
    if (event.data === YT.PlayerState.ENDED) {
        stopVideo();
    }
    else if (event.data === YT.PlayerState.PLAYING) {
        startTimer(duration);
        setTimeout(stopVideo, duration * 1000); // Parar automáticamente
        showLoading(false);
    }
}

function showQuestion() {
    document.getElementById("question-container").style.display = "block";
    let questionObj = questions[currentIndex];
    document.getElementById("question").innerText = questionObj.pregunta;
    let answersDiv = document.getElementById("answers");
    answersDiv.innerHTML = "";
    document.getElementById("puntuacion-pregunta").innerText = questionObj.puntuacion;

    questionObj.respuestas.forEach((answer, index) => {
        let button = document.createElement("button");
        button.innerText = answer;
        button.className = "answer";
        button.onclick = () => checkAnswer(index, questionObj);
        answersDiv.appendChild(button);
    });

    document.getElementById("question-container").style.display = "block";
    currentIndex++;
}

function checkAnswer(selected, questionObj) {
    let buttons = document.querySelectorAll(".answer");
    let correct = questionObj.correcta;
    let puntos = questionObj.puntuacion;
    buttons.forEach((btn, idx) => {
        btn.onclick = null;
        if (idx === correct){
            btn.classList.add("correct");
            if (idx === selected) {
                questionObj["seleccionado"] = idx;
                puntuacion_total += puntos;
                document.getElementById("puntuacion").innerText = puntuacion_total;
            }
        }
        if (idx === selected && idx !== correct) {
            btn.classList.add("incorrect");
            questionObj["seleccionado"] = idx;
        }
    });

    document.getElementById("next-button").style.display = "block";

    if (currentIndex == questions.length) {
        document.getElementById("next-button").innerText = "Resultados";
    }
}

function nextVideo() {
    loadNextVideo();
}

function nextRound() {
    showLoading(false);
    document.getElementById("next-button").style.display = "none";
    if (currentIndex < questions.length) {
        if (questions[currentIndex].tipo === "pregunta") {
            document.getElementById("title-content").innerText = "¡Trivia!";
            changeElementsInCategory("video", "none");
            changeElementsInCategory("pregunta", "block");
            showQuestion();
        } else{
            document.getElementById("title-content").innerText = "¡Audio Quiz!";
            changeElementsInCategory("pregunta", "none");
            changeElementsInCategory("video", "block");
            loadNextVideo();
        }
    } else {
        document.getElementById("title-content").innerText = "¡Se acabó!";
        changeElementsInCategory("pregunta", "none");
        changeElementsInCategory("video", "none");

        // Disparamos el modal
        myModal.show();
    }
}

function changeElementsInCategory(category, newDisplay) {
    if (category === "video") {
        document.getElementById("audio-cover").style.display = newDisplay;
        document.getElementById("timer").style.display = newDisplay;
    }
    else {
        document.getElementById("question-container").style.display = newDisplay;
    }
}




const curiosidades = [
    "¿Sabías qué PostgreSQL tiene transacciones ACID...?\n Más estable que un código que *solo funciona en producción*.",
    "¿Sabías qué MongoDB escala horizontalmente...?\n Como la lista de tareas pendientes que nunca harás.",
    "¿Sabías qué hacer un JOIN sin condiciones...?\n Es como aceptar términos y condiciones sin leer.",
    "¿Sabías qué...?\n Vuestro profesor de base de datos se lo pasa DEMASIADO bien haciendo las prácticas.",
    "¿Sabías qué normalizar una base de datos evita redundancias...?\n Como cuando te repiten la misma broma en clase cinco veces.",
    "¿Sabías qué un DELETE sin WHERE...?\n Es como escribir en WhatsApp sin revisar a quién.",
    "¿Sabías qué los profesores de bases de datos dicen 'esto es fácil'...?\n Justo antes de soltar una query que ocupa media pizarra.",
    "¿Sabías qué la mejor forma de optimizar una consulta...?\n Es cerrar el portátil e irse a dormir.",
    "Cargando datos...\no al menos pretendiendo que sabemos lo que hacemos.",
    "Optimizando consultas...\no como lo llaman los programadores: 'tocarlo hasta que funcione'.",
    "Generando índices...\ncomo cuando finges ser productivo en clase.",
    "Protegiendo contra SQL Injection...\nsi tu usuario se llama 'admin' y tu contraseña es '1234', tenemos que hablar.",
    "Esperando respuesta del servidor...\nigual que esperas que te respondan los correos de la uni.",
    "Optimizando rendimiento...\nsi tu código es lento, tal vez el problema seas tú.",
    "Consejo: Un índice mal puesto es como una broma mal contada, nadie lo entiende y solo ralentiza todo.",
    "Consejo: Siempre haz backups...\nporque llorar no cuenta como solución de emergencia.",
    "Consejo: No confíes en un programador que dice 'esto es rápido, solo tarda unos segundos'.",
    "Consejo: Documenta tu base de datos...\nasí al menos podrás culpar a otro cuando todo falle.",
    "Consejo: Un DELETE sin WHERE es como un spoiler de película: arruina todo en un instante.",
    "Consejo: Si PostgreSQL dice que un campo es NULL, créelo. No discutas con la base de datos.",
    "Consejo: Hacer commits frecuentes no te salvará...\npero al menos tendrás puntos de control cuando todo explote.",
    "Consejo: Si una consulta es demasiado lenta...\nrevisa los índices antes de culpar al servidor.",
    "Consejo: Si tu consulta tarda demasiado, revisa los índices. Si sigue lenta, revisa tu carrera.",
    "Consejo: No puedes optimizar lo que no entiendes. Así que...\nsuerte con eso."
];

function showLoading(isLoading) {
    document.getElementById("loading").style.display = isLoading ? "block" : "none";
    if (isLoading){
        document.getElementById("mensaje-carga").innerText =  curiosidades[Math.floor(Math.random() * curiosidades.length)];
    }
}

loadYouTubeAPI();


// Muestra el resultado
function displayResult() {
    const questionList = document.getElementById('questionList');
    questionList.innerHTML = '';
    // Iteramos sobre las preguntas
    quizData.preguntas.forEach((item, index) => {
        const questionHTML = `
            <div class="card mb-3">
                <div class="card-body">
                    <h5 class="card-title mb-1">Pregunta ${index + 1}:</h5>
                    <h6 class="card-text my-3">${item.pregunta}</h6>
                    <p class="card-text my-1"><strong>Respuesta Correcta:</strong> ${item.respuestas[item.correcta]}</p>
                    <p class="card-text my-1"><strong>Tu Respuesta:</strong> ${item.respuestas[item.seleccionado]}</p>
                </div>
            </div>
        `;
        questionList.innerHTML += questionHTML;
    });
}

var myModal = new bootstrap.Modal(document.getElementById('quizModal'));
var quizModalElement = document.getElementById('quizModal');

quizModalElement.addEventListener('show.bs.modal', function () {
    displayResult();  // Funcion para mostrar las respuestas cuando se abre el modal
});

function mandarRespuestas(){
    fetch('/upload_contest', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken
      },
      body: JSON.stringify(quizData)
    })
    .then(response => response.json())
    .then(data => {
      if (data.redirect) {
        window.location.href = data.redirect;  // Redirigimos la informacion una vez hemos terminado
      } else {
        console.log('Server response:', data);
      }
    })
    .catch(error => console.error('Error:', error));}
