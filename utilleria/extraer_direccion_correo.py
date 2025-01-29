import pymongo
import email

correos_ya_recopilados = set()

def listaDeCorreosYaRecopilados(direccion_de_correo):
    """
    Obtiene una lista de los correos electrónicos ya recopilados
    para una dirección de correo electrónico específica.

    :param direccion_de_correo: La dirección de correo electrónico
    :type direccion_de_correo: str
    :return: Una lista de correos electrónicos ya recopilados
    :rtype: list
    """
    lista = []
    try:
        client = pymongo.MongoClient("mongodb://localhost:2018")
        db = client["direcciones_recopiladas"]
        collection = db[direccion_de_correo]
        correos = collection.find()
        for i in correos:
            lista.append(i["_id"])
            # print(i["_id"])
        return lista
    except Exception as e:
        print("Error al obtener la lista de correos ya recopilados: ", e)


def recuperarDaseDatosMongoDB(direccion):
    """
    Recupera los correos electrónicos guardados en la base de datos MongoDB
    para la cuenta de correo especificada

    :param direccion: La cuenta de correo de Gmail
    :type direccion: str
    :return: Una lista de direcciones de correo electrónico
    :rtype: list[str]
    """
    # Conecta a la base de datos MongoDB
    # La variable "client" es la conexión a la base de datos
    client = pymongo.MongoClient("mongodb://localhost:2018")

    # Selecciona la base de datos "correos"
    # La variable "db" es la base de datos seleccionada
    db = client["correos"]

    # Selecciona la colección que se indica en la variable "direccion"
    # La variable "collection" es la colección seleccionada
    collection = db[direccion]

    # Inicializa una lista vacía para guardar las direcciones de correo
    # La variable "lista_direcciones" es la lista vacía
    lista_direcciones = []

    # Itera sobre los documentos de la colección y extrae el campo "from"
    # de cada documento y lo agrega a la lista "lista_direcciones"
    for document in collection.find():
        lista_direcciones.append(document["from"])

    # Cierra la conexión a la base de datos
    client.close()

    # Devuelve la lista de direcciones de correo electrónico
    return lista_direcciones

def insertarDireccionCorreoMongoDB(correo_recopilado, cuenta_correo):
    """
    Inserta una dirección de correo electrónico en la base de datos MongoDB

    :param direccion: La dirección de correo electrónico
    :type direccion: str
    :param cuenta_correo: La cuenta de correo de Gmail
    :type cuenta_correo: str
    """
    # Conecta a la base de datos MongoDB
    # La variable "client" es la conexión a la base de datos
    try:
        client = pymongo.MongoClient("mongodb://localhost:2018")

        # Selecciona la base de datos "correos"
        # La variable "db" es la base de datos seleccionada
        db = client["direcciones_recopiladas"]

        # Selecciona la colección que se indica en la variable "cuenta_correo"
        # La variable "collection" es la colección seleccionada
        collection = db[cuenta_correo]

        # Inserta la dirección de correo electrónico en la colección
        # La variable "direccion" es la dirección de correo electrónico que se va a insertar
        collection.insert_one({"_id": correo_recopilado})
    except Exception as e:
        print(e)

def limpiar_direccion(direccion):
    """
    Esta función toma una cadena de texto que representa una dirección
    de correo electrónico y devuelve una cadena con la dirección limpia
    de etiquetas HTML.

    La dirección de correo electrónico puede tener etiquetas HTML que
    la envuelven, por ejemplo, "<span>juan.perez@example.com</span>".
    La función busca la primera etiqueta "<" y la última etiqueta ">"
    y devuelve la cadena que está dentro de ambas etiquetas.

    :param direccion: La cadena con la dirección de correo electrónico
    :type direccion: str
    :return: La dirección de correo electrónico limpia de etiquetas HTML
    :rtype: str
    """

    # Busca la primera etiqueta "<" en la cadena de texto
    # La variable "start" es el índice en el que se encuentra la etiqueta "<"
    start = direccion.find("<") + 1

    # Busca la última etiqueta ">" en la cadena de texto
    # La variable "end" es el índice en el que se encuentra la etiqueta ">"
    # El segundo parámetro de la función find() es el índice desde el que se busca
    end = direccion.find(">", start)

    # Devuelve la cadena que está dentro de ambas etiquetas
    # La variable "direccion_limpia" es la cadena que se devuelve
    return direccion[start:end]


def main():
    """
    Función principal del script.
    
    Pide al usuario que introduzca su correo electrónico,
    luego recupera las direcciones de correo electrónico de la base de datos MongoDB,
    las limpia de etiquetas HTML y las inserta en la base de datos MongoDB.
    """
    # Pide al usuario que introduzca su correo electrónico
    # La variable "direccion" es la cadena que se introduce
    direccion = input("Introduce tu correo: ")

    # Recupera la lista de correos electrónicos ya recopilados
    # para la cuenta de correo especificada
    # La variable "correos_ya_recopilados" es la lista de correos electrónicos ya recopilados
    correos_ya_recopilados = listaDeCorreosYaRecopilados(direccion)

    # Recupera la lista de direcciones de correo electrónico
    # guardadas en la base de datos MongoDB
    # La variable "lista_direcciones" es la lista de direcciones de correo electrónico
    lista_direcciones = recuperarDaseDatosMongoDB(direccion)

    # Crea una lista para guardar las direcciones de correo electrónico
    # sin etiquetas HTML
    # La variable "lista_direcciones_limpia" es la lista vacía
    lista_direcciones_limpia = set()

    # Itera sobre la lista de direcciones de correo electrónico
    # y limpia cada dirección de correo electrónico
    # La variable "linea_a_limpiar" es la cadena con la dirección de correo electrónico limpia
    for i in lista_direcciones:
        linea_a_limpiar = limpiar_direccion(i)
        lista_direcciones_limpia.add(linea_a_limpiar)

    # Itera sobre la lista de direcciones de correo electrónico limpias
    # y verifica si cada dirección de correo electrónico ya ha sido recopilada
    # Si no ha sido recopilada, la agrega a la lista de correos electrónicos ya recopilados
    for correo in lista_direcciones_limpia:
        # print(correo)
        if correo not in correos_ya_recopilados:
            insertarDireccionCorreoMongoDB(correo, direccion)
            correos_ya_recopilados.append(correo)
            print(correo)

    # Imprime el número de correos electrónicos recopilados
    print("*" * 24)
    print("Recuperados: ", len(lista_direcciones_limpia), " correos.")
    print("*" * 24)

if __name__ == "__main__":
    main()
