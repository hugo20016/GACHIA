from flask import Flask,session,make_response
from flask import render_template
from flask import request, redirect, url_for
from flask_session import Session
from flask_mail import Mail,Message
import pymysql
import datetime
import psutil
import json
import os
import requests
#Importamos una libreria para hashear las contraseñas
import hashlib
#from pyqrcode import QRCode
from PIL import Image
import random
import qrcode



#El import de pillow es necesario 
from PIL import Image
#importamos secure_filename
from werkzeug.utils import secure_filename

	# Connect to the database

password = "tupdJCkdelmkUBn4bHGq"


from flask_wkhtmltopdf import Wkhtmltopdf

def get_machine_storage():
	hdd = psutil.disk_usage('/')
	used = (hdd.used / (2**30))
	total = (hdd.total / (2**30))
	used_percent = (used / total) * 100
	return int(used_percent)


def generar_qr(url,nombre):
    print("Genera qr")
    url = "https://" + url
    qr = qrcode.QRCode(
    	version=1,
    	error_correction=qrcode.constants.ERROR_CORRECT_L,
    	box_size=10,
    	border=4,
	)
    qr.add_data(url)
    qr.make(fit=True)

	# Crear una imagen SVG del código QR
    img = qr.make_image(fill_color="black", back_color="white")
    print("Salvo")
    img.save("/var/www/html/"+nombre)
    print("Sañvado")


pyconn = pymysql.connect(host='localhost',
							user='root',
							password='M@2de01ad4',
							database='Anarte',
							charset='utf8mb4',
							cursorclass=pymysql.cursors.DictCursor)

def ejecuta_query(sql, params=None):
	with pyconn.cursor() as cursor:
		try:
			cursor.execute(sql, params)
			pyconn.commit()  # confirmar los cambios
		except pymysql.Error as e:
			app.logger.info("Error SQL %d: %s" % (e.args[0], e.args[1]))
			return 255, None
		return 0, cursor


def ejecuta_query_all(sql):
			rc,cursor=ejecuta_query(sql)
			if rc==0:
				return cursor.fetchall()
			return None

def ejecuta_query_one(sql):
			rc,cursor=ejecuta_query(sql)
			if rc==0:
				return cursor.fetchone()
			return None


def eliminar_colaborador(id):
	sql = "DELETE FROM Colaboradores WHERE id = %s"
	params = (id,)
	rc, cursor = ejecuta_query(sql, params)
	if rc == 0:
		return True
	return False

use_celery = False
app = Flask(__name__,template_folder='/var/www/aplicacion/templates')
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['WKHTMLTOPDF_USE_CELERY'] =  False
app.config['WKHTMLTOPDF_BIN_PATH'] =  "/usr/bin/wkhtmltopdf"
app.config["PDF_DIR_PATH"] =  os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'pdf')
app.config["PDF_DIR_PATH"] =  "/tmp"


app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'parroquia.sjc.yt@gmail.com'
app.config['MAIL_PASSWORD'] = 'zwypopdippsvgdmr'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)


#Hacemos que los templates se actualicen sin tener que reiniciar el servidor
app.config['TEMPLATES_AUTO_RELOAD'] = True

wkhtmltopdf = Wkhtmltopdf(app)


Session(app)

@app.route("/manda_mail", methods=["POST", "GET"])
def manda_mail():
  app.logger.info("Entro en mail")
  nombre=request.form.get("name")
  email=request.form.get("email")
  Asunto=request.form.get("subject")
  Cuerpo=request.form.get("Mensaje")
  app.logger.info("Asunto: %s Cuerpo: %s" % (Asunto,Cuerpo))
  msg = Message(Asunto, sender ='parroquia.sjc.yt@gmail.com', recipients = ['aruizori@itelsys.com'])
  msg.html = render_template("cuerpo.html",nombre=nombre,email=email,Cuerpo=Cuerpo)
  mail.send(msg)
  return "Correo enviado", 200, {'ContentType':'text/html'} 


@app.route('/inicio')
def inicio():
	#Obtenemos los textos Desc_general, Desc_quienes, Desc_servicios de la tabla textos
	textos = ejecuta_query_all("SELECT * FROM Textos")
	for row in textos:
		if row['Tipo'] == 'general':
			Desc_general = row['Texto']
		elif row['Tipo'] == 'quienes':
			Desc_quienes = row['Texto']
		elif row['Tipo'] == 'servicios':
			Desc_servicios = row['Texto']

	colaboradores = ejecuta_query_all("SELECT * FROM Colaboradores")
	#Obtenemos las imagenes de la tabla Carrousel
	carrousel = ejecuta_query_all("SELECT Archivo,Titulo FROM Carrousel")

	#Recorremos carroosel para y a todos los elementos en el campo Titulo les quitamos la extension .*
	for row in carrousel:
		row['Titulo'] = row['Titulo'].split('.')[0]
		
	return render_template('/index.html',Desc_general=Desc_general,Desc_quienes=Desc_quienes,Desc_servicios=Desc_servicios,colaboradores=colaboradores,carrousel=carrousel)




