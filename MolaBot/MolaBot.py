# -*- coding: utf-8 -*-
'''
Script:  MolaBot.py

Descripcion:
    Bot de Telegram que gestiona todo un sistema de reputaciones de los usuarios pertenecientes a
    un grupo. Permite a un usuario, dar "Likes" a los mensajes de otros, y el numero global de
    "Likes" (la suma de todos los likes de todos los mensajes de un mismo usuario) determinara los
    puntos de reputacion que dicho usuario tiene.

Autor:   Jose Rios Rubio
Fecha:   19/07/2017
Version: 1.1
'''

### Librerias ###

# Importacion de librerias
import TSjson
import datetime

# Importacion desde librerias
from Constants import CONST
from collections import OrderedDict
from telegram import MessageEntity, ParseMode, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, RegexHandler, \
                         ConversationHandler, CallbackQueryHandler

##############################

### Variables Globales ###
fjson_usr = TSjson.TSjson(CONST['F_USR']) # Objeto de la clase TSjson para el manejo seguro del archivo de usuarios
fjson_msg = TSjson.TSjson(CONST['F_MSG']) # Objeto de la clase TSjson para el manejo seguro del archivo de mensajes

##############################

### Funciones para leer-escribir los archivos json especificos de este programa ###

# Funcion para obtener los datos de reputacion de un usuario a traves de un ID
def get_reputation(user_id):
    
    content = fjson_usr.read_content() # Leer el contenido del archivo de usuarios
    
    for usr in content: # Para cada usuario del archivo
        if user_id == usr['User_id']: # Si el usuario presenta el ID que estamos buscando
            return usr # Devolvemos los datos de reputacion de ese usuario
    
    return {} # Devolvemos un diccionario vacio si no se encontro el usuario

# Funcion para obtener los datos de likes de un mensaje a traves de un ID
def get_likes(msg_id):
    
    content = fjson_msg.read_content() # Leer el contenido del archivo de mensajes
    
    for msg in content: # Para cada mensaje del archivo
        if msg_id == msg['Msg_id']: # Si el mensaje presenta el ID que estamos buscando
            return msg # Devolvemos los datos de ese mensaje
    
    return None # Devolvemos un diccionario vacio si no se encontro el mensaje

# Funcion para dar like a un mensaje
def give_like(voter_id, voter_name, msg_id):
    
    likes_data = get_likes(msg_id) # Obtener los datos de likes del mensaje con dicho ID
    if likes_data is not None: # Si los datos de likes no estan vacios (se encontro al usuario)
        if not hasVoted(voter_id, msg_id): # Si el usuario que vota aun no ha votado
            likes_data['Data']['Likes'] = likes_data['Data']['Likes'] + 1 # Dar el like
            likes_data['Data']['Voters'][voter_name] = voter_id # Añadir al usuario que vota a los votantes de ese mensaje
            fjson_msg.update(likes_data, 'Msg_id') # Actualiza el archivo de mensajes con los nuevos datos (likes y votantes)
            
            if likes_data['Data']['Likes'] % CONST['GIVE_REP_MOD'] : # Si el numero de likes actual es modulo de GIVE_REP_MOD (e.g. para mod 5: 5, 10, 15 ...)
                lvl_up = increase_reputation(likes_data['Data']['User_id']) # Incrementamos la reputacion
                if lvl_up: # Si se ha subido de nivel
                    return "LVL_UP" # Devolvemos "LVL_UP" (se ha subido de nivel)
            return "Ok" # Devolvemos "Ok" (se ha dado el like)
        else: # El usuario que vota ya dio su like con anterioridad
            print("    El votante ya voto con anterioridad") # Escribir en consola
            print("") # Escribir en consola
            return "Voted" # Devolvemos "Voted" (no se ha dado el like porque el usuario que vota ya dio su like con anterioridad)
    else:
        print("    Error: Mensaje con ID {} no encontrado en el archivo {}".format(msg_id, CONST['F_MSG'])) # Escribir en consola el error
        return "Error" # Devolvemos "Error" (no se ha dado el like porque el archivo no existe o se ha producido un fallo al leer/escribir en el)

