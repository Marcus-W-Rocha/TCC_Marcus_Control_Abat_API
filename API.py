from flask import Flask, jsonify, request
from datetime import datetime
import sqlite3

API = Flask(__name__)
def querry(querry): #inicia conexao para cada request, tambem força o uso de chaves estrangeiras
    try:
        conec = sqlite3.connect("Database\database.db")
        cursor = conec.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")
        cursor.execute(querry)
        conec.commit()
        record = cursor.fetchall()
        cursor.close()
        return record
    except sqlite3.Error as error:
        return "database error - {0}".format(error)
    finally:
        if conec:
            conec.close()

@API.route("/clientes", methods = ["GET"]) #retorna todos os clientes
def getClientes():
    q = "SELECT * FROM clientes;"
    return jsonify(querry(q))

@API.route("/clientes/idc/<int:id>", methods=['GET']) #retorna cliente de acordo com ID
def getClientsbyId(id):
    q = "SELECT * FROM clientes WHERE idCliente = {0};".format(id)
    return jsonify(querry(q))

@API.route("/clientes/idc/<int:id>", methods=['PUT']) #edita cliente de acordo com ID
def editClient(id):
    altClient = request.get_json()
    q = "UPDATE clientes SET nomeEmpresa = '{0}', nomeRepresentante = '{1}', numRepresentante = '{2}' WHERE idCliente = {3};".format(altClient[1],altClient[2],altClient[3],id)
    result = querry(q)
    if result == []:
        return jsonify("sucesso")
    else:
        return jsonify(result)

@API.route("/clientes", methods = ['POST']) #adiciona novo cliente
def addClientes():
    novoCliente = request.get_json()
    q = "INSERT INTO clientes (nomeEmpresa, nomeRepresentante, numRepresentante) VALUES ('{0}','{1}','{2}')".format(novoCliente[0],novoCliente[1],novoCliente[2])
    result = querry(q)
    if result == []:
        return jsonify("sucesso")
    else:
        return jsonify(result)

@API.route("/clientes/idc/<int:id>", methods=['DELETE']) #deleta cliente de acordo com ID
def deleteClientes(id):
    q = "DELETE FROM clientes WHERE idCliente = {0}".format(id)
    result = querry(q)
    if result == []:
        return jsonify("sucesso")
    else:
        return jsonify(result)

@API.route("/pedidos", methods = ['POST']) #adiciona pedido
def addPedidos():
    novoPedido = request.get_json()
    q = "INSERT INTO pedidos (idCliente, dataPedido, status) VALUES ('{0}',unixepoch('{1}'),'{2}')".format(novoPedido[0],novoPedido[1],novoPedido[2])
    result = querry(q)
    if result == []:
        return jsonify("sucesso")
    else:
        return jsonify(result)

@API.route("/pedidos", methods = ["GET"]) #retorna todos os pedidos
def getPedidos():
    q = "SELECT * FROM pedidos;"
    return jsonify(querry(q))

@API.route("/pedidos/idp/<int:id>", methods=['GET']) #retorna os pedidos de acordo com o ID
def getPedidosbyId(id):
    q = "SELECT * FROM pedidos WHERE idPedidos = {0};".format(id)
    return jsonify(querry(q))

@API.route("/pedidos/idc/<int:id>", methods=['GET']) #retona pedido de um cliente
def getPedidosbyClienteId(id):
    q = "SELECT * FROM pedidos WHERE idCliente = {0};".format(id)
    return jsonify(querry(q))

@API.route("/pedidos/date/<string:date>", methods=['GET']) #retona todos os pedidos de uma data
def getPedidosbyDate(date): 
    q = "SELECT * FROM pedidos WHERE dataPedido = unixepoch('{0}');".format(date)
    result = querry(q)
    for a in range(0,len(result)):
        b = list(result[a])
        b[2] = datetime.fromtimestamp(int(result[a][2])).strftime("%d/%m/%Y")
        result[a] = tuple(b)
    return jsonify(result)

@API.route("/pedidos/status/<string:status>", methods=['GET']) #retorna todos os pedidos de acordo com o status
def getPedidosbyStatus(status):
    q = "SELECT * FROM pedidos WHERE status = '{}';".format(status)
    return jsonify(querry(q))

@API.route("/pedidos/date/byPeriod/<int:id>", methods=['GET']) #retorna todos os pedidos dentro de um intervalo de tempo
def getPedidosbyPeriod(id): #data dever ser enviada no tipo yyyy-mm-dd (alteravel)
    dates = request.get_json()
    q = "SELECT * FROM pedidos WHERE idCliente = {0} AND dataPedido BETWEEN unixepoch('{1}') and unixepoch('{2}');".format(id,dates[0],dates[1])
    result = querry(q)
    for a in range(0,len(result)):
        b = list(result[a])
        b[2] = datetime.fromtimestamp(int(result[a][2])).strftime("%d/%m/%Y")
        result[a] = tuple(b)
    return jsonify(result)

@API.route("/pedidos/idp/<int:id>", methods=['PUT']) #edita pedido por ID
def editPedidosbyID(id):
    editPedi = request.get_json()
    q = "UPDATE pedidos SET IdCliente = {0}, dataPedido = unixepoch('{1}'), status = '{2}' WHERE idPedidos = {3};".format(editPedi[0],editPedi[1],editPedi[2],id)
    result = querry(q)
    if result == []:
        return jsonify("sucesso")
    else:
        return jsonify(result)

