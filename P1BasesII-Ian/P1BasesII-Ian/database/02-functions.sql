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