# -*- coding: utf-8 -*-
# Script: opibot.py
# Descripción: Bot de Telegram en Python que nos permite consultar y controlar un sistema linux (en este caso Armbian, en un dispositivo Orange pi pc)
# Autor: José Ríos Rubio
##############################

# Importar librerias
import os
import sys
import time
import numbers
import subprocess

# Importar desde librerias
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler, ConversationHandler, CallbackQueryHandler)

##############################

TOKEN = "XXXXXXXXX:XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX" # A establecer por el usuario (consultar mediante @BotFather)
ID = NNNNNNNNN # A establecer por el usuario (consultar mediante @get_id_bot)

##############################

# Funcion para realizar llamadas del sistema (ejecutar comandos Linux)
def llamadaSistema(entrada):
	salida = "" # Creamos variable vacia
	f = os.popen(entrada) # Llamada al sistema
	for i in f.readlines(): # Leemos caracter a caracter sobre la linea devuelta por la llamada al sistema
		salida += i  # Insertamos cada uno de los caracteres en nuestra variable
	salida = salida[:-1] # Truncamos el caracter fin de linea '\n'

	return salida # Devolvemos la respuesta al comando ejecutado

##############################

# Comandos recibidos

# Manejador correspondiente al comando /inicio
def start(bot, update):
	if update.message.chat_id == ID : # Solo hacer caso si quien le habla es el remitente correspondiente a dicha ID
		update.message.reply_text("Este es un Bot que permite controlar y comprobar ciertos aspectos del sistema Orange Pi en el que se aloja. Para conocer los comandos implementados consulta la /ayuda") # Respondemos al comando con el mensaje

# Manejador correspondiente al comando /ayuda
def ayuda(bot, update):
	if update.message.chat_id == ID : # Solo hacer caso si quien le habla es el remitente correspondiente a dicha ID
		update.message.reply_text("Lista de comandos implementados: \n\n/inicio - Comando de inicio\n\n/ayuda - Consulta la lista de comandos implementados y la descripcion de estos\n\n/comandos - Consulta de forma rapida la lista de comandos implementados\n\n/apagar - Apaga el sistema\n\n/reiniciar - Reiniciar el sistema\n\n/red_conectada - Consulta el nombre de la red a la que esta conectado\n\n/ip - Consulta la IP del sistema\n\n/temp - Consulta la temperatura actual del SOC\n\n/fecha - Consulta la fecha del sistema\n\n/almacenamientos - Consulta los dispositivos de almacenamiento en el sistema\n\n/arquitectura - Consulta la arquitectura del SOC\n\n/kernel - Consulta la version del Kernel del sistema\n\n/pwd - Consulta la ruta actual del Script del Bot\n\n/cd - Accede a un directorio especifico\n\n/ls - Lista los archivos de una ruta especifica\n\n/lsusb - Consulta los dispositivos USB conectados al sistema\n\n/montajes - Consulta los dispositivos montados en el sistema\n\n/cat - Muestra el contenido de un archivo\n\n/ssh_on - Activa el servidor SSH\n\n/ssh_off - Detiene el servidor SSH\n\n/ssh_reiniciar - Reinicia el servidor SSH\n\n/ssh_estado - Consulta el estado actual del servidor SSH\n\n/vnc_on - Activa el servidor VNC\n\n/vnc_off - Detiene el servidor VNC\n\n/scriptfex - Genera el archivo script.fex del sistema y lo exporta\n\n/importar - Importa archivos al sistema\n\n/exportar - Exporta archivos del sistema\n\n/drivers - Consulta los Drivers activos en el sistema\n\n/descargar - Realiza la descarga desde una URL (wget)\n\n/buscar - Realiza una busqueda de archivos segun un termino de busqueda en una localizacion especificada") # Respondemos al comando con el mensaje

