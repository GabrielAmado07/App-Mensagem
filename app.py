from flask import Flask, render_template, request, send_file, session, redirect, url_for, flash

import io

from arvore import Arvore

from email.message import EmailMessage
from email.utils import formataddr


app = Flask(__name__)

app.secret_key = "chave-do-sistema-de-mensagens"


mensagens = []


servidor = {
    "nome": None,
    "senha": None,
    "admin": None,
    "usuarios": []
}


@app.route("/")
def inicio():

    return render_template("inicio.html")


@app.route("/enviar", methods=["POST"])
def enviar():

    if "usuario" not in session:
        return "Você precisa entrar em um servidor."

    usuario_atual = session["usuario"]

    destinatario = request.form["destinatario"]
    mensagem = request.form["mensagem"]
    formato = request.form["formato"]

    if destinatario not in servidor["usuarios"]:
        return "Destinatário não está no servidor."

    arvore = Arvore()

    for caractere in mensagem:
        arvore.inserir(caractere)

    mensagem_criptografada = arvore.pre_ordem(arvore.raiz)

    if formato == "texto":

        mensagens.append({
            "id": len(mensagens),
            "remetente": usuario_atual,
            "destinatario": destinatario,
            "mensagem": mensagem_criptografada,
            "formato": formato
        })

        print("Destinatário:", destinatario)
        print("Mensagem original:", mensagem)
        print("Mensagem criptografada:", mensagem_criptografada)
        print("Formato:", formato)

        return render_template(
            "mensagens.html",
            usuario_atual=usuario_atual,
            usuarios=servidor["usuarios"]
        )

    if formato == "download":

        arquivo = io.BytesIO(
            mensagem_criptografada.encode("utf-8")
        )

        return send_file(
            arquivo,
            as_attachment=True,
            download_name="mensagem_criptografada.txt",
            mimetype="text/plain"
        )

    if formato == "email":

        email = EmailMessage()

        email["From"] = formataddr(
            (usuario_atual, "joao@mensagens.local")
        )

        email["To"] = formataddr(
            (destinatario, "destinatario@mensagens.local")
        )

        email["Subject"] = "Mensagem criptografada"

        email.set_content(
            mensagem_criptografada
        )

        arquivo = io.BytesIO(
            email.as_bytes()
        )

        return send_file(
            arquivo,
            as_attachment=True,
            download_name="mensagem.eml",
            mimetype="message/rfc822"
        )

    if formato == "whatsapp":

        mensagem_whatsapp = {
            "remetente": usuario_atual,
            "destinatario": destinatario,
            "mensagem": mensagem_criptografada
        }

        return render_template(
            "whatsapp.html",
            mensagem=mensagem_whatsapp
        )

    return "Formato de mensagem inválido."




@app.route("/recebidas")
def recebidas():

    if "usuario" not in session:
        return "Você precisa entrar em um servidor."


    usuario_atual = session["usuario"]


    mensagens_recebidas = []


    for mensagem in mensagens:

        if mensagem["destinatario"] == usuario_atual:

            mensagens_recebidas.append(mensagem)


    return render_template(

        "recebidas.html",

        mensagens=mensagens_recebidas

    )


@app.route("/descriptografar", methods=["POST"])
def descriptografar():

    if "usuario" not in session:
        return "Você precisa entrar em um servidor."


    usuario_atual = session["usuario"]


    indice = int(request.form["indice"])


    if indice < 0 or indice >= len(mensagens):

        return "Mensagem não encontrada."


    mensagem = mensagens[indice]


    if mensagem["destinatario"] != usuario_atual:

        return "Você não pode descriptografar esta mensagem."


    mensagem_criptografada = mensagem["mensagem"]


    arvore = Arvore()


    mensagem_original = arvore.descriptografar(
        mensagem_criptografada
    )


    mensagem["descriptografada"] = mensagem_original


    mensagens_recebidas = []


    for mensagem in mensagens:

        if mensagem["destinatario"] == usuario_atual:

            mensagens_recebidas.append(mensagem)


    return render_template(

        "recebidas.html",

        mensagens=mensagens_recebidas

    )


