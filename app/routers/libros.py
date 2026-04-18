from fastapi import APIRouter, HTTPException
from app.database import get_connection

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
    ]