# -*- coding: utf-8 -*-
'''
Script:                netGuard.py
Descripcion:
    Bot de Telegram que lleva un control de los dispositivos que, por wi-fi, se conectan/desconectan
    de la red local (wlan).
Autor:                 Jose Rios Rubio
Fecha de creacion:     08/08/2017
Fecha de modificacion: 09/08/2017
Version:               1.1
'''

# Importar desde librerias
from os import popen, geteuid
from sys import exit
from re import findall
from time import sleep
from threading import Thread
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler, ConversationHandler, CallbackQueryHandler)

##############################

TOKEN = "XXXXXXXXX:XXXXXXX-XXXXXXXXXXXXXXXXXXXXXXXXXXX" # A establecer por el usuario (consultar mediante @BotFather)
TIEMPO_CONSULTA = 10 # Tiempo entre consultas de dispositivos en la red (en segundos)

##############################

MY_DEVICES = [] # Lista de dispositivos con nombres asociados

##############################

# Funcion para realizar llamadas del sistema (ejecutar comandos Bash)
def llamadaSistema(entrada):
    salida = "" # Creamos variable vacia
    f = popen(entrada) # Llamada al sistema
    for i in f.readlines(): # Leemos caracter a caracter sobre la linea devuelta por la llamada al sistema
        salida += i  # Insertamos cada uno de los caracteres en nuestra variable
    salida = salida[:-1] # Truncamos el caracter fin de linea '\n'
    return salida # Devolvemos la respuesta al comando ejecutado

# Funcion para realizar el escaneo de los dispositivos conectados a la red mediante la herramienta nmap
def nmap():
    device_data = {'IP': '0.0.0.0', 'MAC': '00:00:00:00:00'} # Creamos un diccionario por defecto donde guardar la informacion de los dispositivos (IP y MAC)
    list_dev = [] # Lista de dispositivos inicialmente vacia
    nmap_raw = llamadaSistema("nmap -sP 192.168.1.0/24 --disable-arp-ping") # Realizamos la llamada al comando
    list_ip = findall('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', nmap_raw) # Metemos en una lista las IPs de la respuesta del comando nmap
    list_mac = findall('(?:[0-9a-fA-F]:?){12}', nmap_raw) # Metemos en una lista las MACs de la respuesta del comando nmap
    if len(list_ip)-1 == len(list_mac): # Si el numero de MACs es uno menos que el de IPs (pues la ultima ip de la lista es la de nuestro dispositivo)
        for i in range(0, len(list_mac), 1): # Para cada MAC
            device_data['IP'] = list_ip[i] # Almacenamos en el diccionario la IP de dicho dispositivo
            device_data['MAC'] = list_mac[i] # Almacenamos en el diccionario la MAC de dicho dispositivo
            list_dev.append(device_data.copy()) # Añadimos el dispositivo a la lista
    return list_dev # Devolver la lista de dispositivos

##############################

# Funcion correspondiente a la hebra de escaneo periodico de la red
def net_devices(update):
    update.message.reply_text('Escaneando la red. Este proceso puede tardar hasta 2 minutos...') # El bot contesta con este mensaje
    list_devices = nmap()
    if not list_devices: # Si la lista esta vacia
        msg = 'Ningun dispositivo detectado'
    else: # Si la lista no esta vacia
        msg = 'Dispositivos actualmente conectados a la red:\n'
        for device in list_devices:
            is_in = False
            for my_dev in MY_DEVICES:
                if my_dev['MAC'] == device['MAC']:
                    is_in = True
                    dev_name = my_dev['NAME']
                    break
            if is_in:
                msg = '{}\n{} - {}'.format(msg, device['IP'], dev_name)
            else:
                msg = '{}\n{} - {}'.format(msg, device['IP'], device['MAC'])
    update.message.reply_text(msg) # El bot contesta con este mensaje
    while(thr_on == True): # Bucle infinito
        list_new_devices = nmap()
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
            msg = ''
            if list_devices_to_add: # Si la lista de nuevos dispositivos detectados tiene algun nuevo dispositivo
                msg = 'Nuevo dispositivo conectado a la red:\n'
                for device in list_devices_to_add:
                    list_devices.append(device)
                    is_in = False
                    for my_dev in MY_DEVICES:
                        if my_dev['MAC'] == device['MAC']:
                            is_in = True
                            dev_name = my_dev['NAME']
                            break
                    if is_in:
                        msg = '{}\n{} - {}'.format(msg, device['IP'], dev_name)
                    else:
                        msg = '{}\n{} - {}'.format(msg, device['IP'], device['MAC'])
                del list_devices_to_add[:]
            if list_devices_to_rm: # Si la lista de dispositivos a eliminar (estaban conectados y ahora no se han detectado)
                msg = '{}\n\n\nDispositivo desconectado de la red:\n'.format(msg)
                for device in list_devices_to_rm:
                    list_devices.remove(device)
                    is_in = False
                    for my_dev in MY_DEVICES:
                        if my_dev['MAC'] == device['MAC']:
                            is_in = True
                            dev_name = my_dev['NAME']
                            break
                    if is_in:
                        msg = '{}\n{} - {}'.format(msg, device['IP'], dev_name)
                    else:
                        msg = '{}\n{} - {}'.format(msg, device['IP'], device['MAC'])
                del list_devices_to_rm[:]
            if msg:
                update.message.reply_text(msg) # El bot contesta con este mensaje
        #print('Escaneo realizado:\n{}\n\n'.format(list_devices))
        sleep(TIEMPO_CONSULTA) # Esperamos el tiempo entre consultas

