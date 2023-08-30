from flask import Flask, jsonify, request, make_response
from datetime import datetime,timedelta
from flask_cors import CORS
import time
import sqlite3
import uuid
from functools import wraps
import pandas as pd

API = Flask(__name__)
CORS(API, resources={r"/*":{"origins":"*"}})


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
    temp = a[-1]
    a.pop()
    a.pop()
    a.append(temp)
    
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
    return jsonify(querry("SELECT * FROM clientes WHERE idCliente = {0};".format(id)))

@API.route("/clientes/idc/<int:id>", methods=['PUT']) #edita cliente de acordo com ID
def editClient(id):
    altClient = request.get_json()
    result = querry("UPDATE clientes SET nomeRepresentante = '{0}', numRepresentante = '{1}',username = '{2}', senha = '{3}' WHERE idCliente = {4};".format(
        altClient["representante"],altClient['contato'],altClient['username'],altClient['senha'],id))
    if result == []:
        return jsonify("sucesso")
    else:
        return jsonify(result)

@API.route("/clientes", methods = ['POST']) #adiciona novo cliente
def addClientes():
    novoCliente = request.get_json()
    q = "INSERT INTO clientes (nomeEmpresa, nomeRepresentante, numRepresentante, username,senha,typeUser) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}')".format(
        novoCliente["empresa"],novoCliente["representante"],novoCliente["contato"],novoCliente["username"],novoCliente["senha"],novoCliente["type"])
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
    def getPedidoDetalhe(id,idAnimal,b):
        for i in b:
            if i[2] == idAnimal and id == i[1]:
                return i[3]
        return 0
    p = querry("SELECT * FROM pedidos;")
    c = querry("SELECT idCliente,nomeEmpresa,nomeRepresentante,numRepresentante FROM clientes")
    a = querry("SELECT * FROM tipoAnimais")
    b = querry("SELECT * FROM detalhesPedidos")
    df_p = pd.DataFrame(p,columns=["1idPedido","2idCliente","3data","4status"])
    df_c = pd.DataFrame(c,columns=["2idCliente","5nomeEmpresa","6nomeRepresentante","7numRepresentante"])
    df_relat = pd.merge(df_p,df_c,on="2idCliente")
    df_relat = df_relat.sort_values("1idPedido")
    df_relat["3data"] = df_relat["3data"].apply(datetime.fromtimestamp).apply(lambda x: x.strftime("%d/%m/%Y"))
    for animal in a:
        df_relat[animal[1]] = df_relat["1idPedido"].apply(lambda id: getPedidoDetalhe(id, animal[0], b) )
    return df_relat.to_json(orient="records")

@API.route("/pedidos/idp/<int:id>", methods=['GET']) #retorna os pedidos de acordo com o ID
def getPedidosbyId(id):
    q = querry("SELECT * FROM pedidos WHERE idPedidos = {0};".format(id))
    q = list(q[0])
    q[2] = datetime.fromtimestamp(q[2]).strftime("%d/%m/%Y")
    return jsonify(q)

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
    result = querry("UPDATE pedidos SET dataPedido = unixepoch('{0}'), status = '{1}' WHERE idPedidos = {2};".format(editPedi["dataPedido"],editPedi["status"],id))
    return result

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
    def getAnimalEstoque(idClienhte, idAnimal, estoque):
        for a in estoque:
            if a[2] == idAnimal and idClienhte == a[1]:
                return a[3]
        return 0

    q = querry("SELECT * FROM clientes")
    b = querry("SELECT * FROM estoque")
    c = querry("SELECT * FROM tipoAnimais")
    df_q = pd.DataFrame(q).rename(columns={
        0:"idCliente",
        1: "nomeEmpresa",
        2: "nomeRepres",
        3: "contRepres",
        6: "tipoConta"
    })
    for animal in c:
        df_q[animal[1]] = df_q["idCliente"].apply(lambda id: getAnimalEstoque(id, animal[0], b) )
    df_q = df_q.query("tipoConta != 2").drop(columns=[5,"tipoConta",4])
    return df_q.to_json(orient="records")

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
    listAni = querry("SELECT * FROM tipoAnimais")
    list = []
    for a in novoEstoque:
        for b in listAni:
            if a["tipoAnimal"] == b[1]:
                list.append({
                    "idTipoAnimal": b[0],
                    "quant":a["quantidade"]
                })
    estoque = querry("SELECT * FROM estoque WHERE idCliente = {}".format(id))
    for a in list:
        est = [
            b
            for b in estoque
            if b[2] == a["idTipoAnimal"]
        ]
        if len(est) != 0 and 0 == a["quant"]:
            querry("DELETE FROM estoque WHERE idCliente = {} AND idTipoAnimal = {}".format(id,a["idTipoAnimal"]))
        if len(est) != 0 and est[0][2]!=a["quant"]:
            querry("UPDATE estoque SET quantidade = {0} WHERE idCliente = {1} AND idTipoAnimal = {2}".format(a["quant"],id,a["idTipoAnimal"]))
        elif len(est)==0 and 0 != a["quant"]:
            a = querry("INSERT INTO estoque (idCliente, idTipoAnimal, quantidade) VALUES ({},{},{});".format(id,a["idTipoAnimal"],a["quant"]))
                
    return ("sucesso")

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

@API.route("/detalhesPedido/idps/<int:id>", methods = ['GET']) #retona os detalhes de um pedido de acordo com o id do pedido para o site
def getDetPedidosbyPedidosParaSite(id):
    dfDet = pd.DataFrame(querry("SELECT * FROM detalhesPedidos WHERE idPedidos = {}".format(id)),columns=["idDetalhePedido","idPedido","idTipoAnimal","quant"])
    dfTipoAni = pd.DataFrame(querry("SELECT * FROM tipoAnimais"),columns=["idTipoAnimal","especie"])
    dfEnviar = pd.DataFrame.merge(dfDet,dfTipoAni,on="idTipoAnimal")
    return dfEnviar.to_json(orient="records")

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

@API.route("/abates/<int:id>", methods = ['POST']) #adiciona um abate
def addAbate(id):
    novoAbate = request.get_json()
    stringteste = ",".join([
        "({0},{1},'{2}','{3}')".format(id,abate["idTipoAnimal"],abate["pesoViavel"],abate["pesoCondenado"])
        for abate in novoAbate  
    ])
    q = querry("INSERT INTO abates (idPedidos, idTipoAnimal, peso, condenacoes) VALUES " + stringteste)
    return q

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