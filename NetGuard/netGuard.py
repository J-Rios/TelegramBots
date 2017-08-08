# -*- coding: utf-8 -*-

# Nota: El script debe ser ejecutado con sudo

# Importar de librerias
from os import popen, geteuid
from sys import exit
from re import findall
from time import sleep
from threading import Thread

# Importar desde librerias
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler, ConversationHandler, CallbackQueryHandler)

##############################

TOKEN = "XXXXXXXXX:XXXXXXX-XXXXXXXXXXXXXXXXXXXXXXXXXXX" # A establecer por el usuario (consultar mediante @BotFather)
TIEMPO_CONSULTA = 10 # Tiempo entre consultas de dispositivos en la red (en segundos)

##############################

# Funcion para realizar llamadas del sistema (ejecutar comandos Linux)
def llamadaSistema(entrada):
    salida = "" # Creamos variable vacia
    f = popen(entrada) # Llamada al sistema
    for i in f.readlines(): # Leemos caracter a caracter sobre la linea devuelta por la llamada al sistema
        salida += i  # Insertamos cada uno de los caracteres en nuestra variable
    salida = salida[:-1] # Truncamos el caracter fin de linea '\n'
    return salida # Devolvemos la respuesta al comando ejecutado


def nmap():
    device_data = {'IP': '0.0.0.0', 'MAC': '00:00:00:00:00'} # Creamos un diccionario por defecto donde guardar la informacion de los dispositivos (IP y MAC)
    list_dev = [] # Lista de dispositivos inicialmente vacia
    nmap_raw = llamadaSistema("nmap -sP 192.168.1.1-100 --disable-arp-ping") # Realizamos la llamada al comando
    list_ip = findall('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', nmap_raw) # Metemos en una lista las IPs de la respuesta del comando nmap
    list_mac = findall('(?:[0-9a-fA-F]:?){12}', nmap_raw) # Metemos en una lista las MACs de la respuesta del comando nmap
    if len(list_ip)-1 == len(list_mac): # Si el numero de MACs es uno menos que el de IPs (pues la ultima ip de la lista es la de nuestro dispositivo)
        for i in range(0, len(list_mac), 1): # Para cada MAC
            device_data['IP'] = list_ip[i] # Almacenamos en el diccionario la IP de dicho dispositivo
            device_data['MAC'] = list_mac[i] # Almacenamos en el diccionario la MAC de dicho dispositivo
            list_dev.append(device_data.copy()) # Añadimos el dispositivo a la lista
    return list_dev # Devolver la lista de dispositivos

##############################

def net_devices(update):
    list_devices = nmap()
    if not list_devices: # Si la lista esta vacia
        msg = 'Ningun dispositivo detectado'
    else: # Si la lista no esta vacia
        msg = 'Dispositivos actualmente conectados a la red:\n'
        print('Dispositivos incialmente conectados a la red:\n {}'.format(list_devices))
        for device in list_devices:
            msg = '{}\n{} - {}'.format(msg, device['IP'], device['MAC'])
    update.message.reply_text(msg) # El bot contesta con este mensaje
    while(thr_on == True): # Bucle infinito
        list_new_devices = nmap()
        print('Nuevo escaneo. Dispositivos conectados a la red:\n {}'.format(list_new_devices))
        if not list_new_devices:
            del list_devices[:]
        else:
            list_devices_to_add = []
            list_devices_to_rm = []
            for new_device in list_new_devices:
                if new_device not in list_devices:
                    list_devices_to_add.append(new_device)
            for old_device in list_devices:
                if old_device not in list_new_devices:
                    list_devices_to_rm.append(old_device)
            print('Dispositivos a insertar:\n{}'.format(list_devices_to_add))
            print('Dispositivos a eliminar:\n{}'.format(list_devices_to_rm))
            msg = ''
            if list_devices_to_add: # Si la lista de nuevos dispositivos detectados tiene algun nuevo dispositivo
                msg = 'Nuevo dispositivo conectado a la red:\n'
                for device in list_devices_to_add:
                    list_devices.append(device)
                    msg = '{}\n{} - {}'.format(msg, device['IP'], device['MAC'])
                del list_devices_to_add[:]
            if list_devices_to_rm: # Si la lista de dispositivos a eliminar (estaban conectados y ahora no se han detectado)
                msg = '{}\n\n\nDispositivo desconectado de la red:\n'.format(msg)
                for device in list_devices_to_rm:
                    list_devices.remove(device)
                    msg = '{}\n{} - {}'.format(msg, device['IP'], device['MAC'])
                del list_devices_to_rm[:]
                print('Lista final de dispositivos conectados a la red:\n {}'.format(list_devices))
            if msg:
                update.message.reply_text(msg) # El bot contesta con este mensaje
        print('sleep')
        sleep(TIEMPO_CONSULTA) # Esperamos el tiempo entre consultas

##############################

thr = None
thr_on = False
def enable(bot, update):
    global thr
    global thr_on
    if not thr_on: # Si la hebra no esta activa
        thr_on = True # Activamos la variable de hebra activa
        update.message.reply_text('Servicio activado') # El bot contesta con este mensaje
        thr = Thread(target=net_devices, args=(update,)) # Creamos un nuevo hilo de ejecucion como demonio, para la funcion "net_devices"
        thr.setDaemon(True) # Establecemos al hilo para ejecucion como demonio
        thr.start() # Lanzamos el nuevo hilo
    else:
        update.message.reply_text('El servicio esta activo') # El bot contesta con este mensaje


def disable(bot, update):
    global thr
    global thr_on
    if thr_on: # Si la hebra esta activa
        thr_on = False # Desactivamos la variable de hebra activa
        update.message.reply_text('Servicio desactivado') # El bot contesta con este mensaje
    else:
        update.message.reply_text('El servicio esta desactivado') # El bot contesta con este mensaje


def devices(bot, update):
    list_devices = nmap()
    msg = 'Dispositivos conectados a la red:\n'
    for device in list_devices:
        msg = '{}\n{} - {}'.format(msg, device['IP'], device['MAC'])
    update.message.reply_text(msg)

##############################

def main():

    # Determinar si se ha ejecutado como root
    if geteuid() != 0: # Si el script ha no ha sido ejecutado por el root (0)
        exit('\n  El Script debe ser lanzado con permisos root para poder acceder a la interfaz de red.\n\n') # Cerramos el script mostrando por salida este mensaje

    # Crear el manejador de eventos a partir del TOKEN del bot
    updater = Updater(TOKEN)

    # Obtener el registro de manejadores del planificador
    dp = updater.dispatcher

    # Asociamos el manejador para el comando
    updater.dispatcher.add_handler(CommandHandler('enable', enable))
    updater.dispatcher.add_handler(CommandHandler('disable', disable))
    updater.dispatcher.add_handler(CommandHandler('devices', devices))

    # Iniciamos el bot
    updater.start_polling(clean=True)

    # Bloqueamos el hilo de ejecucion actual (solo esperar a mensajes recibidos por el Bot)
    updater.idle()


if __name__ == '__main__':
	main()