# Funcion para incrementar la reputacion de un usuario
def increase_reputation(user_id):
    
    lvl_up = 0 # Subida de nivel
    user_data = get_reputation(user_id) # Obtenemos los datos de reputacion del usuario con ese ID
    user_data['Reputation'] = user_data['Reputation'] + CONST['GIVE_REP_POINTS'] # Damos los nuevos puntos de reputacion
    
    lvl = 9 # Iniciamos el posible nivel de usuario a 9
    for i in range(0, 8, 1): # De 0 a 8
        if user_data['Reputation'] < CONST['REP_LVL_POINTS'][i+1]: # Si los puntos de reputacion del usuario son inferiores a los puntos de reputacion necesarios para estar en el siguiente nivel i+1
            lvl = i # Determinamos el nivel de usuario
            break # Interrumpimos y salimos del bucle
    
    if CONST['REP_LVL'][lvl] != user_data['Level']: # Si el nivel de usuario, correspondiente a la nueva reputacion, es distinto al nivel de usuario anterior
        user_data['Level'] = CONST['REP_LVL'][lvl] # Damos el nuevo rango/nivel al usuario
        lvl_up = 1 # Se ha subido de nivel
    
    fjson_usr.update(user_data, 'User_id') # Actualizamos en el archivo de usuarios con los datos de reputacion de dicho usuario

    return lvl_up # Devolvemos si se ha subido de nivel o no

# Funcion para determinar si un usuario ha votado con anterioridad a un mensaje
def hasVoted(voter_id, msg_id):
    
    content = fjson_msg.read_content() # # Leer el contenido del archivo de mensajes
    
    for msg in content: # Para cada mensaje del archivo
        if msg_id == msg['Msg_id']: # Si el mensaje presenta el ID que estamos buscando
            for ids in msg['Data']['Voters'].items(): # Para cada votante de ese mensaje
                if voter_id == ids[1]: # Si el ID del usuario que vota se encuentra entre los votantes
                    return True # Devolvemos True
    return False # Devolvemos False si no se ha encontrado el ID del usuario que vota en la lista de los usuarios que votaron con anterioridad

# Funcion para añadir un nuevo usuario al archivo de usuarios
def add_new_user(user_id, user_name):
    
    rep = OrderedDict([('User_id', 'Null'), ('User_name', 'Null'), ('Reputation', 100), ('Level', CONST['REP_LVL'][0])]) # Estructura inicial basica de usuario
    rep['User_id'] = user_id # Insertamos el ID del usuario en la estructura
    rep['User_name'] = user_name # Insertamos el nombre/alias del usuario en la estructura
    fjson_usr.write_content(rep) # Actualizamos el contenido del archivo de usuarios con los datos del nuevo usuario

# Funcion para añadir un nuevo mensaje en el archivo de mensajes
def add_new_message(msg_id, user_id, user_name, text_fragment, msg_date):
    
    msg = OrderedDict([('Msg_id','Null'), ('Data',OrderedDict([('User_id','Null'), ('User_name','Null'), ('Text','Null'), ('Date','Null'), ('Likes',0), ('Voters',OrderedDict([]))]))]) # Estructura inicial basica de mensaje
    msg['Msg_id'] = msg_id # Insertamos el ID del mensaje en la estructura
    msg['Data']['User_id'] = user_id # Insertamos el ID del mensaje en la estructura
    msg['Data']['User_name'] = user_name # Insertamos el ID del mensaje en la estructura
    msg['Data']['Text'] = text_fragment # Insertamos el ID del mensaje en la estructura
    msg['Data']['Date'] = msg_date # Insertamos el ID del mensaje en la estructura
    msg['Data']['Voters'][user_name] = user_id # Insertamos el ID del mensaje en la estructura
    fjson_msg.write_content(msg) # Actualizamos el contenido del archivo de mensajes con los datos del nuevo mensaje

# Funcion para obtener el ID correspondiente al nobre/alias de un usuario
def id_from_name(user_name):
    
    reputations_data = fjson_usr.read_content() # Leer el contenido del archivo de usuarios
    
    for usr in reputations_data: # Para cada usuario del archivo
        if user_name == usr['User_name']: # Si el nombre de usuario coincide
            return usr['User_id'] # Devuelve el ID asociado a dicho usuario
    return None # Devuelve None si no se encontro al usuario

# Funcion para determinar si un usuario se encuentra en el archivo json a partir de su nombre/alias
def user_in_json(user_name):
    
    if id_from_name(user_name) is not None: # Si se encuentra un ID para dicho nombre/alias de usuario
        return True # Devuelve True
    else: # No se ha encontrado un ID para dicho nombre/alias de usuario
        return False # Devuelve False

##############################

### Manejadores para los mensajes de Telegram recibidos ###

# Manejador correspondiente a la llegada de un nuevo miembro al grupo
def new_user(bot, update):
    
    user_id = str(update.message.from_user.id) # Adquirir su ID
    user_name = update.message.from_user.name # Adquirir su nombre/alias
    add_new_user(user_id, user_name) # Añadir el usuario en el archivo de usuarios

