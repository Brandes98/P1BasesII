-- SP - Autenticación y Autorización
\connect encuestas postgres

-- Insertar usuario
CREATE OR REPLACE PROCEDURE INSERTAR_USUARIO(
    nombre varchar,
    IdRol integer,
    correo varchar,
    contrasenna varchar,
    fechaCreacion timestamp,
    fechaNacimiento timestamp,
    genero varchar,
    IdPais varchar
)
LANGUAGE plpgsql
AS $$
BEGIN
    -- Intenta realizar la inserción
    INSERT INTO Usuarios (Nombre, idRol, Correo, Contrasenna, FechaCreacion, FechaNacimiento, Genero, idPais) 
    VALUES (nombre, IdRol, correo, contrasenna, fechaCreacion, fechaNacimiento, genero, IdPais);
EXCEPTION WHEN unique_violation THEN
    -- Si hay una violación de la restricción UNIQUE (correo duplicado), maneja la excepción aquí
    RAISE NOTICE 'El correo electrónico ya existe en la base de datos';
END;
$$;