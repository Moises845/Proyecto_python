from flask import Flask, render_template, request, url_for, redirect, session, flash
from flask_mysqldb import MySQL
import os
import uuid
from werkzeug.utils import secure_filename

from passlib.hash import pbkdf2_sha256

app = Flask(__name__)
app.secret_key = 'appsecretkey'

mysql = MySQL()

# Conexion a la DB
app.config['MYSQL_HOST'] = 'bq4zq3fgw7bcblup6voc-mysql.services.clever-cloud.com'
app.config['MYSQL_PORT'] = 3306
app.config['MYSQL_USER'] = 'usuq5vcpx5moqqe3'
app.config['MYSQL_PASSWORD'] = 'fC5KKbZWB3r6L7Q7Z5Ws'
app.config['MYSQL_DB'] = 'bq4zq3fgw7bcblup6voc'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# Configuración para subir archivos
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2MB máximo

# Crear directorio de uploads si no existe
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

mysql.init_app(app)

# ----------------- FUNCIONES PARA CONTAR REGISTROS -----------------

def contar_usuarios():
    """Obtiene la cantidad total de usuarios"""
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT COUNT(*) as total FROM usuario")
        resultado = cur.fetchone()
        cur.close()
        return resultado['total'] if resultado else 0
    except Exception as e:
        print(f"Error al contar usuarios: {e}")
        return 0

def contar_productos():
    """Obtiene la cantidad total de productos"""
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT COUNT(*) as total FROM productos")
        resultado = cur.fetchone()
        cur.close()
        return resultado['total'] if resultado else 0
    except Exception as e:
        print(f"Error al contar productos: {e}")
        return 0

# ----------------- RUTAS PRINCIPALES -----------------

@app.route('/')
def inicio():
    return render_template('index.html')

@app.route('/accesologin', methods=['GET', 'POST']) 
def accesologin():
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM usuario WHERE email = %s", (email,))
        user = cursor.fetchone()

        if user and pbkdf2_sha256.verify(password, user['password']):
            session['logueado'] = True
            session['id'] = user['id']
            session['nombre'] = user['nombre']
            session['id_rol'] = user['id_rol']
            session['email'] = user['email']
            session['foto_perfil'] = user.get('foto_perfil', 'img/user.png')
            
            if user['id_rol'] == 1:
                flash('Bienvenido administrador', 'success')
                return redirect(url_for('admin'))
            elif user['id_rol'] == 2:
                return redirect(url_for('usuario'))
        else:
            flash('Usuario o contraseña incorrecta', 'danger')
            return render_template('login.html')
    else: 
        return render_template('login.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        email = request.form.get('email')
        password = pbkdf2_sha256.hash(request.form.get('password'))
        id_rol = 2

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO usuario (email, nombre, password, id_rol) VALUES (%s, %s, %s, %s)",
                    (email, nombre, password, id_rol))
        mysql.connection.commit()
        cur.close()

        flash('Registro exitoso. Ahora puedes iniciar sesión.', 'success')
        return redirect(url_for('login'))
    return render_template("Registro.html")

# ----------------- RUTAS DE USUARIOS -----------------

@app.route('/listar')
def listar(): 
    if 'logueado' in session and session.get('id_rol') == 1:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM usuario")
        usuarios = cur.fetchall()
        cur.close()
        return render_template("listar.html", usuarios=usuarios)
    else:
        flash("Acceso no autorizado", "error")
        return redirect(url_for('login'))

@app.route('/guardar', methods=['POST'])
def guardar():
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        password = pbkdf2_sha256.hash(request.form['password'])
        id_rol = 2
        
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO usuario (nombre, email, password, id_rol) VALUES (%s, %s, %s, %s)", 
                   (nombre, email, password, id_rol))
        mysql.connection.commit()
        cur.close()
        
        flash('Usuario agregado correctamente', 'success')
        return redirect(url_for('listar'))

