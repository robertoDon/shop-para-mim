from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import sqlite3
from collections import defaultdict, Counter
import os
import requests
import json

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

def buscar_informacoes_produto(sku):
    """
    Busca informações do produto via SKU usando APIs públicas
    Retorna um dicionário com as informações encontradas
    """
    try:
        sku = sku.strip().upper()
        # Suporte específico a Nike/Jordan: STYLE-COLOR (ex.: CT1280-001)
        # Vamos construir a URL oficial de imagem do produto no CDN da Nike
        import re
        m = re.match(r"^[A-Z0-9]{5,}-[0-9]{3}$", sku)
        if m:
            style_color = sku.replace('-', '_')
            imagem = f"https://images.nike.com/is/image/DotCom/{style_color}_A_PREM?wid=800&hei=800"
            local = salvar_imagem_local(imagem, sku)
            return {
                'marca': 'Nike',            # Jordan pertence à Nike; manteremos Nike por padrão
                'modelo': sku,               # Sem catálogo local; exibimos o SKU como modelo
                'preco': 0,
                'imagem_url': local or imagem,
                'descricao': f'Imagem oficial para SKU {sku}',
                'cor': 'Não especificada'
            }
        # Tenta buscar no Mercado Livre como alternativa (pode trazer imagem genérica do anúncio)
        url_ml = f"https://api.mercadolibre.com/sites/MLB/search?q={sku}&category=MLB1430"
        response = requests.get(url_ml, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('results'):
                produto = data['results'][0]
                imagem = produto.get('thumbnail', '')
                if imagem:
                    imagem = imagem.replace('http://', 'https://')
                local = salvar_imagem_local(imagem, sku)
                return {
                    'marca': produto.get('attributes', {}).get('BRAND', ['N/A'])[0],
                    'modelo': produto.get('title', sku),
                    'preco': produto.get('price', 0),
                    'imagem_url': local or imagem,
                    'descricao': produto.get('title', ''),
                    'cor': 'Não especificada'
                }
        # Fallback final
        return {
            'marca': 'Nike',
            'modelo': sku,
            'preco': 0,
            'imagem_url': f'https://via.placeholder.com/600x600?text={sku}',
            'descricao': f'Produto SKU: {sku}',
            'cor': 'Não especificada'
        }
        
    except Exception as e:
        print(f"Erro ao buscar informações do produto: {e}")
        return {
            'marca': 'Marca não encontrada',
            'modelo': f'Modelo {sku}',
            'preco': 299.90,
            'imagem_url': f'https://via.placeholder.com/300x300?text={sku}',
            'descricao': f'Produto SKU: {sku}',
            'cor': 'Não especificada'
        }

# Garantir que a pasta de templates seja encontrada corretamente em produção
app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(__file__), 'templates'),
    static_folder=os.path.join(os.path.dirname(__file__), 'static')
)
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

# Inicialização idempotente para produção (Flask 3 removeu before_first_request)
app.config.setdefault('INIT_DONE', False)

@app.before_request
def inicializar_banco_e_admin():
    if app.config.get('INIT_DONE'):
        return
    try:
        with app.app_context():
            db.create_all()
            # Criar usuário admin se não existir
            if Usuario.query.count() == 0:
                admin = Usuario(username='admin', nome='Administrador')
                admin.set_password('123456')
                db.session.add(admin)
                db.session.commit()
        app.config['INIT_DONE'] = True
    except Exception as e:
        # Evitar quebrar a aplicação caso o banco ainda não esteja acessível no primeiro boot
        print(f"Falha ao inicializar banco/usuário admin: {e}")

