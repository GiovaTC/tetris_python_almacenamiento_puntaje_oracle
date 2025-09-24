-- Elimina objetos anteriores si existen (ignora el error si no existen)
BEGIN
  EXECUTE IMMEDIATE 'DROP TABLE tetris_scores CASCADE CONSTRAINTS';
EXCEPTION WHEN OTHERS THEN
  IF SQLCODE != -942 THEN RAISE; END IF;
END;
/

BEGIN
  EXECUTE IMMEDIATE 'DROP SEQUENCE tetris_scores_seq';
EXCEPTION WHEN OTHERS THEN
  IF SQLCODE != -2289 THEN RAISE; END IF;
END;
/

-- Crear tabla
CREATE TABLE tetris_scores ( 
  id NUMBER PRIMARY KEY,
  player_name VARCHAR2(100) NOT NULL,
  score NUMBER NOT NULL,
  lines_cleared NUMBER NOT NULL,
  game_level NUMBER NOT NULL,
  played_at TIMESTAMP DEFAULT SYSTIMESTAMP
);
/

-- Crear secuencia
CREATE SEQUENCE tetris_scores_seq START WITH 1 INCREMENT BY 1 NOCACHE;
/

-- Crear trigger de autoincremento
CREATE OR REPLACE TRIGGER trg_tetris_scores_id
BEFORE INSERT ON tetris_scores
FOR EACH ROW
BEGIN
  IF :NEW.id IS NULL THEN
    SELECT tetris_scores_seq.NEXTVAL INTO :NEW.id FROM dual;
  END IF;
END;
/

COMMIT;

INSERT INTO tetris_scores (player_name, score, lines_cleared, game_level)
VALUES ('Giovanny', 12345, 10, 3);

COMMIT;

SELECT * FROM tetris_scores;