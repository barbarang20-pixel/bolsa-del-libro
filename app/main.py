from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.routers import libros, usuarios, prestamos

app = FastAPI(
    title="Bolsa del Libro - Ingeniería Eléctrica UCV",
    description="Sistema de gestión bibliotecaria con arquitectura de microservicios",
    version="1.0.0"
)

# Registrar los routers de la API
app.include_router(libros.router)
app.include_router(usuarios.router)
app.include_router(prestamos.router)

# Servir archivos estáticos (el frontend)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Ruta raíz → sirve el frontend
@app.get("/")
def inicio():
    return FileResponse("static/index.html")