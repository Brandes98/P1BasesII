-- Funciones
\connect encuestas postgres

-- Obtener género
CREATE OR REPLACE FUNCTION OBTENER_GENERO( genero varchar) RETURNS VARCHAR AS $$
    BEGIN
        IF genero = 'M' THEN
            RETURN 'Masculino';
        ELSIF genero = 'F' THEN
            RETURN 'Femenino';
        ELSE
            RETURN 'Otro';
        END IF;
    END;
$$ LANGUAGE plpgsql;

-- funcion para log in
CREATE OR REPLACE FUNCTION log_in(
    p_correo VARCHAR(50),
    p_contrasena VARCHAR(50)
)
RETURNS JSON AS $$
DECLARE
    v_usuario JSON;
BEGIN
    SELECT to_json(u) INTO v_usuario
    FROM Usuarios u
    WHERE u.Correo = p_correo AND u.Contrasenna = p_contrasena;
    RETURN v_usuario;
END;
$$ LANGUAGE plpgsql;
