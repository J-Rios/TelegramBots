# -*- coding: utf-8 -*-
'''
Script:
    constants.py
Description:
    Constants values for myrssbot.py.
Author:
    Jose Rios Rubio
Creation date:
    23/08/2017
Last modified date:
    06/10/2017
Version:
    1.5.0
'''

####################################################################################################

### Constants ###
CONST = {
    'DEVELOPER' : '@JoseTLG', # Developer Telegram contact
    'DATE' : '06/10/2017', # Last modified date
    'VERSION' : '1.5.0', # Actual version
    'TOKEN' : 'XXXXXXXXX:XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX', # Bot Token (get it from @BotFather)
    'REG_KEY' : 'registrationKey1234', # User registration Key (for signup and let use the Bot)
    'CHATS_DIR' : './data/chats', # Path of chats data directory
    'USERS_LIST_FILE' : './data/users_list.json', # Json file of signed-up users list
    'TLG_MSG_MAX_CHARS' : 4095, # Max number of characters per message allowed by Telegram
    'MAX_ENTRY_SUMMARY' : 2500, # Max number of characters in entry summary (description)
    'T_FEEDS' : 60, # Time between feeds check (60s -> 1m)
    'HTML_ANOYING_TAGS' : [ # HTML tags to remove from entries summary
        '<p>', '</p>', '<br>', '<br/>', '<br />', '</br>', '<hr>', '</hr>', '<pre>', '</pre>', \
        '<li>', '</li>', '<ul>', '</ul>', '<ol>', '</ol>', '<blockquote>', '</blockquote>', \
        '<h1>', '</h1>', '<h2>', '</h2>', '<h3>', '</h3>', '<code>', '</code>', '<em>', '</em>', \
        '<strong>', '</strong>', '<html>', '</html>', '<head>', '</head>', '<body>', '</body>', \
        '<script>', '</script>', '<img>', '</img>', '<div>', '</div>', '<input>', '</input>', \
        '<span>', '</span>', '<form>', '</form>', '<cite>', '</cite>', '&lt;', '&gt;'
    ],
    'HTML_ANOYING_STRUCTS' : [ # HTML structures to remove from entries summary
        '<img(.*?)>', '<div(.*?)>', '<pre(.*?)>', '<span(.*?)>', '<ol(.*?)>', '<ul(.*?)>', \
        '<form(.*?)>'
    ]
}

