
-- . Creamos el nuevo procedimiento 
CREATE OR REPLACE PROCEDURE actualizar_datos_habitacion(
    p_id BIGINT,
    p_tipo VARCHAR,
    p_descripcion VARCHAR,
    p_capacidad INT,
    p_numero_hab INT,
    p_precio NUMERIC,
    p_estado VARCHAR
)
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE reservas_habitacion
    SET 
        tipo = p_tipo,
        descripcion = p_descripcion,
        capacidad = p_capacidad,
        numero_hab = p_numero_hab,
        precio = p_precio,
        estado = p_estado
    WHERE id = p_id;
END;
$$;


select * from reservas_habitacion