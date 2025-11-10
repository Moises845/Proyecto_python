#cryptography

from cryptography.fernet import Fernet 

texto_contraseña = "x?1_p-M.4!eM"

# Generar una clave y crear un objeto Fernet
clave = Fernet.generate_key()
objeto = Fernet(clave)
# Encriptar la contraseña
texto_contraseña_encriptado = objeto.encrypt(texto_contraseña.encode())
print(f"Contraseña encriptada: {texto_contraseña_encriptado}")

# Desencriptar la contraseña
texto_desencriptado = objeto.decrypt(texto_contraseña_encriptado).decode()
print(f"Contraseña desencriptada: {texto_desencriptado}")