def salvar_imagem_local(url: str, sku: str, min_bytes: int = 100_000) -> str:
    try:
        if not url or not sku:
            return ''
        pasta = os.path.join(app.static_folder, 'shoes')
        os.makedirs(pasta, exist_ok=True)
        caminho = os.path.join(pasta, f"{sku}.jpg")
        if os.path.exists(caminho) and os.path.getsize(caminho) > 1000:
            return f"/static/shoes/{sku}.jpg"
        # Baixa com headers para evitar bloqueio
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36',
            'Referer': 'https://www.nike.com/'
        }
        r = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
        if r.status_code == 200 and r.content and len(r.content) >= min_bytes:
            with open(caminho, 'wb') as f:
                f.write(r.content)
            return f"/static/shoes/{sku}.jpg"
    except Exception as e:
        print(f"Erro salvando imagem {sku}: {e}")
    return ''

def garantir_svg_local(sku: str, titulo: str) -> str:
    try:
        pasta = os.path.join(app.static_folder, 'shoes')
        os.makedirs(pasta, exist_ok=True)
        nome = (sku or titulo or 'TENIS').replace(' ', '-').upper()
        caminho = os.path.join(pasta, f"{nome}.svg")
        if not os.path.exists(caminho):
            svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="800" height="800">
<defs>
  <linearGradient id="g" x1="0" x2="1" y1="0" y2="1">
    <stop offset="0%" stop-color="#0b1220"/>
    <stop offset="100%" stop-color="#1e293b"/>
  </linearGradient>
