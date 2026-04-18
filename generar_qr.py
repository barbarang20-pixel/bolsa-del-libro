import qrcode
import os
from app.database import get_connection

# Crear carpeta si no existe
os.makedirs("qr_codes", exist_ok=True)

def generar_qr_libros():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, titulo, autor, codigo_qr FROM libros")
    libros = cursor.fetchall()
    conn.close()
    
    for libro in libros:
        id_libro, titulo, autor, codigo_qr = libro
        
        # Información que tendrá el QR
        url = f"http://127.0.0.1:8000/libros/qr/{codigo_qr}"
        
        # Generar el QR
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)
        
        # Crear imagen
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Guardar con nombre descriptivo
        nombre_archivo = f"qr_codes/{codigo_qr}_{titulo[:20].replace(' ', '_')}.png"
        img.save(nombre_archivo)
        
        print(f"✅ QR generado: {nombre_archivo}")
        print(f"   Libro: {titulo} - {autor}")
        print(f"   URL: {url}\n")

if __name__ == "__main__":
    print("Generando códigos QR...\n")
    generar_qr_libros()
    print("¡Todos los QR fueron generados en la carpeta qr_codes/!")