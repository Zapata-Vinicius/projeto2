from flask import app, Flask, request, jsonify
import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

def conectar_banco():
    ca_path = os.getenv("DB_SSL_CA","ca.pem")
    
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        port=int(os.getenv("DB_PORT", 3306)),
        ssl_ca=ca_path,
        ssl_verify_cert=True
    )

def imovel_to_dict (row):
    return {
        "id": row[0],
        "logradouro": row[1],
        "tipo_logradouro": row[2],
        "bairro": row[3],
        "cidade": row[4],
        "cep": row[5],
        "tipo": row[6],
        "valor": float(row[7]),
        "data_aquisicao": row[8]
    }

@app.route("/imoveis", methods=['GET'])
def listar_imoveis ():
    tipo = request.args.get("tipo")
    cidade = request.args.get("cidade")

    conn = conectar_banco()
    cursor = conn.cursor()

    if tipo:
        cursor.execute("SELECT * FROM imoveis WHERE tipo = %s", (tipo,))
        imoveis = cursor.fetchall()
        cursor.close()
        conn.close()

        if not imoveis:
            return jsonify({"erro":"nenhum imóvel encontrado"}), 404

        return jsonify([imovel_to_dict(i) for i in imoveis]), 200

    if cidade:
        cursor.execute("SELECT * FROM imoveis WHERE cidade = %s", (cidade,))
        imoveis = cursor.fetchall()
        cursor.close()
        conn.close()

        if not imoveis:
            return jsonify({"erro":"nenhum imóvel encontrado"}),404

        return jsonify([imovel_to_dict(i) for i in imoveis]), 200

    cursor.execute("SELECT * FROM imoveis")
    imoveis = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify([imovel_to_dict(t) for t in imoveis]), 200


if __name__ == "__main__":
    app.run(debug=True)