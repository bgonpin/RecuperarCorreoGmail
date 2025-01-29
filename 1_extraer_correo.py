import imaplib
import email
import email.header
from email.header import decode_header
import pymongo


def contarMensajesEnMongodb(username):
    """
    Cuenta el número de correos almacenados en la base de datos MongoDB
    para la cuenta de correo especificada

    :param username: La cuenta de correo de Gmail
    :type username: str
    :return: El número de correos almacenados en MongoDB
    :rtype: int
    """
    # Conectar a la base de datos MongoDB
    client = pymongo.MongoClient("mongodb://localhost:2018")

    # Seleccionar la base de datos "correos"
    db = client["correos"]

    # Seleccionar la colección que se indica en username en la base de datos "correos"
    # La coleccion toma el mismo nombre que la cuenta de correo de Gmail
    collection = db[username]

    # Devuelve el número de correos en la coleccion
    # El método estimated_document_count() devuelve una estimación de la cantidad de documentos en la colección
    # Esto es más rápido que contar todos los documentos manualmente
    return collection.estimated_document_count()

def insertarMongoDB(message, cuenta_correo):
    """
    Inserta un mensaje de correo en una base de datos MongoDB

    :param message: Un diccionario con los campos del mensaje de correo
    :type message: dict

    :param cuenta_correo: La cuenta de correo de Gmail que se va a insertar el mensaje
    :type cuenta_correo: str
    """
    # Conectar a la base de datos MongoDB
    # El string de conexión es "mongodb://localhost:2018"
    # El 2018 es el puerto en el que está escuchando el servidor MongoDB
    # Lo que se hace es crear una conexión a la base de datos MongoDB
    # y asignarla a una variable llamada "client"
    try:
        client = pymongo.MongoClient("mongodb://localhost:2018")

        # Seleccionar la base de datos "correos"
        # La base de datos se llama "correos"
        # La variable "db" es la base de datos seleccionada
        db = client["correos"]

        # Seleccionar la colección que se indica en cuenta_correo en la base de datos "correos"
        # La coleccion toma el mismo nombre que la cuenta de correo de Gmail
        # La variable "collection" es la colección seleccionada
        collection = db[cuenta_correo]

        # Insertar el mensaje en la colección
        # La variable "message" es el mensaje que se va a insertar
        # La función "insert_one" es la función que se utiliza para insertar el mensaje en la colección
        collection.insert_one(message)
    except Exception as e:
        # Imprimir cualquier error que suceda
        # La variable "e" es el error que se produce
        print(e)


def decode_mime_words(s):
    """
    Toma un string codificado en MIME y lo decodifica

    El string puede contener palabras codificadas en diferentes formatos
    como el formato "=?utf-8?q?Hola?= " que es un string que se codificó
    en UTF-8 y se codificó en quoted-printable

    :param s: El string codificado en MIME
    :type s: str
    :return: El string decodificado
    :rtype: str
    """
    # La función decode_header() devuelve una lista de tuplas
    # Donde cada tupla contiene una palabra codificada y su codificación
    # Por ejemplo, si el string es "=?utf-8?q?Hola?= "
    # La función devuelve [("Hola", "utf-8")]
    # La lista de tuplas se itera y se decodifica cada palabra
    # La palabra se decodifica como bytes y se convierte a string
    # Si la palabra no tiene codificación, se devuelve como string
    return "".join(
        word.decode(encoding or "utf8") if isinstance(word, bytes) else word
        for word, encoding in decode_header(s)
    )