def chk_sesion():
	app.logger.info("Entro en Check")
	if not session.get("usuario"):
		app.logger.info("redirect a login")
		return 1
	elif session.get("expires") < datetime.datetime.now():
		app.logger.info("redirect a login")
		return 1
	app.logger.info("Sesion"+ session.get("usuario"))
	return 0
#Esta funcion comprueba si el usuario es administrador si lo es devuelve 0 si no lo es devuelve 1

def chk_admin():
	if not session.get("usuario"):
		return 1
	elif session.get("expires") < datetime.datetime.now():
		return 1
	elif session.get("tipo") != "admin":
		return 1
	return 0

@app.route('/admin/login')
def login():
    return render_template('/admin/login.html',ERROR_MESSAGE="None")

@app.route('/admin/login_attempt', methods=['POST'])
def login_attempt():
	username = request.form['username']
	password = request.form['password']
	#Quitamos el fianl de linea
	username = username.rstrip()
	password = password.rstrip()
	

	current_time = datetime.datetime.now()
	try:
		remenber = request.form['remember']
	except:
		remenber = 'off'

	#Consulta a la base de datos para comprobar si el usuario y la contraseña son correctos
	if username.find("'") == -1 or password.find("'") == -1:
		print("Username: "+username+" Password: "+password+" -- Ejecutando consulta")
		respuesta = ejecuta_query_one("SELECT * FROM admin_users WHERE BINARY user = '"+username+"' AND BINARY password = '"+password+"'")
		


	if respuesta is None:
		return render_template('/admin/login.html',ERROR_MESSAGE="Block")
	else:
		if remenber == 'on':
				#Creamos una cookie con el nombre de usuario que caduque en 1 mes
				session["usuario"] = username
				session["clave"] = password
				#suma 1 mes a la fecha actual
				session["expires"] = current_time + datetime.timedelta(days=30)
		else:
				#Creamos una cookie con el nombre de usuario que caduque en 1 hora
				session["usuario"] = username
				session["clave"] = password
				#suma 1 hora a la fecha actual
				session["expires"] = current_time + datetime.timedelta(minutes=2)
		#Redirigiendo a la pagina de control
		#Añadimos a session el identificador de admin
		session["tipo"] = "admin"

		return redirect(url_for('control_panel',usuario=username))

@app.route('/admin/logout')
def logout():
	session.clear()
	return render_template('/admin/login.html',ERROR_MESSAGE="None")

@app.route('/admin/control_panel', methods=['GET'])
def control_panel():
	Usuario = session.get("usuario")
	if chk_sesion() == 1:
		return render_template('/admin/login.html',ERROR_MESSAGE="None")
	elif chk_admin() == 1:
		return render_template('/admin/login.html',ERROR_MESSAGE="None")
	else:

		#Obtenemos los datos de /home/admin/aplicacion/data.json Con el formato 
		# {
		#     "Memoria": 34,
		#     "Visistas_Mensuales": 316,
		#     "Contador_QR": 4,
		#     "visitas_plot_data": "316",
		#     "country_lables": "[ Spain ,  China ,  United States ]",
		#     "contry_datas": "[15, 8, 11]"
		# }

		json_file = open('/home/admin/aplicacion/data.json', 'r')
		json_data = json.load(json_file)

		used_percent = json_data['Memoria']
		visitas_mensuales = json_data['Visistas_Mensuales']
		Qr_contador = json_data['Contador_QR']
		visitas_meses_string = json_data['visitas_plot_data']
		country_labels = json_data['country_lables']
		country_data = json_data['contry_datas']

		json_file.close()


		return render_template('/admin/index.html',USUARIO=Usuario,DISK_USED=used_percent,VISITAS_MENSUALES= visitas_mensuales,QR_CONTADOR = Qr_contador,YEAR_DATA=visitas_meses_string, COUNTRY_LABELS=country_labels, COUNTRY_DATA=country_data)
        

######################################
# FUNCIONES DE MODIFICACION DE DATOS #
######################################


