import flask
from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash, send_file, send_from_directory, safe_join, abort
#Importamos lo necesario para pyconn
import pymysql
import datetime

#Creamos la conexión a la BBDD

pyconn = pymysql.connect(host='localhost',
							user='root',
							password='la contraseña de la bbdd',
							database='labbdd',
							charset='utf8mb4',
							cursorclass=pymysql.cursors.DictCursor)

def ejecuta_query(sql):
    with pyconn.cursor() as cursor:
        try:
            cursor.execute(sql)
            pyconn.commit()
            return 0,cursor
        except:
            pyconn.rollback()
            return 1,cursor
    


@app.route('/Pedidos', methods=['GET'])
def Pedidos():
    #Obtenemos el ID, User_ID, CreationDate, Status del Get
    ID = request.args.get('ID')
    User_ID = request.args.get('User_ID')
    CreationDate = request.args.get('CreationDate')
    Status = request.args.get('Status')
    
    #Y lo cargamos en la BBDD
    sql = "INSERT INTO Pedidos (ID, User_ID, CreationDate, Status) VALUES ('%s', '%s', '%s', '%s')" % (ID, User_ID, CreationDate, Status)
    rc,cursor=ejecuta_query(sql)
    if rc != 0:
        return jsonify({"Error": "Error al insertar en la BBDD"}), 500
    else:
        return jsonify({"Mensaje": "Insertado correctamente"}), 200
    




 #Transacciones_stock devolvemos (Product_ID, Supplier_ID, Date, Quantity, Type)
@app.route('/Productos', methods=['GET'])
def Productos():
    #Obtenemos el Product_ID del Get
    Product_ID = request.args.get('Product_ID')

    #Buscamos en la BBDD el Spuplier_ID, Date, Quantity, Type relacionado con el Product_ID
    sql = "SELECT Supplier_ID, Date, Quantity, Type FROM Transacciones_stock WHERE Product_ID = '%s'" % (Product_ID)
    rc,cursor=ejecuta_query(sql)
    if rc != 0:
        return jsonify({"Error": "Error al buscar en la BBDD"}), 500
    else:
        #Creamos una lista para guardar los datos
        lista = []
        for row in cursor:
            lista.append(row)
        return jsonify(lista), 200
    



#Proveedores, Transacciones_stock(Supplier_ID, Product_ID, Date, Quantity, Type)
@app.route('/Proveedores', methods=['GET'])
def Proveedores():
    #Obtenemos el Supplier_ID del Get
    Supplier_ID = request.args.get('Supplier_ID')

    #Buscamos en la BBDD el Product_ID, Date, Quantity, Type relacionado con el Supplier_ID
    sql = "SELECT Product_ID, Date, Quantity, Type FROM Transacciones_stock WHERE Supplier_ID = '%s'" % (Supplier_ID)
    
    rc,cursor=ejecuta_query(sql)
    if rc != 0:
        return jsonify({"Error": "Error al buscar en la BBDD"}), 500
    else:
        #Creamos una lista para guardar los datos
        lista = []
        for row in cursor:
            lista.append(row)
        return jsonify(lista), 200
    





#Usuarios Recibimos por post(Name,FirstName,LastName,Email,Password,Address)
@app.route('/Registrar', methods=['POST'])
def Registrar():
    #Obtenemos los datos del post
    Name = request.form.get('Name')
    FirstName = request.form.get('FirstName')
    LastName = request.form.get('LastName')
    Email = request.form.get('Email')
    Password = request.form.get('Password')
    Address = request.form.get('Address')

    #Comprobamos que no exista el usuario
    sql = "SELECT * FROM Usuarios WHERE Email = '%s'" % (Email)
    rc,cursor=ejecuta_query(sql)
    if rc != 0:
        return jsonify({"Error": "Error al buscar en la BBDD"}), 500
    else:
        #Si no existe, lo insertamos
        if cursor.rowcount == 0:
            sql = "INSERT INTO Usuarios (Name, FirstName, LastName, Email, Password, Address) VALUES ('%s', '%s', '%s', '%s', '%s', '%s')" % (Name, FirstName, LastName, Email, Password, Address)
            rc,cursor=ejecuta_query(sql)
            if rc != 0:
                return jsonify({"Error": "Error al insertar en la BBDD"}), 500
            else:
                return jsonify({"Mensaje": "Insertado correctamente"}), 200
        else:
            return jsonify({"Error": "El usuario ya existe"}), 500
        

#Autenticacion Recibimos post (Email, Password)
@app.route('/Autenticacion', methods=['POST'])
def Autenticacion():
    #Obtenemos los datos del post
    Email = request.form.get('Email')
    Password = request.form.get('Password')

    #Buscamos en la BBDD el usuario
    sql = "SELECT * FROM Usuarios WHERE Email = '%s'" % (Email)
    rc,cursor=ejecuta_query(sql)
    if rc != 0:
        return jsonify({"Error": "Error al buscar en la BBDD"}), 500
    else:
        #Si existe, comprobamos la contraseña
        if cursor.rowcount == 1:
            for row in cursor:
                if row['Password'] == Password:
                    return jsonify({"Mensaje": "Autenticado correctamente"}), 200
                else:
                    return jsonify({"Error": "Contraseña incorrecta"}), 500
        else:
            return jsonify({"Error": "El usuario no existe"}), 500
        
#Stock recibimos (ID) por get y devolvemos stock de la bbdd
@app.route('/Stock', methods=['GET'])
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