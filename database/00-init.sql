CREATE DATABASE encuestas;

\connect encuestas;

CREATE TABLE Roles (
  id SERIAL PRIMARY KEY,                -- 1: administrador, 2: creador encuestas, 3: encuestado
  Nombre VARCHAR(200) NOT NULL
);

CREATE TABLE Paises (
  id VARCHAR(3) PRIMARY KEY,          -- ISO 3166-1 alfa-3
  Nombre VARCHAR(100) NOT NULL
);

CREATE TABLE Usuarios (
  id SERIAL PRIMARY KEY,
  Nombre VARCHAR(200) NOT NULL,
  idRol INT NOT NULL,                   -- 1: administrador, 2: creador encuestas, 3: encuestado
  Correo VARCHAR(200) NOT NULL UNIQUE, 
  Contrasenna VARCHAR(200) NOT NULL, 
  FechaCreacion TIMESTAMP NOT NULL,     -- Fecha de creacion del usuario
  FechaNacimiento TIMESTAMP NOT NULL, 
  Genero VARCHAR(1) NOT NULL,          -- M, F u O
  idPais VARCHAR(3) NOT NULL,    -- Codigo de pais

  FOREIGN KEY (idRol) REFERENCES Roles(id),
  FOREIGN KEY (idPais) REFERENCES Paises(id)
);

CREATE TABLE Logs (
  Token SERIAL PRIMARY KEY,           -- Token de sesion       
  IdUsuario INT NOT NULL,             -- Id del usuario que inicio sesion      
  FechaLogIn TIMESTAMP NOT NULL,      -- Fecha de inicio de sesion
  FechaLogOut TIMESTAMP,              -- Fecha de cierre de sesion

  FOREIGN KEY (IdUsuario) REFERENCES Usuarios(id)
);