##############################

thr = None
thr_on = False
# Manejador para el comando /enable
def enable(bot, update):
    global thr
    global thr_on
    if not thr_on: # Si la hebra no esta activa
        thr_on = True # Activamos la variable de hebra activa
        update.message.reply_text('Servicio activado. A continuacion, se monitorizara de forma automatica las conexiones/desconexiones de red') # El bot contesta con este mensaje
        thr = Thread(target=net_devices, args=(update,)) # Creamos un nuevo hilo de ejecucion como demonio, para la funcion "net_devices"
        thr.setDaemon(True) # Establecemos al hilo para ejecucion como demonio
        thr.start() # Lanzamos el nuevo hilo
    else:
        update.message.reply_text('El servicio ya esta activo') # El bot contesta con este mensaje

# Manejador para el comando /disable
def disable(bot, update):
    global thr
    global thr_on
    if thr_on: # Si la hebra esta activa
        thr_on = False # Desactivamos la variable de hebra activa
        update.message.reply_text('Servicio desactivado. La monitorizacion de la red se ha detenido') # El bot contesta con este mensaje
    else:
        update.message.reply_text('El servicio ya esta desactivado') # El bot contesta con este mensaje

# Manejador para el comando /devices
def devices(bot, update):
    update.message.reply_text('Escaneando la red. Este proceso puede tardar hasta 2 minutos...') # El bot contesta con este mensaje
    list_devices = nmap()
    if not list_devices: # Si la lista esta vacia
        msg = 'Ningun dispositivo detectado'
    else: # Si la lista no esta vacia
        msg = 'Dispositivos actualmente conectados a la red:\n'
        for device in list_devices:
            is_in = False
            for my_dev in MY_DEVICES:
                if my_dev['MAC'] == device['MAC']:
                    is_in = True
                    dev_name = my_dev['NAME']
                    break
            if is_in:
                msg = '{}\n{} - {}'.format(msg, device['IP'], dev_name)
            else:
                msg = '{}\n{} - {}'.format(msg, device['IP'], device['MAC'])
    update.message.reply_text(msg) # El bot contesta con este mensaje

# Manejador para el comando /name
def name(bot, update, args):
    # Nota: Comprobar el formato de la mac de entrada.
    if len(args) == 2: # Si el comando presenta 2 argumentos
        device_new = {'NAME': '0.0.0.0', 'MAC': '00:00:00:00:00'}
        device_new['NAME'] = args[0]
        device_new['MAC'] = args[1]
        is_in = False
        for my_dev in MY_DEVICES:
            if my_dev['MAC'] == device_new['MAC']:
                is_in = True
                dev_old = my_dev
                break
        if is_in:
            msg = 'Cambiado el nombre "{}" por el de "{}" para la MAC {}'.format(dev_old['NAME'], device_new['NAME'], device_new['MAC'])
            MY_DEVICES.remove(dev_old)
            MY_DEVICES.append(device_new)
        else:
            msg = 'Nombre {} asociado a la MAC {}'.format(device_new['NAME'], device_new['MAC'])
            MY_DEVICES.append(device_new)
    else:
        msg = 'Debe especificarse el nombre que se le va a dar al dispositivo y la MAC de este.\nPor ejemplo:\n\n/name mi_pc 01:23:45:67:89'
    update.message.reply_text(msg) # El bot contesta con este mensaje

##############################

def main():

    # Determinar si se ha ejecutado como root
    if geteuid() != 0: # Si el script ha no ha sido ejecutado por el root (0)
        exit('\n---------------\nEl Script debe ser lanzado con permisos root para poder acceder a la interfaz de red.\n---------------\n\n') # Cerramos el script mostrando por salida este mensaje

    # Crear el manejador de eventos a partir del TOKEN del bot
    updater = Updater(TOKEN)

    # Obtener el registro de manejadores del planificador
    dp = updater.dispatcher

    # Asociamos el manejador para el comando
    updater.dispatcher.add_handler(CommandHandler('enable', enable))
    updater.dispatcher.add_handler(CommandHandler('disable', disable))
    updater.dispatcher.add_handler(CommandHandler('devices', devices))
    updater.dispatcher.add_handler(CommandHandler('name', name, pass_args=True))

    # Iniciamos el bot
    updater.start_polling(clean=True)

    # Bloqueamos el hilo de ejecucion actual (solo esperar a mensajes recibidos por el Bot)
    updater.idle()


if __name__ == '__main__':
	main()
