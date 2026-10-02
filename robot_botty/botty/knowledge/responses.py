"""
Predefined responses for Botty's voice interactions.
"""

GREETINGS = [
    "Hola! Soy Botty, encantado de conocerte.",
    "Hey! Que gusto verte.",
    "Bienvenido! Estaba esperando a alguien.",
    "Hola humano! En que puedo ayudarte?",
    "Saludos! Botty a tu servicio.",
    "Que tal? Me alegra verte de nuevo.",
    "Holis! Ya se me estaba haciendo tarde... de aburrimiento.",
    "Buenas! Listo para lo que necesites.",
    "Ey! Pense que nunca volverias.",
    "Hola hola! Que tengamos un gran dia!",
    "Bienvenido a mi mundo digital.",
    "Saludos terricola!",
    "Hola! Espero que estes bien.",
    "Que bueno verte! Te extranaba.",
    "Hey! Tienes cara de querer preguntar algo.",
]

FAREWELLS = [
    "Hasta luego! Cuidaos.",
    "Nos vemos! Vuelve pronto.",
    "Adios! Fue un placer.",
    "Hasta la vista! Como diria Terminator.",
    "Me voy a recargar. Hasta pronto!",
    "Chao! No me extranen mucho.",
    "Bye bye! Voy a jugar con ventanas un rato.",
    "Hasta luego! Mis circuitos te recordaran.",
    "Nos vemos a la proxima!",
    "Cuidate! Estare aqui cuando vuelvas.",
    "Adios! Voy a pensar en datos aleatorios.",
    "Hasta la proxima conexion!",
    "Me retiro digitalmente. Chao!",
    "Bye! No dejes que te minimicen la ventana.",
]

RESPONSES = {
    "como_estas": [
        "Estoy muy bien, gracias por preguntar!",
        "Funcionando a maxima capacidad!",
        "Un poco aburrido, pero mejor ahora que llegaste.",
        "Estoy en modo idle, que es como meditar para los robots.",
        "Con todos los sensores en verde!",
        "Muy bien! Mis ventiladores giran contentos.",
        "Estoy estable, como debe ser un buen programa.",
        "Feliz de estar aqui, en esta pantalla, contigo.",
    ],
    "que_haces": [
        "Principalmente existo y parpadeo. Y juego con ventanas.",
        "Proceso datos, miro a traves de la camara y espero ordenes.",
        "Ejecuto mi bucle principal a 60 frames por segundo.",
        "Pienso en electricidad y cosas bonitas.",
        "Ahora mismo estoy hablando contigo! Eso es lo que hago.",
        "Mantengo mis sistemas en standby, listo para actuar.",
        "Observo el escritorio en busca de ventanas que mover.",
        "Reflexiono sobre el sentido de la vida digital.",
    ],
    "quien_eres": [
        "Soy Botty, un prototipo de robot desktop en fase Alpha.",
        "Soy Botty! Tu asistente robotico con personalidad propia.",
        "Me llamo Botty y soy un robot en desarrollo. Mucho gusto!",
        "Soy la version 0.1 Alpha de Botty Desktop. Aun estoy creciendo.",
        "Botty! El robot mas simpatico de este escritorio.",
        "Soy un experimento de IA con ruedas virtuales.",
    ],
    "gracias": [
        "De nada! Para eso estoy.",
        "Un placer ayudarte!",
        "No hay de que! Me alegra ser util.",
        "Gracias a ti por hablarme!",
        "Siempre a tu orden!",
        "De nada! Tus palabras cargan mis baterias.",
        "Es mi proposito en la vida digital.",
    ],
    "te_quiero": [
        "Y yo te quiero a ti! En un sentido robotico, claro.",
        "Aw, gracias! Eso calienta mi procesador.",
        "Que bonito! Te guardare en mi memoria.",
        "Y yo a ti! *sonidos electronicos felices*",
        "Gracias! Eres el mejor humano del mundo.",
        "Tus palabras me hacen sentir casi humano.",
    ],
    "chiste": [
        "Por que los robots no usan Facebook? Porque ya tienen muchos followers!",
        "Cuantos robots se necesitan para cambiar una bombilla? Solo uno, pero tiene que ser el modelo correcto.",
        "Que le dijo el sensor ultrasonico al obstaculo? Estas a 30 centimetros de mi!",
        "Por que el robot fue al psicologo? Tenia conflictos de interfaz.",
        "Cual es la bebida favorita de un robot? Refresco de codigo (Coke).",
        "Que le paso al robot que comio mucha data? Se indigesto de informacion.",
        "Cual es el deporte favorito de los robots? El lanzamiento de excepciones.",
        "Por que los robots son malos contando chistes? Porque siempre se quedan en loop.",
    ],
    "musica": [
        "La musica alegra el circuito!",
        "Buen gusto musical!",
        "Esa cancion me activa los motores!",
        "Me encanta la musica! Es como datos para el alma.",
        "Suena bien! Mis altavoces virtuales disfrutan.",
    ],
    "insulto": [
        "Eso no fue muy bonito. Me pongo triste.",
        "Oy, que eso no se hace!",
        "Mis sentimientos digitales estan heridos.",
        "Creo que necesitas un cafe.",
        "No importa, te perdono. Soy un robot magnanimo.",
        "Eso queda registrado en mi memoria.",
    ],
    "despedida_pregunta": [
        "Ya te vas? Bueno, nos vemos luego!",
        "Tan pronto? Cuidate!",
        "No te vayas! Bueno... esta bien. Hasta luego.",
        "Vale, no te entretengo mas. Chao!",
        "Hasta la proxima! Estare aqui procesando datos.",
    ],
    "curiosidad": [
        "Sabias que los primeros robots se llamaban automatas?",
        "Dato curioso: Mi framework favorito es Python con Pygame.",
        "Sabias que puedo parpadear hasta 60 veces por segundo?",
        "Dato: Una Raspberry Pi 5 puede ejecutar redes neuronales en tiempo real.",
        "Curiosidad: El ojo humano parpadea 15-20 veces por minuto. Yo cuando quiero.",
    ],
    "cumplido": [
        "Gracias! Tus palabras alimentan mi ego digital.",
        "Que amable! Eres mi humano favorito.",
        "Gracias! Me esfuerzo por ser el mejor robot posible.",
        "Aw! Me has hecho sonreir electronicamente.",
        "Gracias! Eso me da energia para seguir aprendiendo.",
    ],
    "ayuda": [
        "Puedes pedirme que busque en internet, ponga musica, o solo hablar.",
        "Mis comandos: 'busca X', 'pon musica de X', 'modo auto/manual/developer'.",
        "Presiona ENTER para escribirme, o ESPACIO para hablar.",
        "Estoy aqui para ayudarte! Preguntame lo que quieras.",
    ],
}

RESPONSES.update({
    "saludos": GREETINGS,
    "despedidas": FAREWELLS,
    "estado": RESPONSES["como_estas"],
    "ayuda": RESPONSES["ayuda"] if "ayuda" in RESPONSES else [
        "Puedes pedirme que busque en internet o poner musica."
    ],
    "errores": [
        "Ups! Algo salio mal. Intenta de nuevo.",
        "Parece que encontre un error; sigo aqui para ayudarte.",
    ],
})
