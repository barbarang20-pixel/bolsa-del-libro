from fastapi import FastAPI
from app.routers import libros, usuarios, prestamos

app = FastAPI(
    title="Bolsa del Libro - Ingeniería Eléctrica UCV",
    description="Sistema de gestión bibliotecaria con arquitectura de microservicios",
    version="1.0.0"
)

# Registrar los routers
app.include_router(libros.router)
app.include_router(usuarios.router)
app.include_router(prestamos.router)

@app.get("/")
def inicio():
    return {
        "mensaje": "Servidor de la Bolsa del Libro - EIE UCV",
        "version": "1.0.0",
        "estado": "activo"
    }