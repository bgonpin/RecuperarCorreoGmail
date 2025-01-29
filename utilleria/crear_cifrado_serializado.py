from cryptography.fernet import Fernet
key = ""
clave_cifrado = ""

def generate_key() -> bytes:
    """
    Genera una clave que se utilizará para cifrar y descifrar mensajes.
    La clave se almacena en un archivo llamado "key.key" en la ruta "/mnt/local/datos/keys/".
    La clave se genera con el método Fernet.generate_key() y luego se escribe en el archivo.
    """
    key = Fernet.generate_key()  # Generate a key with the Fernet.generate_key() method
    with open(
        "/mnt/local/datos/keys/key.key", "wb"
    ) as key_file:  # Open the file in write binary mode
        key_file.write(key)  # Write the key to the file
    return key  # Return the key

def encrypt_message(message: str, key: bytes) -> bytes:
    """
    Encripta un mensaje dado con una clave dada.

    :param message: El mensaje a encriptar
    :type message: str
    :param key: La clave a usar para la encriptación
    :type key: bytes
    :return: El mensaje encriptado
    :rtype: bytes
    """
    # Crea un objeto Fernet con la clave dada
    # La clase Fernet es una biblioteca de criptografía simple que usa AES-128 en modo CBC y relleno PKCS7
    # para encriptar y desencriptar mensajes. El constructor toma una clave como parámetro.
    f = Fernet(key)

    # Encripta el mensaje
    # El método encrypt() del objeto Fernet toma un objeto bytes como parámetro y
    # devuelve el mensaje encriptado como un objeto bytes.
    # El mensaje debe codificarse primero como bytes con el método encode().
    encrypted_message = f.encrypt(message.encode())

    # Devuelve el mensaje encriptado
    return encrypted_message

def decrypt_message(ciphered_text: bytes, key: bytes) -> str:
    """
    Descifra un texto cifrado dado con una clave dada.
    
    Parámetros:
    ciphered_text (bytes): El texto cifrado a descifrar
    key (bytes): La clave a usar para el descifrado
    
    Devuelve:
    str: El mensaje descifrado
    """
    # Crea un objeto Fernet con la clave dada
    # La clase Fernet es una biblioteca de criptografía simple que usa AES-128 en modo CBC y relleno PKCS7
    # para encriptar y desencriptar mensajes. El constructor toma una clave como parámetro.
    f = Fernet(key)

    # Desencripta el texto cifrado
    # El método decrypt() del objeto Fernet toma un objeto bytes como parámetro y
    # devuelve el mensaje desencriptado como un objeto bytes.
    decrypted_message = f.decrypt(ciphered_text)

    # Decodifica el mensaje desencriptado
    # El mensaje desencriptado es un objeto bytes y necesita ser decodificado a una cadena
    # con el método decode().
    decrypted_message = decrypted_message.decode()

    # Devuelve el mensaje desencriptado
    return decrypted_message

# Generate a key
'''
key = generate_key()
print("Key:", key)

'''
def recuperarClave():
    """
    Esta función lee la clave de cifrado de un archivo.
    
    La clave se almacena en un archivo llamado "key.key" en el directorio "/mnt/local/datos/keys/".
    El archivo se abre en modo de lectura binaria ("rb") y la clave se lee del archivo.
    La clave se almacena en la variable "key" y se devuelve desde la función.
    """
    # Abre el archivo en modo de lectura binaria
    with open("/mnt/local/datos/keys/key.key", "rb") as key_file:
        # Lee la clave del archivo
        key = key_file.read()

    # Devuelve la clave
    return key

message = "hola mundo"
clave_cifrado = recuperarClave()

mensaje_encriptado = encrypt_message(message, clave_cifrado)

print(mensaje_encriptado)

mensaje_desencriptado = decrypt_message(mensaje_encriptado, clave_cifrado)

print(mensaje_desencriptado)
