"""
urlBase = "localhost"
Endpoints
    urlbase/clientes (post)
    urlbase/clientes/idCliente (put)
    urlbase/clientes/idCliente (delete)

    urlbase/pedidos (get)
    urlbase/pedidos (post)
    urlbase/pedidos/idPedido (get)
    urlbase/pedidos/idPedido (put)
    urlbase/pedidos/idPedido (delete)
    urlbase/pedidos/idCliente (get)
    urlbase/pedidos/idCliente (delete)
    urlbase/pedidos/date (get)
    urlbase/pedidos/status (get)

    urlbase/estoque/(get)
    urlbase/estoque/(post)
    urlbase/estoque/idCliente (get)
    urlbase/estoque/idCliente (put)
    urlbase/estoque/idCliente (delete)
    urlbase/estoque/idTipoAnimal (get)

    urlbase/detalhesPedidos/idPedidos (get)

    urlbase/tipoAnimais (get)

    urlbase/abates (get)
    urlbase/abates (post)
    urlbase/abates/idAbate (get)
    urlbase/abates/idAbate (put)
    urlbase/abates/idAbate (delete)
    urlbase/abates/idPedido (get)
    urlbase/abates/idTipoAnimal (get)
"""
from flask import Flask, jsonify, request
import sqlite3

API = Flask(__name__)

@API.route("/clientes", methods = ["GET"])
def getClientes():
    try:
        conec = sqlite3.connect("Database\database.db")
        cursor = conec.cursor()
        sqlitequerry = "SELECT * FROM clientes;"
        cursor.execute(sqlitequerry)
        record = cursor.fetchall()
        cursor.close()
    except sqlite3.Error as error:
        print("database error", error)
    finally:
        if conec:
            conec.close()

    return jsonify(record)

@API.route("/clientes/<int:id>", methods=['GET'])
def getClientsbyId(id):
    print(id)
    try:
        conec = sqlite3.connect("Database\database.db")
        cursor = conec.cursor()
        sqlitequerry = "SELECT * FROM clientes WHERE idCliente = {0};".format(id)
        print (sqlitequerry)
        cursor.execute(sqlitequerry)
        record = cursor.fetchall()
        cursor.close()
    except sqlite3.Error as error:
        print("database error", error)
    finally:
        if conec:
            conec.close()

    return jsonify(record)

@API.route("/clientes/<int:id>", methods=['PUT'])
def editClient(id):
    altClient = request.get_json() ##SET UP POSTMAN PARA RECEBER JSONS
    try:
        conec = sqlite3.connect("Database\database.db")
        cursor = conec.cursor()
        sqlitequerry = "--------------".format(id) ##FAZER QUERRY
        print (sqlitequerry)
        cursor.execute(sqlitequerry)
        record = cursor.fetchall()
        cursor.close()
    except sqlite3.Error as error:
        print("database error", error)
    finally:
        if conec:
            conec.close()

    return jsonify(record)
    
API.run(port = 5000, host = "localhost", debug = True)

"""
endpoints feitos
urlbase/clientes (get)
urlbase/clientes/idCliente (get)
 """