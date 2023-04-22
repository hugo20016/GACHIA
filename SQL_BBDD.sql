CREATE DATABASE IF NOT EXISTS gachia_gs;

USE gachia_gs;

CREATE TABLE IF NOT EXISTS Usuarios (
ID INT NOT NULL AUTO_INCREMENT,
FirstName VARCHAR(50),
LastName VARCHAR(50),
Email VARCHAR(100),
Password VARCHAR(100),
Address VARCHAR(200),
PRIMARY KEY (ID)
);

-- Tabla para almacenar la información de los productos.
CREATE TABLE IF NOT EXISTS Productos (
ID INT NOT NULL AUTO_INCREMENT,
Name VARCHAR(50),
Description VARCHAR(200),
Price DECIMAL(10,2),
Stock INT,
PRIMARY KEY (ID)
);

-- Tabla para almacenar la información de los proveedores.
CREATE TABLE IF NOT EXISTS Proveedores (
ID INT NOT NULL AUTO_INCREMENT,
Name VARCHAR(50),
Contact VARCHAR(100),
PRIMARY KEY (ID)
);

-- Tabla para almacenar la información de los pedidos.
CREATE TABLE IF NOT EXISTS Pedidos (
ID INT NOT NULL AUTO_INCREMENT,
User_ID INT,
CreationDate DATE,
Product_ID INT,
Supplier_ID INT,
Status VARCHAR(50),
PRIMARY KEY (ID),
FOREIGN KEY (User_ID) REFERENCES Usuarios(ID),
FOREIGN KEY (Product_ID) REFERENCES Productos(ID),
FOREIGN KEY (Supplier_ID) REFERENCES Proveedores(ID)
);

-- Tabla para almacenar la información de los detalles de los pedidos.
CREATE TABLE IF NOT EXISTS OrderDetails (
ID INT NOT NULL AUTO_INCREMENT,
Order_ID INT,
Product_ID INT,
Quantity INT,
UnitPrice DECIMAL(10,2),
PRIMARY KEY (ID),
FOREIGN KEY (Order_ID) REFERENCES Pedidos(ID),
FOREIGN KEY (Product_ID) REFERENCES Productos(ID)
);

-- Tabla para almacenar la información de las transacciones de stock.
CREATE TABLE IF NOT EXISTS Transacciones_stock (
ID INT NOT NULL AUTO_INCREMENT,
Product_ID INT,
Quantity INT,
Date DATE,
PRIMARY KEY (ID),
FOREIGN KEY (Product_ID) REFERENCES Productos(ID)
);

-- Tabla para almacenar la información de la cola de almacenamiento.
CREATE TABLE IF NOT EXISTS Cola_almacen (
ID INT NOT NULL AUTO_INCREMENT,
Order_ID INT,
Status VARCHAR(50),
PRIMARY KEY (ID),
FOREIGN KEY (Order_ID) REFERENCES Pedidos(ID)
);

-- Tabla para almacenar la información de las etiquetas de envío.
CREATE TABLE IF NOT EXISTS Etiquetas_envio (
ID INT NOT NULL AUTO_INCREMENT,
Order_ID INT,
RecipientName VARCHAR(100),
RecipientPhone VARCHAR(20),
AddressLine1 VARCHAR(200),
AddressLine2 VARCHAR(200),
City VARCHAR(50),
State_Province VARCHAR(50),
PostalCode VARCHAR(20),
Country VARCHAR(50),
PRIMARY KEY (ID),
FOREIGN KEY (Order_ID) REFERENCES Pedidos(ID)
);

-- Tabla para almacenar la información de los puestos de picking.
CREATE TABLE IF NOT EXISTS Puesto_picking (
ID INT NOT NULL AUTO_INCREMENT,
Name VARCHAR(50),
PRIMARY KEY (ID)
);

-- Tabla para almacenar la información de los registros de picking.
CREATE TABLE IF NOT EXISTS PickingRecords (
ID INT NOT NULL AUTO_INCREMENT,
Order_ID INT,
PickingStation_ID INT,
Status VARCHAR(50),
PRIMARY KEY (ID),
FOREIGN KEY (Order_ID) REFERENCES Pedidos(ID)
);

-- INSERTS

INSERT INTO Usuarios (FirstName, LastName, Email, Password, Address) VALUES
("Juan", "Perez", "juanperez@email.com", "password123", "Calle Falsa 123"),
("Maria", "Gonzalez", "mariagonzalez@email.com", "qwerty", "Avenida Siempreviva 456"),
("Pedro", "Sanchez", "pedrosanchez@email.com", "p@$$w0rd", "Plaza Mayor 789");

INSERT INTO Productos (Name, Description, Price, Stock) VALUES
("Camiseta", "Camiseta de algodón para hombre", 19.99, 50),
("Pantalón", "Pantalón de mezclilla para mujer", 29.99, 30),
("Zapatos", "Zapatos de cuero para hombre", 49.99, 20);

INSERT INTO Proveedores (Name, Contact) VALUES
("Proveedor A", "contacto@proveedora.com"),
("Proveedor B", "contacto@proveedorb.com"),
("Proveedor C", "contacto@proveedorc.com");

INSERT INTO Pedidos (User_ID, CreationDate, Product_ID, Supplier_ID, Status) VALUES
(1, '2023-04-14', 1, 1, 'Pendiente'),
(2, '2023-04-15', 2, 2, 'En proceso'),
(3, '2023-04-16', 3, 3, 'Entregado');

INSERT INTO OrderDetails (Order_ID, Product_ID, Quantity, UnitPrice) VALUES
(1, 1, 2, 19.99),
(1, 3, 1, 49.99),
(2, 2, 1, 29.99),
(3, 3, 2, 49.99);

INSERT INTO Transacciones_stock (Product_ID, Quantity, Date) VALUES
(1, -2, '2023-04-14'),
(3, -1, '2023-04-14'),
(2, -1, '2023-04-15'),
(3, -2, '2023-04-16');

INSERT INTO Cola_almacen (Order_ID, Status) VALUES
(1, 'En espera'),
(2, 'En espera'),
(3, 'En proceso');

INSERT INTO Etiquetas_envio (Order_ID, RecipientName, RecipientPhone, AddressLine1, City, State_Province, PostalCode, Country) VALUES
(1, 'Juan Perez', '555-1234', 'Calle Falsa 123', 'Madrid', 'Madrid', '28001', 'España'),
(2, 'Maria Gonzalez', '555-5678', 'Avenida Siempreviva 456', 'Barcelona', 'Cataluña', '08001', 'España'),
(3, 'Pedro Sanchez', '555-9012', 'Plaza Mayor 789', 'Valencia', 'Comunidad Valenciana', '46001', 'España');

INSERT INTO Puesto_picking (Name) VALUES
('Puesto 1'),
('Puesto 2'),
('Puesto 3');


INSERT INTO PickingRecords (Order_ID, PickingStation_ID, Status)
VALUES (1, 1, 'Pendiente');

INSERT INTO PickingRecords (Order_ID, PickingStation_ID, Status)
VALUES (2, 2, 'Completado');

INSERT INTO PickingRecords (Order_ID, PickingStation_ID, Status)
VALUES (3, 1, 'Pendiente');