# Manejador correspondiente al comando /comandos
def comandos(bot, update):
	if update.message.chat_id == ID : # Solo hacer caso si quien le habla es el remitente correspondiente a dicha ID
		update.message.reply_text("Lista de comandos implementados: \n/inicio\n/ayuda\n/comandos\n/apagar\n/reiniciar\n/red_conectada\n/ip\n/temp\n/fecha\n/almacenamientos\n/arquitectura\n/kernel\n/pwd\n/cd\n/ls\n/lsusb\n/montajes\n/cat\n/ssh_on\n/ssh_off\n/ssh_reiniciar\n/ssh_estado\n/vnc_on\n/vnc_off\n/scriptfex\n/importar\n/exportar\n/drivers\n/descargar\n/buscar") # Respondemos al comando con el mensaje

# Manejador correspondiente al comando /apagar
def apagar(bot, update):
	if update.message.chat_id == ID : # Solo hacer caso si quien le habla es el remitente correspondiente a dicha ID
		update.message.reply_text("Apagando el sistema") # Respondemos al comando con el mensaje
		llamadaSistema("shutdown -h now") # Llamada al sistema

# Manejador correspondiente al comando /reiniciar
def reiniciar(bot, update):
	if update.message.chat_id == ID : # Solo hacer caso si quien le habla es el remitente correspondiente a dicha ID
		update.message.reply_text("Reiniciando el sistema") # Respondemos al comando con el mensaje
		llamadaSistema("reboot") # Llamada al sistema

# Manejador correspondiente al comando /red_conectada
def red_conectada(bot, update):
	if update.message.chat_id == ID : # Solo hacer caso si quien le habla es el remitente correspondiente a dicha ID
		ssidred = llamadaSistema("iwgetid") # Llamada al sistema
		update.message.reply_text(ssidred) # Respondemos al comando con el mensaje

# Manejador correspondiente al comando /ip
def ip(bot, update):
	if update.message.chat_id == ID : # Solo hacer caso si quien le habla es el remitente correspondiente a dicha ID
		ip = llamadaSistema("hostname -I") # Llamada al sistema
		ip = ip[:-2] # Eliminamos ultimos caracteres
		update.message.reply_text(ip) # Respondemos al comando con el mensaje

# Manejador correspondiente al comando /temp
def temp(bot, update):
	if update.message.chat_id == ID : # Solo hacer caso si quien le habla es el remitente correspondiente a dicha ID
		temp = llamadaSistema("cat /etc/armbianmonitor/datasources/soctemp") # Llamada al sistema
		temp = "Temperatura del SOC: " + temp + "ºC" # Escribimos el mensaje a devolver
		update.message.reply_text(temp) # Respondemos al comando con el mensaje

# Manejador correspondiente al comando /fecha
def fecha(bot, update):
	if update.message.chat_id == ID : # Solo hacer caso si quien le habla es el remitente correspondiente a dicha ID
		fecha = llamadaSistema("date") # Llamada al sistema
		update.message.reply_text(fecha) # Respondemos al comando con el mensaje

# Manejador correspondiente al comando /almacenamientos
def almacenamientos(bot, update):
	if update.message.chat_id == ID : # Solo hacer caso si quien le habla es el remitente correspondiente a dicha ID
		_fdisk = llamadaSistema("fdisk -l") # Llamada al sistema
		update.message.reply_text(_fdisk) # Respondemos al comando con el mensaje

# Manejador correspondiente al comando /arquitectura
def arquitectura(bot, update):
	if update.message.chat_id == ID : # Solo hacer caso si quien le habla es el remitente correspondiente a dicha ID
		_arquitectura = llamadaSistema("arch") # Llamada al sistema
		update.message.reply_text(_arquitectura) # Respondemos al comando con el mensaje

# Manejador correspondiente al comando /kernel
def kernel(bot, update):
	if update.message.chat_id == ID : # Solo hacer caso si quien le habla es el remitente correspondiente a dicha ID
		_kernel = llamadaSistema("cat /proc/version") # Llamada al sistema
		update.message.reply_text(_kernel) # Respondemos al comando con el mensaje

