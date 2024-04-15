\connect encuestas;

INSERT INTO Roles (Nombre) VALUES ('Administrador'), ('Creador de encuestas'), ('Encuestado');

INSERT INTO Paises (id, Nombre) VALUES 
    ('CRC', 'Costa Rica'), 
    ('USA', 'Estados Unidos'), 
    ('MEX', 'Mexico'), 
    ('ESP', 'España'),
    ('ARG', 'Argentina'),
    ('COL', 'Colombia'),
    ('PER', 'Peru'),
    ('CHL', 'Chile'),
    ('BRA', 'Brasil'),
    ('URY', 'Uruguay');

INSERT INTO Usuarios (Nombre, idRol, Correo, Contrasenna, FechaCreacion, FechaNacimiento, Genero, idPais) 
VALUES 
    ('AdminCR', 1, 'admin@dominio.com', 'contrasenna123', NOW(), '1990-01-01 00:00:00', 'M', 'CRC'),
    ('EncuestasMX', 2, 'encuestas@dominio.com', 'clave456', NOW(), '1985-05-15 00:00:00', 'F', 'MEX'), 
    ('EncuestadoES', 3, 'encuestado@dominio.com', 'p4ssw0rd', NOW(), '2000-12-30 00:00:00', 'O', 'ESP');

INSERT INTO Logs (IdUsuario, FechaLogIn) 
VALUES 
    (1, NOW()), 
    (2, NOW()), 
    (3, NOW());