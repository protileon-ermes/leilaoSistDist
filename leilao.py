import datetime
import sqlite3
import hashlib

from functools import wraps
from flask import Flask, render_template, request, redirect, flash, url_for, session

con = sqlite3.connect("banco.sqlite", check_same_thread=False)
con.row_factory = sqlite3.Row

app = Flask(__name__)
app.secret_key = 'CHAVE_SESSAO'

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            flash('Voce precisa logar', 'error')
            return redirect(location='/login')
        return f(*args, **kwargs)
    return decorated_function

@app.get('/')
@login_required
def home():
    return render_template('home.html')

@app.get('/login')
def login():
    return render_template('login.html')

@app.post('/login_executar')
def login_executar():
    email = request.form['email']
    senha = request.form['senha']
    
    usuario = con.execute('SELECT * FROM usuarios WHERE email = ?', (email,)).fetchone()

    if usuario and usuario['senha'] == hashlib.md5(senha.encode('utf-8')).hexdigest():
        session['logged_in'] = True
        session['usuario_id'] = usuario['id']
        return redirect(location="/")
    else:
        flash('email/senha invalidos!', 'error')

    return redirect(location="/")

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(location="/login")

@app.get('/leiloes')
@login_required
def leiloes():
    leiloes = con.cursor().execute("""
        SELECT l.*, u.email as usuario_email,
        (SELECT MAX(lan.valor) FROM lances lan WHERE lan.leilao_id = l.id) as maior_lance 
        FROM leiloes l 
        INNER JOIN usuarios u ON l.usuario_id = u.id
    """).fetchall()

    leiloes_list = []
    for leilao in leiloes:
        leilao_dict = dict(leilao)
        if leilao_dict['maior_lance']:
            vencedor = con.execute('SELECT u.email FROM lances l INNER JOIN usuarios u ON l.usuario_id = u.id WHERE l.leilao_id = ? AND l.valor = ?', (leilao_dict['id'], leilao_dict['maior_lance'])).fetchone()
            leilao_dict['vencedor'] = vencedor['email'] if vencedor else None
        else:
            leilao_dict['vencedor'] = None
        leiloes_list.append(leilao_dict)

    return render_template('leiloes.html', leiloes=leiloes_list)



@app.get('/cadastro')
def cadastro():
    return render_template('cadastro.html')

@app.post('/cadastro_salvar')
def cadastro_salvar():
    email = request.form['email']
    senha = request.form['senha']

    con.execute('INSERT INTO usuarios (email, senha) VALUES (?, ?)', (email,  hashlib.md5(senha.encode('utf-8')).hexdigest()))
    con.commit()

    return redirect(location="/login")

@app.get('/criar_leilao')
@login_required
def criar_leilao():
    return render_template('criar_leilao.html')

@app.post('/leilao_salvar')
@login_required
def leilao_salvar():
    nome = request.form['nome']
    valor_inicial = request.form['valor_inicial']
    data_inicio = request.form['data_inicio']
    data_fim = request.form['data_fim']
    usuario_id = session['usuario_id']

    con.execute('INSERT INTO leiloes (nome, valor_inicial, data_inicio, data_fim, usuario_id) VALUES (?, ?, ?, ?, ?)', 
                (nome, valor_inicial, data_inicio, data_fim, usuario_id))
    con.commit()

    return redirect(location="/leiloes")


@app.get('/criar_lance/<leilao_id>')
@login_required
def criar_lance(leilao_id):
    return render_template('criar_lance.html', leilao_id=leilao_id)

@app.post('/lance_salvar')
@login_required
def lance_salvar():
    usuario_id = session['usuario_id']
    valor = request.form['valor']
    leilao_id = request.form['leilao_id']

    # Verificar se a data de fim do leilão é anterior à data atual
    leilao = con.execute('SELECT * FROM leiloes WHERE id = ?', (leilao_id,)).fetchone()
    data_fim = datetime.datetime.strptime(leilao['data_fim'], '%Y-%m-%dT%H:%M')
    if datetime.datetime.now() > data_fim:
        flash('Este leilão já foi encerrado.', 'error')
        return redirect('/leiloes')

    criador = con.execute('SELECT usuario_id FROM leiloes WHERE id = ?', (leilao_id,)).fetchone()

    if criador and criador['usuario_id'] == usuario_id:
        flash('Você não pode dar lances no seu próprio leilão!', 'error')
        return redirect(location="/leiloes")

    con.execute('INSERT INTO lances (valor, leilao_id, usuario_id) VALUES (?, ?, ?)', (valor, leilao_id, usuario_id))
    con.commit()

    return redirect(location="/leiloes")

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