# Manejador correspondiente al comando /drivers
def drivers(bot, update):
	if update.message.chat_id == ID : # Solo hacer caso si quien le habla es el remitente correspondiente a dicha ID
		_lsmod = llamadaSistema("lsmod") # Llamada al sistema
		update.message.reply_text(_lsmod) # Respondemos al comando con el mensaje

# Manejador correspondiente al comando /pwd
def pwd(bot, update):
	if update.message.chat_id == ID : # Solo hacer caso si quien le habla es el remitente correspondiente a dicha ID
		_pwd = llamadaSistema("pwd") # Llamada al sistema
		update.message.reply_text(_pwd) # Respondemos al comando con el mensaje

# Manejador correspondiente al comando /cd
def cd(bot, update, args):
	if update.message.chat_id == ID : # Solo hacer caso si quien le habla es el remitente correspondiente a dicha ID
		if len(args) == 1: # Comprobar si el comando presenta argumento o no
			directorio = args[0]
			os.chdir(directorio)
			update.message.reply_text("Cambiando al directorio " + directorio) # Respondemos al comando con el mensaje
		else:
			update.message.reply_text("Se debe especificar el directorio al que acceder.\n\nEjemplo:\n/cd /home/usuario") # Respondemos al comando con el mensaje

# Manejador correspondiente al comando /ls
def ls(bot, update, args):
	if update.message.chat_id == ID : # Solo hacer caso si quien le habla es el remitente correspondiente a dicha ID
		if len(args) == 1: # Comprobar si el comando presenta argumento o no
			_ls = llamadaSistema("ls " + args[0]) # Llamada al sistema
		else:
			_ls = llamadaSistema("ls") # Llamada al sistema
		update.message.reply_text(_ls) # Respondemos al comando con el mensaje

# Manejador correspondiente al comando /lsusb
def lsusb(bot, update):
	if update.message.chat_id == ID : # Solo hacer caso si quien le habla es el remitente correspondiente a dicha ID
		_lsusb = llamadaSistema("lsusb") # Llamada al sistema
		update.message.reply_text(_lsusb) # Respondemos al comando con el mensaje

# Manejador correspondiente al comando /montajes
def montajes(bot, update):
	if update.message.chat_id == ID : # Solo hacer caso si quien le habla es el remitente correspondiente a dicha ID
		_df = llamadaSistema("df") # Llamada al sistema
		update.message.reply_text(_df) # Respondemos al comando con el mensaje

# Manejador correspondiente al comando /borrar
def borrar(bot, update, args):
	if update.message.chat_id == ID : # Solo hacer caso si quien le habla es el remitente correspondiente a dicha ID
		if len(args) == 1: # Comprobar si el comando presenta argumento o no
			archivo = args[0]
			llamadaSistema("rm -rf " + args[0]) # Llamada al sistema
			update.message.reply_text("Archivo " + archivo + " borrado") # Respondemos al comando con el mensaje
		else:
			update.message.reply_text("Especifica un archivo.\n\nEjemplo:\n/borrar /home/user/archivo.txt") # Respondemos al comando con el mensaje

