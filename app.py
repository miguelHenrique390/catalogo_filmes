import os
import uuid
import json
from flask import Flask, request, jsonify, render_template, redirect, url_for
from psycopg2.extras import RealDictCursor
from database import get_connection

app = Flask(__name__)

# --- CONFIGURAÇÕES DE UPLOAD ---
# Define a pasta onde os arquivos serão salvos (static/uploads)
UPLOAD_FOLDER = os.path.join('static', 'uploads')
# Permite apenas as extensões solicitadas
ALLOWED_EXTENSIONS = {'jpeg', 'jpg', 'png'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# -------------------------------

# Teste API
@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "API de catalogo de filmes"}), 200


# Ping
@app.route('/ping', methods=['GET'])
def ping():
    conn = get_connection()
    conn.close()
    return jsonify({"message": "pong! API Rodando!", "db": str(conn)}), 200


# Listar todos os filmes
@app.route('/filmes', methods=['GET'])
def listar_filmes():
    sql = "SELECT * FROM filmes"
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(sql)
        filmes = cursor.fetchall()
        print('filmes: --------------------------', filmes)
        conn.close()
        return render_template("index.html", filmes=filmes)
    except Exception as ex:
        print('erro: ', str(ex))
        return jsonify({"message": "erro ao listar filmes"}), 500


@app.route("/novo", methods=["GET", "POST"])
def novo_filme():
    if request.method == "POST":
        try:
            titulo = request.form["titulo"]
            genero = request.form["genero"]
            ano = request.form["ano"]

            # ATENÇÃO: Puxando pelo name="capa" que está no seu novo_filme.html
            file = request.files.get("capa")

            if file and allowed_file(file.filename):
                # 1. Renomeia para uma hash única
                extensao = file.filename.rsplit('.', 1)[1].lower()
                nome_hash = f"{uuid.uuid4().hex}.{extensao}"

                # 2. Salva na pasta static/uploads
                caminho_salvar = os.path.join(app.config['UPLOAD_FOLDER'], nome_hash)
                file.save(caminho_salvar)
            else:
                return jsonify({"message": "Arquivo inválido. Permitido apenas JPEG, JPG, PNG."}), 400

            # 3. Salva no banco de dados apenas o nome do arquivo (hash)
            sql = "INSERT INTO filmes (titulo, genero, ano, url_capa) VALUES (%s, %s, %s, %s)"
            params = [titulo, genero, ano, nome_hash]

            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(sql, params)
            conn.commit()
            conn.close()
            return redirect(url_for("listar_filmes"))

        except Exception as ex:
            print('erro: ', str(ex))
            return jsonify({"message": "erro ao cadastrar filme"}), 500

    return render_template("novo_filme.html")


@app.route("/editar/<int:id>", methods=["GET", "POST"])
def editar_filme(id):
    try:
        conn = get_connection()
        if request.method == "POST":
            titulo = request.form["titulo"]
            genero = request.form["genero"]
            ano = request.form["ano"]

            # Adaptando a edição para também suportar upload (opcional)
            file = request.files.get("capa")

            if file and allowed_file(file.filename):
                extensao = file.filename.rsplit('.', 1)[1].lower()
                nome_hash = f"{uuid.uuid4().hex}.{extensao}"
                caminho_salvar = os.path.join(app.config['UPLOAD_FOLDER'], nome_hash)
                file.save(caminho_salvar)
                url_capa = nome_hash
            else:
                # Se não enviou imagem nova, pega o valor atual que deve vir de um input hidden
                url_capa = request.form.get("url_capa_atual")

            sql_update = "UPDATE filmes SET titulo = %s, genero = %s, ano = %s, url_capa = %s WHERE id = %s"
            params = [titulo, genero, ano, url_capa, id]

            cursor = conn.cursor()
            cursor.execute(sql_update, params)
            conn.commit()
            conn.close()
            return redirect(url_for("listar_filmes"))

        cursor = conn.cursor(cursor_factory=RealDictCursor)
        sql = "SELECT * FROM filmes WHERE id = %s"
        params = [id]
        cursor.execute(sql, params)
        filme = cursor.fetchone()
        conn.close()

        if filme is None:
            return redirect(url_for("listar_filmes"))
        return render_template("editar_filme.html", filme=filme)
    except Exception as ex:
        print('erro: ', str(ex))
        return jsonify({"message": "erro ao editar filme"}), 500


@app.route("/deletar/<int:id>", methods=["POST"])
def deletar_filme(id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        sql = "DELETE FROM filmes WHERE id = %s"
        params = [id]
        cursor.execute(sql, params)
        conn.commit()
        conn.close()
        return redirect(url_for("listar_filmes"))
    except Exception as ex:
        print('erro: ', str(ex))
        return jsonify({"message": "erro ao deletar filme"}), 500


if __name__ == '__main__':
    app.run(debug=True)