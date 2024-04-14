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

-- Loguear usuario
CREATE OR REPLACE PROCEDURE LOGIN_USUARIO(
    p_correo varchar,
    p_contrasenna varchar,
    p_fecha_actual timestamp,
    OUT p_token varchar
)
LANGUAGE plpgsql
AS $$
DECLARE
    idU INT;
BEGIN
    -- Intenta realizar la inserción
    EXECUTE 'SELECT id FROM Usuarios WHERE Correo = $1 AND Contrasenna = $2'
    INTO idU
    USING p_correo, p_contrasenna;

    IF idU IS NULL THEN
        RAISE EXCEPTION 'Correo o contraseña incorrectos';
    END IF;

    -- Realiza la inserción en la tabla Logs
    INSERT INTO Logs (IdUsuario, FechaLogIn)
    VALUES (idU, p_fecha_actual);

    -- Obtener el token de la tabla Logs
    SELECT CAST(IdUsuario AS VARCHAR) INTO p_token 
    FROM Logs 
    WHERE IdUsuario = idU AND FechaLogIn = p_fecha_actual;

    RETURN p_token;
END;
$$;