# Manejador correspondiente al comando /cat
def cat(bot, update, args):
	if update.message.chat_id == ID : # Solo hacer caso si quien le habla es el remitente correspondiente a dicha ID
		if len(args) == 1: # Comprobar si el comando presenta argumento o no
			_cat = llamadaSistema("cat " + args[0]) # Llamada al sistema
			num_caracteres_fichero = len(_cat) # Determinamos el numero de caracteres que tiene el archivo
			if num_caracteres_fichero < 4096: # Si el numero de caracteres es menor a 4096 se envia un unico mensaje con todo el contenido
				update.message.reply_text(_cat) # Respondemos al comando con el mensaje
			else: # Si el numero de caracteres es superior a 4096, se divide el contenido del archivo en diversos fragmentos de texto que se enviaran en varios mensajes
				num_mensajes = num_caracteres_fichero/float(4095) # Se determina el numero de mensajes a enviar
				if isinstance(num_mensajes, numbers.Integral) != True: # Si no es un numero entero (es decimal)
					num_mensajes = int(num_mensajes) + 1 # Se aumenta el numero de mensajes en 1
				fragmento = 0
				for i in range(0, num_mensajes): # Se van enviando cada fragmento de texto en diversos mensajes
					mensaje = _cat[fragmento:fragmento+4095].decode('utf-8', 'ignore') # Creamos un mensaje correspondiente al fragmento de texto actual
					update.message.reply_text(mensaje) # Respondemos al comando con el mensaje
					fragmento = fragmento + 4095 # Aumentamos el fragmento de texto (cursor de caracteres)
		else:
			update.message.reply_text("Especifica un archivo.\n\nEjemplo:\n/cat /home/user/archivo.txt") # Respondemos al comando con el mensaje

# Manejador correspondiente al comando /ssh_on
def ssh_on(bot, update):
	if update.message.chat_id == ID : # Solo hacer caso si quien le habla es el remitente correspondiente a dicha ID
		llamadaSistema("/etc/init.d/ssh start") # Llamada al sistema
		update.message.reply_text("Iniciando servidor SSH") # Respondemos al comando con el mensaje

# Manejador correspondiente al comando /ssh_off
def ssh_off(bot, update):
	if update.message.chat_id == ID : # Solo hacer caso si quien le habla es el remitente correspondiente a dicha ID
		llamadaSistema("/etc/init.d/ssh stop") # Llamada al sistema
		update.message.reply_text("Deteniendo servidor SSH") # Respondemos al comando con el mensaje

# Manejador correspondiente al comando /ssh_reiniciar
def ssh_reiniciar(bot, update):
	if update.message.chat_id == ID : # Solo hacer caso si quien le habla es el remitente correspondiente a dicha ID
		llamadaSistema("/etc/init.d/ssh restart") # Llamada al sistema
		update.message.reply_text(respuesta) # Respondemos al comando con el mensaje

# Manejador correspondiente al comando /ssh_estado
def ssh_estado(bot, update):
	if update.message.chat_id == ID : # Solo hacer caso si quien le habla es el remitente correspondiente a dicha ID
		respuesta = llamadaSistema("/etc/init.d/ssh status") # Llamada al sistema
		update.message.reply_text(respuesta) # Respondemos al comando con el mensaje

# Manejador correspondiente al comando /vnc_on
def vnc_on(bot, update):
	if update.message.chat_id == ID : # Solo hacer caso si quien le habla es el remitente correspondiente a dicha ID
		update.message.reply_text("Iniciando servidor VNC")     # Respondemos al comando con el mensaje
		llamadaSistema("vncserver :1 -geometry 1080x720 -depth 16 -pixelformat rgb565") # Llamada al sistema

# Manejador correspondiente al comando /vnc_off
def vnc_off(bot, update):
	if update.message.chat_id == ID : # Solo hacer caso si quien le habla es el remitente correspondiente a dicha ID
		update.message.reply_text("Cerrando servidor VNC") # Respondemos al comando con el mensaje
		llamadaSistema("vncserver -kill :1") # Llamada al sistema

		
# Manejador correspondiente al comando /scriptfex
def scriptfex(bot, update):
	if update.message.chat_id == ID : # Solo hacer caso si quien le habla es el remitente correspondiente a dicha ID
		llamadaSistema("bin2fex /boot/script.bin /boot/script.fex") # Transforma Script.bin en Script.fex
		time.sleep(5) # Esperamos 5 segundos (para que se complete la transformacion)
		bot.sendDocument(ID, open('/boot/script.fex', 'rb')) # Enviamos el archivo

