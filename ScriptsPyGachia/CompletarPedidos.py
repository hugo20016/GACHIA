import mysql.connector
import requests

def marcar_pedido_completado(order_id):
# Conectar a la base de datos
mydb = mysql.connector.connect(
host="gachia-db.cqhzxnm4nr1w.eu-west-1.rds.amazonaws.com",
username="admin",
password="gachiaproyecto23",
database="gachia-db",
port="3306"
)
mycursor = mydb.cursor()

makefile
Copy code
# Actualizar el estado del pedido a "completado"
sql = "UPDATE Pedidos SET Status = 'completado' WHERE Order_ID = %s"
val = (order_id,)
mycursor.execute(sql, val)
mydb.commit()

# Actualizar el estado del registro de picking correspondiente
sql = "UPDATE PickingRecords SET Status = 'completado' WHERE Order_ID = %s"
val = (order_id,)
mycursor.execute(sql, val)
mydb.commit()

# Cerrar la conexión a la base de datos
mycursor.close()
mydb.close()

# Hacer una solicitud POST a la API con la respuesta
url = "http://localhost:5000/pedidos"
  body = {
        'order_id': order_id,
        'status': 'completado'
    }
headers = {'Content-Type': 'application/json'}
response = requests.post(url, headers=headers, data=payload)
print(response.text)

# Devolver la respuesta de la API
return response.text