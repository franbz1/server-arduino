import serial
import time
import re
import json
from typing import Union, List, Dict

class SerialConnection:
    """
    Clase genérica para manejar conexiones seriales.
    """
    def __init__(self, puerto: str, velocidad: int, timeout: int = 1):
        self.puerto = puerto
        self.velocidad = velocidad
        self.timeout = timeout
        self.conexion_serial = None

    def abrir_conexion(self) -> bool:
        """
        Establece la conexión serial.
        """
        try:
            if self.conexion_serial and self.conexion_serial.is_open:
                return True
            self.conexion_serial = serial.Serial(self.puerto, self.velocidad, timeout=self.timeout)
            time.sleep(2)
            return True
        except serial.SerialException as e:
            print(f"Error al abrir la conexión serial: {e}")
            return False

    def cerrar_conexion(self) -> bool:
        """
        Cierra la conexión serial si está abierta.
        """
        if self.conexion_serial and self.conexion_serial.is_open:
            self.conexion_serial.close()
            return True
        return False

    def enviar_comando(self, comando: str) -> Union[dict, str]:
        """
        Envía un comando al dispositivo y espera una respuesta JSON válida.
        """
        try:
            if self.conexion_serial and self.conexion_serial.is_open:
                # Limpiar el buffer antes de enviar el comando
                self.conexion_serial.reset_input_buffer()
                
                # Enviar el comando
                self.conexion_serial.write(comando.encode())
                time.sleep(0.1)  # Pausa para permitir al ESP32 procesar

                buffer_respuesta = ""  # Acumulador para la respuesta
                inicio_timeout = time.time()
                tiempo_maximo = 10  # Tiempo máximo en segundos para recibir un JSON válido

                while True:
                    # Leer datos disponibles
                    if self.conexion_serial.in_waiting > 0:
                        buffer_respuesta += self.conexion_serial.read(self.conexion_serial.in_waiting).decode('utf-8')

                        # Verificar si se puede parsear como JSON
                        try:
                            print(buffer_respuesta)
                            respuesta_json = json.loads(buffer_respuesta.strip())
                            return respuesta_json  # JSON válido recibido
                        except json.JSONDecodeError:
                            # JSON incompleto, seguir leyendo
                            pass

                    # Verificar timeout
                    if time.time() - inicio_timeout > tiempo_maximo:
                        return {
                            "datos": "Error: tiempo de espera agotado para recibir respuesta JSON completa."
                        }

                return {
                    "datos": "Error desconocido durante la recepción del JSON."
                }
            return {
                "datos": "Error: conexión serial no abierta."
            }
        except Exception as e:
            return {"datos": f"Error al enviar comando: {e}"}

class ConexionESP32:
    """
    Clase específica para manejar la conexión con el ESP32.
    """
    def __init__(self, puerto: str, velocidad: int):
        self.serial = SerialConnection(puerto, velocidad)

    def iniciar_conexion(self) -> bool:
        """
        Inicia la conexión con el ESP32.
        """
        return self.serial.abrir_conexion()

    def cerrar_conexion(self) -> bool:
        """
        Cierra la conexión con el ESP32.
        """
        return self.serial.cerrar_conexion()

    def obtener_datos_ultimo_experimento(self) -> str:
        """
        Solicita y obtiene los datos del último experimento del ESP32.
        """
        respuesta = self.serial.enviar_comando("datos\n")
        if respuesta:
            return respuesta
        return "No se recibieron datos." if respuesta else "Error al obtener datos."

    def iniciar_experimento(self) -> Union[List[Dict], str]:
        """
        Envía un comando para iniciar el experimento y procesa la respuesta.
        """
        respuesta = self.serial.enviar_comando("inicio\n")
        if not respuesta:
            return "Error al iniciar el experimento o conexión no abierta."
        return respuesta

    @staticmethod
    def _filtrar_jsons(lineas: List[str]) -> List[Dict]:
        """
        Filtra y valida líneas que contienen JSON.
        """
        jsons_validos = []
        for linea in lineas:
            if re.match(r'^\{.*\}$', linea):  # Verificar formato JSON
                try:
                    jsons_validos.append(json.loads(linea))
                except json.JSONDecodeError:
                    continue
        return jsons_validos
