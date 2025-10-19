
"""
A Flask-based RESTful API with token-based authentication and PostgreSQL integration.
"""
import os
from flask import Flask, request, jsonify
import psycopg2
app = Flask(__name__)


TOKEN_VALIDO = "token-secreto"

def autenticar():
    """
    check for valid Bearer token in Authorization header
    1. If header is missing or doesn't start with 'Bearer ', return False
    2. Extract token and compare with TOKEN_VALIDO
    3. Return True if valid, else False.
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return False
    token = auth_header.split(" ")[1]
    return token == TOKEN_VALIDO

@app.before_request
def verificar_token():
    """
    This is executed before each request to verify whether the authorization 
    token is valid.
    If it is invalid, access is denied.
    """
    if not autenticar():
        return jsonify({"error": "No autorizado"}), 401

def get_db_connection():
    """
    Establish a connection to the PostgreSQL database using environment variables.
    Returns the connection object.
    """
    try:
        user = os.environ.get("POSTGRES_USER")
        password = os.environ.get("POSTGRES_PASSWORD")
        host = os.environ.get("POSTGRES_HOST")
        db = os.environ.get("POSTGRES_DB")

        conn_str = f"postgresql://{user}:{password}@{host}:5432/{db}"

        return psycopg2.connect(conn_str, connect_timeout=5)
    except Exception as e:
        print("Error al conectar a la DB:", e)
        raise

@app.route("/usuarios", methods=["GET"])
def obtener_usuarios():
    """P
    Fetch all users from the 'usuarios' table and return as JSON.
    1. Connect to the database.
    2. Execute SELECT query.
    3. Fetch results and format as list of dictionaries.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, correo FROM usuarios;")
    rows = cursor.fetchall()

    usuarios = []
    for row in rows:
        usuarios.append({
            "id": row[0],
            "nombre": row[1],
            "correo": row[2]
        })

    cursor.close()
    conn.close()

    return jsonify(usuarios), 200

@app.route("/metodos", methods=["GET"])
def info_metodos():
    """
    Provide information about the HTTP methods supported by the API.
    
    """
    return jsonify({
        "GET": "Obtener datos. No necesita token.",
        "POST": "Crear nuevo recurso. Requiere token Bearer.",
        "PUT": "Actualizar recurso. Requiere token Bearer.",
        "DELETE": "Eliminar recurso. Requiere token Bearer."
    }), 200

@app.route("/items", methods=["GET"])
def obtener_items():
    """
    Fetch all items from the 'items' table and return as JSON.
    
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre FROM items;")
    rows = cursor.fetchall()
    items = []
    for row in rows:
        items.append({
            "id": row[0],
            "nombre": row[1],
        })

    cursor.close()
    conn.close()
    return jsonify(items), 200

@app.route("/items", methods=["POST"])
def crear_item():
    """
    Create a new item in the 'items' table.
    Expects JSON body with 'nombre' field
    
    """
    nuevo_item = request.get_json()
    nombre = nuevo_item.get("nombre")
    if not nombre:
        return jsonify({"error": "Dato faltante 'nombre'"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO items (nombre) VALUES (%s) RETURNING id;", (nombre,))
    nuevo_id = cursor.fetchone()[0]
    conn.commit()

    cursor.close()
    conn.close()
    return jsonify({"mensaje": "Item creado", "id": nuevo_id, "nombre": nombre}), 201

@app.route("/items/<int:item_id>", methods=["PUT"])
def actualizar_item(item_id):
    """
    Update an existing item in the 'items' table by ID.
    Expects JSON body with 'nombre' field
    """
    datos = request.get_json()
    nombre = datos.get("nombre")
    if not nombre:
        return jsonify({"error": "Dato faltante 'nombre'"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE items SET nombre = %s WHERE id = %s RETURNING id;", (nombre, item_id))
    actualizado = cursor.fetchone()
    conn.commit()

    cursor.close()
    conn.close()

    if actualizado is not None:
        return jsonify({"mensaje": "Item actualizado", "id": item_id, "nombre": nombre}), 200
    else:
        return jsonify({"error": "Item no encontrado"}), 404


@app.route("/items/<int:item_id>", methods=["DELETE"])
def eliminar_item(item_id):
    """
    Delete an item from the 'items' table by ID.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM items WHERE id = %s RETURNING id;', (item_id,))
    eliminado = cursor.fetchone()
    conn.commit()

    cursor.close()
    conn.close()

    if eliminado:
        return jsonify({"mensaje": "Item eliminado", "id": item_id}), 200
    else:
        return jsonify({"error": "Item no encontrado"}), 404

@app.route("/rutas", methods=["GET"])
def listar_rutas():
    """
    List all available routes in the Flask application.
    """
    rutas = []
    for regla in app.url_map.iter_rules():
        rutas.append({
            "ruta": str(regla),
            "metodos": list(regla.methods)
        })
    return jsonify(rutas)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
