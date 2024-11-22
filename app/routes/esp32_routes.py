from flask import Blueprint, jsonify, render_template
from app.services.conexion_esp32 import ConexionESP32
from app.config import PUERTO_ESP32, VELOCIDAD_BAUDIOS

esp32_blueprint = Blueprint("esp32", __name__)
esp32 = None

@esp32_blueprint.route("/")
def inicio():
    return render_template("index.html")

@esp32_blueprint.route("/conectar", methods=["GET"])
def conectar():
    global esp32
    if esp32:
        return jsonify({"estado": "Conexión ya iniciada"})
    try:
        esp32 = ConexionESP32(PUERTO_ESP32, VELOCIDAD_BAUDIOS)
        if esp32.iniciar_conexion():
          return jsonify({"estado": "Conexión iniciada"})
        else:
          return jsonify({"estado": "Error al iniciar la conexión"}), 500
    except Exception as e:
        return jsonify({"estado": f"Error al iniciar la conexión: {e}"}), 500

@esp32_blueprint.route("/datos", methods=["GET"])
def obtener_datos():
    if not esp32:
        return jsonify({"estado": "Error: conexión no iniciada"}), 400
    respuesta = esp32.obtener_datos_ultimo_experimento()
    return jsonify(respuesta)

@esp32_blueprint.route("/desconectar", methods=["GET"])
def desconectar():
    if esp32 and esp32.cerrar_conexion():
        return jsonify({"estado": "Conexión cerrada"})
    return jsonify({"estado": "Error al cerrar la conexión"}), 500

@esp32_blueprint.route("/iniciar", methods=["GET"])
def iniciar():
    if not esp32:
        return jsonify({"estado": "Error: conexión no iniciada"}), 400
    respuesta = esp32.iniciar_experimento()
    return jsonify(respuesta)