# Manejador para mensajes (no comandos)
def msg_nocmd(bot, update):

    msg_id = str(update.message.message_id) # Adquirir el ID del mensaje
    user_id = str(update.message.from_user.id) # Adquirir el ID del usuario
    user_name = update.message.from_user.name # Adquirir el nombre/alias del usuario
    msg_date = (update.message.date).now().strftime("%Y-%m-%d %H:%M:%S") # Adquirir la fecha-hora en que se envio el mensaje
    text = update.message.text # Adquirir el texto del mensaje

    if len(text) > 50: # Si el numero de caracteres del texto es mayor a 50
        text = text[0:50] # Truncamos a 50

    words_text = text.split() # Separamos el texto en una lista de palabras
    if len(words_text) == 1: # Si solo hay una palabra
        for emoti in CONST['EMO_HAND_UP']: # Para cada emoticono de EMO_HAND_UP
            if CONST['PYTHON'] == 2:# Compatibilidad con Python 2
                if not isinstance(emoti, unicode): # Si el valor no es unicode
                    emoti = emoti.decode('utf8') # Decodificamos a unicode
            if words_text[0] == emoti: # Si la palabra se corresponde con el emoticono de manita arriba
                like(bot, update) # Hacemos like
                break

    text = str(text.encode('utf-8')) # Codificamos en UTF-8 y transformamos a string
    text = "{}...".format(text) # Añadimos puntos suspensivos al final del fragmento de texto

    add_new_message(msg_id, user_id, user_name, text, msg_date) # Añadimos el mensaje en el archivo de mensajes

    if not user_in_json(user_name): # Si el usuario que escribio el mensaje no se encuentra en el archivo de usuarios
        add_new_user(user_id, user_name) # Añadimos al usuario

##############################

### Manejadores para los comandos de Telegram recibidos ###

# Manejador para el comando /start
def start(bot, update):
    update.message.reply_text("Escribe el comando /help para ver informacion sobre mi uso") # El Bot reponde al comando con el siguiente mensaje

# Manejador para el comando /help
def help(bot, update):
    update.message.reply_text("Responde a un mensaje con un /like para dar tu voto al usuario.\n\nPuedes ver la reputacion de cada usuario mediante el comando /reputation @usuario") # El Bot reponde al comando con el siguiente mensaje

