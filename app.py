from flask import Flask, request, jsonify, render_template, url_for

app = Flask(__name__)

@app.route('/') #Decorador para la ruta principal
def index():
    return render_template('index.html')

@app.route('/Registro')
def Registro():
    return render_template("Registro.html")

@app.route('/acercade')
def acercade():
    return render_template('acercade.html')

@app.route('/login')
def login():
    return render_template("login.html")

@app.route('/usuario')
def usuario():
    return render_template("usuario.html")

@app.route('/servicios/<nombre>')
def servicios(nombre): # Funcion para la ruta de servicios
    return f'El nombre del servicio es: %s' % nombre

@app.route('/edad/<edad>')
def edad(edad):
    return 'La edad es de: {} años'.format(edad)

@app.route('/suma/<int:num1>/<int:num2>')
def suma(num1, num2):
    resultado = num1 + num2
    return 'La suma de {} y {} es: {}'.format(num1, num2, resultado)

@app.route('/edadvalor/<int:edad>')   # Ruta con parámetro entero
def edadvalor(edad):
    if edad < 18:
        return 'Eres menor de edad'
    elif edad >= 18 and edad < 65:
        return 'Eres mayor de edad tienes {} años'.format(edad)
    else:
        return 'Eres un adulto mayor, tienes {} años'.format(edad)


if __name__ == '__main__':
    app.run(debug=True, port=8000) #ejecuta la aplicacion en modo de depuracion
