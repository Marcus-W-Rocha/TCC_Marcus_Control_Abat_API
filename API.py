from flask import Flask, jsonify, request
from datetime import datetime,timedelta
import time
import sqlite3
import json
import uuid

API = Flask(__name__)
def querry(querry): #inicia conexao para cada request, tambem força o uso de chaves estrangeiras
    try:
        conec = sqlite3.connect("Database\database.db")
        cursor = conec.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")
        cursor.execute(querry)
        record = cursor.fetchall()
        conec.commit()
        cursor.close()
        return record
    except sqlite3.Error as error:
        return "database error - {0}".format(error)
    finally:
        if conec:
            conec.close()

@API.before_request
def before_request():    
    if not "/login" in request.url:
        token = request.headers.get('token',default=False)
        if token == False:
            return "Token nao existente"
        q = "SELECT * FROM token WHERE tokenCliente = '{0}' AND data >= {1}".format(token,time.mktime(datetime.now().timetuple())) 
        a = querry(q)
        if len(a) == 0:
            return "token invalido"


@API.route("/clientes", methods = ["GET"]) #retorna todos os clientes
def getClientes():
    q = "SELECT * FROM clientes;"
    return jsonify(querry(q))

@API.route("/clientes/login", methods = ["POST"]) #login
def loginCliente():
    login = request.get_json()
    q = "SELECT * FROM clientes WHERE username = '{0}' AND senha = '{1}'".format(login["user"],login["senha"])
    a = querry(q)
    if len(a)==0:
        return "Credenciais Invalidas"
    a = list(a[0])
    a.pop()

    q = querry("SELECT * FROM token where idCliente = '{0}' and data >={1}".format(a[0],time.mktime((datetime.now()).timetuple())))
    if len(q)!= 0:
        q = q[0][1]
        a.append(q)
        return jsonify(a)
    newToken = uuid.uuid4()
    x = 0
    while True:
        newToken = uuid.uuid5(newToken,login["senha"])
        newToken = uuid.uuid5(newToken,login["user"])
        newToken = uuid.uuid5(newToken,datetime.now().strftime("%d-%m-%Y %H:%M:%S"))
        q = "SELECT * FROM token where tokenCliente = '{0}'".format(newToken)
        data = time.mktime((datetime.now()+timedelta(1)).timetuple())
        if len(querry(q))==0:
            querry("DELETE FROM token WHERE idCliente = {0}".format(a[0]))
            querry("INSERT INTO token (idCliente, tokenCliente, data) VALUES ('{0}','{1}','{2}')".format(a[0],newToken,data))
            break
        if x > 10:
            break
        x += 1

    a.append(newToken)
    return jsonify(a)
        

@API.route("/clientes/idc/<int:id>", methods=['GET']) #retorna cliente de acordo com ID
def getClientsbyId(id):
    q = "SELECT * FROM clientes WHERE idCliente = {0};".format(id)
    return jsonify(querry(q))

@API.route("/clientes/idc/<int:id>", methods=['PUT']) #edita cliente de acordo com ID
def editClient(id):
    altClient = request.get_json()
    q = "UPDATE clientes SET nomeRepresentante = '{0}', numRepresentante = '{1}', senha = '{2}' WHERE idCliente = {3};".format(
        altClient["nomeRepresentante"],altClient['contatoRepre'],altClient['senha'],id)
    result = querry(q)
    if result == []:
        return jsonify("sucesso")
    else:
        return jsonify(result)

@API.route("/clientes", methods = ['POST']) #adiciona novo cliente
def addClientes():
    novoCliente = request.get_json()
    q = "INSERT INTO clientes (nomeEmpresa, nomeRepresentante, numRepresentante, username,senha) VALUES ('{0}','{1}','{2}','{3}','{4}')".format(
        novoCliente[0],novoCliente[1],novoCliente[2],novoCliente[3],novoCliente[4])
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
    q = "INSERT INTO pedidos (idCliente, dataPedido, status) VALUES ('{0}',unixepoch('{1}'),'{2}') RETURNING *".format(novoPedido["idCliente"],novoPedido["dataPedido"],novoPedido["status"])
    result = querry(q)
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
    result = querry(q)
    return jsonify(result)