# Manejador para el comando /like
def like(bot, update):

    error = False
    chat_id = update.message.chat_id # Adquirir el ID del chat (grupo) que hace la consulta
    try:
        user_name = update.message.from_user.name # Aquirir el nombre/alias del usuario que vota
        user_id = str(update.message.from_user.id) # Adquirir el ID del usuario que vota
        liked_user_name = update.message.reply_to_message.from_user.name # Adquirir el nombre/alias del usuario al que se vota (propietario del mensaje)
        liked_user_id = str(update.message.reply_to_message.from_user.id) # Adquirir el ID del usuario al que se vota
        liked_msg_id = str(update.message.reply_to_message.message_id) # Adquirir el ID del mensaje votado

        if user_id != liked_user_id: # Si el usuario que vota no es el propietario de ese mensaje
            like_result = give_like(user_id, user_name, liked_msg_id) # Dar el like
            if like_result == "Ok": # Si el like se dio de forma exitosa
                liks = get_likes(liked_msg_id) # Obtener los datos de likes de ese mensaje
                rep = get_reputation(liked_user_id) # Obtener los datos de reputacion del usuario al que le pertenece el mensaje
                actual_likes = liks['Data']['Likes'] # Obtener el numero actual de likes totales de ese mensaje
                actual_reputation = rep['Reputation'] # Obtener la reputacion actual de ese usuario
                actual_level = rep['Level'] # Obtener el nivel actual de ese usuario
                emoti = u'\U0001f44d' # Emoti de manita arriba
                if CONST['PYTHON'] == 2:# Compatibilidad con Python 2
                    emoti = u'\U0001f44d'.encode('utf8') # Codificamos a utf-8 el emoti de manita arriba
                response = "{} x {}!".format(emoti, actual_likes) # Respuesta del Bot
            elif like_result == "LVL_UP": # Se dio el like de forma exitosa y el usuario subio de nivel/rango
                liks = get_likes(liked_msg_id) # Obtener los datos de likes de ese mensaje
                rep = get_reputation(liked_user_id) # Obtener los datos de reputacion del usuario al que le pertenece el mensaje
                actual_likes = liks['Data']['Likes'] # Obtener el numero actual de likes totales de ese mensaje
                actual_reputation = rep['Reputation'] # Obtener la reputacion actual de ese usuario
                actual_level = rep['Level'] # Obtener el nivel actual de ese usuario
                emoti = u'\U0001f44d' # Emoti de manita arriba
                if CONST['PYTHON'] == 2:# Compatibilidad con Python 2
                    emoti = u'\U0001f44d'.encode('utf8') # Codificamos a utf-8 el emoti de manita arriba
                response = "{} x {}!".format(emoti, actual_likes) # Respuesta del Bot
                lvl_up_msg = "{} subio de rango!!!\n————————————\n\nReputacion actual:\n```\nTotal de Likes recibidos: {}\nPuntos: {}\nNuevo rango: {}\n```".format(liked_user_name, (actual_reputation-100)//5, actual_reputation, actual_level) # Respuesta del Bot
            elif like_result == "Voted": # El usuario que vota ya habia votado a ese mensaje
                response = "Ya has votado a ese mensaje antes" # Respuesta del Bot
            else: # No se encontro el mesaje en el archivo de mensajes
                response = "No se puede votar a ese mensaje" # Respuesta del Bot
        else: # El usuario que vota es quien escribio ese mensaje
                response = "No puedes votar a un mensaje tuyo" # Respuesta del Bot
    except:
        error = True
        update.message.reply_text("Tienes que usarlo en respuesta al mensaje de otro usuario") # El Bot responde al comando con el siguiete mensaje

    if not error:
        update.message.reply_text(response, reply_to_message_id=liked_msg_id, parse_mode=ParseMode.MARKDOWN) # El Bot reponde al comando con la respuesta generada en el proceso
        if like_result == "LVL_UP":
            bot.send_message(chat_id=chat_id, text=lvl_up_msg, parse_mode=ParseMode.MARKDOWN) # El Bot envia el mesnaje de que el usuario ha subido de nivel

# Manejador para el comando /reputation
def reputation(bot, update, args):

    chat_id = update.message.chat_id # Adquirir el ID del chat (grupo) que hace la consulta
    if len(args) == 1: # Si el comando presenta 1 argumento
        user_name = args[0] # Adquirir el nombre/alias del usuario (argumento)
        user_id = id_from_name(user_name) # Adquirir el ID de usuario correspondiente a ese nombre/alias
        if user_id is not None: # Si se encontro al usuario en el archivo de usuarios
            user_reputation = get_reputation(user_id) # Obtener los datos de reputacion de dicho usuario
            bot.send_message(chat_id=chat_id, text="Reputacion de {}:\n————————————\n```\nTotal de Likes recibidos: {}\nPuntos: {}\nRango: {}\n```".format(user_reputation['User_name'], (user_reputation['Reputation']-100)//5, user_reputation['Reputation'], user_reputation['Level']), parse_mode=ParseMode.MARKDOWN) # El Bot reponde al comando con los datos de reputacion de dicho usuario
        else: # No se encontro al usuario en el archivo de usuarios
            bot.send_message(chat_id=chat_id, text="El usuario {} no se encuentra en este grupo o todavia no ha escrito ningun mensaje".format(user_name)) # El Bot responde al comando con el siguiete mensaje
    elif len(args) < 1: # Si el comando no presenta argumento alguno
        bot.send_message(chat_id=chat_id, text="Tienes que especificar el nombre/alias del usuario.\n\nPor ejemplo:\n/reputation @alias") # El Bot responde al comando con el siguiete mensaje
    else: # El comando presenta más de 1 argumento
        bot.send_message(chat_id=chat_id, text="Demasiados argumentos suministrados, el comando solo acepta 1 argumento el nombre/alias del usuario.\n\nPor ejemplo:\n/reputation @mrguy") # El Bot responde al comando con el siguiete mensaje

##############################

### Funcion Principal ###

def main():
    
    # Crear un manejador de eventos (updater) para el Bot con dicho Token, y obtener un planificador de manejadores (dispatcher)
    updater = Updater(CONST['TOKEN'])
    dp = updater.dispatcher
    
    # Añadir al dispatcher un manejador de mensajes (no comandos)
    dp.add_handler(MessageHandler(Filters.text, msg_nocmd))
    
    # Añadir al dispatcher un manejador correspondiente a la llegada de un nuevo miembro al grupo (un nuevo usuario se une al grupo)
    dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, new_user))
    
    # Añadir al dispatcher manejadores para los comandos recibidos
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("like", like))
    dp.add_handler(CommandHandler("reputation", reputation, pass_args=True))
    
    # Lanzar el Bot ignorando los mensajes pendientes (clean=True)
    updater.start_polling(clean=True)
    
    # Parar la ejecucion de este hilo (Funcion principal), y esperar la llegada de mensajes que se trataran por los manejadores asincronos
    updater.idle()

if __name__ == '__main__':
    main()

### Fin del codigo ###