# Manejador correspondiente al comando /exportar
def exportar(bot, update, args):
	if update.message.chat_id == ID : # Solo hacer caso si quien le habla es el remitente correspondiente a dicha ID
		if len(args) == 1: # Solo hacer caso si el comando presenta argumento
			archivo = open(args[0], 'rb') # Abrimos el archivo
			try:
				bot.sendDocument(ID, archivo) # Intentar enviar el archivo
			finally:
				archivo.close() # Cerrar el archivo
		else:
			update.message.reply_text("Se debe especificar el archivo que deseas extraer.\n\nEjemplo:\n/exportar /home/user/archivo") # Respondemos al comando con el mensaje
			
esperando_archivo = 0
ruta_poner_archivo = ""
# Manejador correspondiente al comando /importar
def importar(bot, update, args):
	global esperando_archivo
	global ruta_poner_archivo
	if update.message.chat_id == ID : # Solo hacer caso si quien le habla es el remitente correspondiente a dicha ID
		if len(args) == 1: # Solo hacer caso si el comando presenta argumento
			ruta_poner_archivo = args[0]
			update.message.reply_text("Inserta el archivo a enviar (tipo documento)")
			esperando_archivo = 1
		else:
			update.message.reply_text("Se debe especificar la ruta donde deseas importar el archivo.\n\nEjemplo:\n/importar /home/user") # Respondemos al comando con el mensaje

esperando_ruta = 0
enlace_descarga = ""
# Manejador correspondiente al comando /descargar
def descargar(bot, update, args):
	global esperando_ruta
	global enlace_descarga
	if update.message.chat_id == ID: # Solo hacer caso si quien le habla es el remitente correspondiente a dicha ID
		if len(args) == 2: # Si el comando presenta 2 argumentos
			enlace_descarga = args[0]
			ruta = args[1]
			subprocess.Popen(["nohup", "wget", enlace_descarga, "-P", ruta])
			update.message.reply_text("Descargando en '" + ruta + "' desde el enlace " + enlace_descarga) # Respondemos al comando con el mensaje
		elif len(args) == 1: # Si el comando presenta 1 argumento
			if esperando_ruta == 0:
				enlace_descarga = args[0]
				update.message.reply_text("Especifica a continuacion, la ruta donde almacenar el archivo a descargar.\n\nEjemplo:\n/descargar https://raw.githubusercontent.com/J-Rios/TelegramBots/master/opibot.py /home/usuario/descargas")
				esperando_ruta = 1
		else:
			update.message.reply_text("Se debe especificar el enlace (URL) de descarga y el directorio de descarga.\n\nEjemplo:\n/descargar https://raw.githubusercontent.com/J-Rios/TelegramBots/master/opibot.py /home/usuario/descargas") # Respondemos al comando con el mensaje

# Manejador correspondiente al comando /buscar
def buscar(bot, update, args):
	if update.message.chat_id == ID: # Solo hacer caso si quien le habla es el remitente correspondiente a dicha ID
		if len(args) == 2: # Si el comando presenta 2 argumentos
			nombre_archivo = args[0]
			ruta = args[1]
			resultado = llamadaSistema("find " + ruta + " -name '*" + nombre_archivo + "*'") # Llamada al sistema
			update.message.reply_text("Archivos encontrados para el termino de busqueda:\n\n'" + resultado) # Respondemos al comando con el mensaje
		else:
			update.message.reply_text("Se debe especificar el archivo y el directorio desde el que buscar.\n\nEjemplo:\n/buscar .log /") # Respondemos al comando con el mensaje

##############################

# Manejador para mensajes recibidos que no son comandos
def mensaje_nocomando(bot, update):
	global esperando_ruta
	if update.message.chat_id == ID : # Solo hacer caso si quien le habla es el remitente correspondiente a dicha ID
		if esperando_ruta == 1:
			esperando_ruta = 0
			ruta = update.message.text
			subprocess.Popen(["nohup", "wget", enlace_descarga, "-P", ruta])
			update.message.reply_text("Descargando en '" + ruta + "' desde el enlace " + enlace_descarga) # Respondemos al comando con el mensaje
		else:
			update.message.reply_text("Por favor envia un comando adecuado.\n\nPara conocer los comandos implementados consulta la /ayuda") # Respondemos al comando con el mensaje

