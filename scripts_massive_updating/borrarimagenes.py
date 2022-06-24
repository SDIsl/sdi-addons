import os
import shutil


directorio = '/home/sdi/Escritorio/clonecitos/sdi-addons'  #Directorio donde empieza
#directorio='/home/sdi/dodoo-ws/odoo/14.0/sdisl/talleres-addons'


for ruta_actual, subdirectorios, archivos in os.walk(directorio): #Directorio sobre el que camino
    subdirectorios = [n for n in subdirectorios]  #Moverme por los subdirectorios
    contents = subdirectorios+archivos  #coger el subdirectorio y los archivos
    


    for f in contents:
       # print(ruta_actual+"/"+f)
        
        if os.path.isfile(ruta_actual+"/"+f) and f.startswith('icon.png'):         # Si es un archivo y empieza por icon.png
            print(f)
            os.remove(ruta_actual+"/"+f)                                           # Lo elimino
            print('Ha sido borrado')
            shutil.copy('/home/sdi/Descargas/icon.png', ruta_actual+"/")           # Añado el bueno en la posicion del file 
     

        if os.path.isfile(ruta_actual+"/"+f) and f.startswith('icon.svg'):         # Si es un archivo y empieza por icon.svg
            print(ruta_actual+"/"+f)
            os.remove(ruta_actual+"/"+f)                                           # Lo elimino
            print('Ha sido borrado')
 

     