</defs>
<rect width="100%" height="100%" fill="url(#g)"/>
<text x="50%" y="50%" font-family="Arial,Helvetica,sans-serif" font-size="42" fill="#e2e8f0" text-anchor="middle">{titulo}</text>
</svg>'''
            with open(caminho, 'w', encoding='utf-8') as f:
                f.write(svg)
        return f"/static/shoes/{nome}.svg"
    except Exception as e:
        print(f"Erro criando SVG para {sku}: {e}")
    return ''

def buscar_imagem_por_sku(sku: str, titulo: str) -> str:
    """Retorna caminho LOCAL da imagem salva para o SKU, buscando em fontes externas uma única vez.
    Estratégia: 1) Nike CDN se SKU STYLECOLOR-COLOR; 2) Google Images (thumbnail) sem API; 3) SVG com título.
    """
    sku_up = (sku or '').strip().upper()
    nome_base = (sku_up or titulo or 'TENIS').replace(' ', '-').upper()
    # Já existe local?
    pasta = os.path.join(app.static_folder, 'shoes')
    os.makedirs(pasta, exist_ok=True)
    destino_jpg = os.path.join(pasta, f"{nome_base}.jpg")
    if os.path.exists(destino_jpg) and os.path.getsize(destino_jpg) > 1000:
        return f"/static/shoes/{nome_base}.jpg"

    # 0) Droper (prioridade alta) – procura página do produto e extrai imagem OG
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        # tentativa 1: busca direta por SKU
        r = requests.get(f"https://droper.app/search?q={requests.utils.quote(sku_up)}", headers=headers, timeout=12)
        if r.status_code == 200:
            import re as _re
            # pega primeiro link de produto /d/{id}/slug
            m = _re.search(r"/d/\d+/[A-Za-z0-9_\-]+", r.text)
            if m:
                prod_url = "https://droper.app" + m.group(0)
                rp = requests.get(prod_url, headers=headers, timeout=12)
                if rp.status_code == 200:
                    # tenta og:image
                    mo = _re.search(r"property=\"og:image\"\s*content=\"(https:[^\"]+)\"", rp.text)
                    img = mo.group(1) if mo else None
                    if not img:
                        mo = _re.search(r"<img[^>]+src=\"(https:[^\"]+)\"", rp.text)
                        img = mo.group(1) if mo else None
                    if img:
                        # garantir alta resolução quando possível
                        img = _re.sub(r"=s\d+", "=s1200", img)
                        local = salvar_imagem_local(img, nome_base, min_bytes=120_000)
                        if local:
                            return local
    except Exception as e:
        print(f"Droper falhou {sku_up}: {e}")

    # 1) Nike CDN
    import re
    import re
    style_candidate = sku_up if re.match(r"^[A-Z0-9]{5,}-[0-9]{3}$", sku_up) else map_model_to_stylecode(sku, titulo)
    if style_candidate:
        # pedir 1200px para garantir qualidade ~720p+
        nike_url = f"https://images.nike.com/is/image/DotCom/{style_candidate.replace('-', '_')}_A_PREM?wid=1200&hei=1200"
        local = salvar_imagem_local(nike_url, nome_base, min_bytes=50_000)
        if local:
            return local

    # 2) Google Images (consulta simples ao HTML, buscando primeiro img src)
    try:
        q = requests.utils.quote(sku_up or titulo)
        headers = {'User-Agent': 'Mozilla/5.0'}
        resp = requests.get(f"https://www.google.com/search?tbm=isch&q={q}", headers=headers, timeout=10)
        if resp.status_code == 200:
            import re as _re
            # procura primeiro src e depois data-src maior
            m = _re.search(r"data-src=\"(https:[^\"]+?=s\d+)\"", resp.text) or _re.search(r"<img[^>]+src=\"(https:[^\"]+)\"", resp.text)
            if m:
                img = m.group(1)
                # tenta aumentar tamanho quando for formato '=s200' -> '=s1200'
                img = _re.sub(r"=s\d+", "=s1200", img)
                local = salvar_imagem_local(img, nome_base, min_bytes=120_000)
                if local:
                    return local
    except Exception as e:
        print(f"Google images falhou {sku_up}: {e}")

    # 3) SVG fallback
    return garantir_svg_local(sku_up, titulo)

def caminho_local_por_sku(sku: str, titulo: str) -> str:
    """Verifica em static/shoes por arquivos locais com nome do SKU (extensões comuns)."""
    pasta = os.path.join(app.static_folder, 'shoes')
    os.makedirs(pasta, exist_ok=True)
    base = (sku or titulo or 'TENIS').replace(' ', '-').upper()
    for ext in ('.jpg', '.jpeg', '.png', '.webp', '.svg'):
        p = os.path.join(pasta, base + ext)
        if os.path.exists(p) and os.path.getsize(p) > 0:
            return f"/static/shoes/{base + ext}"
    # tenta por style-code conhecido quando o SKU não é padrão
    alt = map_model_to_stylecode(sku, titulo)
    if alt:
        for ext in ('.jpg', '.jpeg', '.png', '.webp', '.svg'):
            p = os.path.join(pasta, alt + ext)
            if os.path.exists(p) and os.path.getsize(p) > 0:
                return f"/static/shoes/{alt + ext}"
    return ''

def map_model_to_stylecode(sku: str, titulo: str) -> str:
    key = (titulo or sku or '').lower()
    MAP = {
        'air max 270 black': 'CT1280-001',
        'air force 1 white': '315122-111',
        'air max 90 grey': 'CN8490-002',
        'dunk low panda': 'DD1391-100',
        'air jordan 1 mid chicago': '554724-173',
    }
    for name, style in MAP.items():
        if name in key:
            return style
    return ''

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
    sku = db.Column(db.String(100), unique=True, nullable=False)
    marca = db.Column(db.String(50), nullable=False)
    modelo = db.Column(db.String(100), nullable=False)
    cor = db.Column(db.String(50), nullable=False)
    tamanho = db.Column(db.String(10), nullable=False)
    preco = db.Column(db.Float, nullable=False)
    imagem_url = db.Column(db.String(500))
    descricao = db.Column(db.Text)
    data_chegada = db.Column(db.DateTime, default=datetime.utcnow)
    vendido = db.Column(db.Boolean, default=False)

# Template inline para resolver erro no Render
LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - Shop Pra Mim</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; display: flex; align-items: center; justify-content: center; }
        .login-card { background: white; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.3); overflow: hidden; max-width: 400px; width: 100%; }
        .login-header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; }
        .login-header h2 { font-size: 3.0rem; font-weight: 1000; letter-spacing: .3px; }
        .login-body { padding: 30px; }
        .btn-login { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border: none; width: 100%; padding: 12px; border-radius: 8px; color: white; font-weight: 500; }
        .form-control { border-radius: 8px; padding: 12px; border: 2px solid #e9ecef; }
    </style>
</head>
<body>
    <div class="login-card">
        <div class="login-header">
            <i class="fas fa-shopping-bag fa-3x mb-3"></i>
            <h2 class="mb-0">Shop Pra Mim</h2>
            <p class="mb-0 opacity-75">Sistema de Gestão</p>
        </div>
        <div class="login-body">
            {% with messages = get_flashed_messages(with_categories=true) %}
                {% if messages %}
                    {% for category, message in messages %}
                        <div class="alert alert-{{ 'danger' if category == 'error' else category }}">{{ message }}</div>
                    {% endfor %}
                {% endif %}
            {% endwith %}
            <form method="POST">
                <div class="mb-3">
                    <label for="username" class="form-label"><i class="fas fa-user me-2"></i>Usuário</label>
                    <input type="text" class="form-control" id="username" name="username" required value="admin">
                </div>
                <div class="mb-4">
                    <label for="password" class="form-label"><i class="fas fa-lock me-2"></i>Senha</label>
                    <input type="password" class="form-control" id="password" name="password" required value="123456">
                </div>
                <button type="submit" class="btn btn-login"><i class="fas fa-sign-in-alt me-2"></i>Entrar</button>
            </form>
            <div class="mt-4 text-center">
                <small class="text-muted"><i class="fas fa-info-circle me-1"></i>Credenciais: <strong>admin</strong> / <strong>123456</strong></small>
            </div>
        </div>
    </div>
</body>
</html>
'''

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
    
    # Usar template inline como fallback
    try:
        return render_template('login.html')
    except Exception as e:
        print(f"Erro ao carregar template login.html: {e}")
        from flask import render_template_string
        return render_template_string(LOGIN_TEMPLATE)

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
        sku = request.form['sku']
        tamanho = request.form['tamanho']
        preco = float(request.form['preco'])
        
        # Buscar informações do produto via SKU
        info_produto = buscar_informacoes_produto(sku)
        
        produto = Produto(
            sku=sku,
            marca=info_produto['marca'],
            modelo=info_produto['modelo'],
            cor=info_produto['cor'],
            tamanho=tamanho,
            preco=preco,
            imagem_url=info_produto['imagem_url'],
            descricao=info_produto['descricao']
        )
        # Força download/salvamento local e atualiza DB para uso futuro sem rede
        local_path = buscar_imagem_por_sku(produto.sku, produto.modelo)
        if local_path:
            produto.imagem_url = local_path
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

