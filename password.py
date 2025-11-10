#flask-bcrypt
from flask import Flask, request, jsonify
from flask_bcrypt import Bcrypt

inicio = Flask(__name__)
bcrypt = Bcrypt(inicio)

password_plano = "secure_password_123"
hashed_password = bcrypt.generate_password_hash(password_plano).decode('utf-8')
print(f"Contraseña encriptada: {hashed_password}")

# Para verificar la contraseña
contraseña_interna = "secure_password_123"
contraseña_interna = bcrypt.check_password_hash(hashed_password, contraseña_interna)
print(f"¿La contraseña es válida? {contraseña_interna}")