import os
#################################################################
'''Ejecutar dos veces para eliminar y renombrar los archivos'''##
#################################################################
directorio = '/home/sdi/Escritorio/reposACambiar/sdi-addons'  # Directorio donde empieza
cadena = "'website':"  # Cadena que deseo encontrar en el archivo
nombreComun = '__manifest__.py'  # Nombre del archivo que buscaremos
textoAEscribir = "    'website': 'https://www.sdi.es/odoo-cloud/',\n"
LineasFichero = []

for ruta_actual, subdirectorios, archivos in os.walk(directorio): #Directorio sobre el que camino
    subdirectorios = [n for n in subdirectorios]  #Moverme por los subdirectorios
    contents = subdirectorios+archivos  #coger el subdirectorio y los archivos

    for f in contents:  #Para cada fichero hago cosas

        if os.path.isfile(ruta_actual+"/"+f) and f.startswith(nombreComun):         # Si es un archivo y empieza por __manifest__.py
            NumeroLinea = 0
            NumeroLineaGuardada = 0                                                 # Guarda la linea que me interesa
            fichero2 = open(ruta_actual+"/2"+f, 'w')                                # Creo y abro un nuevo archivo que será el bueno
            print(f)
            print(ruta_actual+"/"+f)
            fichero = open(ruta_actual+"/"+f, 'r+')                                 # Abro y leo el archivo que quiero cambiar
            listaLineas = fichero.readlines()                                       # Leo todo el archivo y lo paso a un lista
            for linea in listaLineas:
                NumeroLinea = NumeroLinea + 1
                if linea.find(cadena) > -1:                                         # Encuentro el texto que busco
                    print(NumeroLinea)
                    NumeroLineaGuardada = NumeroLinea                               # Guardo la linea que aparece en el texto que busco
            print(NumeroLineaGuardada)
            if NumeroLineaGuardada > 0:
                listaLineas[NumeroLineaGuardada-1] = textoAEscribir                 # Al ser una lista le tengo que restar 1 al numero de linea
            fichero2.writelines(listaLineas)                                        # Escribo el contenido de la lista en el archivo de respaldo
            fichero.close()
            fichero2.close()

        if os.path.isfile(ruta_actual+"/"+f) and f.startswith(nombreComun):
            os.remove(ruta_actual+"/"+f)                                            # Elimino el archivo viejo
            print("He borrado" + f)
        if os.path.isfile(ruta_actual+"/"+f) and f.startswith("2"+nombreComun):
            os.rename(ruta_actual+"/"+f, ruta_actual+"/"+nombreComun)               # Renombro el nuevo archivo como el antiguo