##### Carga de datos en la pagina de modificacion de datos
@app.route('/admin/modificar_contenido')
def modificar_contenido():
	Usuario = session.get("usuario")
	textos = ejecuta_query_all("SELECT * FROM Textos")
	for row in textos:
		if row['Tipo'] == 'general':
			Desc_general = row['Texto']
		elif row['Tipo'] == 'quienes':
			Desc_quienes = row['Texto']
		elif row['Tipo'] == 'servicios':
			Desc_servicios = row['Texto']
	colaboradores = ejecuta_query_all("SELECT * FROM Colaboradores")
	if chk_sesion() == 1:
		return render_template('/admin/login.html',ERROR_MESSAGE="None")
	elif chk_admin() == 1:
		return render_template('/admin/login.html',ERROR_MESSAGE="None")
	else:
		return render_template('/admin/modini.html',USUARIO=Usuario,Desc_general=Desc_general,Desc_quienes=Desc_quienes,Desc_servicios=Desc_servicios,colaboradores=colaboradores)
	

@app.route('/admin/download_inform')
def download_inform():
	Usuario = session.get("usuario")
	if chk_sesion() == 1:
		return render_template('/admin/login.html',ERROR_MESSAGE="None")
	elif chk_admin() == 1:
		return render_template('/admin/login.html',ERROR_MESSAGE="None")
	else:
		json_file = open('/home/admin/aplicacion/data.json', 'r')
		json_data = json.load(json_file)

		used_percent = json_data['Memoria']
		visitas_mensuales = json_data['Visistas_Mensuales']
		Qr_contador = json_data['Contador_QR']
		visitas_meses_string = json_data['visitas_plot_data']
		country_labels = json_data['country_lables']
		country_data = json_data['contry_datas']

		json_file.close()
		#Obtenemos la fehca en formato dd/mm/yyyy
		fecha = datetime.datetime.now().strftime("%d/%m/%Y")
		
	pdf = wkhtmltopdf.render_template_to_pdf(template_name_or_list='/admin/Informe_template.html',download=False,save=True,USUARIO=Usuario,FECHA=fecha,DISK_USED=used_percent,VISITAS_MENSUALES= visitas_mensuales,QR_CONTADOR = Qr_contador,YEAR_DATA=visitas_meses_string, COUNTRY_LABELS=country_labels, COUNTRY_DATA=country_data, \
			wkhtmltopdf_args="--debug-javascript  --javascript-delay 2000  --no-stop-slow-scripts")


	response = make_response(pdf)
	response.headers["Content-Type"] = "application/pdf"
	response.headers["Content-Disposition"] = "inline; filename=output.pdf"
	return response

@app.route('/admin/admin_qr')
def admin_qr():
	Usuario = session.get("usuario")
	if chk_sesion() == 1 :
		return render_template('/admin/login.html',ERROR_MESSAGE="None")
	elif chk_admin() == 1:
		return render_template('/admin/login.html',ERROR_MESSAGE="None")
	else:
		json_file = open('/home/admin/aplicacion/data.json', 'r')
		json_data = json.load(json_file)

		used_percent = json_data['Memoria']
		Qr_contador = json_data['Contador_QR']

		json_file.close()
	
	sql = "SELECT * FROM Pedidos"
	Archivos = ejecuta_query_all(sql)



	return render_template('/admin/admin_qrs.html',USUARIO=Usuario,DISK_USED=used_percent,QR_CONTADOR = Qr_contador,Archivos=Archivos)


##### Funcion para actualizar los datos de la pagina de inicio

@app.route('/admin/Eliminar_colaboradores', methods=['GET'])
def Eliminar_colaboradores():
	Usuario = session.get("usuario")
	if chk_sesion() == 1 :
		return render_template('/admin/login.html',ERROR_MESSAGE="None")
	elif chk_admin() == 1:
		return render_template('/admin/login.html',ERROR_MESSAGE="None")
	else:
		id = request.args.get('id')
		eliminar_colaborador(id)
		#redirigimos a /admin/modificar_contenido
		return redirect(url_for('modificar_contenido'))
	

@app.route('/admin/actualizar_colaborador', methods=['GET'])
def actualizar_colaborador():
    if chk_sesion() == 1 :
        return render_template('/admin/login.html',ERROR_MESSAGE="None")
    elif chk_admin() == 1:
        return render_template('/admin/login.html',ERROR_MESSAGE="None")
    else:
        id = request.args.get('id')
        nombre = request.args.get('nombre')
        link = request.args.get('link')
		# Verificar que se hayan proporcionado los valores necesarios
        if id and nombre and link:
            sql = "UPDATE Colaboradores SET nombre=%s, link=%s WHERE id=%s"
            params = (nombre, link, id)
            rc, cursor = ejecuta_query(sql, params)
			# Si se ha actualizado el registro, redirigimos a la página de inicio
        if rc == 0:
            return redirect(url_for('modificar_contenido'))
		# Si faltan valores, redirigimos a la página de error
        return render_template('admin/404.html'), 404

