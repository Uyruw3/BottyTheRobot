"""
Cooking module — recipes, food facts, and culinary knowledge.
"""

COOKING_FACTS = [
    "La mayonesa fue inventada en el siglo XVIII en Mahon, Menorca.",
    "La pizza margherita lleva los colores de la bandera italiana.",
    "El chocolate fue considerado bebida de dioses por los aztecas.",
    "La patata francesa no es francesa, es belga.",
    "El sushi se invento como metodo de conservacion del pescado.",
    "El cafe es la segunda bebida mas consumida del mundo despues del agua.",
    "La mostaza amarilla es la especia mas consumida del mundo.",
    "El queso mas caro del mundo es el Pule, hecho de leche de burra.",
    "Las especias impulsaron la exploracion global durante siglos.",
    "El pan tiene mas de 30,000 variedades diferentes en el mundo.",
    "Las manzanas flotan porque tienen 25% de aire en su interior.",
    "La miel nunca se echa a perder. Se han encontrado miel comestible en tumbas egipcias.",
    "Los pimientos picantes deben su picor a la capsaicina.",
    "El te verde y el te negro vienen de la misma planta.",
    "El aceite de oliva es la grasa mas saludable del mundo.",
    "Las almendras son semillas, no nueces.",
    "El champanon es la seta mas cultivada del mundo.",
    "El vinagre balsamico tradicional se envejece minimo 12 anos.",
    "La paella valenciana original lleva conejo y pollo, no marisco.",
    "Los espaguetis a la carbonara originales no llevan nata.",
]

COOKING_TIPS = [
    "Sazonar la pasta con sal gruesa en el agua de coccion potencia su sabor.",
    "Dejar reposar la carne despues de cocinarla redistribuye los jugos.",
    "Usar mantequilla fria para masas quebradas da una textura mas hojaldrada.",
    "El punto de coccion de un huevo se controla por la temperatura del agua.",
    "Marinar la carne minimo 30 minutos antes de cocinar mejora el sabor.",
    "Tostar las especias en seco antes de usarlas intensifica su aroma.",
    "No lavar los champiñones: limpiarlos con un pano humedo.",
    "El aceite de oliva virgen extra no debe usarse para freir a altas temperaturas.",
    "La sal en el cafe reduce su amargor, no el azucar.",
    "Un chorrito de limon realza el sabor de casi cualquier plato.",
    "La temperatura ambiente es clave para masas de pan y bollería.",
    "Usar agua fria para hervir huevos evita que se rompan.",
]

RECIPES = {
    "tortilla_patatas": {
        "name": "Tortilla de Patatas",
        "origin": "Espana",
        "ingredients": ["4 huevos", "3 patatas grandes", "1 cebolla", "aceite de oliva", "sal"],
        "instructions": "Pelar y cortar patatas en rodajas finas. Freir en abundante aceite hasta que esten tiernas. Batir huevos con sal. Mezclar con patatas. Cuajar en sarten con un poco de aceite.",
        "time_minutes": 30,
        "difficulty": "media"
    },
    "guacamole": {
        "name": "Guacamole",
        "origin": "Mexico",
        "ingredients": ["2 aguacates", "1 tomate", "cebolla", "cilantro", "limon", "sal", "chile"],
        "instructions": "Machacar aguacates. Picar finamente tomate, cebolla y cilantro. Mezclar todo con jugo de limon, sal y chile al gusto.",
        "time_minutes": 10,
        "difficulty": "facil"
    },
    "pasta_aglio_olio": {
        "name": "Pasta Aglio e Olio",
        "origin": "Italia",
        "ingredients": ["200g spaghetti", "4 dientes ajo", "guindilla", "aceite oliva", "perejil", "sal"],
        "instructions": "Cocer pasta al dente. Dorar ajo laminado y guindilla en aceite. Mezclar con pasta escurrida. Anadir perejil fresco.",
        "time_minutes": 20,
        "difficulty": "facil"
    },
    "ceviche": {
        "name": "Ceviche Peruano",
        "origin": "Peru",
        "ingredients": ["500g pescado blanco", "limon", "cebolla morada", "aji limo", "cilantro", "sal", "camote"],
        "instructions": "Cortar pescado en cubos. Macerar en jugo de limon con sal por 15 minutos. Anadir cebolla en juliana, aji y cilantro. Servir con camote cocido.",
        "time_minutes": 30,
        "difficulty": "media"
    },
    "chilaquiles": {
        "name": "Chilaquiles Verdes",
        "origin": "Mexico",
        "ingredients": ["tortillas", "salsa verde", "crema", "queso fresco", "pollo", "cebolla", "cilantro"],
        "instructions": "Cortar tortillas en triangulos y freir. Calentar salsa verde. Mezclar totopos con salsa caliente. Servir con crema, queso, pollo deshebrado, cebolla y cilantro.",
        "time_minutes": 25,
        "difficulty": "facil"
    },
    "falafel": {
        "name": "Falafel",
        "origin": "Medio Oriente",
        "ingredients": ["garbanzos", "cebolla", "ajo", "perejil", "comino", "cilantro", "sal", "aceite"],
        "instructions": "Triturar garbanzos crudos con cebolla, ajo y hierbas. Formar bolitas y freir en aceite caliente hasta dorar. Servir con pan pita y salsa de yogur.",
        "time_minutes": 40,
        "difficulty": "media"
    },
    "ratatouille": {
        "name": "Ratatouille",
        "origin": "Francia",
        "ingredients": ["berenjena", "calabacin", "tomate", "pimiento", "cebolla", "ajo", "hierbas provenzales", "aceite oliva"],
        "instructions": "Cortar todas las verduras en rodajas finas. Sofreir cebolla y ajo. Colocar verduras en capas. Anadir hierbas y hornear a 180 grados por 45 minutos.",
        "time_minutes": 60,
        "difficulty": "media"
    },
}
