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
            return jsonify({"erro":"Nenhum imóvel encontrado"}), 404

        return jsonify([imovel_to_dict(i) for i in imoveis]), 200

    if cidade:
        cursor.execute("SELECT * FROM imoveis WHERE cidade = %s", (cidade,))
        imoveis = cursor.fetchall()
        cursor.close()
        conn.close()

        if not imoveis:
            return jsonify({"erro":"Nenhum imóvel encontrado"}),404

        return jsonify([imovel_to_dict(i) for i in imoveis]), 200

    cursor.execute("SELECT * FROM imoveis")
    imoveis = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify([imovel_to_dict(t) for t in imoveis]), 200

@app.route("/imoveis/<int:id>", methods=["GET"])
def buscar_imovel(id):
    conn = conectar_banco()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM imoveis WHERE id = %s",
        (id,)
    )

    imovel = cursor.fetchone()

    cursor.close()
    conn.close()

    if not imovel:
        return jsonify({"erro": "Imóvel não encontrado"}), 404

    return jsonify(imovel_to_dict(imovel)), 200

@app.route("/imoveis", methods=["POST"])
def adicionar_imovel():
    imovel = request.get_json()
    campos_obrigatorios = [
        "logradouro",
        "tipo_logradouro",
        "bairro",
        "cidade",
        "cep",
        "tipo",
        "valor",
        "data_aquisicao"
    ]

    if imovel is None or any(campo not in imovel for campo in campos_obrigatorios):
        return jsonify({
            "erro": "Campos obrigatórios: logradouro, tipo_logradouro, bairro, cidade, cep, tipo, valor, data_aquisicao"
        }), 400
    
    conn = conectar_banco()
    cursor = conn.cursor()

    logradouro =  imovel.get("logradouro")
    tipo_logradouro =  imovel.get("tipo_logradouro")
    bairro =  imovel.get("bairro")
    cidade =  imovel.get("cidade")
    cep =  imovel.get("cep")
    tipo =  imovel.get("tipo")
    valor =  imovel.get("valor")
    data_aquisicao =  imovel.get("data_aquisicao")

    cursor.execute("INSERT INTO imoveis (logradouro, tipo_logradouro, bairro, cidade, cep, tipo, valor, data_aquisicao) VALUES (%s, %s, %s, %s ,%s, %s, %s, %s)",
                   (logradouro, tipo_logradouro, bairro, cidade, cep, tipo, valor, data_aquisicao))
    conn.commit()
    id = cursor.lastrowid

    cursor.close()
    conn.close()

    return jsonify({"id":id}), 201

@app.route("/imoveis/<int:id>", methods=["PUT"])
def atualizar_imovel(id):
    imovel = request.get_json()
    campos_obrigatorios = [
    "logradouro",
    "tipo_logradouro",
    "bairro",
    "cidade",
    "cep",
    "tipo",
    "valor",
    "data_aquisicao"
]
    if imovel is None or any(campo not in imovel for campo in campos_obrigatorios):
        return jsonify({
            "erro": "Campos obrigatórios: logradouro, tipo_logradouro, bairro, cidade, cep, tipo, valor, data_aquisicao"
        }), 400
    
    conn = conectar_banco()
    cursor = conn.cursor()

    logradouro =  imovel.get("logradouro")
    tipo_logradouro =  imovel.get("tipo_logradouro")
    bairro =  imovel.get("bairro")
    cidade =  imovel.get("cidade")
    cep =  imovel.get("cep")
    tipo =  imovel.get("tipo")
    valor =  imovel.get("valor")
    data_aquisicao =  imovel.get("data_aquisicao")

    cursor.execute("UPDATE imoveis SET logradouro = %s , tipo_logradouro = %s , bairro = %s , cidade = %s , cep = %s , tipo = %s , valor = %s , data_aquisicao = %s WHERE id  = %s ",
                    (logradouro, tipo_logradouro, bairro, cidade, cep, tipo, valor, data_aquisicao, id))
    conn.commit()

    if cursor.rowcount == 0:
        cursor.close()
        conn.close()
        return jsonify({"erro": "Imóvel não encontrado"}), 404

    cursor.close()
    conn.close()

    return jsonify({"mensagem": "Imóvel atualizado com sucesso!"}), 200

@app.route("/imoveis/<int:id>", methods=["DELETE"])
def deletar_imovel(id):
    conn = conectar_banco()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM imoveis WHERE id= %s",
            (id,))
    conn.commit()

    if cursor.rowcount == 0:
        cursor.close()
        conn.close()
        return jsonify({"erro": "Imóvel não encontrado"}), 404

    cursor.close()
    conn.close()

    return jsonify({"mensagem": "Imóvel apagado com sucesso!"}), 200


if __name__ == "__main__":
    app.run(debug=True)