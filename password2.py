#werkzeug
from werkzeug.security import generate_password_hash, check_password_hash

texto_contraseña = "x?1_p-M.4!eM"

texto_contraseña_encriptado = generate_password_hash(texto_contraseña)
print(f"Contraseña encriptada: {texto_contraseña_encriptado}")

print(f"Verificando la contraseña... {check_password_hash(texto_contraseña_encriptado, texto_contraseña)}")