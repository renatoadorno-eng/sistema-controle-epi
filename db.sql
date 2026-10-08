CREATE DATABASE IF NOT EXISTS sistema_epi;
USE sistema_epi;

CREATE TABLE Colaborador 
( 
 ID INT AUTO_INCREMENT PRIMARY KEY,  
 Nome VARCHAR(100) NOT NULL,  
 Setor VARCHAR(50) NOT NULL,  
 UNIQUE (ID)
); 

CREATE TABLE Equipamento 
( 
 ID INT AUTO_INCREMENT PRIMARY KEY,  
 Nome VARCHAR(100) NOT NULL,  
 QTD_estoque INT NOT NULL,  
 UNIQUE (ID)
); 

CREATE TABLE Emprestimo 
( 
 Data DATETIME NOT NULL,  
 ID INT PRIMARY KEY AUTO_INCREMENT,  
 idColaborador INT NOT NULL,  
 Situacao BOOLEAN NOT NULL,
 FOREIGN KEY (idColaborador) REFERENCES colaborador(ID)  
); 

CREATE TABLE contem 
( 
 idEmprestimo INT NOT NULL,  
 idEquipamento INT NOT NULL,  
 Quantidade INT NOT NULL,
 PRIMARY KEY (idEmprestimo, idEquipamento),
 FOREIGN KEY (idEmprestimo) REFERENCES emprestimo(ID),
 FOREIGN KEY (idEquipamento) REFERENCES equipamento(ID)  
); 

