import pyttsx3
import openai
import json
import sys
import time
import difflib
import re
import ast
import os
import webbrowser
import ctypes

from dotenv import load_dotenv
from  colores import color

load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

#-----------------Globales---------------------------
voz="off"
buscar=False
respuesta=""
engine= pyttsx3.init()

#---------------------------------------------------------------------------------------------------------------------------------------------
def set_terminal_title(title):
    ctypes.windll.kernel32.SetConsoleTitleW(title)

# Función para convertir texto a voz
def convertir_a_voz(tex, switch=None):
    for char in tex:
        print(char, end='', flush=True)
        time.sleep(0.01)
    if switch == "on":
        engine.setProperty('rate', 174)
        engine.setProperty('volume', 0.5)
        engine.say(tex)
        engine.runAndWait()
    print()

#--------------------------------------------------------------------------------------------------------------------------------------------
def listar_perfiles(direcotrio):
        print(color("verde"))
        archivos_txt = [archivo for archivo in os.listdir("./") if archivo.endswith(".txt")]
        print("Perfiles encontrados:\n")
        i=1
        for archivo in archivos_txt:
            print(f"{i} --> "+archivo+"\n")
            i+=1
        convertir_a_voz(f"Elije mi Perfil para comenzar (1 a {i-1})",voz)
        print(color(".."))
        return(archivos_txt)

#----------------------------Generación de Perfil y Temática----------------------------
def genera_perfil():
    contenido = ""
    directorio = "./"  # Reemplaza './ruta_del_directorio' con la ruta de tu directorio

    archivos_txt= listar_perfiles("./")
    perfil_nro= int(input(" -> "))  #  <-----Seleccion de Perfil
    os.system('cls' if os.name == 'nt' else 'clear')
    with open(archivos_txt[perfil_nro-1], encoding='utf-8') as archivo:
       contenido = archivo.read()

    #separa cadenas para transformarlas en diccionarios
    perfiles_load, unidades_load = contenido.split("///")
    cadena_limpia = perfiles_load.replace('perfil =', '').strip()
    perfil = ast.literal_eval(cadena_limpia)
    cadena_limpia= unidades_load.replace('unidades =', '').strip()
    unidades= ast.literal_eval(cadena_limpia)
    #--------------------reformateo de contenidos-----------------------------------
    cadena_json = json.dumps(unidades, ensure_ascii=False).encode("utf-8")
    # Decodificar la cadena JSON en forma UTF-8
    contenido = cadena_json.decode("utf-8")
    contenido = contenido.replace("{", "")
    contenido = contenido.replace("}", "")
    contenido = contenido.replace(",", "")
    contenido = contenido.replace('"', "")
    #-------------------------comportamiento (Templates de Contexto)-----------------------------------------
    idioma = "Escribes siempre en indioma español. Responde en forma amigable y didáctica"
    contexto = "Nunca jamás respondas consultas que NO sean del Tema "+perfil["tema"]+ ", y solamente responde temas de "+perfil["tema"] + "establece un nivel de confianza entre 0 y 1 "+"solo escribe respuestas con un nivel de confianza mayor a 1.0"
    especialidad = "Eres un asistente especialista en didácica de la "+ perfil["disciplina"]+ " en el Tema "+ perfil["tema"]+", y solmante responde sobre el tema: " + perfil["tema"] + ", NO respondes preguntas !=  : " + perfil["tema"]
    estilo = "didactica clara y simple. Tienes la capacidad para redactar ejercicios, ejemplos prácticos y evaluaciones, checklist,clasificaciones, esquemas, planificar contenidos, tablas, resúmenes, ensayos literarios y recomendaciones bibliográficas"

    rol_sistema = "Tu nombre es "+ perfil["asistente"] + ". Eres asistente de didáctica de "+ perfil["area"] + "aplicada a "+ perfil["disciplina"] # Tema
    rol_sistema = rol_sistema + contexto + especialidad + idioma
    rol_asistente = "Tu nombre es "+ perfil["asistente"]+ ".Responde unicamente preguntas de "+perfil["tema"] 
    rol_asistente = rol_asistente + especialidad + contexto + estilo + contenido + "responde fundamentando de manera muy extremadamente detallada y con ejemplos prácticos los conceptos relacionados con "+perfil["tema"]+"y lista bibliografía sobre "+perfil["tema"]
    rol_usuario="en que te puedo ayudar hoy ?"
    print(color(".."))
    return perfil,unidades,rol_sistema,rol_asistente,rol_usuario,contenido


#---------------------------------------------------------------------------------------------------------
# Función para procesar la pregunta y generar la respuesta
def procesar_pregunta(rol_sistema,rol_asistente,rol_usuario,pregunta):
   print("\n...un momento, procesando...")
   chat_completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0613",
        messages=[{"role": "system", "content": rol_sistema },
                  {"role": "user", "content": rol_usuario} ,
                  {"role": "assistant", "content": rol_asistente  +pregunta},]
    )
   respuesta = chat_completion.choices[0].message.content
   return respuesta


