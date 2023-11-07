from flask import Flask 
from flask import render_template, redirect, request, Response, session, url_for, session
from flask_mysqldb import MySQL, MySQLdb

app = Flask(__name__, template_folder="template")

app.config["MYSQL_HGOST"]="localhost"
app.config["MYSQL_USER"]="root"
app.config["MYSQL_PASSWORD"]=""
app.config["MYSQL_DB"]="ventamu"
app.config["MYSQL_CURSORCLASS"]="DictCursor"
mysql=MySQL(app)




@app.route("/")
def home ():
    return render_template("index.html")

@app.route("/")
def admin ():
    return render_template("admin.html")


# Función para iniciar sesión de usuario
@app.route("/acceso-login", methods=[ "POST"])
def login():
    if request.method == "POST" and "txtCorreo" in request.form and "txtPassword" in request.form:
        _correo = request.form["txtCorreo"]
        _password = request.form["txtPassword"]

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM usuarios WHERE correo = %s AND password = %s", (_correo, _password))
        account = cur.fetchone()

        if account:
            session["logged"] = True
            session["id"] = account["id"]
            session["correo"] = account["correo"]
            return redirect('/vista_productos')
        else:
            return render_template("index.html")
        
# Función para cerrar sesión
@app.route('/logout')
def logout():
    session.pop('logged', None)
    session.pop('id', None)
    session.pop("correo", None)
    return redirect('/')

        
#funcion de registro
@app.route("/registro")
def registro():
    return render_template("registro.html")

@app.route("/crear-registro", methods= ["GET", "POST"])
def crear_registro():
    
    correo=request.form["txtCorreo"]
    password=request.form["txtPassword"]
    
    cur = mysql.connection.cursor()
    cur.execute(" INSERT INTO usuarios (correo, password) VALUES (%s, %s)",(correo,password))
    mysql.connection.commit()
    
    return render_template("index.html")

#Ruta para ventas
@app.route('/ventas', methods=['GET', 'POST'])
def ventas():
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM pj_venta WHERE usuario=%s", (session["correo"],))
        data = cur.fetchall()
        cur.close()
        return render_template('ventas.html', data=data)
    elif request.method == 'POST':
        detalles_venta = request.form
        nombre_pj = detalles_venta['nombre_pj']
        tipo_pj = detalles_venta["tipo_pj"]
        fuerza = detalles_venta['fuerza']
        agilidad = detalles_venta['agilidad']
        constitucion = detalles_venta['constitucion']
        energia = detalles_venta['energia']
        comando = detalles_venta["comando"]
        precio = detalles_venta["precio"]
        descripcion = detalles_venta["descripcion"]
        usuario = session["correo"]
        print(session["correo"])

        # Manejar la carga de la imagen
        imagen = request.files['imagen']
        # Asegúrate de guardar la imagen en la ubicación deseada
        # Aquí, puedes usar una biblioteca como Pillow para procesar la imagen si es necesario
        
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO pj_venta (nombre_pj,tipo_pj, fuerza, agilidad, constitucion, energia, comando, precio, descripcion, imagen, usuario) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s)",
                    (nombre_pj,tipo_pj, fuerza, agilidad, constitucion, energia, comando, precio, descripcion, imagen.filename, usuario))
        mysql.connection.commit()
        cur.close()
        return redirect('/productos')

    
 #Ruta para mostrar la lista de productos
@app.route('/productos', methods=['GET'])
def mostrar_productos():
    if "logged" in session and session["logged"]:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM pj_venta WHERE usuario=%s", (session["correo"],))
        articles = cur.fetchall()
        cur.close()
        return render_template('productos.html', articles=articles) 
    else:
        return redirect("/")

#Ruta para eliminar
@app.route('/productos/eliminar/<int:id>', methods=['POST'])
def eliminar_venta(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM pj_venta WHERE id=%s", (id,))
    mysql.connection.commit()
    cur.close()
    return redirect('/productos')

#Ruta editar
@app.route('/editar_ventas/<int:id>', methods=['GET', 'POST'])
def editar_articulo(id):
    print(id)
    cursor = mysql.connection.cursor()
    if request.method == 'POST':        
        nombre_pj = request.form['nombre_pj']
        tipo_pj = request.form['tipo_pj']      
        fuerza = request.form['fuerza']
        agilidad = request.form['agilidad']
        constitucion = request.form['constitucion']
        energia = request.form['energia']
        comando = request.form['comando']
        descripcion = request.form['descripcion']
        precio = request.form['precio']
        imagen = request.form['imagen']
        cursor.execute("""
            UPDATE pj_venta
            SET nombre_pj = %s,tipo_pj = %s, fuerza = %s, agilidad = %s, constitucion = %s, energia = %s, comando = %s, descripcion = %s, precio = %s, imagen = %s
            WHERE id = %s
        """, (nombre_pj, tipo_pj, fuerza, agilidad, constitucion, energia, comando, descripcion, precio, imagen, id))
        mysql.connection.commit()
        return redirect('/productos') 
    cursor.execute('SELECT * FROM pj_venta WHERE id = %s', (id,))
    article = cursor.fetchone()
    return render_template('editar_ventas.html', article=article)

#ruta para ver los productos a vender
# Ruta para mostrar la lista de productos
# Ruta para mostrar la lista de productos
@app.route('/vista_productos', methods=['GET'])
def mostrar_productos_a():
    if "logged" in session and session["logged"]:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM pj_venta")
        productos = cur.fetchall()
        cur.close()
        imagenes_predeterminadas = {
            "Blade King": r"C:/Users/Usuario\Desktop\proyecto\demo\static\logo.jpg",
            "Soul Master": r"C:\Users\Usuario\Desktop\proyecto\demo\imagenes\logo.jpg",
            "Muse Elf": r"C:\Users\Usuario\Desktop\proyecto\demo\imagenes\logo.jpg",
            "Magic Gladiator": r"C:\Users\Usuario\Desktop\proyecto\demo\imagenes\logo.jpg",
            "Dark Lord": r"C:\Users\Usuario\Desktop\proyecto\demo\imagenes\logo.jpg",
        }
        return render_template('vista_productos.html', productos=productos, imagenes_predeterminadas=imagenes_predeterminadas)
    else:
        return redirect("/")
 #Ruta para ver los detalles de una venta específica
@app.route('/comprar/<int:id>', methods=['GET'])
def detalle_venta(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM pj_venta WHERE id=%s", (id,))
    venta = cur.fetchone()
    cur.close()
    return render_template('comprar.html', venta=venta)


if __name__ == "__main__":
    app.secret_key="123456"
    app.run(debug=True,host="0.0.0.0", port=5000, threaded=True)
    