@app.route('/estoque')
def estoque():
    """Página de estoque para clientes visualizarem os tênis disponíveis"""
    produtos = Produto.query.filter_by(vendido=False).all()
    # Seed automático: 10 itens (5 Nike, 5 Jordan) se estoque estiver vazio
    if not produtos:
        seeds = [
            # Nike
            { 'sku': 'NIKE-AIR-MAX-270-BLACK', 'marca': 'Nike', 'modelo': 'Air Max 270 Black', 'cor': 'Preto', 'tamanho': '42', 'preco': 799.90, 'imagem_url': 'https://images.nike.com/is/image/DotCom/CT1280_001_A_PREM?bgc=f5f5f5&wid=800&hei=800', 'descricao': 'Nike Air Max 270 Black'},
            { 'sku': 'NIKE-AIR-FORCE-1-WHITE', 'marca': 'Nike', 'modelo': 'Air Force 1 White', 'cor': 'Branco', 'tamanho': '41', 'preco': 749.90, 'imagem_url': 'https://images.nike.com/is/image/DotCom/315122_111_A_PREM?bgc=f5f5f5&wid=800&hei=800', 'descricao': 'Nike Air Force 1 White'},
            { 'sku': 'NIKE-AIR-MAX-90-GREY', 'marca': 'Nike', 'modelo': 'Air Max 90 Grey', 'cor': 'Cinza', 'tamanho': '40', 'preco': 899.90, 'imagem_url': 'https://images.nike.com/is/image/DotCom/CN8490_002_A_PREM?bgc=f5f5f5&wid=800&hei=800', 'descricao': 'Nike Air Max 90'},
            { 'sku': 'NIKE-DUNK-LOW-PANDA', 'marca': 'Nike', 'modelo': 'Dunk Low Panda', 'cor': 'Preto', 'tamanho': '43', 'preco': 999.90, 'imagem_url': 'https://images.nike.com/is/image/DotCom/DD1391_100_A_PREM?bgc=f5f5f5&wid=800&hei=800', 'descricao': 'Nike Dunk Low Panda'},
            # Jordan
            { 'sku': 'JORDAN-1-MID-CHICAGO', 'marca': 'Jordan', 'modelo': 'Air Jordan 1 Mid Chicago', 'cor': 'Vermelho', 'tamanho': '42', 'preco': 1299.90, 'imagem_url': 'https://images.nike.com/is/image/DotCom/554724_173_A_PREM?bgc=f5f5f5&wid=800&hei=800', 'descricao': 'AJ1 Mid Chicago'},
            { 'sku': 'JORDAN-4-WHITE-OREO', 'marca': 'Jordan', 'modelo': 'Air Jordan 4 White Oreo', 'cor': 'Branco', 'tamanho': '42', 'preco': 1699.90, 'imagem_url': 'https://images.nike.com/is/image/DotCom/CT8527_100_A_PREM?bgc=f5f5f5&wid=800&hei=800', 'descricao': 'AJ4 White Oreo'}
        ]
        for item in seeds:
            try:
                if not Produto.query.filter_by(sku=item['sku']).first():
                    db.session.add(Produto(**item))
            except Exception as e:
                print(f"Falha seed {item['sku']}: {e}")
        db.session.commit()
        produtos = Produto.query.filter_by(vendido=False).all()
    # Baixar e servir imagens locais para cada produto
    import re
    for p in produtos:
        sku = (p.sku or '').strip().upper()
        # Sempre resolve para local e atualiza no DB uma vez
        # Prioriza arquivo local já colocado manualmente na pasta static/shoes
        local_display = caminho_local_por_sku(sku, p.modelo) or buscar_imagem_por_sku(sku, p.modelo)
        if local_display and p.imagem_url != local_display:
            p.imagem_url = local_display
            try:
                db.session.add(p)
                db.session.commit()
            except Exception as e:
                print('Falha ao atualizar imagem local do produto:', e)
        setattr(p, 'display_image', local_display or p.imagem_url)
    return render_template('estoque.html', produtos=produtos)