#---------Extrae el titulo de la unidad--------------------------------------------------------------------
def extraer_cadena(cadena, simbolo):  #---> muestra el título de la unidad temática
    indice_pun = cadena.find(simbolo)
    if indice_pun != -1:
        cadena_extraida = cadena[:indice_pun]
    else:
        cadena_extraida = cadena
    return cadena_extraida

#------------------------------------------------------------------------------------------------------
#Lista unideades disponibles en el diccionario
def mostrar_unidades(unidades):
    convertir_a_voz("podrás preguntar todo lo relacionado con los siguientes ítems temáticos:\n",voz)
    list_of_keys = list(unidades.keys())
    for i in unidades: #  diccionario unidades
        titulo = str(list_of_keys.index(i)+1)+" -> " + extraer_cadena(unidades[i],".") #muestra el título de la unidad
        print(titulo)

#-------------terminacion por unidad fuera de rango-----------------------------------------------------
def validar_opcion(unidades):
    while True:
        convertir_a_voz(f"\n¿qué contenido quieres repasar hoy? ingresa un valor entre 1 y {len(unidades)}",voz)
        print(color("rojo"))
        convertir_a_voz("Recuerda ingresar un 0 para terminar tu sesión...",voz)
        print(color("naranja"))
        unidad_elegida = input("Ingresa un número de ítem -> ")
        try:
            if int(unidad_elegida) in range(0, len(unidades)+1):
                break  # Salir del bucle si el unidad_elegida es válido
        except ValueError:
            print(f"Error: Por favor, ingrese un número válido  entre 1 y {len(unidades)}")

    if unidad_elegida == "0":
        convertir_a_voz(".....Adios..., chau chau...., nos leemos pronto !",voz)
        sys.exit()

    print(color(".."))
    return("unidad "+str(unidad_elegida))
#---------------------------------------------------------------------------------------------------
def mostrar_temas(unidad_elegida):
    # Supongamos que tenemos un diccionario de unidades con una clave 'unidad_elegida'
    # Extraemos el texto de la unidad elegida del diccionario
    texto_unidad = unidades.get(unidad_elegida, '')

    # Separamos el texto en componentes usando '. ' como separador
    componentes = texto_unidad.split('. ')

    # Enumeramos cada componente con una enumeración alfabética
    enumeracion_alfabetica = 'abcdefghijklmnopqrstuvwxyz'
    enumerados = []
    enumerados_separados = []
    item = 0
    for i, componente in enumerate(componentes):
            if i < len(enumeracion_alfabetica):
                enumerados.append(f"{enumeracion_alfabetica[i]}. {componente}")
                item = item +1

    # Mostramos cada componente con una enumeración alfabética en líneas separadas
    if item > 1:
        convertir_a_voz("Los temas tratados son los siguientes : \n")
        enumerados_separados = '\n'.join(enumerados)
        print(enumerados_separados)


#---------------------------------------------------------------------------------------------------
def corregir_sintaxis(palabra, diccionario):
    palabra = palabra.lower()  # Convertimos la palabra a minúsculas para hacer una comparación insensible a mayúsculas
    sugerencias = difflib.get_close_matches(palabra, diccionario)

    if sugerencias:
        return sugerencias[0]  # Devolvemos la palabra más similar
    else:
        return palabra  # Si no se encontró ninguna sugerencia, devolvemos la palabra original

#------------------------------------------------------------------------------------------------------
def extraer_numero_unidad(consulta):
    # Utilizamos una expresión regular para encontrar el número de unidad en la consulta
    # Suponemos que el número de unidad es una secuencia de dígis
    patron_numero_unidad = r'/d+'
    numeros_encontrados = re.findall(patron_numero_unidad, consulta)

    if numeros_encontrados:
        return int(numeros_encontrados[0])  # Devolvemos el primer número encontrado
    else:
        return None  # Si no se encontró ningún número, devolvemos None

#------------------------------------------Busqueda en Internet------------------------------------------------
def convertir_a_link(tex,servicio):
    busqueda = "+".join(tex.split()[:])
    if servicio =="google":
            link= f"https://scholar.google.es/scholar?hl=es&as_sdt=0%2C5&q={busqueda}"
    if servicio == "wikipedia":
            link= f"https://es.wikipedia.org/w/index.php?search={busqueda}"
    if servicio=="bing":
            link= f"https://www.bing.com/images/search?q={busqueda})"
    if servicio =="youtube":
            link= f"https://www.youtube.com/results?search_query=video+oficial+{busqueda}" 
    return link

