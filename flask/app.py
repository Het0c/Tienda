from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

# Ruta para servir un HTML
@app.route('/')
def home():
    return render_template('index.html')

# Ejemplo de API REST: GET
@app.route('/api/saludo', methods=['GET'])
def saludo():
    return jsonify({"mensaje": "Hola desde la API REST"})

# Ejemplo de API REST: POST
@app.route('/api/eco', methods=['POST'])
def eco():
    data = request.get_json()
    return jsonify({"recibido": data})

# Ejemplo de API REST: PUT
@app.route('/api/actualizar/<int:item_id>', methods=['PUT'])
def actualizar(item_id):
    data = request.get_json()
    return jsonify({"item_id": item_id, "nuevo_valor": data})

# Ejemplo de API REST: DELETE
@app.route('/api/eliminar/<int:item_id>', methods=['DELETE'])
def eliminar(item_id):
    return jsonify({"mensaje": f"Item {item_id} eliminado"})

if __name__ == '__main__':
    app.run(debug=True)
