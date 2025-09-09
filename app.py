from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import sqlite3
from collections import defaultdict, Counter
import os

# Função auxiliar para templates
def get_color_code(color):
    colors = {
        'Preto': '#000000',
        'Branco': '#ffffff', 
        'Azul': '#0066cc',
        'Vermelho': '#cc0000',
        'Verde': '#00cc00',
        'Amarelo': '#cccc00',
        'Rosa': '#ff69b4',
        'Roxo': '#8B00FF',
        'Laranja': '#ff8c00',
        'Cinza': '#808080',
        'Marrom': '#8B4513'
    }
    return colors.get(color, '#6c757d')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///loja_tenis.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'shop_pra_mim_2024_secreto'

db = SQLAlchemy(app)

# Configurar Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Por favor, faça login para acessar esta página.'
login_manager.login_message_category = 'info'

# Modelos de dados
class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    telefone = db.Column(db.String(20))
    genero = db.Column(db.String(10), nullable=False)  # M/F
    idade = db.Column(db.Integer, nullable=False)
    tamanho_preferido = db.Column(db.String(10))
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    
    vendas = db.relationship('Venda', backref='cliente', lazy=True)

class Venda(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)
    valor = db.Column(db.Float, nullable=False)
    data_venda = db.Column(db.DateTime, default=datetime.utcnow)
    cor_tenis = db.Column(db.String(50), nullable=False)
    tamanho = db.Column(db.String(10), nullable=False)
    marca = db.Column(db.String(50), nullable=False)
    modelo = db.Column(db.String(100), nullable=False)

class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    marca = db.Column(db.String(50), nullable=False)
    modelo = db.Column(db.String(100), nullable=False)
    cor = db.Column(db.String(50), nullable=False)
    tamanho = db.Column(db.String(10), nullable=False)
    preco = db.Column(db.Float, nullable=False)
    data_chegada = db.Column(db.DateTime, default=datetime.utcnow)
    vendido = db.Column(db.Boolean, default=False)