def get_message_dict(email_message):
    """
    Toma un mensaje de correo electrónico y lo convierte en un diccionario
    que contiene los campos del mensaje, como el asunto, el remitente, el
    destinatario, la fecha y el cuerpo del mensaje

    :param email_message: El mensaje de correo electrónico a convertir
    :type email_message: email.message.Message
    :return: El diccionario con los campos del mensaje
    :rtype: dict
    """
    message_dict = {}

    # Extrae el asunto del mensaje
    message_dict["subject"] = decode_mime_words(email_message["subject"])

    # Extrae el remitente del mensaje
    message_dict["from"] = decode_mime_words(email_message["from"])

    # Extrae el destinatario del mensaje
    message_dict["to"] = decode_mime_words(email_message["to"])

    # Extrae la fecha del mensaje
    message_dict["date"] = email_message["date"]

    # Extrae el cuerpo del mensaje
    message_dict["body"] = {}

    # Verifica si el mensaje tiene partes (por ejemplo, texto plano y HTML)
    if email_message.is_multipart():
        # Itera sobre las partes del mensaje
        for part in email_message.walk():
            # Extrae el tipo de contenido de la parte
            content_type = part.get_content_type()

            # Verifica si la parte es un archivo adjunto
            content_disposition = str(part.get("Content-Disposition"))

            # Si la parte es texto plano y no es un archivo adjunto, extrae el texto
            if (
                content_type == "text/plain"
                and "attachment" not in content_disposition
            ):
                body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                message_dict["body"]["plain"] = body
            # Si la parte es HTML y no es un archivo adjunto, extrae el texto
            elif (
                content_type == "text/html"
                and "attachment" not in content_disposition
            ):
                body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                message_dict["body"]["html"] = body
            # Si la parte es un archivo adjunto, extrae el nombre del archivo
            elif "attachment" in content_disposition:
                filename = part.get_filename()
                if filename:
                    message_dict.setdefault("attachments", []).append(filename)
    else:
        # Si el mensaje no tiene partes, extrae el cuerpo del mensaje
        content_type = email_message.get_content_type()
        body = email_message.get_payload(decode=True).decode("utf-8", errors="ignore")
        message_dict["body"][content_type] = body

    return message_dict

def fetch_email_by_id(email_id, username, password):
    """
    Extrae el correo con el ID especificado de la cuenta de correo de Gmail

    :param email_id: El ID del correo que se va a extraer
    :type email_id: str
    :param username: La cuenta de correo de Gmail
    :type username: str
    :param password: La contraseña de la cuenta de correo de Gmail
    :type password: str
    :return: El correo extraido como un diccionario
    :rtype: dict
    """
    # Configura la conexión IMAP
    imap_server = "imap.gmail.com"
    imap_port = 993

    # Conéctate al servidor IMAP
    mail = imaplib.IMAP4_SSL(imap_server, imap_port)
    mail.login(username, password)
    mail.select("INBOX")

    # Busca el correo por ID
    # La función fetch() devuelve una tupla con dos elementos
    # El primer elemento es una cadena que indica el resultado de la búsqueda
    # El segundo elemento es una lista de tuplas que contiene los datos del correo
    # Cada tupla contiene el ID del correo y el contenido del correo
    # Itera sobre la lista de tuplas y extrae el contenido del correo
    # La variable "email_body" es el contenido del correo
    _, msg_data = mail.fetch(str(email_id), "(RFC822)")

    for response_part in msg_data:
        if isinstance(response_part, tuple):
            email_body = response_part[1]
            # Convierte el contenido del correo en un objeto Message
            # La función message_from_bytes() devuelve un objeto Message
            # El objeto Message contiene los campos del correo como atributos
            # Por ejemplo, el atributo "subject" contiene el asunto del correo
            email_message = email.message_from_bytes(email_body)
            # Extrae los campos del correo en un diccionario
            message_dict = get_message_dict(email_message)

    # Cierra la conexión
    mail.close()
    mail.logout()

    return message_dict


