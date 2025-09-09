#!/usr/bin/env python3
"""
Script para popular o banco de dados com dados de exemplo usando Flask-SQLAlchemy
"""

from app import app, db, Cliente, Venda, Produto, Usuario
from datetime import datetime, timedelta
import random

def criar_dados_exemplo():
    """Cria dados de exemplo para demonstrar o sistema"""
    
    with app.app_context():
        # Criar tabelas se não existirem
        db.create_all()
        
        print("🎲 Criando dados de exemplo...")
        
        # Verificar se já existem dados
        if Cliente.query.count() > 0:
            print("ℹ️  Dados já existem no banco. Cancelando...")
            return
            
        # Criar usuário administrador padrão
        if Usuario.query.count() == 0:
            admin = Usuario(
                username='admin',
                nome='Administrador'
            )
            admin.set_password('123456')
            db.session.add(admin)
            db.session.commit()
            print("✅ Usuário admin criado! (admin/123456)")
        
        # Clientes de exemplo
        clientes_dados = [
            ('João Silva', 'joao@email.com', '(11) 99999-1111', 'M', 28, '42'),
            ('Maria Santos', 'maria@email.com', '(11) 99999-2222', 'F', 25, '37'),
            ('Pedro Costa', 'pedro@email.com', '(11) 99999-3333', 'M', 35, '41'),
            ('Ana Oliveira', 'ana@email.com', '(11) 99999-4444', 'F', 30, '38'),
            ('Carlos Ferreira', 'carlos@email.com', '(11) 99999-5555', 'M', 22, '43'),
            ('Juliana Lima', 'juliana@email.com', '(11) 99999-6666', 'F', 27, '36'),
            ('Roberto Alves', 'roberto@email.com', '(11) 99999-7777', 'M', 40, '41'),
            ('Fernanda Souza', 'fernanda@email.com', '(11) 99999-8888', 'F', 24, '37'),
            ('Lucas Pereira', 'lucas@email.com', '(11) 99999-9999', 'M', 26, '40'),
            ('Camila Rocha', 'camila@email.com', '(11) 99999-0000', 'F', 29, '38')
        ]
        
        # Inserir clientes
        clientes = []
        for dados in clientes_dados:
            cliente = Cliente(
                nome=dados[0],
                email=dados[1],
                telefone=dados[2],
                genero=dados[3],
                idade=dados[4],
                tamanho_preferido=dados[5],
                data_cadastro=datetime.now() - timedelta(days=random.randint(30, 365))
            )
            clientes.append(cliente)
            db.session.add(cliente)
        
        db.session.commit()
        print("✅ Clientes criados!")
        
        # Dados para vendas
        marcas = ['Nike', 'Adidas', 'Puma', 'Vans', 'Converse', 'Mizuno']
        modelos = ['Air Max', 'Stan Smith', 'Suede Classic', 'Old Skool', 'Chuck Taylor', 'Wave']
        cores = ['Preto', 'Branco', 'Azul', 'Vermelho', 'Verde', 'Cinza']
        tamanhos = ['36', '37', '38', '39', '40', '41', '42', '43']
        
        # Criar vendas históricas para gerar padrões
        vendas_count = 0
        for cliente in clientes:
            # Cada cliente tem entre 1 e 5 compras
            num_compras = random.randint(1, 5)
            
            # Definir preferências do cliente
            marca_pref = random.choice(marcas)
            cor_pref = random.choice(cores)
            
            for _ in range(num_compras):
                # 70% chance de comprar marca preferida
                marca = marca_pref if random.random() < 0.7 else random.choice(marcas)
                # 60% chance de comprar cor preferida
                cor = cor_pref if random.random() < 0.6 else random.choice(cores)
                
                venda = Venda(
                    cliente_id=cliente.id,
                    valor=round(random.uniform(150, 800), 2),
                    data_venda=datetime.now() - timedelta(days=random.randint(1, 180)),
                    cor_tenis=cor,
                    tamanho=random.choice(tamanhos),
                    marca=marca,
                    modelo=random.choice(modelos)
                )
                db.session.add(venda)
                vendas_count += 1
        
        db.session.commit()
        print(f"✅ {vendas_count} vendas criadas!")
        
        # Produtos em estoque
        produtos_dados = [
            ('Nike', 'Air Max 90', 'Branco', '42', 350.00),
            ('Adidas', 'Stan Smith', 'Verde', '39', 280.00),
            ('Puma', 'Suede Classic', 'Preto', '41', 220.00),
            ('Vans', 'Old Skool', 'Azul', '38', 190.00),
            ('Converse', 'Chuck Taylor', 'Vermelho', '37', 160.00),
            ('Nike', 'Air Force 1', 'Branco', '40', 400.00),
            ('Adidas', 'Superstar', 'Preto', '43', 320.00),
            ('Mizuno', 'Wave Prophecy', 'Cinza', '41', 450.00)
        ]
        
        # Inserir produtos
        for dados in produtos_dados:
            produto = Produto(
                marca=dados[0],
                modelo=dados[1],
                cor=dados[2],
                tamanho=dados[3],
                preco=dados[4],
                data_chegada=datetime.now() - timedelta(days=random.randint(1, 30)),
                vendido=False
            )
            db.session.add(produto)
        
        db.session.commit()
        print(f"✅ {len(produtos_dados)} produtos adicionados ao estoque!")
        
        print("🎉 Dados de exemplo criados com sucesso!")
        print("💡 Agora você pode testar o sistema de recomendações adicionando novos produtos!")

if __name__ == "__main__":
    criar_dados_exemplo()