@app.route('/updateUsuario', methods=['POST'])
def updateUsuario():
    if request.method == 'POST':
        id = request.form['id']
        nombre = request.form['nombre']
        email = request.form['email']
        password = pbkdf2_sha256.hash(request.form['password'])
        
        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE usuario 
            SET nombre = %s, email = %s, password = %s 
            WHERE id = %s
        """, (nombre, email, password, id))
        mysql.connection.commit()
        cur.close()
        
        flash('Usuario actualizado correctamente', 'success')
        return redirect(url_for('listar'))

@app.route('/borrarUser/<string:id>')
def borrarUser(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM usuario WHERE id = %s", (id,))
    mysql.connection.commit()
    cur.close()
    
    flash('Usuario eliminado correctamente', 'success')
    return redirect(url_for('listar'))

# ----------------- RUTAS DE PRODUCTOS -----------------

@app.route('/listar_productos_agregados', methods=['GET', 'POST'])
def listar_productos_agregados():
    if request.method == 'POST':
        nombre = request.form['nombre']
        precio = request.form['precio']
        descripcion = request.form['descripcion']
        
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO productos (Nombre, Precio, Descripcion) VALUES (%s, %s, %s)", 
                   (nombre, precio, descripcion))
        mysql.connection.commit()
        cur.close()
        
        flash('Producto agregado correctamente', 'success')
        return redirect(url_for('listar_productos'))
    
    return render_template("agregar_productos.html")

@app.route('/listar_productos')
def listar_productos():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM productos ORDER BY id DESC")
    productos = cur.fetchall()
    cur.close()
    return render_template("listar_productos.html", productos=productos)

@app.route('/editar_producto/<int:id>', methods=['POST'])
def editar_producto(id):
    if request.method == 'POST':
        nombre = request.form['nombre']
        precio = request.form['precio']
        descripcion = request.form['descripcion']
        
        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE productos 
            SET Nombre = %s, Precio = %s, Descripcion = %s 
            WHERE id = %s
        """, (nombre, precio, descripcion, id))
        mysql.connection.commit()
        cur.close()
        
        flash('Producto actualizado correctamente', 'success')
        return redirect(url_for('listar_productos'))