@API.route("/pedidos/date/<string:date>", methods=['GET']) #retona todos os pedidos de uma data
def getPedidosbyDate(date): 
    q = "SELECT * FROM pedidos WHERE dataPedido = unixepoch('{0}');".format(date)
    result = querry(q)
    for a in range(0,len(result)):
        b = list(result[a])
        b[2] = datetime.fromtimestamp(int(result[a][2])).strftime("%d/%m/%Y")
        result[a] = tuple(b)
    return jsonify(result)

@API.route("/pedidos/status/<string:status>", methods=['POST']) #retorna todos os pedidos de acordo com o status e o cliente
def getPedidosbyStatus(status):
    cliente = request.get_json()
    q = "SELECT * FROM pedidos WHERE idCliente = {0} AND status = '{1}';".format(cliente["idCliente"],status)
    return jsonify(querry(q))

@API.route("/pedidos/date/byPeriod/<int:id>", methods=['POST']) #retorna todos os pedidos dentro de um intervalo de tempo
def getPedidosbyPeriod(id): #data dever ser enviada no tipo yyyy-mm-dd (alteravel)
    dates = request.get_json()
    q = "SELECT * FROM pedidos WHERE idCliente = {0} AND dataPedido BETWEEN unixepoch('{1}') and unixepoch('{2}');".format(id,dates["start"],dates["end"])
    result = querry(q)
    return jsonify(result)

@API.route("/pedidos/idp/<int:id>", methods=['PUT']) #edita pedido por ID
def editPedidosbyID(id):
    editPedi = request.get_json()
    q = "UPDATE pedidos SET dataPedido = unixepoch('{0}'), status = '{1}' WHERE idPedidos = {2};".format(editPedi["dataPedido"],editPedi["status"],id)
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
    b = querry(q)
    return jsonify(b)

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

@API.route("/detalhesPedido/", methods = ['POST']) #novo detalhe
def addDetPedidosbyPedidos():
    novoDetPedido = request.get_json()
    stringteste = ",".join([
        "({0},{1},{2})".format(det["idPedido"],det["idTipoAnimal"],det["quantidade"])
        for det in novoDetPedido  
    ])
    q = "INSERT INTO detalhesPedidos (idPedidos, idTipoAnimal, quantidade) VALUES {}".format(stringteste)
    
    result = querry(q)
    if result == []:
        return jsonify("sucesso")
    else:
        return jsonify(result)


@API.route("/detalhesPedido/idp/<int:id>", methods = ['GET']) #retona os detalhes de um pedido de acordo com o id do pedido
def getDetPedidosbyPedidos(id):
    q = "SELECT * FROM detalhesPedidos WHERE idPedidos = {}".format(id)
    return jsonify(querry(q))


@API.route("/detalhesPedido/idd/<int:id>", methods=['PUT']) #edita detalhes de pedidos por id
def editDetPedidobyID(id):
    editDet = request.get_json()
    q = "UPDATE detalhesPedidos SET IdPedidos = {0}, idTipoAnimal = {1}, quantidade = {2} WHERE idDetalhe = {3};".format(editDet["idPedido"],editDet["idTipoAnimal"],editDet["quantidade"],id)
    result = querry(q)
    if result == []:
        return jsonify("sucesso")
    else:
        return jsonify(result)



@API.route("/detalhesPedido/idp/<int:id>", methods = ['DELETE']) #deleta detalhes de acordo com o pedido
def deleteDetPedidobyPedido(id):
    q = "DELETE FROM detalhesPedidos WHERE idPedidos = {0}".format(id)
    return jsonify(querry(q))

@API.route("/detalhesPedido/idd/<int:id>", methods = ['DELETE']) #deleta detalhes de acordo com o Id
def deleteDetPedidobyId(id):
    q = "DELETE FROM detalhesPedidos WHERE idDetalhe = {0}".format(id)
    return jsonify(querry(q))

@API.route("/tipoAnimais", methods = ['GET']) #retorna todos os tipos de animais
def getTipoAnimais():
    q = "SELECT * FROM tipoAnimais"
    response = (querry(q))
    return jsonify(response)

@API.route("/tipoAnimais/idta/<int:id>", methods = ['GET']) #retorna todos os tipos de animais de acordo com o id
def getTipoAnimaisbyId(id):
    q = "SELECT * FROM tipoAnimais WHERE idTipoAnimal = {}".format(id)
    response = (querry(q))
    return jsonify(response)

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

API.run(port = 3000, host = "0.0.0.0", debug = True)