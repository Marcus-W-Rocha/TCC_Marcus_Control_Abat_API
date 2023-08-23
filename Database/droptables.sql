-- SQLite
INSERT INTO abates (idPedidos, idTipoAnimal, peso, condenacoes) VALUES (2,2,'19','0');
INSERT INTO abates (idPedidos, idTipoAnimal, peso, condenacoes) VALUES (2,2,'21','0');
INSERT INTO abates (idPedidos, idTipoAnimal, peso, condenacoes) VALUES (2,2,'24','1')

INSERT INTO pedidos (idCliente, dataPedido, status) VALUES ('1','1692500400','Processado') RETURNING * 

SELECT * FROM pedidos WHERE idCliente = 3 AND status = 'Enviado'

UPDATE pedidos SET dataPedido = 1692662400, status = 'Enviado' WHERE idPedidos = 1;

SELECT * FROM clientes WHERE username = 'Username1' AND senha = 'e10adc3949ba59abbe56e057f20f883e'

UPDATE clientes SET senha = 'e10adc3949ba59abbe56e057f20f883e' WHERE idCliente = 3

INSERT INTO abates (idPedidos, idTipoAnimal, peso, condenacoes) VALUES (2,1,'75,65,60,70',0),(2,2,'25',0),(2,3,'10,11',1)


/* DROP TABLE clientes;
DROP TABLE clientes;
DROP TABLE clientes;
DROP TABLE clientes; */