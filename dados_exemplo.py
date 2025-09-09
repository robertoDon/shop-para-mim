#!/usr/bin/env python3
"""
Script para popular o banco de dados com dados de exemplo
Execute este script após inicializar o sistema pela primeira vez
"""

import sqlite3
from datetime import datetime, timedelta
import random

def criar_dados_exemplo():
    """Cria dados de exemplo para demonstrar o sistema"""
    
    # Conectar ao banco
    conn = sqlite3.connect('loja_tenis.db')
    cursor = conn.cursor()
    
    print("🎲 Criando dados de exemplo...")
    
    # Verificar se já existem dados
    cursor.execute("SELECT COUNT(*) FROM cliente")
    if cursor.fetchone()[0] > 0:
        print("ℹ️  Dados já existem no banco. Cancelando...")
        conn.close()
        return
    
    # Clientes de exemplo
    clientes = [
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
    for cliente in clientes:
        cursor.execute("""
            INSERT INTO cliente (nome, email, telefone, genero, idade, tamanho_preferido, data_cadastro)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, cliente + (datetime.now() - timedelta(days=random.randint(30, 365)),))
    
    print("✅ Clientes criados!")
    
    # Vendas de exemplo
    marcas = ['Nike', 'Adidas', 'Puma', 'Vans', 'Converse', 'Mizuno']
    modelos = ['Air Max', 'Stan Smith', 'Suede Classic', 'Old Skool', 'Chuck Taylor', 'Wave']
    cores = ['Preto', 'Branco', 'Azul', 'Vermelho', 'Verde', 'Cinza']
    tamanhos = ['36', '37', '38', '39', '40', '41', '42', '43']
    
    # Criar vendas históricas para gerar padrões
    vendas = []
    for cliente_id in range(1, 11):
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
            
            modelo = random.choice(modelos)
            tamanho = random.choice(tamanhos)
            valor = round(random.uniform(150, 800), 2)
            data_venda = datetime.now() - timedelta(days=random.randint(1, 180))
            
            vendas.append((cliente_id, valor, data_venda, cor, tamanho, marca, modelo))
    
    # Inserir vendas
    for venda in vendas:
        cursor.execute("""
            INSERT INTO venda (cliente_id, valor, data_venda, cor_tenis, tamanho, marca, modelo)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, venda)
    
    print(f"✅ {len(vendas)} vendas criadas!")
    
    # Produtos em estoque
    produtos_estoque = [
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
    for produto in produtos_estoque:
        cursor.execute("""
            INSERT INTO produto (marca, modelo, cor, tamanho, preco, data_chegada, vendido)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, produto + (datetime.now() - timedelta(days=random.randint(1, 30)), False))
    
    print(f"✅ {len(produtos_estoque)} produtos adicionados ao estoque!")
    
    # Salvar e fechar
    conn.commit()
    conn.close()
    
    print("🎉 Dados de exemplo criados com sucesso!")
    print("💡 Agora você pode testar o sistema de recomendações adicionando novos produtos!")
    print("🔗 Acesse: http://localhost:5000")

if __name__ == "__main__":
    criar_dados_exemplo()