from flask import Flask 
from flask import render_template, redirect, request, Response, session
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

#funcion del loguin
@app.route("/acceso-login", methods= ["GET","POST"])
def login ():
    
    if request.method == "POST" and "txtCorreo" in request.form and "txtPassword":
        _correo = request.form ["txtCorreo"]
        _password = request.form ["txtPassword"]
        
        cur=mysql.connect.cursor()
        cur.execute("SELECT * FROM usuarios WHERE correo = %s AND PASSWORD = %s",(_correo,_password))
        account = cur.fetchone()
        
        if account:
            session["Looguedo"] = True
            session["id"] = account["id"]
            
            return render_template("admin.html")
        else: 
    
            return render_template("index.html")
        
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

# Ruta para la sección de ventas
@app.route('/ventas', methods=['GET', 'POST'])
def ventas():
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM pj_venta")
        data = cur.fetchall()
        cur.close()
        return render_template('ventas.html', data=data)
    elif request.method == 'POST':
        detalles_venta = request.form
        nombre_pj = detalles_venta['nombre_pj']
        fuerza = detalles_venta['fuerza']
        agilidad = detalles_venta['agilidad']
        constitucion = detalles_venta['constitucion']
        energia = detalles_venta['energia']
        comando = detalles_venta["comando"]
        precio = detalles_venta["precio"]

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO pj_venta (nombre_pj, fuerza, agilidad, constitucion, energia, comando, precio) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    (nombre_pj, fuerza, agilidad, constitucion, energia, comando, precio))
        mysql.connection.commit()
        cur.close()
        return redirect('/productos')
    
 #Ruta para mostrar la lista de productos
@app.route('/productos', methods=['GET'])
def mostrar_productos():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM pj_venta")
    articles = cur.fetchall()
    cur.close()
    return render_template('productos.html', articles=articles) 

#Ruta para eliminar
@app.route('/productos/eliminar/<int:id>', methods=['POST'])
def eliminar_venta(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM pj_venta WHERE id=%s", (id,))
    mysql.connection.commit()
    cur.close()
    return redirect('/productos')




if __name__ == "__main__":
    app.secret_key="123456"
    app.run(debug=True,host="0.0.0.0", port=5000, threaded=True)
    