@app.route('/admin/agregar_colaborador', methods=['GET'])
def agregar_colaborador():
	if chk_sesion() == 1 :
		return render_template('/admin/login.html',ERROR_MESSAGE="None")
	elif chk_admin() == 1:
		return render_template('/admin/login.html',ERROR_MESSAGE="None")
	else:
		nombre = request.args.get('nombre')
		link = request.args.get('link')
		# Verificar que se hayan proporcionado los valores necesarios
		if nombre and link:
			sql = "INSERT INTO Colaboradores (Nombre, Link) VALUES (%s, %s)"
			params = (nombre, link)
			rc, cursor = ejecuta_query(sql, params)
			# Si se ha agregado el registro, redirigimos a la página de inicio
			if rc == 0:
				return redirect(url_for('modificar_contenido'))
		# Si faltan valores, redirigimos a la página de error
		return render_template('admin/404.html'), 404

@app.route('/admin/actualizar_desc', methods=['GET'])
def actualizar_desc():
	if chk_sesion() == 1 :
		return render_template('/admin/login.html',ERROR_MESSAGE="None")
	elif chk_admin() == 1:
		return render_template('/admin/login.html',ERROR_MESSAGE="None")
	else:
		index = request.args.get('index')
		desc = request.args.get('desc')
		if index and desc:
			sql = "UPDATE Textos SET Texto=%s WHERE id=%s"
			params = (desc, index)
			rc, cursor = ejecuta_query(sql, params)
			# Si se ha actualizado el registro, redirigimos a la página de inicio
			if rc == 0:
				return redirect(url_for('modificar_contenido'))
		# Si faltan valores, redirigimos a la página de error
		return render_template('admin/404.html'), 404


@app.route('/admin/upload_qr')
def archivos():
	if chk_sesion() == 1 :
		return render_template('/admin/login.html',ERROR_MESSAGE="None")
	elif chk_admin() == 1:
		return render_template('/admin/login.html',ERROR_MESSAGE="None")
	else:

		Productos = ejecuta_query_all("SELECT * FROM Productos")
		return render_template('/admin/archivos.html',Productos=Productos,USUARIO=session.get("usuario"))



#<form action="/be/admin/actualizar_img" method="post" enctype="multipart/form-data">
#Creacion de la ruta para actualizar la imagen de la pagina de inicio teniendo en cuenta que se tiene que subir un archivo
@app.route('/admin/actualizar_img', methods=['POST'])
def actualizar_img():
	if chk_sesion() == 1 :
		return render_template('/admin/login.html',ERROR_MESSAGE="None")
	elif chk_admin() == 1:
		return render_template('/admin/login.html',ERROR_MESSAGE="None")
	else:
		#Obtenemos el archivo que se ha subido
		file = request.files['Img_file']
		id = request.form['id']
		if file.filename == '':
			return "No se ha seleccionado ningun archivo"

		#Guardamos el archivo en la carpeta /var/www/html/assets/img/
		filename = secure_filename(file.filename)
		print(filename)
		file.save('/var/www/html/assets/img/' + secure_filename(file.filename))
		#return "Archivo subido correctamente"
		#Actualizamos la base de datos con el nombre del archivo que se ha subido
		# la tabla de la base de datos se llama Carrousel y tiene 3 campos, id, Titulo y Archivo
		# el campo Archivo es donde se guarda el nombre del archivo que se ha subido con el path /assets/img/ y el nombre del archivo
		sql = "UPDATE Carrousel SET Archivo=%s , Titulo=%s WHERE id=%s"
		params = ('/assets/img/' + filename, filename, id)
		rc, cursor = ejecuta_query(sql, params)

		return "Archivo subido correctamente"
	

@app.route('/admin/archivo_qr_individual', methods=['POST'])
def archivo_qr_individual():
#Obtenemos el id del archivo que se va a adminsitrar
	if chk_sesion() == 1 :
		return render_template('/admin/login.html',ERROR_MESSAGE="None")
	elif chk_admin() == 1:
		return render_template('/admin/login.html',ERROR_MESSAGE="None")
	else:
		#Obtenemos el id de archivo que recibimos por la url
		id = request.form['id']
		#Obtenemos el nombre del usuario de la sesion
		admin = session['usuario']
		
		sql = "SELECT Productos.Name, Productos.Description, Productos.Price, OrderDetails.Quantity FROM Productos INNER JOIN OrderDetails ON Productos.ID = OrderDetails.Product_ID INNER JOIN Pedidos ON OrderDetails.Order_ID = Pedidos.ID WHERE Pedidos.ID = "
		sql = sql + id
		Productos = ejecuta_query_all(sql)
				
		
		return render_template('/admin/admin_qrs_unico.html', ADMIN=admin, Productos=Productos, ID=id, NUM_PEDIDO = id)

		
