from flask import Flask, request, jsonify, render_template
import serial
import time

# Configuración de puerto serie
esp32_port = 'COM10'
baud_rate = 115200

# Clase para manejar la conexión con el ESP32
class ESP32Connection:
    def __init__(self, port: str, baud_rate: int):
        self.port = port
        self.baud_rate = baud_rate
        self.serial_connection = None

    def start_connection(self):
        try:
            if self.serial_connection and self.serial_connection.is_open:
                return True
            self.serial_connection = serial.Serial(self.port, self.baud_rate, timeout=1)
            time.sleep(2)  # Tiempo para estabilizar conexión
            return True
        except serial.SerialException as e:
            print(f"Error al conectar con el ESP32: {e}")
            return False

    def get_last_experiment_data(self):
        try:
            if self.serial_connection and self.serial_connection.is_open:
                self.serial_connection.write(b"datos\n")  # Enviar comando al ESP32
                time.sleep(1)  # Esperar respuesta
                response = self.serial_connection.read_all().decode('utf-8').strip()
                return response if response else "No se recibieron datos."
            return "Error: conexión no abierta."
        except Exception as e:
            return f"Error al obtener datos: {e}"

    def close_connection(self):
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
            return True
        return False

# Instancia global de conexión
esp32 = ESP32Connection(esp32_port, baud_rate)

# Configuración de Flask
app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/connect", methods=["GET"])
def connect():
    if esp32.start_connection():
        return jsonify({"status": "Conexión iniciada"})
    return jsonify({"status": "Error al iniciar la conexión"}), 500

@app.route("/data", methods=["GET"])
def get_data():
    response = esp32.get_last_experiment_data()
    return jsonify({"data": response})

@app.route("/disconnect", methods=["GET"])
def disconnect():
    if esp32.close_connection():
        return jsonify({"status": "Conexión cerrada"})
    return jsonify({"status": "Error al cerrar la conexión"}), 500

# Ejecutar la aplicación Flask
if __name__ == "__main__":
    try:
        app.run(host="0.0.0.0", port=5000, debug=False)
    except KeyboardInterrupt:
        esp32.close_connection()
        print("Aplicación detenida.")
