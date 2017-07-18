# -*- coding: utf-8 -*-
'''
Script:  MolaBot.py

Descripcion:
    Bot de Telegram que gestiona todo un sistema de reputaciones de los usuarios pertenecientes a
    un grupo. Permite a un usuario, dar "Likes" a los mensajes de otros, y el numero global de
    "Likes" (la suma de todos los likes de todos los mensajes de un mismo usuario) determinara los
    puntos de reputacion que dicho usuario tiene.

Autor:   Jose Rios Rubio
Fecha:   18/07/2017
Version: 1.0
'''

### Librerias ###

# Importacion de librerias
import os
import json
import datetime

# Importacion desde librerias
from Constants import *
from threading import Lock
from collections import OrderedDict
from telegram import MessageEntity, ParseMode, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, RegexHandler, \
                         ConversationHandler, CallbackQueryHandler

##############################

### Variables Globales ###
lock = Lock() # Mutex para los archivos
#lock_usr = Lock() # Mutex para el archivo de usuarios
#lock_msg = Lock() # Mutex para el archivo de mensajes

##############################

### Funciones "Back-level" para lectura/escritura de archivos json generales ###

# Funcion para leer de un archivo json
def json_read(file):
    
    try: # Intentar abrir el archivo
        lock.acquire() # Cerramos (adquirimos) el mutex
        if not os.path.exists(file): # Si el archivo no existe
            read = {} # Devolver un diccionario vacio
        else: # Si el archivo existe
            if not os.stat(file).st_size: # Si el archivo esta vacio
                read = {} # Devolver un diccionario vacio
            else: # El archivo existe y tiene contenido
                with open(file, "r") as f: # Abrir el archivo en modo lectura
                    read = json.load(f, object_pairs_hook=OrderedDict) # Leer todo el archivo y devolver la lectura de los datos json usando un diccionario ordenado
    except: # Error intentando abrir el archivo
        print("    Error cuando se abria para lectura, el archivo {}".format(file)) # Escribir en consola el error
        read = None # Devolver None
    finally: # Para acabar, haya habido excepcion o no
        lock.release() # Abrimos (liberamos) el mutex
    
    return read # Devolver el resultado de la lectura de la funcion

# Funcion para escribir en un archivo json
def json_write(file, data):
    
    # Si no existe el directorio que contiene los archivos de datos, lo creamos
    directory = os.path.dirname(file) # Obtener el nombre del directorio que contiene al archivo
    if not os.path.exists(directory): # Si el directorio (ruta) no existe
        os.makedirs(directory) # Creamos el directorio
    
    try: # Intentar abrir el archivo
        lock.acquire() # Cerramos (adquirimos) el mutex
        with open(file, "w") as f: # Abrir el archivo en modo escritura (sobre-escribe)
            f.write("\n{}\n".format(json.dumps(data, ensure_ascii=False, encoding="utf-8", indent=4))) # Escribimos en el archivo los datos json asegurando todos los caracteres ascii, codificacion utf-8 y una "indentacion" de 4 espacios
    except: # Error intentando abrir el archivo
        print("    Error cuando se abria para escritura, el archivo {}".format(file)) # Escribir en consola el error
    finally: # Para acabar, haya habido excepcion o no
        lock.release() # Abrimos (liberamos) el mutex

# Funcion para leer el contenido de un archivo json (datos json)
def json_read_content(file):
    
    read = json_read(file) # Leer todo el archivo json
    
    if read != {}: # Si la lectura no es vacia
        return read['Content'] # Devolvemos el contenido de la lectura (datos json)
    else: # Lectura vacia
        return read # Devolvemos la lectura vacia