@app.route('/admin/archivos_actualizar_permisos', methods=['POST'])
def archivos_actualizar_permisos():
	#Obtenemos los permisos que ya tenia el archivo
	sql ="SELECT * FROM permisos_usuarios WHERE id_archivo="
	sql = sql + request.form['id_archivo']
	Permisos = ejecuta_query_all(sql)
	Usuarios_Eliminar = []
	#El post que recbimos tiene el siguien formato id_archivo=1&13=on&15=on ...
	#El primer valor es el id del archivo y el resto son los id de todos los usuarios que tienen permiso para ese archivo
	#Recorremos todos los usuarios que tenian permiso y si no estan en el post, los eliminamos de la tabla de permisos
	for permiso in Permisos:
		#Recorremos todos los valores del post
		tiene_permiso = 0
		for key in request.form:
			if key == 'id_archivo':
				continue
			else:
				#Si el id del usuario esta en el post, no hacemos nada
				if permiso['id_usuario'] == int(key):
					tiene_permiso = 1
		#Si el usuario no esta en el post, lo eliminamos de la tabla de permisos
		if tiene_permiso == 0:
			Usuarios_Eliminar.append(permiso['id_usuario'])
		#Eliminamos los usuarios que no tienen permiso
	for usuario in Usuarios_Eliminar:
		sql = "DELETE FROM permisos_usuarios WHERE id_archivo=%s AND id_usuario=%s"
		params = (request.form['id_archivo'], usuario)
		rc, cursor = ejecuta_query(sql, params)
	#Recorremos todos los usuarios que estan en el post y si no estan en la tabla de permisos, los añadimos
	for key in request.form:
		if key == 'id_archivo':
			continue
		else:
			#Comprobamos si el usuario ya tiene permiso
			tiene_permiso = 0
			for permiso in Permisos:
				if permiso['id_usuario'] == int(key):
					tiene_permiso = 1
			#Si el usuario no tiene permiso, lo añadimos
			if tiene_permiso == 0:
				sql = "INSERT INTO permisos_usuarios (id_archivo,id_usuario) VALUES (%s,%s)"
				params = (request.form['id_archivo'], key)
				rc, cursor = ejecuta_query(sql, params)
	#Redirigimos a la pagina de administracion de archivos
	return redirect(url_for('admin_qr'))


@app.route('/admin/upload_files', methods=['POST'])
def upload_files():
	
	#Obtenemos el usuario recibido por el post
	usuario = request.form['usuario']
	agencia = request.form['agencia']
	envio = request.form['envio']
	status = 'Pedido Creado'
	dateActual = datetime.datetime.now()
	date = dateActual.strftime("%Y-%m-%d %H:%M:%S")


	#Recorremos todos los campos del post y generamos un array donde el primer campo es productoX y el segundo es cantidadX donde X es un numero
	#Esto lo hacemos para poder recorrerlo facilmente
	Productos = []
	for key in request.form:
		if key == 'usuario' or key == 'agencia' or key == 'envio':
			continue
		#Comrpobamos si el campo es un producto 
		if key.startswith('producto'):
			#Obtenemos el valor del producto
			producto = request.form[key]
			#Buscamos la cantidad del producto
			cantidad = request.form['cantidad' + key[8:]]
			#Añadimos el producto y la cantidad al array
			Productos.append([producto,cantidad])
		
	#Obtenemos de la tabla admin_users el id del usuario
	sql = "SELECT ID FROM admin_users WHERE user=" + usuario
	usuario = ejecuta_query_one(sql)

	sql = "INSERT INTO Pedidos (Agencia,CreationDate,Status,Tipo_envio,User_ID) VALUES (%s,%s,%s,%s,%s)"
	params = (agencia,date,status,envio,usuario)
	rc, cursor = ejecuta_query(sql, params)
	
	
	#Obtenemos el ID de pedidos mas alto
	sql = "SELECT MAX(ID) FROM Pedidos"
	id_pedido = ejecuta_query_one(sql)


	#Obtenemos el sql para obtener el unitprice de cada producto


	sql = "INSERT INTO OrderDetails (ID,Order_ID,Product_ID,Quantity,UnitPrice) VALUES (%s,%s,%s,%s,%s)"
	for producto in Productos:
		#El array producto tiene el siguiente formato [producto_id,cantidad]
		sql2 = "SELECT Price FROM Productos WHERE ID=" + producto[0]
		precio = ejecuta_query_one(sql2)
		precio = precio['Price']
		sql3 = "SELECT MAX(ID) FROM OrderDetails"
		id_ORD = ejecuta_query_one(sql3)
		id_ORD = id_ORD['MAX(ID)'] + 1
		id_ORD = str(id_ORD)

		params = (id_ORD,id_pedido['MAX(ID)'],producto[0],producto[1],precio)
		rc, cursor = ejecuta_query(sql, params)
		


	return redirect(url_for('admin_qr'))





