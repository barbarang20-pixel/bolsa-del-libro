from fastapi import APIRouter, HTTPException
from app.database import get_connection
from pydantic import BaseModel

router = APIRouter(prefix="/prestamos", tags=["Préstamos"])

class PrestamoCreate(BaseModel):
    libro_id: int
    usuario_id: int

# Solicitar préstamo con lógica FIFO
@router.post("/solicitar")
def solicitar_prestamo(prestamo: PrestamoCreate):
    conn = get_connection()
    cursor = conn.cursor()
    
    # Verificar disponibilidad del libro
    cursor.execute("""
        SELECT cantidad_disponible FROM libros 
        WHERE id = %s
    """, (prestamo.libro_id,))
    libro = cursor.fetchone()
    
    if not libro:
        conn.close()
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    
    if libro[0] > 0:
        # Hay disponibilidad → préstamo directo
        cursor.execute("""
            UPDATE libros SET cantidad_disponible = cantidad_disponible - 1 
            WHERE id = %s
        """, (prestamo.libro_id,))
        cursor.execute("""
            INSERT INTO prestamos (libro_id, usuario_id) 
            VALUES (%s, %s) RETURNING id
        """, (prestamo.libro_id, prestamo.usuario_id))
        prestamo_id = cursor.fetchone()[0]
        conn.commit()
        conn.close()
        return {
            "mensaje": "Préstamo registrado exitosamente",
            "prestamo_id": prestamo_id,
            "estado": "activo"
        }
    else:
        # No hay disponibilidad → entra a la cola FIFO
        cursor.execute("""
            INSERT INTO cola_solicitudes (libro_id, usuario_id) 
            VALUES (%s, %s) RETURNING id, 
            (SELECT COUNT(*) FROM cola_solicitudes 
             WHERE libro_id = %s AND estado = 'en_espera')
        """, (prestamo.libro_id, prestamo.usuario_id, prestamo.libro_id))
        resultado = cursor.fetchone()
        conn.commit()
        conn.close()
        return {
            "mensaje": "Libro no disponible. Agregado a la cola de espera",
            "cola_id": resultado[0],
            "posicion_en_cola": resultado[1],
            "estado": "en_espera"
        }

# Devolver un libro
@router.put("/devolver/{prestamo_id}")
def devolver_libro(prestamo_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    
    # Registrar devolución
    cursor.execute("""
        UPDATE prestamos 
        SET estado = 'devuelto', fecha_devolucion = CURRENT_TIMESTAMP
        WHERE id = %s AND estado = 'activo'
        RETURNING libro_id
    """, (prestamo_id,))
    resultado = cursor.fetchone()
    
    if not resultado:
        conn.close()
        raise HTTPException(status_code=404, detail="Préstamo no encontrado")
    
    libro_id = resultado[0]
    
    # Verificar si hay alguien en la cola FIFO
    cursor.execute("""
        SELECT id, usuario_id FROM cola_solicitudes 
        WHERE libro_id = %s AND estado = 'en_espera'
        ORDER BY fecha_solicitud ASC 
        LIMIT 1
    """, (libro_id,))
    siguiente = cursor.fetchone()
    
    if siguiente:
        # Asignar el libro al siguiente en la cola
        cursor.execute("""
            UPDATE cola_solicitudes SET estado = 'atendido' 
            WHERE id = %s
        """, (siguiente[0],))
        cursor.execute("""
            INSERT INTO prestamos (libro_id, usuario_id) 
            VALUES (%s, %s)
        """, (libro_id, siguiente[1]))
        mensaje = f"Libro asignado al siguiente usuario en cola (ID: {siguiente[1]})"
    else:
        # No hay cola → aumentar disponibilidad
        cursor.execute("""
            UPDATE libros SET cantidad_disponible = cantidad_disponible + 1 
            WHERE id = %s
        """, (libro_id,))
        mensaje = "Libro devuelto y disponible"
    
    conn.commit()
    conn.close()
    return {"mensaje": mensaje}

# Ver préstamos activos
@router.get("/activos")
def ver_prestamos_activos():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.id, l.titulo, u.nombre, u.cedula, p.fecha_prestamo
        FROM prestamos p
        JOIN libros l ON p.libro_id = l.id
        JOIN usuarios u ON p.usuario_id = u.id
        WHERE p.estado = 'activo'
        ORDER BY p.fecha_prestamo ASC
    """)
    prestamos = cursor.fetchall()
    conn.close()
    
    return [
        {
            "prestamo_id": p[0],
            "titulo": p[1],
            "usuario": p[2],
            "cedula": p[3],
            "fecha_prestamo": p[4]
        }
        for p in prestamos
    ]