TEXT = {
    'en' : {
        'START' : \
            'I am a feed parser Bot, that let you subscribe to multiple feeds contents, handles ' \
            'RSS, CDF and ATOM formats. I will notify you when a new feed comes out.\n' \
            '\n' \
            'Check the /help command for get usefull information about my use.',

        'HELP' : \
            'I am open source and completely free, but you need to know the actual registration ' \
            'key for sign-up your telegram user and get access to add feeds and manage yours ' \
            'subscriptions.\n'
            '\n' \
            'Check the /commands command to get a list of all the implemented commands and a ' \
            'description of them.',

        'LANG_NOT_ARG' : \
            'The command needs a language to set (en - english, es - spanish).\n' \
            '\n' \
            'Examples:\n' \
            '/language es\n' \
            '/language en',

        'LANG_BAD_LANG' : \
            'Invalid language provided. The actual languages supported are english and spanish, ' \
            'change any of them using "es" or "en".\n' \
            '\n' \
            'Examples:\n' \
            '/language es\n' \
            '/language en',

        'LANG_SAME' : \
            'You can not change to same language that is actually set.',

        'LANG_CHANGE' : \
            'Language changed to english.',

        'SIGNUP_NOT_ARG' : \
            'The command needs a registration key for signup your user.\n' \
            '\n' \
            'Example:\n' \
            '/signup registrationKey1234',

        'SIGNUP_FAIL' : \
            'Sign-up fail. Wrong or out-dated registration key?\n' \
            '\n' \
            'Ask the owner about the key.',

        'SIGNUP_EXIST_USER' : \
            'You alredy have an account in the Bot system. If you want to create a new one, ' \
            'first you need to remove your old account with the /signdown command.',

        'SIGNUP_SUCCESS' : \
            'Sign-up success. Created an account for your user, now you are free to use all the ' \
            'commands, enjoy!',

        'SIGNDOWN_SURE' : \
            'The /signdown command will delete your account. If you are sure to do this, you ' \
            'have to use the next statement:\n' \
            '\n' \
            '/signdown iamsuretoremovemyaccount',

        'NO_EXIST_USER' : \
            'You does not have an account yet.',

        'SIGNDOWN_CONFIRM_INVALID' : \
            'Invalid confirmation. If you are sure to do this, you have to use the next ' \
            'statement:\n' \
            '\n' \
            '/signdown iamsuretoremovemyaccount',

        'SIGNDOWN_SUCCESS' : \
            'Sign-down success. Now you can create and start a new account with new feeds.',

        'CMD_NOT_ALLOW' : \
            'You are not allowed to use this command. First you need to get access, signing up ' \
            'in the Bot data base to create an account of your user. You can do that with the ' \
            '/signup command and using the registration Key provided by the owner.',

        'ADD_NOT_ARG' : \
            'The command needs a feed URL.\n' \
            '\n' \
            'Example:\n' \
            '/add https://www.kickstarter.com/projects/feed.atom',

        'ADD_ALREADY_FEED' : \
            'You are already subscribed to that feed.',

        'ADD_NO_ENTRIES' : \
            'Invalid URL.',

        'ADD_FEED' : \
            'Feed added. Now you are subscribed to:\n',

        'RM_NOT_ARG' : \
            'The command needs a feed URL.\n' \
            '\n' \
            'Example:\n' \
            '/remove https://www.kickstarter.com/projects/feed.atom',

        'RM_NOT_SUBS' : \
            'The chat does not have that feed subscription (feed not added).',

        'RM_FEED' : \
            'Feed successfull removed.',

        'NO_ENTRIES' : \
            'There is no current entries in this feed.',

        'ENA_NOT_DISABLED' : \
            'I am already enabled.',

        'ENA_NOT_SUBS' : \
            'There is no feeds subscriptions yet.',

        'FR_ENABLED' : \
            'Feeds notifications enabled. Stop It with /disable command when you want.',

        'DIS_NOT_ENABLED' : \
            'I am already disabled.',

        'FR_DISABLED' : \
            'Feeds notifications disabled. Start It with /enable command when you want.',

        'FR_ACTIVE' : \
            'The FeedReader is active, to use that command you need to disable it. Run the ' \
            'command /disable first.',

        'LINE' : \
            '\n—————————————————\n',

        'COMMANDS' : \
            'List of commands:\n' \
            '—————————————————\n' \
            '/start - Show the initial information about the bot.\n' \
            '\n' \
            '/help - Show the help information.\n' \
            '\n' \
            '/commands - Show the actual message. Information about all the commands implemented ' \
            'and their description.\n' \
            '\n' \
            '/language - Allow to change the language of the bot messages. To use it, is ' \
            'necessary that the user was already signed-up in the bot system.\n' \
            '\n' \
            '/signup - Allow to create a user account in the bot system to use it. To sign-up, ' \
            'is necessary to provide a key that the Bot owner has give to the user.\n' \
            '\n' \
            '/signdown - Allow to remove the user account from the bot system. To use it, is ' \
            'necessary that the user was already signed-up in the bot system.\n' \
            '\n' \
            '/list - List the actual chat feeds subscriptions (feeds added).\n' \
            '\n' \
            '/add - Add a new feed to the current chat. To use it, is necessary that the ' \
            'user was already signed-up in the bot system.\n' \
            '\n' \
            '/remove - Remove a subscribed feed from the current chat. To use it, is necessary ' \
            'that the user was already signed-up in the bot system.\n' \
            '\n' \
            '/enable - Enable the FeedsReader of the current chat (start feeds notifications). ' \
            'To use it, is necessary that the user was already signed-up in the bot system.\n' \
            '\n' \
            '/disable - Disable the FeedsReader of the current chat (stop feeds notifications). ' \
            'To use it, is necessary that the user was already signed-up in the bot system.'
    },
    'es' : {
        'START' : \
            'Soy un Bot feed parser, que permite subscribirte a multiples contenidos feeds, ' \
            'puedo manejar los formatos RSS, CDF y ATOM. Te notificare cuando un feed presente ' \
            'alguna nueva entrada.\n' \
            '\n' \
            'Consulta el comando /help para obtener mas informacion sobre mi uso.',

        'HELP' : \
            'Soy completamente gratuito y open source, pero necesitas conocer la clave de ' \
            'registro para inscribir a tu usuario de telegram en el sistema del Bot y obtener ' \
            'asi permiso para añadir feeds y gestionar las subscripciones.\n' \
            '\n' \
            'Consulta el comando /commands para obtener una lista con los comandos implementados ' \
            'y una descripcion de todos ellos.',

        'LANG_NOT_ARG' : \
            'El comando necesita un idioma al cual cambiar (en - ingles, es - español).\n' \
            '\n' \
            'Ejemplo:\n' \
            '/language es\n' \
            '/language en',

        'LANG_BAD_LANG' : \
            'Idioma proporcionado no valido. Los idiomas que actualmente estan soportados son el ' \
            'español y el ingles, cambia a cualquiera de ellos usando "es" o "en".\n' \
            '\n' \
            'Ejemplos:\n' \
            '/language es\n' \
            '/language en',

        'LANG_SAME' : \
            'No puedes cambiarme al mismo idioma en el que actualmente me encuentro.',

        'LANG_CHANGE' : \
            'Idioma cambiado a español.',

        'SIGNUP_NOT_ARG' : \
            'El comando necesita una clave de registro para inscribir al usuario.\n' \
            '\n' \
            'Ejemplo:\n' \
            '/signup registrationKey1234',

        'SIGNUP_FAIL' : \
            'La inscripcion fallo. Clave de registro erronea o caducada?\n' \
            '\n' \
            'Preguntale al propietario del Bot sobre la clave actual.',

        'SIGNUP_EXIST_USER' : \
            'Ya tienes una cuenta en el sistema del Bot. Si quieres crear una nueva, primero ' \
            'tienes que eliminar tu cuenta anterior mediante el comando /signdown.',

        'SIGNUP_SUCCESS' : \
            'Te has incrito correctamente. Se ha creado una cuenta para tu usuario, ahora tienes ' \
            'un acceso completo a todos los comandos, disfruta!',

        'SIGNDOWN_SURE' : \
            'El comando /signdown eliminara tu cuenta del sistema del Bot. Si estas seguro de ' \
            'querer hacerlo, utiliza la siguiente sentencia:\n' \
            '\n' \
            '/signdown iamsuretoremovemyaccount',

        'NO_EXIST_USER' : \
            'Todavia no tienes una cuenta.',

        'SIGNDOWN_CONFIRM_INVALID' : \
            'Confirmacion no valida. Si estas seguro de hacer esto, tienes que utilizar la ' \
            'siguiente sentencia:\n' \
            '\n' \
            '/signdown iamsuretoremovemyaccount',

        'SIGNDOWN_SUCCESS' : \
            'Te has dado de baja correctamente.',

        'CMD_NOT_ALLOW' : \
            'No tienes permiso para utilizar este comando. Primero se necesita obtener acceso, ' \
            'inscribite en la base de datos del bot creando una cuenta de tu usuario. Puedes ' \
            'hacerlo mediante el comando /signup utilizando la clave de registro que te entrege ' \
            'el propietario del Bot.',

        'ADD_NOT_ARG' : \
            'El comando necesita la URL del feed.\n' \
            '\n' \
            'Ejemplo:\n' \
            '/add https://www.kickstarter.com/projects/feed.atom',

        'ADD_ALREADY_FEED' : \
            'Ya estas subscrito a dicho feed.',

        'ADD_NO_ENTRIES' : \
            'URL no valida.',

        'ADD_FEED' : \
            'Feed añadido. Subscrito a:\n',

        'RM_NOT_ARG' : \
            'El comando necesita la URL del feed.\n' \
            '\n' \
            'Ejemplo:\n' \
            '/remove https://www.kickstarter.com/projects/feed.atom',

        'RM_NOT_SUBS' : \
            'El chat no esta subscrito a ese feed (no esta añadido).',

        'RM_FEED' : \
            'Feed eliminado correctamente.',

        'NO_ENTRIES' : \
            'Actualmente no hay entradas para este feed.',

        'ENA_NOT_DISABLED' : \
            'Ya estoy activado.',

        'ENA_NOT_SUBS' : \
            'Aun no hay ningun feed subscrito.',

        'FR_ENABLED' : \
            'Notificaciones de los feeds activadas. Detenlas con el comando /disable cuando lo ' \
            'necesites.',

        'DIS_NOT_ENABLED' : \
            'Ya estoy desactivado.',

        'FR_DISABLED' : \
            'Notificaciones de los feeds desactivadas. Ponlas nuevamente en funcionamiento con ' \
            'el comando /enable cuando necesites.',

        'FR_ACTIVE' : \
            'El lector de feeds esta activo, para usar este comando tienes que detenerlo. Envia ' \
            'el comando /disable primero.',

        'LINE' : \
            '\n—————————————————\n',

        'COMMANDS' : \
            'Lista de comandos:\n' \
            '—————————————————\n' \
            '/start - Muestra la información inicial sobre el Bot.\n' \
            '\n' \
            '/help - Muestra la informacion de ayuda.\n' \
            '\n' \
            '/commands - Muestra el mensaje actual. Información sobre todos los comandos ' \
            'implementados y la descripción de estos.\n' \
            '\n' \
            '/language - Permite cambiar el lenguaje de los mensajes del Bot. Para usarlo, es ' \
            'necesario que el usuario este inscrito previamente en el sistema del Bot.\n' \
            '\n' \
            '/signup - Permite crear una cuenta de usuario en el sistema del Bot para poder ' \
            'utilizarlo. Para inscribirse, es necesario utilizar una clave que el propietario ' \
            'del Bot le haya suministrado al usuario\n' \
            '\n' \
            '/signdown - Permite eliminar la cuenta de usuario del sistema del Bot. Para usarlo, ' \
            'es necesario que el usuario este inscrito previamente en el sistema del Bot.\n' \
            '\n' \
            '/list - Lista los feeds subscritos en el chat actual (feeds añadidos).\n' \
            '\n' \
            '/add - Añade un nuevo feed al chat actual. Para usarlo, es necesario que el usuario ' \
            'este inscrito previamente en el sistema del Bot.\n' \
            '\n' \
            '/remove - Elimina un feed subscrito del chat actual. Para usarlo, es necesario que ' \
            'el usuario este inscrito previamente en el sistema del Bot.\n' \
            '\n' \
            '/enable - Habilita el lector de feeds del chat actual (pone en funcionamiento las ' \
            'notificaciones de los feeds). Para usarlo, es necesario que el usuario este ' \
            'inscrito previamente en el sistema del Bot.\n' \
            '\n' \
            '/disable - Deshabilita el lector de feeds del chat actual (detiene las ' \
            'notificaciones de los feeds). Para usarlo, es necesario que el usuario este ' \
            'inscrito previamente en el sistema del Bot.'
    }
}