###############################
# Seccion de rutas de usuario #
###############################

@app.route('/usuario')
def usuario():
	if chk_sesion() == 1:
		return render_template('/usuario/login.html',error="Sesión caducada",errorDisplay="Block" , success="",successDisplay="None")
	else:
		usuario = session.get("usuario")
		#Obtenemos de la base de datos el id del usuario sql = "SELECT email FROM usuarios WHERE BINARY user ='%s'" % Usuario
		sql = "SELECT id FROM usuarios WHERE BINARY user ='%s'" % usuario
		id_usuario = ejecuta_query_one(sql)
		#Obtenemos los archivos que tiene permiso el usuario
		sql = "SELECT id_archivo FROM permisos_usuarios WHERE id_usuario=%s" % id_usuario['id']
		archivos = ejecuta_query_all(sql)
		#Obtenemos los datos de todos los archivos que tiene permiso el usuario
		Archivos = []
		for archivo in archivos:
			sql = "SELECT * FROM Archivos WHERE id=%s" % archivo['id_archivo']
			archivo = ejecuta_query_one(sql)
			Archivos.append(archivo)
		

		return render_template('/usuario/usuario.html',USUARIO=usuario, archivos=Archivos)
		

@app.route('/usuario/perfil')
def perfil():
	if chk_sesion() == 1:
		return render_template('/usuario/login.html',error="Sesión caducada",errorDisplay="Block" , success="",successDisplay="None")
	else:
		Usuario = session.get("usuario")
		sql = "SELECT email FROM usuarios WHERE BINARY user ='%s'" % Usuario
		Email = ejecuta_query_one(sql)
		Email = Email['email']

		return render_template('/usuario/perfil.html',USUARIO=Usuario,EMAIL=Email)





@app.route('/ClubAnarte')
def ClubAnarte():
	return render_template('/usuario/login.html',error="",errorDisplay="None" , success="",successDisplay="None")
	

@app.route('/registrarse', methods=['POST'])
def registrarse():
	#Obtenemos los datos del formulario
	Usuario = request.form['usuario']
	Password = request.form['password']
	Email = request.form['email']

	#Limpiamos los datos de posibles ataques sql injection
	Usuario = Usuario.replace("'","")
	Email = Email.replace("'","")

	# Codificar la contraseña en bytes antes de hashearla
	Password_bytes = Password.encode('utf-8')
	hash_object = hashlib.sha256(Password_bytes)
	hex_dig = hash_object.hexdigest()
	Password = hex_dig
	

	#Verificamos que no exista el usuario
	#Para ello, hacemos una consulta a la base de datos
	sql = "SELECT * FROM usuarios WHERE user = %s or email = %s"
	params = (Usuario, Email)
	#Ejecutamos la consulta
	rc, cursor = ejecuta_query(sql, params)
	for row in cursor:
		#Si existe, devolvemos un error
		return render_template('/usuario/login.html',error="El usuario o el email ya existen",errorDisplay="block" , success="",successDisplay="None")
	
	sql = "INSERT INTO usuarios (user, password, email) VALUES (%s, %s, %s)"
	params = (Usuario, Password, Email)
	rc, cursor = ejecuta_query(sql, params)
	#Si se ha insertado correctamente, redirigimos a la pagina de login
	if rc == 0:
		return render_template('/usuario/login.html',error="",errorDisplay="None",success="Usuario registrado correctamente",successDisplay="block")
	else:
		return render_template('/usuario/login.html',error="Error al registrar el usuario",errorDisplay="block" , success="",successDisplay="None")



