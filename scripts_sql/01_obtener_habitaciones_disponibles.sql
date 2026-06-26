CREATE OR REPLACE FUNCTION obtener_habitaciones_disponibles(f_inicio DATE, f_fin DATE)
RETURNS TABLE (
    id BIGINT,              
    tipo VARCHAR,
    descripcion VARCHAR,
    capacidad INT,
    numero_hab INT,
    precio NUMERIC,
    estado VARCHAR,
    imagen VARCHAR
) 
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT h.id, h.tipo, h.descripcion, h.capacidad, h.numero_hab, h.precio, h.estado, h.imagen
    FROM reservas_habitacion h
    WHERE h.id NOT IN (
        SELECT r.habitacion_id 
        FROM reservas_reserva r
        WHERE (f_inicio < r.fecha_salida AND f_fin > r.fecha_ingreso)
    );
END;
$$;