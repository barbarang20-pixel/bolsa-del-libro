from locust import HttpUser, task, between
import random

class EstudianteUCV(HttpUser):
    # Simula el tiempo de espera entre acciones de un estudiante
    wait_time = between(1, 3)
    
    # URL de tu servidor en Render
    host = "https://bolsa-del-libro.onrender.com"
    
    @task(3)
    def consultar_libros(self):
        """Tarea más frecuente: ver todos los libros"""
        self.client.get("/libros/")
    
    @task(3)
    def escanear_qr(self):
        """Simula escanear un QR de un libro"""
        qr_codes = ["QR-001", "QR-002", "QR-003", 
                    "QR-004", "QR-005", "QR-006"]
        qr = random.choice(qr_codes)
        self.client.get(f"/libros/qr/{qr}")
    
    @task(2)
    def buscar_libro(self):
        """Buscar libro por título"""
        titulos = ["Circuitos", "Señales", "Electrónica", 
                   "Matemáticas", "Comunicaciones"]
        titulo = random.choice(titulos)
        self.client.get(f"/libros/buscar/{titulo}")
    
    @task(1)
    def solicitar_prestamo(self):
        """Tarea menos frecuente: solicitar préstamo"""
        libro_id = random.randint(1, 6)
        usuario_id = random.randint(1, 3)
        self.client.post("/prestamos/solicitar", json={
            "libro_id": libro_id,
            "usuario_id": usuario_id
        })
    
    @task(1)
    def ver_prestamos_activos(self):
        """Ver préstamos activos"""
        self.client.get("/prestamos/activos")