@app.route('/borrar_producto/<string:id>')
def borrar_producto(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM productos WHERE id = %s", (id,))
    mysql.connection.commit()
    cur.close()
    
    flash('Producto eliminado correctamente', 'success')
    return redirect(url_for('listar_productos'))

# ----------------- RUTAS DE PERFIL -----------------

@app.route('/perfil')
def perfil():
    if 'logueado' in session:
        # Obtener información actualizada del usuario
        cur = mysql.connection.cursor()
        cur.execute("SELECT nombre, email, foto_perfil FROM usuario WHERE id = %s", (session['id'],))
        user = cur.fetchone()
        cur.close()
        
        if user:
            session['nombre'] = user['nombre']
            session['email'] = user['email']
            session['foto_perfil'] = user['foto_perfil'] if user['foto_perfil'] else 'img/user.png'
        
        return render_template("perfil.html")
    else:
        flash("Debe iniciar sesión para ver el perfil", "error")
        return redirect(url_for('login'))

@app.route('/cambiar_foto_perfil', methods=['POST'])
def cambiar_foto_perfil():
    if 'logueado' in session:
        user_id = session['id']
        foto_path = None
        
        # Verificar si se subió un archivo
        if 'foto' in request.files and request.files['foto'].filename != '':
            file = request.files['foto']
            if file and allowed_file(file.filename):
                # Generar nombre único para el archivo
                filename = secure_filename(file.filename)
                unique_filename = f"{uuid.uuid4().hex}_{filename}"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(file_path)
                foto_path = f"uploads/{unique_filename}"
        
        # Verificar si se seleccionó una foto predefinida
        elif 'foto_predefinida' in request.form:
            foto_path = request.form['foto_predefinida']
        
        if foto_path:
            # Actualizar en la base de datos
            cur = mysql.connection.cursor()
            cur.execute("UPDATE usuario SET foto_perfil = %s WHERE id = %s", 
                       (foto_path, user_id))
            mysql.connection.commit()
            cur.close()
            
            # Actualizar sesión
            session['foto_perfil'] = foto_path
            flash('Foto de perfil actualizada correctamente', 'success')
        else:
            flash('No se seleccionó ninguna imagen', 'error')
        
        return redirect(url_for('perfil'))
    else:
        flash("Debe iniciar sesión", "error")
        return redirect(url_for('login'))

@app.route('/actualizar_perfil', methods=['POST'])
def actualizar_perfil():
    if 'logueado' in session:
        nombre = request.form['nombre']
        email = request.form['email']
        user_id = session['id']
        
        cur = mysql.connection.cursor()
        cur.execute("UPDATE usuario SET nombre = %s, email = %s WHERE id = %s", 
                   (nombre, email, user_id))
        mysql.connection.commit()
        cur.close()
        
        # Actualizar la sesión
        session['nombre'] = nombre
        session['email'] = email
        
        flash('Perfil actualizado correctamente', 'success')
        return redirect(url_for('perfil'))
    else:
        flash("Debe iniciar sesión", "error")
        return redirect(url_for('login'))

@app.route('/cambiar_password', methods=['POST'])
def cambiar_password():
    if 'logueado' in session:
        password_actual = request.form['password_actual']
        nueva_password = request.form['nueva_password']
        confirmar_password = request.form['confirmar_password']
        user_id = session['id']
        
        # Verificar contraseña actual
        cur = mysql.connection.cursor()
        cur.execute("SELECT password FROM usuario WHERE id = %s", (user_id,))
        user = cur.fetchone()
        
        if user and pbkdf2_sha256.verify(password_actual, user['password']):
            if nueva_password == confirmar_password:
                hashed_password = pbkdf2_sha256.hash(nueva_password)
                cur.execute("UPDATE usuario SET password = %s WHERE id = %s", 
                           (hashed_password, user_id))
                mysql.connection.commit()
                cur.close()
                flash('Contraseña cambiada correctamente', 'success')
            else:
                flash('Las contraseñas nuevas no coinciden', 'error')
        else:
            flash('Contraseña actual incorrecta', 'error')
        
        return redirect(url_for('perfil'))
    else:
        flash("Debe iniciar sesión", "error")
        return redirect(url_for('login'))

# ----------------- RUTAS EXISTENTES -----------------

@app.route('/logout')
def logout():
    session.clear()
    flash("Has cerrado sesión correctamente", "success")
    return redirect(url_for('login'))

@app.route('/contacto', methods=['GET', 'POST'])
def contacto():
    user = {
        'nombre': '',
        'email': '',
        'mensaje': '' 
    }
    
    if request.method == 'GET':
        user['nombre'] = request.args.get('nombre', '')
        user['email'] = request.args.get('email', '')
        user['mensaje'] = request.args.get('mensaje', '')
    return render_template("contacto.html", usuario=user)

@app.route('/contactopost', methods=['GET', 'POST'])
def contactopost():
    user = {
        'nombre': '',
        'email': '',
        'mensaje': ''
    }
    
    if request.method == 'POST':
        user['nombre'] = request.form.get('nombre', '')
        user['email'] = request.form.get('email', '')
        user['mensaje'] = request.form.get('mensaje', '')
    return render_template("contactopost.html", usuario=user)

@app.route('/login')
def login():
    return render_template("login.html")

@app.route('/admin')
def admin():
    if 'logueado' in session and session.get('id_rol') == 1:
        # Obtener las cantidades de usuarios y productos
        cantidad_usuarios = contar_usuarios()
        cantidad_productos = contar_productos()
        
        return render_template("admin.html", 
                             usuario=session['nombre'],
                             cantidad_usuarios=cantidad_usuarios,
                             cantidad_productos=cantidad_productos)
    else:
        flash("Acceso no autorizado", "error")
        return redirect(url_for('login'))

@app.route('/usuario')
def usuario():
    if 'logueado' in session:
        return render_template('usuario.html', usuario=session['nombre'])
    else:
        return redirect(url_for('login'))

@app.route('/acercade')
def acercade():
    return render_template("acercade.html")

if __name__ == '__main__':
    app.run(debug=True, port=8000)