def get_email_ids(username, password):
    """
    Obtiene una lista de los IDs de correo de la cuenta de correo de Gmail

    :param username: La cuenta de correo de Gmail
    :type username: str
    :param password: La contraseña de la cuenta de correo de Gmail
    :type password: str
    :return: Una lista de los IDs de correo de la cuenta de correo
    :rtype: list[int]
    """
    # Configura la conexión IMAP
    # La variable "imap_server" es el servidor IMAP de Gmail
    # La variable "imap_port" es el puerto en el que se encuentra el servidor IMAP
    imap_server = "imap.gmail.com"
    imap_port = 993

    # Conéctate al servidor IMAP
    # La función login() se utiliza para conectarse al servidor IMAP
    # La función select() se utiliza para seleccionar la carpeta de correo que se va a examinar
    # En este caso, se selecciona la carpeta "INBOX"
    mail = imaplib.IMAP4_SSL(imap_server, imap_port)
    mail.login(username, password)
    mail.select("INBOX")

    # Obtén los IDs de correo
    # La función search() se utiliza para buscar correos en la carpeta seleccionada
    # El primer par metro es None, lo que indica que se va a buscar todos los correos
    # El segundo par metro es 'ALL', lo que indica que se va a buscar todos los correos
    # La función search() devuelve una tupla con dos elementos
    # El primer elemento es una cadena que indica el resultado de la búsqueda
    # El segundo elemento es una lista de tuplas que contiene los IDs de correo
    # Cada tupla contiene un ID de correo
    # Itera sobre la lista de tuplas y extrae los IDs de correo
    # La variable "email_ids" es una lista de los IDs de correo de la cuenta de correo
    _, msg_ids = mail.search(None, "ALL")

    # Extrae los IDs de correo de la lista de tuplas
    # La variable "email_ids" es una lista de los IDs de correo
    email_ids = [int(id.split()[0]) for id in msg_ids[0].split()]

    # Cierra la conexión
    # La función close() se utiliza para cerrar la conexión con el servidor IMAP
    # La función logout() se utiliza para desconectarse del servidor IMAP
    mail.close()
    mail.logout()

    return email_ids


def main():
    """
    Función principal del script.
    
    Solicita al usuario su correo y contraseña de Gmail,
    luego extrae los correos de Gmail y los inserta en una base de datos MongoDB.
    """
    username = input("Introduce tu correo: ")
    password = input("Introduce tu contraseña: ")

    # Recupera los IDs de correo y los contamos
    email_ids = get_email_ids(username, password)
    total_mensajes_en_servidor = len(email_ids)
    total_mensajes_en_mongodb = contarMensajesEnMongodb(username)

    # Si hay correos en el servidor que no est n en MongoDB, extraelos y los inserta
    if total_mensajes_en_mongodb < total_mensajes_en_servidor:
        # Extrae los correos y insertalos en MongoDB
        # Por cada correo, extrae los campos y los inserta en MongoDB
        # Extrae los correos que no est n en MongoDB y los inserta
        for i, email_id in enumerate(
            range(total_mensajes_en_mongodb, total_mensajes_en_servidor),
            total_mensajes_en_mongodb,
        ):
            try:
                # Extrae el correo por ID
                # La funci n fetch_email_by_id() extrae el correo por ID
                # y devuelve un diccionario con los campos del correo
                message_dict = fetch_email_by_id(email_id, username, password)
                # Agrega el ID como campo _id
                # Se agrega el ID del correo como campo "_id"
                # para que se pueda identificar el correo en MongoDB
                message_dict["_id"] = email_id
                # Inserta en MongoDB
                # La funci n insertarMongoDB() inserta el correo en MongoDB
                # y devuelve el resultado de la inserci n
                insertarMongoDB(message_dict, username)

            except Exception as e:
                # Imprime cualquier error que suceda
                # Si sucede un error al extraer o insertar el correo
                # se imprime el error para que se pueda depurar
                print(f"Error al extraer el correo {email_id}: {e}")

            # Imprime el progreso
            # Se imprime el progreso para que se pueda ver c mo va la extracci n
            # de correos
            print(f"Email {i+1}/{total_mensajes_en_servidor} extraido e insertado en MongoDB")

if __name__ == "__main__":
    main()
