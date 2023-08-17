CREATE TABLE clientes (
    idCliente INTEGER PRIMARY KEY,
    nomeEmpresa TEXT NOT NULL,
    nomeRepresentante TEXT NOT NULL,
    numRepresentante TEXT NOT NULL,
    username TEXT NOT NULL,
    senha TEXT NOT NULL
);

CREATE TABLE pedidos(
    idPedidos INTEGER PRIMARY KEY ,
    idCliente INTEGER NOT NULL, 
    dataPedido INTEGER NOT NULL,
    status TEXT NOT NULL,
    FOREIGN KEY (IdCliente) REFERENCES clientes(IdCliente)
);

CREATE TABLE tipoAnimais(
    idTipoAnimal INTEGER PRIMARY KEY,
    especie TEXT NOT NULL
);

CREATE TABLE detalhesPedidos(
    idPedidos INTEGER NOT NULL,
    idTipoAnimal INTEGER NOT NULL,
    quantidade INTEGER NOT NULL,
    FOREIGN KEY (idPedidos) REFERENCES pedidos(idPedidos),
    FOREIGN KEY (idTipoAnimal) REFERENCES tipoAnimais(idTipoAnimal)
);

CREATE TABLE estoque(
    idCliente INTEGER NOT NULL,
    idTipoAnimal INTEGER NOT NULL,
    quantidade INTEGER NOT NULL,
    FOREIGN KEY (idCliente) REFERENCES clientes(idCliente),
    FOREIGN KEY (idTipoAnimal) REFERENCES tipoAnimais(idTipoAnimal)
);

CREATE TABLE abates(
    idAbate INTEGER PRIMARY KEY,
    idPedidos INTEGER NOT NULL,
    idTipoAnimal  INTEGER NOT NULL,
    peso INTEGER NOT NULL,
    viabilidade BOOLEAN NOT NULL,
    FOREIGN KEY (idPedidos) REFERENCES pedidos(idPedidos),
    FOREIGN KEY (idTipoAnimal) REFERENCES tipoAnimais(idTipoAnimal)
); 