# Rotas de autenticação
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = Usuario.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        
        flash('Usuário ou senha incorretos.', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você foi desconectado com sucesso.', 'success')
    return redirect(url_for('login'))

# Rotas principais
@app.route('/')
@login_required
def index():
    total_clientes = Cliente.query.count()
    total_vendas = Venda.query.count()
    vendas_mes = Venda.query.filter(
        Venda.data_venda >= datetime.now().replace(day=1)
    ).count()
    receita_total = db.session.query(db.func.sum(Venda.valor)).scalar() or 0
    
    return render_template('index.html', 
                         total_clientes=total_clientes,
                         total_vendas=total_vendas,
                         vendas_mes=vendas_mes,
                         receita_total=receita_total)

@app.route('/clientes')
@login_required
def listar_clientes():
    clientes = Cliente.query.all()
    return render_template('clientes.html', clientes=clientes)

@app.route('/cadastrar_cliente', methods=['GET', 'POST'])
@login_required
def cadastrar_cliente():
    if request.method == 'POST':
        cliente = Cliente(
            nome=request.form['nome'],
            email=request.form['email'],
            telefone=request.form['telefone'],
            genero=request.form['genero'],
            idade=int(request.form['idade']),
            tamanho_preferido=request.form['tamanho_preferido']
        )
        db.session.add(cliente)
        db.session.commit()
        return redirect(url_for('listar_clientes'))
    
    return render_template('cadastrar_cliente.html')

@app.route('/vendas')
@login_required
def listar_vendas():
    vendas = Venda.query.join(Cliente).all()
    return render_template('vendas.html', vendas=vendas)

@app.route('/cadastrar_venda', methods=['GET', 'POST'])
@login_required
def cadastrar_venda():
    if request.method == 'POST':
        venda = Venda(
            cliente_id=int(request.form['cliente_id']),
            valor=float(request.form['valor']),
            cor_tenis=request.form['cor_tenis'],
            tamanho=request.form['tamanho'],
            marca=request.form['marca'],
            modelo=request.form['modelo']
        )
        db.session.add(venda)
        db.session.commit()
        return redirect(url_for('listar_vendas'))
    
    clientes = Cliente.query.all()
    return render_template('cadastrar_venda.html', clientes=clientes)

@app.route('/produtos')
@login_required
def listar_produtos():
    produtos = Produto.query.filter_by(vendido=False).all()
    return render_template('produtos.html', produtos=produtos)

@app.route('/cadastrar_produto', methods=['GET', 'POST'])
@login_required
def cadastrar_produto():
    if request.method == 'POST':
        produto = Produto(
            marca=request.form['marca'],
            modelo=request.form['modelo'],
            cor=request.form['cor'],
            tamanho=request.form['tamanho'],
            preco=float(request.form['preco'])
        )
        db.session.add(produto)
        db.session.commit()
        
        # Gerar recomendações para o novo produto
        recomendacoes = gerar_recomendacoes(produto)
        return render_template('recomendacoes.html', produto=produto, recomendacoes=recomendacoes)
    
    return render_template('cadastrar_produto.html')

def gerar_recomendacoes(produto):
    """Gera recomendações de clientes para um produto baseado no histórico de compras"""
    clientes = Cliente.query.all()
    scores = []
    
    for cliente in clientes:
        score = 0
        vendas_cliente = Venda.query.filter_by(cliente_id=cliente.id).all()
        
        if not vendas_cliente:
            # Cliente novo - score baseado apenas em tamanho preferido
            if cliente.tamanho_preferido == produto.tamanho:
                score = 30
            scores.append((cliente, score))
            continue
        
        # Análise de frequência de marca
        marcas = [v.marca for v in vendas_cliente]
        if produto.marca in marcas:
            score += 40 * (marcas.count(produto.marca) / len(marcas))
        
        # Análise de frequência de cor
        cores = [v.cor_tenis for v in vendas_cliente]
        if produto.cor in cores:
            score += 30 * (cores.count(produto.cor) / len(cores))
        
        # Análise de tamanho
        tamanhos = [v.tamanho for v in vendas_cliente]
        if produto.tamanho in tamanhos:
            score += 20
        elif cliente.tamanho_preferido == produto.tamanho:
            score += 15
        
        # Análise de faixa de preço
        valores = [v.valor for v in vendas_cliente]
        if valores:
            valor_medio = sum(valores) / len(valores)
            diferenca_preco = abs(produto.preco - valor_medio) / valor_medio
            if diferenca_preco <= 0.2:  # Até 20% de diferença
                score += 20
            elif diferenca_preco <= 0.5:  # Até 50% de diferença
                score += 10
        
        # Bonus por frequência de compra
        if len(vendas_cliente) >= 3:
            score += 10
        
        scores.append((cliente, score))
    
    # Ordenar por score e retornar top 5
    scores.sort(key=lambda x: x[1], reverse=True)
    return [(cliente, round(score, 2)) for cliente, score in scores[:5] if score > 0]

@app.route('/analytics')
@login_required
def analytics():
    # Estatísticas por marca
    marcas = db.session.query(Venda.marca, db.func.count(Venda.id), db.func.sum(Venda.valor)).group_by(Venda.marca).all()
    
    # Estatísticas por cor
    cores = db.session.query(Venda.cor_tenis, db.func.count(Venda.id)).group_by(Venda.cor_tenis).all()
    
    # Clientes por gênero
    generos = db.session.query(Cliente.genero, db.func.count(Cliente.id)).group_by(Cliente.genero).all()
    
    return render_template('analytics.html', marcas=marcas, cores=cores, generos=generos)

# Registrar função auxiliar no contexto do template
app.jinja_env.globals.update(get_color_code=get_color_code)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Criar usuário admin se não existir
        if Usuario.query.count() == 0:
            admin = Usuario(username='admin', nome='Administrador')
            admin.set_password('123456')
            db.session.add(admin)
            db.session.commit()
    
    # Para hospedagem em produção
    import os
    port = int(os.environ.get('PORT', 5001))
    app.run(debug=False, host='0.0.0.0', port=port)