@app.route("/adicionar_usuario", methods=["POST"])
def adicionar_usuario():

    if "usuario" not in session:
        return "Você precisa entrar em um servidor."


    usuario_atual = session["usuario"]


    if usuario_atual != servidor["admin"]:

        return "Apenas o administrador pode adicionar usuários."


    nome = request.form["nome"]


    if nome and nome not in servidor["usuarios"]:

        servidor["usuarios"].append(nome)


    return render_template(

        "servidor.html",

        servidor=servidor,

        usuario_atual=usuario_atual,

        usuarios=servidor["usuarios"]

    )


@app.route("/deletar_usuario", methods=["POST"])
def deletar_usuario():

    if "usuario" not in session:
        return "Você precisa entrar em um servidor."


    usuario_atual = session["usuario"]


    if usuario_atual != servidor["admin"]:

        return "Apenas o administrador pode excluir usuários."


    nome = request.form["nome"]


    if nome == servidor["admin"]:

        return "O administrador não pode ser excluído."


    if nome in servidor["usuarios"]:

        servidor["usuarios"].remove(nome)


    return render_template(

        "servidor.html",

        servidor=servidor,

        usuario_atual=usuario_atual,

        usuarios=servidor["usuarios"]

    )


@app.route("/criar_servidor", methods=["POST"])
def criar_servidor():

    nome = request.form["nome"]

    senha = request.form["senha"]

    admin = request.form["admin"]


    servidor["nome"] = nome

    servidor["senha"] = senha

    servidor["admin"] = admin

    servidor["usuarios"] = [admin]


    session["usuario"] = admin


    return render_template(

        "servidor.html",

        servidor=servidor,

        usuario_atual=admin,

        usuarios=servidor["usuarios"]

    )


@app.route("/servidor")
def pagina_servidor():

    if "usuario" not in session:

        return "Você precisa entrar em um servidor."


    usuario_atual = session["usuario"]


    if servidor["nome"] is None:

        return "Nenhum servidor foi criado."


    if usuario_atual not in servidor["usuarios"]:

        return "Você não faz parte deste servidor."


    return render_template(

        "servidor.html",

        servidor=servidor,

        usuario_atual=usuario_atual,

        usuarios=servidor["usuarios"]

    )


@app.route("/entrar_servidor", methods=["GET", "POST"])
def entrar_servidor():

    if request.method == "GET":

        return render_template("entrar.html")


    nome_servidor = request.form["nome_servidor"]

    senha = request.form["senha"]

    usuario = request.form["usuario"]


    if servidor["nome"] is None:

        return "Nenhum servidor foi criado."


    if nome_servidor != servidor["nome"]:

        return "Nome do servidor incorreto."


    if senha != servidor["senha"]:

        return "Senha incorreta."


    if not usuario:

        return "Digite o nome do usuário."


    if usuario not in servidor["usuarios"]:

        servidor["usuarios"].append(usuario)


    session["usuario"] = usuario


    return render_template(

        "servidor.html",

        servidor=servidor,

        usuario_atual=usuario,

        usuarios=servidor["usuarios"]

    )


@app.route("/mensagens")
def pagina_mensagens():

    if "usuario" not in session:

        return "Você precisa entrar em um servidor."


    usuario_atual = session["usuario"]
    mensagem_descriptografada = session.pop("mensagem_descriptografada", None)


    return render_template(

        "mensagens.html",

        usuario_atual=usuario_atual,

        usuarios=servidor["usuarios"],

        mensagem_descriptografada=mensagem_descriptografada

    )

@app.route("/descriptografar_manual", methods=["POST"])
def descriptografar_manual():

    if "usuario" not in session:
        return "Você precisa entrar em um servidor."

    mensagem_criptografada = request.form.get("mensagem_criptografada")

    if not mensagem_criptografada:
        flash("Por favor, insira o dado necessário novamente para descriptografar.")
        return redirect(url_for("pagina_mensagens"))

    arvore = Arvore()

    mensagem_original = arvore.descriptografar(
        mensagem_criptografada
    )

    session["mensagem_descriptografada"] = mensagem_original

    return redirect(url_for("pagina_mensagens"))

app.run(debug=True)

