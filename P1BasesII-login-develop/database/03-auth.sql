-- SP - Autenticación y Autorización
\connect encuestas postgres

-- Insertar usuario
-- Procedimiento almacenado para insertar un nuevo usuario en la base de datos postgres
DROP PROCEDURE IF EXISTS insertar_usuario;

CREATE OR REPLACE PROCEDURE insertar_usuario(
    p_nombre VARCHAR(50),
    p_idRol INT,
    p_correo VARCHAR(50),
    p_contrasena VARCHAR(50),
    p_fechaCreacion TIMESTAMP,
    p_fechaNacimiento DATE,
    p_genero VARCHAR(50),
    p_idPais VARCHAR(50)
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO Usuarios(Nombre, idRol, Correo, Contrasenna, FechaCreacion, FechaNacimiento, Genero, idPais)
    VALUES (p_nombre, p_idRol, p_correo, p_contrasena, p_fechaCreacion, p_fechaNacimiento, p_genero, p_idPais);
END;
$$;