# Funcion para añadir al contenido de un archivo json, nuevos datos json
def json_write_content(file, data):
    
    # Si no existe el directorio que contiene los archivos de datos, lo creamos
    directory = os.path.dirname(file) # Obtener el nombre del directorio que contiene al archivo
    if not os.path.exists(directory): # Si el directorio (ruta) no existe
        os.makedirs(directory) # Creamos el directorio
    
    try: # Intentar abrir el archivo
        lock.acquire() # Cerramos (adquirimos) el mutex
        
        if os.path.exists(file) and os.stat(file).st_size: # Si el archivo existe y no esta vacio
            with open(file, "r") as f: # Abrir el archivo en modo lectura
                content = json.load(f, object_pairs_hook=OrderedDict) # Leer todo el archivo y devolver la lectura de los datos json usando un diccionario ordenado
            
            content['Content'].append(data) # Añadir los nuevos datos al contenido del json
            
            with open(file, "w") as f: # Abrir el archivo en modo escritura (sobre-escribe)
                f.write("\n{}\n".format(json.dumps(content, ensure_ascii=False, encoding="utf-8", indent=4))) # Escribimos en el archivo los datos json asegurando todos los caracteres ascii, codificacion utf-8 y una "indentacion" de 4 espacios
        else: # El archivo no existe o esta vacio
            with open(file, "w") as f: # Abrir el archivo en modo escritura (sobre-escribe)
                f.write('\n{\n    "Content": []\n}\n') # Escribir la estructura de contenido basica
            
            with open(file, "r") as f: # Abrir el archivo en modo lectura
                content = json.load(f) # Leer todo el archivo
            
            content['Content'].append(data) # Añadir los datos al contenido del json

            with open(file, "w") as f:  # Abrir el archivo en modo escritura (sobre-escribe)
                f.write("\n{}\n".format(json.dumps(content, ensure_ascii=False, encoding="utf-8", indent=4))) # Escribimos en el archivo los datos json asegurando todos los caracteres ascii, codificacion utf-8 y una "indentacion" de 4 espacios
    except: # Error intentando abrir el archivo
        print("    Error cuando se abria para escritura, el archivo {}".format(file)) # Escribir en consola el error
    finally: # Para acabar, haya habido excepcion o no
        lock.release() # Abrimos (liberamos) el mutex

# Funcion para limpiar todos los datos de un archivo json (no se usa actualmente)
def json_clear_content(file):
    
    try: # Intentar abrir el archivo
        lock.acquire() # Cerramos (adquirimos) el mutex
        if os.path.exists(file) and os.stat(file).st_size: # Si el archivo existe y no esta vacio
            with open(file, "w") as f: # Abrir el archivo en modo escritura (sobre-escribe)
                f.write('\n{\n    "Content": [\n    ]\n}\n') # Escribir la estructura de contenido basica
    except: # Error intentando abrir el archivo
        print("    Error cuando se abria para escritura, el archivo {}".format(file)) # Escribir en consola el error
    finally: # Para acabar, haya habido excepcion o no
        lock.release() # Abrimos (liberamos) el mutex

# Funcion para actualizar datos de un archivo json
# [Nota: cada dato json necesita al menos 1 elemento identificador unico (uide), si no es asi, la actualizacion se producira en el primer elemento que se encuentre]
def json_update(file, data, uide):
    
    file_data = json_read(file) # Leer todo el archivo json
    
    # Buscar la posicion del dato en el contenido json
    found = 0 # Posicion encontrada a 0
    i = 0 # Posicion inicial del dato a 0
    for msg in file_data['Content']: # Para cada mensaje en el archivo json
        if data[uide] == msg[uide]: # Si el mensaje tiene el UIDE buscado
            found = 1 # Marcar que se ha encontrado la posicion
            break # Interrumpir y salir del bucle
        i = i + 1 # Incrementar la posicion del dato
    
    if found: # Si se encontro en el archivo json datos con el UIDE buscado
        file_data['Content'][i] = data # Actualizamos los datos json que contiene ese UIDE
        json_write(file, file_data) # Escribimos el dato actualizado en el archivo json
    else: # No se encontro ningun dato json con dicho UIDE
        print("    Error: UIDE no encontrado en el archivo, o el archivo no existe") # Escribir en consola el error

# funcion para eliminar un archivo json (no se usa actualmente)
def json_delete(file):

    lock.acquire() # Cerramos (adquirimos) el mutex
    if os.path.exists(file): # Si el archivo existe
        os.remove(file) # Eliminamos el archivo
    lock.release() # Abrimos (liberamos) el mutex

##############################

### Funciones "Top-level" para leer-escribir los archivos json especificos de este programa ###

# Funcion para obtener los datos de reputacion de un usuario a traves de un ID
def get_reputation(user_id):
    
    content = json_read_content(F_USR) # Leer el contenido del archivo de usuarios
    
    for usr in content: # Para cada usuario del archivo
        if user_id == usr['User_id']: # Si el usuario presenta el ID que estamos buscando
            return usr # Devolvemos los datos de reputacion de ese usuario
    
    return {} # Devolvemos un diccionario vacio si no se encontro el usuario

