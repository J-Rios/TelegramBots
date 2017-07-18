# -*- coding: utf-8 -*-
# Script: Constants.py
# Descripción: Telegram Bot that manage a reputation system of users in a group. It let give 
#              "likes" to a user message and when the message get a minimun value of likes, the
#              bot add some points reputation for that user.
# Autor: José Ríos Rubio
# Fecha: 01/07/2017
# Version: 0.1
##############################

# Constants for the Bot
'''
CONST = {
    'TOKEN': '440644484:AAHiW2jWHB-KKKt6XbosdnSWpRelPX4H5YY', # To set by the user (get It with @BotFather)
    'MASTER_ID': 231874677, # To set by user (get It with @get_id_bot)
    'ADMINS_ID': [231874677],
    'F_USR' : './data/users.json',
    'F_MSG' : './data/messages.json',
    'GIVE_REP_MOD' : 5, # When a msg reach module 5 likes (5, 10, 15 ...), give reputation to the user
    'GIVE_REP_POINTS' : 5, # Reputations per GIVE_REP_MOD likes. Actually, give same 5 reputation points for every 5 likes obtained in a msg
    'REP_LVL_POINTS' : [100, 200, 350, 500, 700, 1000, 1500, 2500, 5000, 10000],
    'REP_LVL' : ['0 - Noobie', '1 - Novice', '2 - Second class', '3 - First class', '4 - Captain', '5 - General', '6 - Pro', '7 - Master', '8 - King', '9 - God']
}
'''

TOKEN = "440644484:AAHiW2jWHB-KKKt6XbosdnSWpRelPX4H5YY" # To set by the user (get It with @BotFather)
MASTER_ID = 231874677 # To set by user (get It with @get_id_bot)
ADMINS_ID = [231874677]
F_USR = './data/users.json'
F_MSG = './data/messages.json'
GIVE_REP_MOD = 5 # When a msg reach module 5 likes (5, 10, 15 ...), give reputation to the user
GIVE_REP_POINTS = 5 # Reputations per GIVE_REP_MOD likes. Actually, give same 5 reputation points for every 5 likes obtained in a msg
REP_LVL_POINTS = [100, 200, 350, 500, 700, 1000, 1500, 2500, 5000, 10000]
REP_LVL = ['0 - Recien llegado (Noob)', '1 - Novato y a mucha honra!', '2 - El que se queda en las sombras', '3 - El que pide mas que ayuda xD', '4 - El que ayuda de vez en cuando', '5 - El que controla del tema', '6 - El Pro del codigo', '7 - Capitan del Grupo', '8 - El ', '9 - God']
#REP_LVL = ['0 - Noobie', '1 - Novice', '2 - Second class', '3 - First class', '4 - Captain', '5 - General', '6 - Pro', '7 - Master', '8 - King', '9 - God']