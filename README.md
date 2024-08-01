use bd_pi;
-- Tabla de logs para mensajes
CREATE TABLE log_eventos (
  id INT AUTO_INCREMENT PRIMARY KEY,
  mensaje VARCHAR(255),
  fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
-- Tabla calculadora_co2
CREATE TABLE calculadora_co2 (
  id_calculadora_co2 INT NOT NULL AUTO_INCREMENT,
  id_usuario INT NOT NULL,
  fecha DATE NOT NULL,
  calculo_co2 DECIMAL(10,2) NOT NULL,
  PRIMARY KEY (id_calculadora_co2),
  FOREIGN KEY (id_usuario) REFERENCES usuarios (id_usuarios)
);

-- Tabla curso
CREATE TABLE curso (
  id_curso INT NOT NULL AUTO_INCREMENT,
  titulo VARCHAR(255) NOT NULL,
  descripcion varchar(700),
  id_usuario INT NOT NULL,
  fecha_publicacion DATE NOT NULL,
  fecha_inicio DATE NOT NULL,
  fecha_fin DATE NOT NULL,
  estatus varchar(255) NOT NULL,
  certificacion varchar(255) NOT NULL,
  categoria varchar(255),
  PRIMARY KEY (id_curso),
  FOREIGN KEY (id_usuario) REFERENCES usuarios (id_usuarios)
);

-- Tabla inscripcion
CREATE TABLE inscripcion (
  id_inscripcion INT NOT NULL AUTO_INCREMENT,
  id_usuario INT NOT NULL,
  id_curso INT NOT NULL,
  fecha_inscripcion DATE NOT NULL,
  estatus TINYINT NOT NULL,
  PRIMARY KEY (id_inscripcion),
  FOREIGN KEY (id_curso) REFERENCES curso (id_curso),
  FOREIGN KEY (id_usuario) REFERENCES usuarios (id_usuarios)
);

-- Tabla tipo_usuario
CREATE TABLE tipo_usuario (
  id_tipo_usuario INT NOT NULL AUTO_INCREMENT,
  descripcion VARCHAR(100) NOT NULL,
  PRIMARY KEY (id_tipo_usuario)
);

-- Tabla usuarios
CREATE TABLE usuarios (
  id_usuarios INT NOT NULL AUTO_INCREMENT,
  nombre VARCHAR(100) NOT NULL,
  apellido_pa VARCHAR(100) NOT NULL,
  apellido_ma VARCHAR(100) NOT NULL,
  correo VARCHAR(100) NOT NULL,
  fecha_ingreso DATE NOT NULL,
  id_tipo_usuario INT NOT NULL,
  PRIMARY KEY (id_usuarios),
  FOREIGN KEY (id_tipo_usuario) REFERENCES tipo_usuario (id_tipo_usuario)
);

-- 5 disparadores --
-- 1. antes de ingresar algo a la tablas usuario se va a actualizar la fecha ya que no tenemos un campo datetime que obtenga la fecha al momento
DELIMITER //
CREATE TRIGGER desp_actuali_usuario
BEFORE UPDATE ON usuarios -- este disparador se ejecuta antes de que se actualice un registro en la tabla
FOR EACH ROW -- afecta la nueva fila que se inserto
BEGIN
  SET NEW.fecha_ingreso = CURDATE(); -- pone la fecha exacta del momento del registro
END;
//
-- 2. disparador para verificacion de fechas, que no sea primero la fecha de fin que la de ingreso
CREATE TRIGGER antes_insert_curso
BEFORE INSERT ON curso
FOR EACH ROW -- afecta la nueva fila que se inserto
BEGIN
  IF NEW.fecha_fin <= NEW.fecha_inicio THEN -- condicional para asegurar que las fechas esten correctamente
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'La fecha de fin debe ser posterior a la fecha de inicio.';
  END IF;
END;
//
-- 3. disparador para prevenir eliminacion de ususarios con inscripciones
CREATE TRIGGER antes_elimin_usuario
BEFORE DELETE ON usuarios
FOR EACH ROW -- afecta la nueva fila que se inserto
BEGIN
  DECLARE user_count INT; -- hace la funcion de contar cuantos usuarios estan en cursos corroborando con los id, si hay mas de 0 se mandara un error
  SELECT COUNT(*) INTO user_count FROM inscripcion WHERE id_usuario = OLD.id_usuarios;
  IF user_count > 0 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'No se puede eliminar un usuario con inscripciones.';
  END IF;
END;
//
-- 4. disparador para actualizar el estado de inscripcion cuando se elimina un curso
CREATE TRIGGER despues_elimin_curso
AFTER DELETE ON curso
FOR EACH ROW -- afecta la nueva fila que se inserto
BEGIN
  UPDATE inscripcion SET estatus = 0 WHERE id_curso = OLD.id_curso; -- establece todas las inscripciones al curso eliminado a 0 (no disponible)
END;
//
-- 5. despues de insertar algo en la calculadora de carbono
CREATE TRIGGER despues_insert_calculadora
AFTER INSERT ON calculadora_co2
FOR EACH ROW
BEGIN
  INSERT INTO log_eventos (mensaje) VALUES ('Se ha insertado algo nuevo en la tabla calculadora_co2');
END;
//DELIMITER ;

-- 2 funciones --
-- 1. funcion para obtener el nombre completo del usuario
DELIMITER //
CREATE FUNCTION obtener_nombre_completo(user_id INT) RETURNS VARCHAR(255)
BEGIN
  DECLARE nombre_completo VARCHAR(255); -- declaramos donde vamos a guardar el nombre completo 
  SELECT CONCAT(nombre, ' ', apellido_pa, ' ', apellido_ma) INTO nombre_completo -- y los concatenamos para completar
  FROM usuarios WHERE id_usuarios = user_id; -- los obtenemos de parte del id 
  RETURN nombre_completo; -- retorna el nombre completo ya concatenado y todo
END;
//
-- 2. funcion para clacular la duracion de un curso en dias, uncamente informativo
CREATE FUNCTION duracion_curso(curso_id INT) RETURNS INT
BEGIN
  DECLARE duracion INT; -- declaramos donde guardar la duracion
  SELECT DATEDIFF(fecha_fin, fecha_inicio) INTO duracion FROM curso WHERE id_curso = curso_id; 
  -- declara y devuelve la diferencia de dias entre fechas para obtener la duracion
  RETURN duracion;
END; 

-- 5 procedimientos almacenados --
-- 1. procedimiento almacenado para insertar en la tabla usuarios
CREATE PROCEDURE agregar_usuario(
  IN p_nombre VARCHAR(100),
  IN p_apellido_pa VARCHAR(100),
  IN p_apellido_ma VARCHAR(100),
  IN p_correo VARCHAR(100),
  IN p_id_tipo_usuario INT
)
BEGIN
  INSERT INTO usuarios (nombre, apellido_pa, apellido_ma, correo, fecha_ingreso, id_tipo_usuario)
  VALUES (p_nombre, p_apellido_pa, p_apellido_ma, p_correo, CURDATE(), p_id_tipo_usuario);
END;

-- 2. procedimiento para listar inscripciones de un usuario
CREATE PROCEDURE listar_inscripciones_usuario(IN p_id_usuario INT) -- p_id_usuario es el parametro que se va a pedir al momento de ejecutar el procedimiento almacenado
BEGIN
  SELECT * FROM inscripcion WHERE id_usuario = p_id_usuario; 
END; 

-- 3. procedimiento para actualizar el estado de un curso
CREATE PROCEDURE actualizar_estado_curso(IN p_id_curso INT, IN p_nuevo_estatus VARCHAR(255)) -- utilizamos los dos parametros el id curso y el nuevo estatus que pondremos
BEGIN
  UPDATE curso SET estatus = p_nuevo_estatus WHERE id_curso = p_id_curso; -- actualiza la tabla estatus con el nuevo estatus que pusimos
END;

-- 4. procedimiento para eliminar un usuario por correo
CREATE PROCEDURE eliminar_usuario_por_correo(IN p_correo VARCHAR(100)) -- utilizamos el parametro de correo para poder eliminar abajo
BEGIN
  DELETE FROM usuarios WHERE correo = p_correo; -- lo eliminamos por medio del correo
END;

-- 5. procedimiento para obtener cursos activos
CREATE PROCEDURE obtener_cursos_activos()
BEGIN
  SELECT * FROM curso WHERE estatus = 'activo'; -- seleccionamos con el estatus activo
END;

-- 2 vistas -- 
-- 1. vista para ver los usuarios con su tipo de usuario
CREATE VIEW vista_usuarios_tipo AS
SELECT u.id_usuarios, u.nombre, u.apellido_pa, u.apellido_ma, t.descripcion AS tipo_usuario
FROM usuarios u
JOIN tipo_usuario t ON u.id_tipo_usuario = t.id_tipo_usuario;
 
-- 2. vista para ver las inscripciones con detalles de curso
CREATE VIEW vista_inscripciones_detalles AS
SELECT i.id_inscripcion, i.fecha_inscripcion, c.titulo, c.fecha_inicio, c.fecha_fin, u.nombre AS usuario
FROM inscripcion i
JOIN curso c ON i.id_curso = c.id_curso
JOIN usuarios u ON i.id_usuario = u.id_usuarios;
