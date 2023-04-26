# ==== Para ejecutar el servidor: python api.py y está en localhost:5000 ====

from flask import Flask, request, render_template
import requests
import mysql.connector


app = Flask(__name__)
comprobador_Usuario = False
comprobador_Producto = False
comprobador_Pedido = False
comprobador_OrderDetail = False

with open('info.txt', 'r') as f:
    password = f.read()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/tramita_pedido', methods=['POST'])
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

    mycursor.execute("SELECT MAX(ID) FROM Pedidos")
    myresult = mycursor.fetchall()
    for x in myresult:
        id_pedido = x[0] + 1

    val = (user_id, id_pedido, creation_date, status)

    mycursor.execute(sql, val)

    mydb.commit()

    comprobador_Pedido = True

    # Comprobar si los productos están en la BBDD

    mycursor.execute("SELECT * FROM Productos WHERE ID = %s", (product_id,))

    myresult = mycursor.fetchall()

    if len(myresult) == 0:
        return 'El producto no existe'
    else:
        sql = "INSERT INTO Productos (ID, Quantity, UnitPrice) VALUES (%s, %s, %s)"
        val = (product_id, quantity, unit_price)

        mycursor.execute(sql, val)

        mydb.commit()

        comprobador_Producto = True

    # Crea un nuevo OrderDetail en la tabla OrderDetails con los datos correspondientes.

    sql = "INSERT INTO OrderDetails (Order_ID, Product_ID, Quantity, UnitPrice) VALUES (%s, %s, %s, %s)"

    # El valor del ID del pedido es el mismo que el ID del pedido que se ha creado en la tabla Pedidos.
    mycursor.execute("SELECT MAX(ID) FROM Pedidos")

    myresult = mycursor.fetchall()

    for x in myresult:
        id_pedido = x[0]

    val = (id_pedido, product_id, quantity, unit_price)

    mycursor.execute(sql, val)

    mydb.commit()

    

@app.route('/nuevo_pedido', methods=['POST'])
def nuevo_pedido():

    order_id = request.json['Order_ID']
    status = request.json['Status']

    # Almacena los datos en la BBDD, en la tabla Cola_almacen

    mydb = mysql.connector.connect(
            host="localhost",
            username="root",
            password=password,
            database="gachia_gs",
            port="3306"
        )
    
    mycursor = mydb.cursor()

    sql = "INSERT INTO cola_almacen (Order_ID, Status) VALUES (%s, %s)"
    val = (order_id, status)

    mycursor.execute(sql, val)

    mydb.commit()

    return 'Nuevo pedido confirmado'


@app.route('/pedir_pedido', methods=['POST'])
def pedir_pedido():
    # Recibe los datos Order_ID y Status de cola_almacen, y el PickingStation_ID, date de picking_records
    picking_station_id = request.json['PickingStation_ID']
    
    # Utilizando el picking_station_id, obtengo order_id, status y date de picking_records, sabiendo que esa tabla tiene como atributos PickingRecord_ID, Picking_Statin_ID, Order_ID, Date y Status

    mydb = mysql.connector.connect(
            host="localhost",
            username="root",
            password=password,
            database="gachia_gs",
            port="3306"
        )
    
    mycursor = mydb.cursor()

    mycursor.execute("SELECT * FROM picking_records WHERE PickingStation_ID = %s", (picking_station_id,))
    myresult = mycursor.fetchall()

    for x in myresult:
        order_id = x[2]
        status = x[4]
    
    # Actualizo la tabla cola_almacen con los datos obtenidos de picking_records, sabiendo que la tabla cola_almacen tiene como atributos Queue_ID, Order_ID y Status

    mycursor.execute("SELECT * FROM cola_almacen WHERE Order_ID = %s", (order_id,))
    myresult = mycursor.fetchall()

    for x in myresult:
        queue_id = x[0]

    sql = "UPDATE cola_almacen SET Status = %s WHERE Queue_ID = %s"
    val = (status, queue_id)

    mycursor.execute(sql, val)

    mydb.commit()

    return 'Datos enviados a la cola del almacen'

@app.route('/envia_pedido', methods=['POST'])
def envia_pedido():

    # Coge el último pedido de la cola_almacen y lo envías a puesto_picking

    mycursor.execute("SELECT MAX(Order_ID) FROM cola_almacen")

    myresult = mycursor.fetchall()

    for x in myresult:
        order_id = x[0]



    # Obtenemos el PickingStation_ID

    mycursor.execute("SELECT MAX(PickingStation_ID) FROM Puesto_picking")

    myresult = mycursor.fetchall()

    for x in myresult:
        id_puestoPicking = x[0]

    # Asignamos ese pedido a un PickingRecord con el OrderID 

    mycursor.execute("SELECT * FROM pickingRecord WHERE Order_ID = %s", (order_id,))
    myresult = mycursor.fetchall()

    if len(myresult) != 0:
        return 'El pedido ya existe en la cola del puesto de picking'
    else:
        mycursor.execute("INSERT into PickingRecord VALUES (%s, %s)")
        val = (order_id, id_puestoPicking)

        mycursor.execute(sql, val)

        mydb.commit()

        # Actualizamos el status del pedido

        mycursor.execute("UPDATE Pedidos SET Status = 'En almacen' WHERE ID = %s", (order_id,))

        mydb.commit()



        return 'Pedido enviado al puesto de picking'
    
@app.route('/escanea_producto', methods=['POST'])
def escanea_producto():

    # Función que simule el que se estén escanando los pedidos en el puesto picking
    # correspondiente al último order que exista

    # Una vez termine, indicar que el pedido se ha completado

if __name__ == '__main__':
    app.run(debug=True)