# Funcion para obtener los datos de likes de un mensaje a traves de un ID
def get_likes(msg_id):
    
    content = json_read_content(F_MSG) # Leer el contenido del archivo de mensajes
    
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
            json_update(F_MSG, likes_data, 'Msg_id') # Actualiza el archivo de mensajes con los nuevos datos (likes y votantes)
            
            if likes_data['Data']['Likes'] % GIVE_REP_MOD : # Si el numero de likes actual es modulo de GIVE_REP_MOD (e.g. para mod 5: 5, 10, 15 ...)
                increase_reputation(likes_data['Data']['User_id']) # Incrementamos la reputacion
            return "Ok" # Devolvemos "Ok" (se ha dado el like)
        else: # El usuario que vota ya dio su like con anterioridad
            print("    El votante ya voto con anterioridad") # Escribir en consola
            print("") # Escribir en consola
            return "Voted" # Devolvemos "Voted" (no se ha dado el like porque el usuario que vota ya dio su like con anterioridad)
    else:
        print("    Error: Mensaje con ID {} no encontrado en el archivo {}".format(msg_id, F_MSG)) # Escribir en consola el error
        return "Error" # Devolvemos "Error" (no se ha dado el like porque el archivo no existe o se ha producido un fallo al leer/escribir en el)

# Funcion para incrementar la reputacion de un usuario
def increase_reputation(user_id):
    
    user_data = get_reputation(user_id) # Obtenemos los datos de reputacion del usuario con ese ID
    user_data['Reputation'] = user_data['Reputation'] + GIVE_REP_POINTS # Damos los nuevos puntos de reputacion
    
    lvl = 9 # Iniciamos el posible nivel de usuario a 9
    for i in range(0, 8, 1): # De 0 a 8
        if user_data['Reputation'] < REP_LVL_POINTS[i+1]: # Si los puntos de reputacion del usuario son inferiores a los puntos de reputacion necesarios para estar en el siguiente nivel i+1
            lvl = i # Determinamos el nivel de usuario
            break # Interrumpimos y salimos del bucle
    
    if REP_LVL[lvl] != user_data['Level']: # Si el nivel de usuario, correspondiente a la nueva reputacion, es distinto al nivel de usuario anterior
        user_data['Level'] = REP_LVL[lvl] # Damos el nuevo rango/nivel al usuario
    
    json_update(F_USR, user_data, 'User_id') # Actualizamos en el archivo de usuarios con los datos de reputacion de dicho usuario

# Funcion para determinar si un usuario ha votado con anterioridad a un mensaje
def hasVoted(voter_id, msg_id):
    
    content = json_read_content(F_MSG) # # Leer el contenido del archivo de mensajes
    
    for msg in content: # Para cada mensaje del archivo
        if msg_id == msg['Msg_id']: # Si el mensaje presenta el ID que estamos buscando
            for ids in msg['Data']['Voters'].items(): # Para cada votante de ese mensaje
                if voter_id == ids[1]: # Si el ID del usuario que vota se encuentra entre los votantes
                    return True # Devolvemos True
    return False # Devolvemos False si no se ha encontrado el ID del usuario que vota en la lista de los usuarios que votaron con anterioridad

# Funcion para añadir un nuevo usuario al archivo de usuarios
def add_new_user(user_id, user_name):
    
    rep = OrderedDict([('User_id', 'Null'), ('User_name', 'Null'), ('Reputation', 100), ('Level', '0 - Noobie')]) # Estructura inicial basica de usuario
    rep['User_id'] = user_id # Insertamos el ID del usuario en la estructura
    rep['User_name'] = user_name # Insertamos el nombre/alias del usuario en la estructura
    json_write_content(F_USR, rep) # Actualizamos el contenido del archivo de usuarios con los datos del nuevo usuario