@app.route('/sync-estoque')
def sync_estoque():
    """Endpoint temporário para sincronizar estoque com arquivos locais"""
    # Limpa estoque atual
    for p in Produto.query.all():
        db.session.delete(p)
    db.session.commit()
    
    # SKUs específicos que existem em static/shoes/
    skus_corretos = [
        '554724-173', 'CN8490-002', 'CT8527-100', 
        'CZ0790-106', 'DD1391-100', 'DM7866-140'
    ]
    
    created = []
    for sku in skus_corretos:
        info = buscar_informacoes_produto(sku)
        marca = info.get('marca') or 'Nike'
        modelo = info.get('modelo') or sku
        cor = info.get('cor') or ''
        tamanho = info.get('tamanho') or '42'
        preco = float(info.get('preco') or 0) or 999.90
        local = f"/static/shoes/{sku}.webp"  # Assumindo formato webp
        
        produto = Produto(
            sku=sku,
            marca=marca,
            modelo=modelo,
            cor=cor,
            tamanho=tamanho,
            preco=preco,
            imagem_url=local,
            descricao=info.get('descricao') or modelo
        )
        db.session.add(produto)
        created.append((sku, modelo, local))
    
    db.session.commit()
    return f"Estoque sincronizado com {len(created)} itens: {[f'{sku}|{modelo}' for sku, modelo, _ in created]}"

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