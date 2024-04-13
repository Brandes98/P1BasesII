-- SP - Usuaarios
\connect encuestas postgres

-- Obtener usuarios
CREATE OR REPLACE FUNCTION OBTENER_USUARIOS()
  RETURNS TABLE (id integer)
  LANGUAGE plpgsql AS
$func$
BEGIN
   RETURN QUERY
   SELECT id
   FROM Usuarios;
END
$func$;