# Manejador para recepcion de archivos enviados por el usuario
def archivo_recibido(bot, update):	
	global esperando_archivo
	global ruta_poner_archivo
	if update.message.chat_id == ID : # Solo hacer caso si quien le habla es el remitente correspondiente a dicha ID
		if esperando_archivo == 1:
			nombre_archivo = update.message.document.file_name
			id_archivo = update.message.document.file_id
			archivo = bot.getFile(id_archivo)
			ruta_actual = os.getcwd()
			os.chdir(ruta_poner_archivo)
			archivo.download(nombre_archivo)
			os.chdir(ruta_poner_archivo)
			update.message.reply_text("Archivo " + nombre_archivo + " recibido y posicionado en " + ruta_poner_archivo)
			esperando_archivo = 0

##############################

def main():
	# Crear el manejador de eventos a partir del TOKEN del bot
	updater = Updater(TOKEN)

	# Obtener el registro de manejadores del planificador
	dp = updater.dispatcher

	# Asociamos manejadores para cada comando reconocible
	dp.add_handler(CommandHandler("start", start))
	dp.add_handler(CommandHandler("ayuda", ayuda))
	dp.add_handler(CommandHandler("comandos", comandos))
	dp.add_handler(CommandHandler("apagar", apagar))
	dp.add_handler(CommandHandler("reiniciar", reiniciar))
	dp.add_handler(CommandHandler("red_conectada", red_conectada))
	dp.add_handler(CommandHandler("ip", ip))
	dp.add_handler(CommandHandler("temp", temp))
	dp.add_handler(CommandHandler("fecha", fecha))
	dp.add_handler(CommandHandler("almacenamientos", almacenamientos))
	dp.add_handler(CommandHandler("arquitectura", arquitectura))
	dp.add_handler(CommandHandler("kernel", kernel))
	dp.add_handler(CommandHandler("pwd", pwd))
	dp.add_handler(CommandHandler("drivers", drivers))
	dp.add_handler(CommandHandler("cd", cd, pass_args=True))
	dp.add_handler(CommandHandler("ls", ls, pass_args=True))
	dp.add_handler(CommandHandler("lsusb", lsusb))
	dp.add_handler(CommandHandler("montajes", montajes))
	dp.add_handler(CommandHandler("borrar", borrar, pass_args=True))
	dp.add_handler(CommandHandler("cat", cat, pass_args=True))
	dp.add_handler(CommandHandler("ssh_on", ssh_on))
	dp.add_handler(CommandHandler("ssh_off", ssh_off))
	dp.add_handler(CommandHandler("ssh_reiniciar", ssh_reiniciar))
	dp.add_handler(CommandHandler("ssh_estado", ssh_estado))
	dp.add_handler(CommandHandler("vnc_on", vnc_on))
	dp.add_handler(CommandHandler("vnc_off", vnc_off))
	dp.add_handler(CommandHandler("scriptfex", scriptfex))
	dp.add_handler(CommandHandler("exportar", exportar, pass_args=True))
	dp.add_handler(CommandHandler("importar", importar, pass_args=True))
	dp.add_handler(CommandHandler("descargar", descargar, pass_args=True))
	dp.add_handler(CommandHandler("buscar", buscar, pass_args=True))

	# Asociamos un manejador para cualquier mensaje recibido (no comando)
	dp.add_handler(MessageHandler(Filters.text, mensaje_nocomando))
	dp.add_handler(MessageHandler(Filters.document, archivo_recibido))

	# Iniciamos el bot
	updater.start_polling()

	# Actualizamos el estado del bot (bloquea la ejecucion a la espera de mensajes)
	updater.idle()


if __name__ == '__main__':
	main()

# Fin del Codigo
