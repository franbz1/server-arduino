import serial
import time
import re
import json

class ConexionESP32:
    def __init__(self, puerto: str, velocidad: int):
        self.puerto = puerto
        self.velocidad = velocidad
        self.conexion_serial = None

    def iniciar_conexion(self):
        try:
            if self.conexion_serial and self.conexion_serial.is_open:
                return True
            self.conexion_serial = serial.Serial(self.puerto, self.velocidad, timeout=1)
            time.sleep(2)  # Tiempo para estabilizar conexión
            return True
        except serial.SerialException as e:
            print(f"Error al conectar con el ESP32: {e}")
            return False

    def obtener_datos_ultimo_experimento(self):
        try:
            if self.conexion_serial and self.conexion_serial.is_open:
                self.conexion_serial.write(b"datos\n")  # Enviar comando al ESP32
                time.sleep(1)  # Esperar respuesta
                respuesta = self.conexion_serial.read_all().decode('utf-8').strip()
                return respuesta if respuesta.startswith("Datos:") else "No se recibieron datos."
            return "Error: conexión no abierta."
        except Exception as e:
            return f"Error al obtener datos: {e}"

    def cerrar_conexion(self):
        if self.conexion_serial and self.conexion_serial.is_open:
            self.conexion_serial.close()
            return True
        return False

    def iniciar_experimento(self):
        try:
            if self.conexion_serial and self.conexion_serial.is_open:
                self.conexion_serial.write(b"inicio\n")  # Enviar comando al ESP32
                time.sleep(1)  # Esperar respuesta
                respuesta = self.conexion_serial.read_all().decode('utf-8').strip()

                # Filtrar solo líneas que contienen JSON con "estado" o "resultados"
                lineas = respuesta.split('\r\n')
                jsons_validos = [
                    json.loads(linea) for linea in lineas if re.match(r'^\{.*\}$', linea)
                ]
                return jsons_validos if jsons_validos else "No se encontraron datos relevantes."
            return "Error: conexión no abierta."
        except Exception as e:
            return f"Error al obtener datos: {e}"