@app.route('/entrar', methods=['POST'])
def entrar():
	
	Usuario = request.form['usuario']
	Password = request.form['password']
	#Hash de la contraseña
	Password_bytes = Password.encode('utf-8')
	hash_object = hashlib.sha256(Password_bytes)
	hex_dig = hash_object.hexdigest()
	Password = hex_dig

	#Verificamos que el usuario exista
	#Para ello, hacemos una consulta a la base de datos
	sql = "SELECT * FROM usuarios WHERE BINARY user = %s and BINARY password = %s"
	params = (Usuario, Password)
	#Ejecutamos la consulta
	rc , cursor = ejecuta_query(sql, params)
	

	
	if cursor.rowcount == 0:
		return render_template('/usuario/login.html',error="El usuario o la contraseña son incorrectos",errorDisplay="block" , success="",successDisplay="None")
	else:
		current_time = datetime.datetime.now()
		session['usuario'] = Usuario
		session["expires"] = current_time + datetime.timedelta(days=90)
		#Añaadimos la etiqueta de usuario a la sesion
		session['tipo'] = "usuario"

		#Redirigimos a la pagina de usuario
		return redirect(url_for('usuario'))
		

#Añadimos la ruta para cualquier pagina que no exista
@app.errorhandler(404)
def page_not_found(e):
	return render_template('/admin/404.html')


