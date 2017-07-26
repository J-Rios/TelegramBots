# -*- coding: utf-8 -*-
'''
Script:  MolaBot.py

Descripcion:
    Bot de Telegram que gestiona todo un sistema de reputaciones de los usuarios pertenecientes a
    un grupo. Permite a un usuario, dar "Likes" a los mensajes de otros, y el numero global de
    "Likes" (la suma de todos los likes de todos los mensajes de un mismo usuario) determinara los
    puntos de reputacion que dicho usuario tiene.

Autor:   Jose Rios Rubio
Fecha:   26/07/2017
Version: 1.7
'''

import os
import json
from threading import Lock
from collections import OrderedDict


class TSjson:
    '''
    Clase de acceso para lectura y escritura de archivos json generales de forma segura desde
    cualquier hilo de ejecucion (Thread-Safe).
    '''

    # Constructor de la clase
    def __init__(self, file_name):
        
        self.lock = Lock() #Inicializa el Lock
        self.file_name = file_name # Adquiere el nombre del archivo a controlar


    # Funcion para leer de un archivo json
    def read(self):
        
        try: # Intentar abrir el archivo
            self.lock.acquire() # Cerramos (adquirimos) el mutex
            if not os.path.exists(self.file_name): # Si el archivo no existe
                read = {} # Devolver un diccionario vacio
            else: # Si el archivo existe
                if not os.stat(self.file_name).st_size: # Si el archivo esta vacio
                    read = {} # Devolver un diccionario vacio
                else: # El archivo existe y tiene contenido
                    with open(self.file_name, "r") as f: # Abrir el archivo en modo lectura
                        read = json.load(f, object_pairs_hook=OrderedDict) # Leer todo el archivo y devolver la lectura de los datos json usando un diccionario ordenado
        except: # Error intentando abrir el archivo
            print("    Error cuando se abria para lectura, el archivo {}".format(self.file_name)) # Escribir en consola el error
            read = None # Devolver None
        finally: # Para acabar, haya habido excepcion o no
            self.lock.release() # Abrimos (liberamos) el mutex
        
        return read # Devolver el resultado de la lectura de la funcion


    # Funcion para escribir en un archivo json
    def write(self, data):
        
        # Si no existe el directorio que contiene los archivos de datos, lo creamos
        directory = os.path.dirname(self.file_name) # Obtener el nombre del directorio que contiene al archivo
        if not os.path.exists(directory): # Si el directorio (ruta) no existe
            os.makedirs(directory) # Creamos el directorio
        
        try: # Intentar abrir el archivo
            self.lock.acquire() # Cerramos (adquirimos) el mutex
            with open(self.file_name, "w") as f: # Abrir el archivo en modo escritura (sobre-escribe)
                #if CONST['PYTHON'] == 2: # Compatibilidad con Python 2
                #    f.write("\n{}\n".format(json.dumps(data, ensure_ascii=False, indent=4))) # Escribimos en el archivo los datos json asegurando todos los caracteres ascii, codificacion utf-8 y una "indentacion" de 4 espacios
                #else:
                f.write("\n{}\n".format(json.dumps(data, indent=4))) # Escribimos en el archivo los datos json asegurando todos los caracteres ascii, codificacion utf-8 y una "indentacion" de 4 espacios
        except: # Error intentando abrir el archivo
            print("    Error cuando se abria para escritura, el archivo {}".format(self.file_name)) # Escribir en consola el error
        finally: # Para acabar, haya habido excepcion o no
            self.lock.release() # Abrimos (liberamos) el mutex


    # Funcion para leer el contenido de un archivo json (datos json)
    def read_content(self):
        
        read = self.read() # Leer todo el archivo json
        
        if read != {}: # Si la lectura no es vacia
            return read['Content'] # Devolvemos el contenido de la lectura (datos json)
        else: # Lectura vacia
            return read # Devolvemos la lectura vacia


    # Funcion para añadir al contenido de un archivo json, nuevos datos json
    def write_content(self, data):
        
        # Si no existe el directorio que contiene los archivos de datos, lo creamos
        directory = os.path.dirname(self.file_name) # Obtener el nombre del directorio que contiene al archivo
        if not os.path.exists(directory): # Si el directorio (ruta) no existe
            os.makedirs(directory) # Creamos el directorio
        
        try: # Intentar abrir el archivo
            self.lock.acquire() # Cerramos (adquirimos) el mutex
            
            if os.path.exists(self.file_name) and os.stat(self.file_name).st_size: # Si el archivo existe y no esta vacio
                with open(self.file_name, "r") as f: # Abrir el archivo en modo lectura
                    content = json.load(f, object_pairs_hook=OrderedDict) # Leer todo el archivo y devolver la lectura de los datos json usando un diccionario ordenado

                content['Content'].append(data) # Añadir los nuevos datos al contenido del json
                
                with open(self.file_name, "w") as f: # Abrir el archivo en modo escritura (sobre-escribe)
                    f.write("\n{}\n".format(json.dumps(content, indent=4))) # Escribimos en el archivo los datos json asegurando todos los caracteres ascii, codificacion utf-8 y una "indentacion" de 4 espacios
            else: # El archivo no existe o esta vacio
                with open(self.file_name, "w") as f: # Abrir el archivo en modo escritura (sobre-escribe)
                    f.write('\n{\n    "Content": []\n}\n') # Escribir la estructura de contenido basica
                
                with open(self.file_name, "r") as f: # Abrir el archivo en modo lectura
                    content = json.load(f) # Leer todo el archivo

                content['Content'].append(data) # Añadir los datos al contenido del json

                with open(self.file_name, "w") as f:  # Abrir el archivo en modo escritura (sobre-escribe)
                    f.write("\n{}\n".format(json.dumps(content, indent=4))) # Escribimos en el archivo los datos json asegurando todos los caracteres ascii, codificacion utf-8 y una "indentacion" de 4 espacios
        except IOError as e:
            print("    I/O error({0}): {1}".format(e.errno, e.strerror))
        except ValueError:
            print("    Error en conversion de dato")
        except: # Error intentando abrir el archivo
            print("    Error cuando se abria para escritura, el archivo {}".format(self.file_name)) # Escribir en consola el error
        finally: # Para acabar, haya habido excepcion o no
            self.lock.release() # Abrimos (liberamos) el mutex


    # Funcion para actualizar datos de un archivo json
    # [Nota: cada dato json necesita al menos 1 elemento identificador unico (uide), si no es asi, la actualizacion se producira en el primer elemento que se encuentre]
    def update(self, data, uide):
        
        file_data = self.read() # Leer todo el archivo json
        
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
            self.write(file_data) # Escribimos el dato actualizado en el archivo json
        else: # No se encontro ningun dato json con dicho UIDE
            print("    Error: UIDE no encontrado en el archivo, o el archivo no existe") # Escribir en consola el error

    # Funcion para actualizar datos internos de los datos de un archivo json
    # [Nota: cada dato json necesita al menos 1 elemento identificador unico (uide), si no es asi, la actualizacion se producira en el primer elemento que se encuentre]
    def update_twice(self, data, uide1, uide2):
        
        file_data = self.read() # Leer todo el archivo json
        
        # Buscar la posicion del dato en el contenido json
        found = 0 # Posicion encontrada a 0
        i = 0 # Posicion inicial del dato a 0
        for msg in file_data['Content']: # Para cada mensaje en el archivo json
            if (data[uide1] == msg[uide1]) and (data[uide2] == msg[uide2]): # Si el mensaje tiene el UIDE buscado
                found = 1 # Marcar que se ha encontrado la posicion
                break # Interrumpir y salir del bucle
            i = i + 1 # Incrementar la posicion del dato
        
        if found: # Si se encontro en el archivo json datos con el UIDE buscado
            file_data['Content'][i] = data # Actualizamos los datos json que contiene ese UIDE
            self.write(file_data) # Escribimos el dato actualizado en el archivo json
        else: # No se encontro ningun dato json con dicho UIDE
            print("    Error: UIDE no encontrado en el archivo, o el archivo no existe") # Escribir en consola el error


    # Funcion para limpiar todos los datos de un archivo json (no se usa actualmente)
    def clear_content(self):
        
        try: # Intentar abrir el archivo
            self.lock.acquire() # Cerramos (adquirimos) el mutex
            if os.path.exists(self.file_name) and os.stat(self.file_name).st_size: # Si el archivo existe y no esta vacio
                with open(self.file_name, "w") as f: # Abrir el archivo en modo escritura (sobre-escribe)
                    f.write('\n{\n    "Content": [\n    ]\n}\n') # Escribir la estructura de contenido basica
        except: # Error intentando abrir el archivo
            print("    Error cuando se abria para escritura, el archivo {}".format(self.file_name)) # Escribir en consola el error
        finally: # Para acabar, haya habido excepcion o no
            self.lock.release() # Abrimos (liberamos) el mutex
    

    # funcion para eliminar un archivo json (no se usa actualmente)
    def delete(self):

        self.lock.acquire() # Cerramos (adquirimos) el mutex
        if os.path.exists(self.file_name): # Si el archivo existe
            os.remove(self.file_name) # Eliminamos el archivo
        self.lock.release() # Abrimos (liberamos) el mutex
