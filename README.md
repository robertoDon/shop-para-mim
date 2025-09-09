# 👟 Sistema Shop Pra Mim

Um sistema completo para gerenciar vendas de tênis com **recomendações inteligentes** baseadas no histórico de compras dos clientes.

## ✨ Funcionalidades

### 📊 Dashboard Principal
- Visão geral das vendas e estatísticas
- Cards com métricas importantes (total de clientes, vendas, receita)
- Ações rápidas para cadastros

### 👥 Gestão de Clientes
- Cadastro completo de clientes (nome, email, telefone, gênero, idade, tamanho preferido)
- Lista de todos os clientes com informações detalhadas
- Histórico de compras por cliente

### 🛒 Controle de Vendas
- Registro de vendas com todas as informações do produto
- Histórico completo de vendas
- Associação automática com clientes

### 📦 Gestão de Estoque
- Cadastro de produtos no estoque
- Controle de disponibilidade
- Informações detalhadas (marca, modelo, cor, tamanho, preço)

### 🎯 Sistema de Recomendação Inteligente
**O grande diferencial do sistema!** Sempre que um novo produto chega ao estoque, o sistema automaticamente:

- Analisa o histórico de compras de todos os clientes
- Calcula scores baseados em:
  - **Frequência de marca** (40% do score)
  - **Preferência por cor** (30% do score) 
  - **Compatibilidade de tamanho** (20% do score)
  - **Faixa de preço habitual** (até 20% adicional)
  - **Frequência de compra** (bonus de 10%)

- Gera uma lista dos **5 melhores clientes** para receber a recomendação
- Inclui botão direto para **WhatsApp** com mensagem personalizada

### 📈 Relatórios e Analytics
- Vendas por marca (quantidade e receita)
- Cores mais vendidas
- Distribuição de clientes por gênero
- Ticket médio e outras métricas
- Dicas para aumentar vendas

## 🚀 Como Executar

### Pré-requisitos
- Python 3.7 ou superior
- pip (gerenciador de pacotes do Python)

### Instalação

1. **Clone ou baixe o projeto:**
```bash
cd Conthales
```

2. **Instale as dependências:**
```bash
pip install -r requirements.txt
```

3. **Execute o sistema:**
```bash
python app.py
```

4. **Acesse no navegador:**
```
http://localhost:5000
```

### ⚡ Início Rápido (Recomendado)

**Uso Local:**
```bash
# Inicie o sistema localmente
./iniciar.sh     # Linux/Mac
# ou
iniciar.bat      # Windows

# Acesse: http://localhost:5001
# Login: admin / 123456
```

**Uso Online (Outras pessoas acessam de qualquer lugar):**
```bash
# Inicie o sistema online
./iniciar_online.sh

# Sistema mostra URL pública
# Compartilhe a URL com quem quiser
# Login: admin / 123456
```

Isso criará 10 clientes, 25+ vendas históricas e 8 produtos no estoque para você testar o sistema de recomendação!

## 💡 Como Usar

### 1. Primeiro Acesso
- **Login:** admin / 123456
- **Local:** http://localhost:5001  
- **Online:** Execute `./iniciar_online.sh` e use a URL gerada
- O sistema já vem com dados de exemplo!

### 2. Testando o Sistema de Recomendação
- Vá em "Produtos" → "Adicionar Produto"
- Cadastre um novo tênis
- **Automaticamente** veja recomendações inteligentes!
- Use os botões de WhatsApp para contatar clientes

### 3. Usando Online (Várias pessoas)
- Execute `./iniciar_online.sh`
- Compartilhe a URL pública
- Todos fazem login: admin / 123456
- Trabalhem colaborativamente!

### 4. Funcionalidades Principais
- **Clientes:** Cadastro completo com preferências
- **Vendas:** Registro detalhado que alimenta a IA
- **Produtos:** Adição com recomendações automáticas  
- **Relatórios:** Analytics para decisões inteligentes

## 🎯 Sistema de Score das Recomendações

O algoritmo considera:

| Fator | Peso | Descrição |
|-------|------|-----------|
| **Marca** | 40% | Frequência de compra da marca pelo cliente |
| **Cor** | 30% | Histórico de preferência por cores |
| **Tamanho** | 20% | Compatibilidade com tamanho usado/preferido |
| **Preço** | 0-20% | Proximidade com faixa de preço habitual |
| **Frequência** | +10% | Bonus para clientes frequentes (3+ compras) |

**Score total de 0-100%** - Quanto maior, melhor a chance de interesse!

## 🛠️ Tecnologias Utilizadas

- **Backend:** Python 3 + Flask
- **Banco de Dados:** SQLite (simples e sem configuração)
- **Frontend:** Bootstrap 5 + HTML/CSS/JavaScript
- **Ícones:** Font Awesome
- **Responsivo:** Funciona em celular, tablet e desktop

## 📱 Integração WhatsApp

O sistema gera automaticamente links do WhatsApp com mensagens personalizadas:
- Nome do cliente
- Detalhes do produto recomendado
- Preço
- Link direto para envio

## 🔧 Personalização

Você pode facilmente personalizar:
- Cores do sistema (editando os templates)
- Marcas disponíveis (adicionando no código)
- Algoritmo de recomendação (ajustando pesos no `app.py`)
- Mensagens do WhatsApp (editando template de recomendações)

## 📊 Estrutura do Banco

- **Clientes:** id, nome, email, telefone, gênero, idade, tamanho_preferido
- **Vendas:** id, cliente_id, valor, data_venda, cor_tenis, tamanho, marca, modelo
- **Produtos:** id, marca, modelo, cor, tamanho, preco, data_chegada, vendido

## 🎨 Interface

- **Design moderno** com Bootstrap 5
- **Responsivo** para todos os dispositivos
- **Intuitivo** e fácil de usar
- **Cores e ícones** organizados por categoria
- **Navegação simples** com menu superior

## 💰 Sem Custos Adicionais

- **100% gratuito** para usar
- **Sem mensalidades** ou taxas
- **Banco local** (não precisa de servidor)
- **Roda em qualquer computador** com Python

---

**Desenvolvido com ❤️ para a Shop Pra Mim!**

*Sistema de recomendação inteligente que aprende com seu negócio e ajuda você a vender mais para os clientes certos.*