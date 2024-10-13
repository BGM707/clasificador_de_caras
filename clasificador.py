import flet as ft
import base64
import cv2
import threading
import numpy as np

# Iniciar la captura de video
cap = cv2.VideoCapture(0)
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Constante para ajustar la estimación de edad en base a la distancia (ajusta según tus necesidades)
DISTANCE_CONSTANT = 100

# Función mejorada para estimar edad
def estimate_age(face_height):
    # Calcular la edad considerando la altura de la cara y la distancia
    # Aquí asumimos que la altura promedio de una cara es 20 cm a 1 metro de distancia
    distance = DISTANCE_CONSTANT / face_height if face_height > 0 else 1
    age = max(0, min(120, 30 - (distance * 10)))  # Rango de edad entre 0 y 120
    return int(age)

# Función mejorada para estimar género
def estimate_gender(face_height):
    # La estimación de género puede basarse en la altura de la cara
    if face_height > 80:  # Valor de umbral ajustable
        return "Hombre"
    else:
        return "Mujer"

class YouFace(ft.UserControl):
    def __init__(self):
        super().__init__()
        self.you_gender = ft.Text("", size=30, weight="bold", color="white")
        self.you_age = ft.Text("", size=30, weight="bold", color="white")
        self.img = ft.Image(border_radius=ft.border_radius.all(20))
        self.is_running = True  # Control para el hilo

    def update_timer(self):
        while self.is_running:
            _, frame = cap.read()
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

            if len(faces) > 0:
                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    
                    # Estimar edad y género
                    age = estimate_age(h)  # Usar altura de la cara para estimar edad
                    gender = estimate_gender(h)
                    
                    cv2.putText(frame, f"Edad: {age}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                    cv2.putText(frame, f"Género: {gender}", (x, y + h + 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (12, 255, 0), 2)
                    
                    self.you_age.value = str(age)
                    self.you_gender.value = gender
                    self.update()
            else:
                cv2.putText(frame, "No encontré caras", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            
            # Convertir el frame a base64 para mostrar en Flet
            _, im_arr = cv2.imencode(".png", frame)
            im_b64 = base64.b64encode(im_arr).decode("utf-8")
            self.img.src_base64 = im_b64
            
            # Actualizar la interfaz
            self.update()
    
    def build(self):
        return ft.Column([
            self.img,
            ft.Row([
                ft.Text("Género: ", size=30, weight="bold", color="white"),
                self.you_gender
            ]),
            ft.Row([
                ft.Text("Edad: ", size=30, weight="bold", color="white"),
                self.you_age
            ])
        ])

def main(page: ft.Page):
    page.padding = 50
    page.window_width = 800
    page.theme_mode = "Default"

    you_face = YouFace()
    page.add(you_face)
    
    # Iniciar el hilo de actualización de video
    threading.Thread(target=you_face.update_timer, daemon=True).start()

    # Detener la captura al cerrar la ventana
    def on_close(e):
        you_face.is_running = False  # Detener el hilo
        cap.release()
        cv2.destroyAllWindows()
    
    page.on_close = on_close

if __name__ == "__main__":
    ft.app(target=main)
