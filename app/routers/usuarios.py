from fastapi import APIRouter, HTTPException
from app.database import get_connection
from pydantic import BaseModel

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

class UsuarioCreate(BaseModel):
    nombre: str
    cedula: str
    correo: str

# Ver todos los usuarios
@router.get("/")
def obtener_usuarios():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, cedula, correo FROM usuarios")
    usuarios = cursor.fetchall()
    conn.close()
    
    return [
        {
            "id": u[0],
            "nombre": u[1],
            "cedula": u[2],
            "correo": u[3]
        }
        for u in usuarios
    ]

# Registrar nuevo usuario
@router.post("/")
def crear_usuario(usuario: UsuarioCreate):
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO usuarios (nombre, cedula, correo) 
            VALUES (%s, %s, %s) RETURNING id
        """, (usuario.nombre, usuario.cedula, usuario.correo))
        nuevo_id = cursor.fetchone()[0]
        conn.commit()
        conn.close()
        return {"mensaje": "Usuario registrado", "id": nuevo_id}
    except Exception as e:
        conn.rollback()
        conn.close()
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")