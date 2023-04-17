import requests

def obtener_informacion_envio(order_id):
    url_pedidos = "http://localhost:5000/pedidos"
    url_etiquetas = "http://localhost:5000/etiquetas_envio"
    headers = {'Content-Type': 'application/json'}

    # Obtener información del pedido
    params = {'Order_ID': order_id}
    response_pedidos = requests.get(url_pedidos, params=params, headers=headers)
    pedido = response_pedidos.json()

    # Obtener información de las etiquetas de envío
    params = {'Order_ID': order_id}
    response_etiquetas = requests.get(url_etiquetas, params=params, headers=headers)
    etiquetas = response_etiquetas.json()

    # Combinar información de pedido y etiquetas de envío
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
        'Country': etiquetas['Country']
    }

    # Imprimir información de envío
    print(informacion_envio)