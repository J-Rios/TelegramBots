# -*- coding: utf-8 -*-
'''
Script:  MolaBot.py

Descripcion:
    Bot de Telegram que gestiona todo un sistema de reputaciones de los usuarios pertenecientes a
    un grupo. Permite a un usuario, dar "Likes" a los mensajes de otros, y el numero global de
    "Likes" (la suma de todos los likes de todos los mensajes de un mismo usuario) determinara los
    puntos de reputacion que dicho usuario tiene.

Autor:   Jose Rios Rubio
Fecha:   23/07/2017
Version: 1.6
'''

# Constantes para el Bot
CONST = {
    'PYTHON' : 2, # Compatibiidad con version de python (2 o 3)
    'TOKEN': 'XXXXXXXXX:XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX', # A establecer por el usuario (obtener de @BotFather)
    'MASTER_ID': 'NNNNNNNNN', # A establecer por el usuario (obtener de @get_id_bot)
    'ADMINS_ID': ['NNNNNNNNN'], # ID de los Admins
    'F_USR' : './data/users.json', # Nombre del archivo json de usuarios
    'F_MSG' : './data/messages.json', # Nombre del archivo json de mensajes
    'GIVE_REP_MOD' : 5, # Cuando un mensaje alcanza un modulo de 5 en sus likes (5, 10, 15 ...), dar reputacion al usuario
    'GIVE_REP_POINTS' : 5, # Reputacion por GIVE_REP_MOD likes. Actualmente, dar los mismos 5 puntos de reputacion por cada like obtenido en un mensaje
    'REP_LVL_POINTS' : [100, 200, 350, 500, 700, 1000, 1500, 2500, 5000, 10000], # Puntos correspondientes a los niveles/rangos de reputacion
    'REP_LVL' : ['0 - Recien llegado (Raspynoob)', '1 - Novato y a mucha honra!', '2 - Aprendiendo y ayudando...', '3 - De los que piden para churros', '4 - El de la Pole!', '5 - El que controla algo del tema', '6 - Usuario poco comun', '7 - A ver quien alcanza a este', '8 - Sabe mas que el diablo', '9 - Por encima de cualquiera'], # Niveles/Rangos de reputacion
    'EMO_HAND_UP' : ['👍', u'\U0001f44d', '👍🏻', u'\U0001f44d\U0001f3fb', '👍🏼', u'\U0001f44d\U0001f3fc', '👍🏽', u'\U0001f44d\U0001f3fd', '👍🏾', u'\U0001f44d\U0001f3fe', '👍🏿', u'\U0001f44d\U0001f3ff'], # Lista de emoticono de manita arriba
    'EMO_HAND_DOWN' : ['👎', u'\U0001f44e', '👎🏻', u'\U0001f44e\U0001f3fb', '👎🏼', u'\U0001f44e\U0001f3fc', '👎🏽', u'\U0001f44e\U0001f3fd', '👎🏾', u'\U0001f44e\U0001f3fe', '👎🏿', u'\U0001f44e\U0001f3ff'] # Lista de emoticono de manita abajo
}