'''

# ==== Login ====

# Nacho lo tiene

# ==== Pide stock ====

# @app.route('/Stock', methods=['GET'])
def Stock():
    #Obtenemos el ID del Get
    ID = request.args.get('ID')

    #Buscamos en la BBDD el Stock relacionado con el ID
    sql = "SELECT Stock FROM Productos WHERE ID = '%s'" % (ID)
    rc,cursor=ejecuta_query(sql)
    if rc != 0:
        return jsonify({"Error": "Error al buscar en la BBDD"}), 500
    else:
        #Creamos una lista para guardar los datos
        lista = []
        for row in cursor:
            lista.append(row)
        return jsonify(lista), 200
	
# ==== Pide stock (ver si hay stock) + envio stock ====

# Lo tiene hecho nacho

# ==== Tramita pedido ====

# @app.route('/tramita_pedido', methods=['POST'])
def enviar_datos():

    # Obtener los datos del formulario
    
    user_id = request.form['user_id']
    product_id = request.form['product_id']
    quantity = request.form['quantity']
    unit_price = request.form['unit_price']
    creation_date = request.form['creation_date']
    status = request.form['status']


    sql = "INSERT INTO Pedidos (User_ID, ID, CreationDate, Status) VALUES (%s, %s, %s, %s)"

    # El valor del ID del pedido se genera automáticamente en la BBDD, cogiendo el último valor y sumándole 1 a este.

    ejecutar_query("SELECT MAX(ID) FROM Pedidos")

    val = (user_id, id_pedido, creation_date, status)

    ejecutar_query(sql, val)

    

    comprobador_Pedido = True

    # Comprobar si los productos están en la BBDD COMPROBAR STOCK TODOS LOS 6.X

    ejecutar_query("SELECT * FROM Productos WHERE ID = %s", (product_id,))

    myresult = mycursor.fetchall()

    if len(myresult) == 0:
        return 'El producto no existe'
    else:
        sql = "INSERT INTO Productos (ID, Quantity, UnitPrice) VALUES (%s, %s, %s)"
        val = (product_id, quantity, unit_price)

        ejecutar_query(sql, val)

        

        comprobador_Producto = True

    # Crea un nuevo OrderDetail en la tabla OrderDetails con los datos correspondientes.

    sql = "INSERT INTO OrderDetails (Order_ID, Product_ID, Quantity, UnitPrice) VALUES (%s, %s, %s, %s)"

    # El valor del ID del pedido es el mismo que el ID del pedido que se ha creado en la tabla Pedidos.
    ejecutar_query("SELECT MAX(ID) FROM Pedidos")

    myresult = mycursor.fetchall()

    for x in myresult:
        id_pedido = x[0]

    val = (id_pedido, product_id, quantity, unit_price)

    ejecutar_query(sql, val)

    
# ==== Enviar Pedido a Picking y escanear productos ====

# @app.route('/pedir_pedido', methods=['POST'])
def pedir_pedido():
    # Recibe los datos Order_ID y Status de cola_almacen, y el PickingStation_ID, date de picking_records
    picking_station_id = request.json['PickingStation_ID']
    
    # Utilizando el picking_station_id, obtengo order_id, status y date de picking_records, sabiendo que esa tabla tiene como atributos PickingRecord_ID, Picking_Statin_ID, Order_ID, Date y Status

    

    ejecutar_query("SELECT * FROM picking_records WHERE PickingStation_ID = %s", (picking_station_id,))


    
    # Actualizo la tabla cola_almacen con los datos obtenidos de picking_records, sabiendo que la tabla cola_almacen tiene como atributos Queue_ID, Order_ID y Status

    ejecutar_query("SELECT * FROM cola_almacen WHERE Order_ID = %s", (order_id,))


    sql = "UPDATE cola_almacen SET Status = %s WHERE Queue_ID = %s"
    val = (status, queue_id)

    ejecutar_query(sql, val)

    

    return 'Datos enviados a la cola del almacen'

@app.route('/envia_pedido', methods=['POST'])
def envia_pedido():

    # Coge el último pedido de la cola_almacen y lo envías a puesto_picking

    ejecutar_query("SELECT MAX(Order_ID) FROM cola_almacen")

    myresult = mycursor.fetchall()



    # Obtenemos el PickingStation_ID

    ejecutar_query("SELECT MAX(PickingStation_ID) FROM Puesto_picking")

    myresult = mycursor.fetchall()

    for x in myresult:
        id_puestoPicking = x[0]

    # Asignamos ese pedido a un PickingRecord con el OrderID 

    ejecutar_query("SELECT * FROM pickingRecord WHERE Order_ID = %s", (order_id,))
    myresult = mycursor.fetchall()

    if len(myresult) != 0:
        return 'El pedido ya existe en la cola del puesto de picking'
    else:
        ejecutar_query("INSERT into PickingRecord VALUES (%s, %s)")
        val = (order_id, id_puestoPicking)

        ejecutar_query(sql, val)

        

        # Actualizamos el status del pedido

        ejecutar_query("UPDATE Pedidos SET Status = 'En almacen' WHERE ID = %s", (order_id,))

        



        return 'Pedido enviado al puesto de picking'
    
@app.route('/escanea_producto', methods=['POST'])
def escanea_producto():

    # Función que simule el que se estén escanando los pedidos en el puesto picking
    # correspondiente al último order que exista

    # Una vez termine, indicar que el pedido se ha terminado de preparar
    
# ==== Contactar con transportes ====

# # Modificar para que sea la que indique el parámetro "Transport" de la tabla pedidos

def obtener_informacion_envio(order_id):
    url_pedidos = "http://localhost:5000/pedidos"
    url_etiquetas = "http://localhost:5000/etiquetas_envio"
    headers = {'Content-Type': 'application/json'}

    # Una vez el pedido está terminado, esta función se llama

    # Obtenemos el ID del pedido, y dependiendo de las condiciones, se le asigna un tipo de envío u otro

    
    En el alcance incial se establecía como una de las salidas:
			 La aplicación generará una etiqueta de envío con ID PEDIDO, nombre y dirección.
			 La aplicación generará un albarán con referencias y cantidades reales enviadas.
			La necesidad de integrarse con empresas de transporte requiere una pequeña modificación en esta salida,
			tendrá que poder seleccionarse:
			 Tipo de envío: estándar o urgente.
			 Agencia de transporte: Correos, Seur o DHL.
		Esta información deberá reflejarse en la etiqueta de envío de la siguiente manera:
		 DHL
			o Día y hora de pedido.
			o Tipo de envío.
			o ID de pedido, nombre y dirección.
			o Listado de artículos reales a enviar.
		 SEUR
			o Día de entrega (estándar día de recogida +3, urgente día de recogida +1).
			o Tipo de envío
			o ID de pedido, nombre y dirección.
			o Peso total del pedido (se estima 200gr por cada unidad).
		 CORREOS
			o Día de pedido.
			o Tipo de envío.
			o ID de pedido, nombre y dirección.
			o Código postal de la entrega.
			o Peso total del pedido (se estima 200gr por cada unidad).
			o Cantidad en unidades total en la entrega.

    
    # Comprobar si la agencia es seur, dhl o correos y ver si se envía todo correctamente

    informacion_envio = {
        'Order_ID': pedido['Order_ID'],
        'User_ID': pedido['User_ID'],
        'CreationDate': pedido['CreationDate'],
        'Status': pedido['Status'],
        'RecipientName': etiquetas['RecipientName'],
        'RecipientPhone': etiquetas['RecipientPhone'],
        'AddressLine1': etiquetas['AddressLine1'],
        'AddressLine2': etiquetas['AddressLine2'],
        'City': etiquetas['City'],
        'State_Province': etiquetas['State_Province'],
        'PostalCode': etiquetas['PostalCode'],
        'Country': etiquetas['Country'],
        'Transport': etiquetas['Transport']
    }



    # Imprimir información de envío QR
    print(informacion_envio)

    # Notificar usuario y cambiar STATUS


'''