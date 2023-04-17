# ==== Para ejecutar el servidor: python api.py y está en localhost:5000 ====

from flask import Flask, request, render_template
import requests
app = Flask(__name__)


@app.route('/hola')
def hola():
    return '¡Hola, mundo!'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/enviar_datos', methods=['POST'])
def enviar_datos():
    # Obtener los datos del formulario
    user_id = request.form['user_id']
    product_id = request.form['product_id']
    quantity = request.form['quantity']
    unit_price = request.form['unit_price']
    creation_date = request.form['creation_date']
    status = request.form['status']

    # Enviar los datos a la BBDD

    
    import mysql.connector

    mydb = mysql.connector.connect(
            host="gachia-db.cqhzxnm4nr1w.eu-west-1.rds.amazonaws.com",
            username="admin",
            password="gachiaproyecto23",
            database="gachia-db",
            port="3306"
        )
        
    mycursor = mydb.cursor()

    # Comprobar que el User_ID existe en la tabla Usuarios

    mycursor.execute("SELECT * FROM Usuarios WHERE ID = %s", (user_id,))
    myresult = mycursor.fetchall()

    if len(myresult) == 0:
        return 'El usuario no existe'
    else:
        sql = "INSERT INTO Usuarios (ID, Product_ID, Quantity, UnitPrice) VALUES (%s, %s, %s, %s)"
        val = (user_id, product_id, quantity, unit_price)

        mycursor.execute(sql, val)

        mydb.commit()

    # Comprobar que el Product_ID no existe en la tabla Pedidos

    mycursor.execute("SELECT * FROM Pedidos WHERE Product_ID = %s", (product_id,))

    myresult = mycursor.fetchall()

    if len(myresult) != 0:
        return 'El producto ya existe'
    else:
        sql = "INSERT INTO Pedidos (ID, User_ID, CreationDate, Product_ID, Status) VALUES (%s, %s, %s, %s, %s)"
        val = (product_id, user_id, creation_date, product_id, status)

        mycursor.execute(sql, val)

        mydb.commit()
    
    



    # Devolver una respuesta al cliente
    return 'Datos recibidos'
if __name__ == '__main__':
    app.run(debug=True)