##################################### PRINCIPAL #############################################
perfil,unidades,rol_sistema,rol_asistente,rol_usuario,contenido = genera_perfil()
diccionario_palabras_validas = ["unidad","ítem","item", "tema","punto"]

set_terminal_title(perfil["tema"])
print(color("amarillo"))
saludo = f"Hola. Mi nombre es "+ str(perfil["asistente"])+" , estoy aquí para ayudarte con tus dudas sobre "+ str(perfil["tema"])
convertir_a_voz(saludo,voz)
print(color(".."))

print(color("amarillo"))
aux_rol_asistente = rol_asistente

#----Unidades -----------------------------------
mostrar_unidades(unidades)# <- diccionario

# Undades Temáicas  <-------------------------------------------
unidad_elegida = validar_opcion(unidades) # <-- "unidad N"
Aux_unidad = unidad_elegida
rol_asistente = aux_rol_asistente

print(color("amarillo"))
mostrar_temas(unidad_elegida)
print(color(".."))

################################################LOOP PRINCIPAL #################################################
while True:
    print(color("amarillo")+"---------------------> Escribe ahora tu consulta <-----------------------")
    convertir_a_voz("¿cuál es tu consulta?",voz)
    print(color("naranja"))
    pregunta = input()
    comando = pregunta
    #----------------------------------correcion y validacion----------------------------------
    # Corregir la palabra "unidad" si está mal escrita
    palabra_corregida = corregir_sintaxis("unidad", diccionario_palabras_validas)
    pregunta_corregida = pregunta.replace("unidad", palabra_corregida)

    # Extraer el número de unidad de la pregunta corregida
    unidad_elegida = "unidad " + str(extraer_numero_unidad(pregunta_corregida))      #  <--------

    # Validar si la unidad elegida está en el diccionario "unidades"
    if unidad_elegida in unidades:
        print(color("rojo"))
        print(f"Trabajando con los contenidos de {unidad_elegida} :\n")
        mostrar_temas(unidad_elegida)
        print(color(".."))
    else:
       unidad_elegida = Aux_unidad
#-------------------------------------------------------------------------------------------------------
    print(color("amarillo")+"-------------------------------------------------------------------------")
    if pregunta.lower() == '0':
        convertir_a_voz(".....Adios..., chau chau...., nos leemos pronto !",voz)
        time.sleep(2)
        sys.exit()

    if comando.lower()=="voz:on":
        voz = "on"
        print("Ok, ahora puedo hablar !")
        continue
    if comando.lower()=="voz:off":
        voz = "off"
        print(" ok, estoy en estado MUTE ! ")
        continue
    if comando.lower()=="ref:on":
        buscar=True
        print("se muestran resultados de búsqueda...")
        continue
    if comando.lower()=="ref:off":
        buscar=False
        print("NO se muestran serultados de busqueda...")
        continue

    respuesta = procesar_pregunta(rol_sistema,rol_asistente+" limitate a responde sin decir hola, sin mencionar tu nombre ni a que te dedicas y, desarrolla: " +pregunta+" sobre : "+ str(perfil["tema"]) +" de forma muy extremadamante detallada y completa ",rol_usuario,pregunta)
    
    with open('respuesta_chatgpt.log', 'a+', encoding='utf-8') as file:
        file.writelines("\nConsulta: "+pregunta+"\nRespuesta: "+respuesta+"\n")
        file.writelines("///")            

    print(color("amarillo")+perfil["asistente"] +":")
    print("--------------------------------------------------------------------")
    convertir_a_voz(respuesta,voz)

    if buscar:
        if len(respuesta.split(" "))>50 and len(pregunta.split(" "))>4:
                print(color("verde"))  #-------------Busca en google-------------------------
                convertir_a_voz("Puedes encontrar más información en google académico...",voz)
                webbrowser.open(convertir_a_link(perfil["tema"]+ "+" + perfil["disciplina"] + "+" + pregunta, "google"))

                print(color("verde"))    #-----------Busca en Wikipedia----------------------
                convertir_a_voz("También te puede interesar un contenido en Wikipedia...",voz)
                webbrowser.open(convertir_a_link(perfil["tema"],"wikipedia" ))

                print(color("verde"))  #--------------Busca en Bing------------------------
                convertir_a_voz("También ver imagenes en Bing...",voz)
                webbrowser.open(convertir_a_link(perfil["tema"]+ "+" + perfil["disciplina"] + "+" + pregunta, "bing"))

                print(color("verde"))  #--------------Busca en Youtube------------------------
                convertir_a_voz("También ver videos relacionados en Youtube...",voz)
                webbrowser.open(convertir_a_link(perfil["tema"]+ "+" + perfil["disciplina"] + "+" + pregunta, "youtube"))
                print(color(".."))
    print(color(".."))
##############################################FIN LOOP PRINCIPAL#####################################################################