# Funcion para añadir un nuevo mensaje en el archivo de mensajes
def add_new_message(msg_id, user_id, user_name, text_fragment, msg_date):
    
    msg = OrderedDict([('Msg_id','Null'), ('Data',OrderedDict([('User_id','Null'), ('User_name','Null'), ('Text','Null'), ('Date','Null'), ('Likes',0), ('Voters',OrderedDict([]))]))]) # Estructura inicial basica de mensaje
    msg['Msg_id'] = msg_id # Insertamos el ID del mensaje en la estructura
    msg['Data']['User_id'] = user_id # Insertamos el ID del mensaje en la estructura
    msg['Data']['User_name'] = user_name # Insertamos el ID del mensaje en la estructura
    msg['Data']['Text'] = text_fragment # Insertamos el ID del mensaje en la estructura
    msg['Data']['Date'] = msg_date # Insertamos el ID del mensaje en la estructura
    msg['Data']['Voters'][user_name] = user_id # Insertamos el ID del mensaje en la estructura
    json_write_content(F_MSG, msg) # Actualizamos el contenido del archivo de mensajes con los datos del nuevo mensaje

# Funcion para obtener el ID correspondiente al nobre/alias de un usuario
def id_from_name(user_name):
    
    reputations_data = json_read_content(F_USR) # Leer el contenido del archivo de usuarios
    
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
    text = (update.message.text).split() # Adquirir una lista con las palabras que conforman el texto del mensaje

    num_words = len(text) # Determinamos el numero de palabras del mensaje
    if num_words == 1: # Si el mensaje solo tiene 1 palabra
        text_fragment = "{}".format(text[0]) # Añadimos esa palabra al fragmento de texto que se insertara en los datos de mensaje
    elif num_words == 2: # Si el mensaje tiene 2 palabras
        text_fragment = "{} {}".format(text[0],text[1]) # Añadimos esas palabras al fragmento de texto que se insertara en los datos de mensaje
    elif num_words == 3: # Si el mensaje tiene 3 palabras
        text_fragment = "{} {} {}".format(text[0],text[1],text[2]) # Añadimos esas palabras al fragmento de texto que se insertara en los datos de mensaje
    else:  # Si el mensaje tiene mas de 3 palabras
        text_fragment = "{} {} {}...".format(text[0],text[1],text[2]) # Añadimos esas palabras seguidas de "..." al fragmento de texto que se insertara en los datos de mensaje

    add_new_message(msg_id, user_id, user_name, text_fragment, msg_date) # Añadimos el mensaje en el archivo de mensajes

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
            response = "A {} le mola este mensaje!\n\n`Likes: {}`\n\n————————————\nReputacion actual de {}:\n```\nPuntos: {}\nNivel: {}\n```".format(user_name, actual_likes, liked_user_name, actual_reputation, actual_level) # Respuesta del Bot
        elif like_result == "Voted": # El usuario que vota ya habia votado a ese mensaje
            response = "Ya has votado a ese mensaje antes" # Respuesta del Bot
        else: # No se encontro el mesaje en el archivo de mensajes
            response = "No se puede votar a ese mensaje" # Respuesta del Bot
    else: # El usuario que vota es quien escribio ese mensaje
            response = "No puedes votar a un mensaje tuyo" # Respuesta del Bot
    
    update.message.reply_text(response, reply_to_message_id=liked_msg_id, parse_mode=ParseMode.MARKDOWN) # El Bot reponde al comando con la respuesta generada en el proceso

# Manejador para el comando /reputation
def reputation(bot, update, args):

    if len(args) == 1: # Si el comando presenta 1 argumento
        user_name = args[0] # Adquirir el nombre/alias del usuario (argumento)
        chat_id = update.message.chat_id # Adquirir el ID del chat (grupo) que hace la consulta
        user_id = id_from_name(user_name) # Adquirir el ID de usuario correspondiente a ese nombre/alias
        if user_id is not None: # Si se encontro al usuario en el archivo de usuarios
            user_reputation = get_reputation(user_id) # Obtener los datos de reputacion de dicho usuario
            bot.send_message(chat_id=chat_id, text="Reputacion del usuario {}:\n————————————\n```\nPuntos: {}\nNivel: {}\n```".format(user_reputation['User_name'], user_reputation['Reputation'], user_reputation['Level']), parse_mode=ParseMode.MARKDOWN) # El Bot reponde al comando con los datos de reputacion de dicho usuario
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
    updater = Updater(TOKEN)
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
    
    # Lanzar el Bot
    updater.start_polling()
    
    # Parar la ejecucion de este hilo (Funcion principal), y esperar la llegada de mensajes que se trataran por los manejadores asincronos
    updater.idle()

if __name__ == '__main__':
    main()

### Fin del codigo ###
