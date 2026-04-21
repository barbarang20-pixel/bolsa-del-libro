from fastapi import APIRouter, HTTPException
from app.database import get_connection
from pydantic import BaseModel

router = APIRouter(prefix="/libros", tags=["Libros"])

# Ver todos los libros
@router.get("/")
def obtener_libros():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, titulo, autor, isbn, 
               cantidad_total, cantidad_disponible, codigo_qr 
        FROM libros
    """)
    libros = cursor.fetchall()
    conn.close()
    
    return [
        {
            "id": l[0],
            "titulo": l[1],
            "autor": l[2],
            "isbn": l[3],
            "cantidad_total": l[4],
            "cantidad_disponible": l[5],
            "codigo_qr": l[6]
        }
        for l in libros
    ]

# Buscar libro por QR
@router.get("/qr/{codigo_qr}")
def buscar_por_qr(codigo_qr: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, titulo, autor, cantidad_disponible 
        FROM libros 
        WHERE codigo_qr = %s
    """, (codigo_qr,))
    libro = cursor.fetchone()
    conn.close()
    
    if not libro:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    
    return {
        "id": libro[0],
        "titulo": libro[1],
        "autor": libro[2],
        "disponible": libro[3] > 0,
        "cantidad_disponible": libro[3]
    }

# Buscar libro por título
@router.get("/buscar/{titulo}")
def buscar_por_titulo(titulo: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, titulo, autor, cantidad_disponible 
        FROM libros 
        WHERE titulo ILIKE %s
    """, (f"%{titulo}%",))
    libros = cursor.fetchall()
    conn.close()
    
    return [
        {
            "id": l[0],
            "titulo": l[1],
            "autor": l[2],
            "cantidad_disponible": l[3]
        }
        for l in libros
    ]# Endpoint temporal para reset de datos
@router.post("/reset-datos")
def reset_datos():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("TRUNCATE TABLE cola_solicitudes, prestamos RESTART IDENTITY CASCADE")
        cursor.execute("UPDATE libros SET titulo='Circuitos Eléctricos', autor='Nilsson & Riedel', cantidad_total=3, cantidad_disponible=3 WHERE codigo_qr='QR-001'")
        cursor.execute("UPDATE libros SET titulo='Señales y Sistemas', autor='Oppenheim & Willsky', cantidad_total=2, cantidad_disponible=2 WHERE codigo_qr='QR-002'")
        cursor.execute("UPDATE libros SET titulo='Comunicaciones Analógicas', autor='Haykin', cantidad_total=2, cantidad_disponible=2 WHERE codigo_qr='QR-003'")
        cursor.execute("UPDATE libros SET titulo='Electrónica', autor='Boylestad & Nashelsky', cantidad_total=4, cantidad_disponible=4 WHERE codigo_qr='QR-004'")
        cursor.execute("UPDATE libros SET titulo='Matemáticas para Ingenieros', autor='Kreyszig', cantidad_total=3, cantidad_disponible=3 WHERE codigo_qr='QR-005'")
        cursor.execute("UPDATE libros SET titulo='Teoría Electromagnética', autor='Hayt & Buck', cantidad_total=2, cantidad_disponible=2 WHERE codigo_qr='QR-006'")
        cursor.execute("UPDATE libros SET cantidad_total=2, cantidad_disponible=2 WHERE codigo_qr='QR-007'")
        cursor.execute("UPDATE libros SET cantidad_total=2, cantidad_disponible=2 WHERE codigo_qr='QR-008'")
        cursor.execute("UPDATE libros SET cantidad_total=2, cantidad_disponible=2 WHERE codigo_qr='QR-002'")
        conn.commit()
        conn.close()
        return {"mensaje": "Base de datos reseteada correctamente"}
    except Exception as e:
        conn.rollback()
        conn.close()
        return {"error": str(e)} 
    
class LibroCreate(BaseModel):
    titulo: str
    autor: str
    isbn: str
    cantidad_total: int
    codigo_qr: str

@router.post("/")
def crear_libro(libro: LibroCreate):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO libros (titulo, autor, isbn, cantidad_total, cantidad_disponible, codigo_qr)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (libro.titulo, libro.autor, libro.isbn,
              libro.cantidad_total, libro.cantidad_total, libro.codigo_qr))
        nuevo_id = cursor.fetchone()[0]
        conn.commit()
        conn.close()
        return {"mensaje": "Libro agregado exitosamente", "id": nuevo_id}
    except Exception as e:
        conn.rollback()
        conn.close()
        return {"error": str(e)}