@API.route("/pedidos/idp/<int:id>", methods=['DELETE']) #deleta pedidos por ID
def deletePedidosbyId(id):
    q = "DELETE FROM pedidos WHERE idPedidos = {0}".format(id)
    result = querry(q)
    if result == []:
        return jsonify("sucesso")
    else:
        return jsonify(result)
    
@API.route("/pedidos/idc/<int:id>", methods=['DELETE']) #deleta pedido por cliente
def deletePedidosbyCliente(id):
    q = "DELETE FROM pedidos WHERE idCliente = {0}".format(id)
    result = querry(q)
    if result == []:
        return jsonify("sucesso")
    else:
        return jsonify(result)

@API.route("/estoque", methods = ["GET"]) #retorna estoque
def getEstoque():
    q = "SELECT * FROM estoque"
    return jsonify(querry(q))

@API.route("/estoque/idc/<int:id>", methods = ['GET']) #retorna estoque por cliente
def getEstoquebyCliente(id):
    q = "SELECT * FROM estoque WHERE idCliente = {}".format(id)
    return jsonify(querry(q))

@API.route("/estoque/idt/<int:id>", methods = ['GET']) #retorna estoque por Tipo de Animal
def getEstoquebyTipo(id):
    q = "SELECT * FROM estoque WHERE idTipoAnimal = {}".format(id)
    return jsonify(querry(q))

@API.route("/estoque/", methods = ['POST']) #adiciona no estoque
def addEstoque():
    novoEstoque = request.get_json()
    q ="INSERT INTO estoque (idCliente, idTipoAnimal, quantidade) VALUES ({},{},{});".format(novoEstoque[0],novoEstoque[1],novoEstoque[2])
    result = querry(q)
    if result == []:
        return jsonify("sucesso")
    else:
        return jsonify(result)

@API.route("/estoque/idc/<int:id>", methods=['PUT']) #edita estoque (usado para adicionar ou retirar animais)
def usarEstoquebyCliente(id): #tambem checa se algum contador de animais chegou a 0, caso tenha chegado o elimina da tabela
    novoEstoque = request.get_json()
    q = "UPDATE estoque SET quantidade = {0} WHERE idCliente = {1} AND idTipoAnimal = {2}".format(novoEstoque[1],id,novoEstoque[0])
    result = querry(q)
    querry("DELETE FROM estoque WHERE quantidade = 0")
    if result == []:
        return jsonify("sucesso")
    else:
        return jsonify(result)

@API.route("/detalhesPedido/idp/<int:id>", methods = ['GET']) #retona os detalhes de um pedido de acordo com o id do pedido
def getDetPedidosbyPedidos(id):
    q = "SELECT * FROM detalhesPedidos WHERE idPedidos = {}".format(id)
    return jsonify(querry(q))

@API.route("/tipoAnimais", methods = ['GET']) #retorna todos os tipos de animais
def getTipoAnimais():
    q = "SELECT * FROM tipoAnimais"
    return jsonify(querry(q))

@API.route("/abates", methods = ['GET']) #retorna todos os abates
def getAbates():
    q = "SELECT * FROM abates"
    return jsonify(querry(q))

@API.route("/abates/ida/<int:id>", methods = ['GET']) #retorna abates de acordo com id
def getAbatesbyId(id):
    q = "SELECT * FROM abates WHERE IdAbate = {0}".format(id)
    return jsonify(querry(q))

@API.route("/abates/idp/<int:id>", methods = ['GET']) #retona os abates de um determinado pedido
def getAbatesbyPedido(id):
    q = "SELECT * FROM abates WHERE idPedidos = {0}".format(id)
    return jsonify(querry(q))

@API.route("/abates", methods = ['POST']) #adiciona um abate
def addAbate():
    novoAbate = request.get_json()
    q = "INSERT INTO abates (idPedidos, idTipoAnimal, peso, viabilidade) VALUES ({0},{1},{2},'{3}')".format(novoAbate[0],novoAbate[1],novoAbate[2],novoAbate[3])
    result = querry(q)
    if result == []:
        return jsonify("sucesso")
    else:
        return jsonify(result)

@API.route("/abates/ida/<int:id>", methods=['PUT']) #edita abates por id(somente para corrigir erros de entrada)
def editAbatebyID(id):
    editAbat = request.get_json()
    q = "UPDATE abates SET IdPedidos = {0}, idTipoAnimal = {1}, peso = {2}, viabilidade = '{3}' WHERE idAbate = {4};".format(editAbat[0],editAbat[1],editAbat[2],editAbat[3],id)
    print(q)
    result = querry(q)
    if result == []:
        return jsonify("sucesso")
    else:
        return jsonify(result)

@API.route("/abates/ida/<int:id>", methods=['DELETE']) #deleta abates por id(somente para corrigir erros)
def deleteAbate(id):
    q = "DELETE FROM abates WHERE idAbate = {0}".format(id)
    result = querry(q)
    if result == []:
        return jsonify("sucesso")
    else:
        return jsonify(result)

API.run(port = 3000, host = "localhost", debug = True)