# 🎯 Guia de Demonstração - Sistema de Recomendação

## 🚀 Como Testar o Sistema de Recomendação

### Passo 1: Configuração Inicial
```bash
# 1. Instalar dependências
pip3 install -r requirements.txt

# 2. Criar dados de exemplo
python3 dados_exemplo.py

# 3. Iniciar o sistema
./iniciar.sh  # ou python3 app.py
```

### Passo 2: Explorar o Sistema
1. **Acesse:** http://localhost:5000
2. **Dashboard:** Veja estatísticas gerais
3. **Clientes:** 10 clientes já cadastrados com perfis variados
4. **Vendas:** 25+ vendas históricas para criar padrões
5. **Produtos:** 8 tênis no estoque aguardando recomendações

---

## 🎲 Testando as Recomendações

### Cenário 1: Nike Air Max (Cliente Fiel à Nike)
1. Vá em **Produtos** → **Adicionar Produto**
2. Cadastre: **Nike Air Max 270, Preto, Tamanho 42, R$ 350**
3. **Resultado esperado:** João Silva (cliente fiel à Nike) deve aparecer em 1º lugar

### Cenário 2: Tênis Feminino (Perfil por Gênero)
1. Cadastre: **Adidas Superstar, Rosa, Tamanho 37, R$ 280**
2. **Resultado esperado:** Clientes femininas com tamanho 37-38 no topo

### Cenário 3: Tênis Caro (Análise de Faixa de Preço)
1. Cadastre: **Nike Air Jordan, Branco, Tamanho 41, R$ 800**
2. **Resultado esperado:** Clientes com histórico de compras caras

### Cenário 4: Cor Específica (Preferência por Cor)
1. Cadastre: **Vans Old Skool, Azul, Tamanho 40, R$ 200**
2. **Resultado esperado:** Clientes que já compraram azul antes

---

## 📊 Analisando os Resultados

### Score de Recomendação (0-100%)
- **80-100%:** 🟢 **Muito Provável** - Cliente ideal para este produto
- **60-79%:** 🟡 **Provável** - Boa chance de interesse  
- **40-59%:** 🟠 **Possível** - Vale tentar contato
- **20-39%:** 🔴 **Improvável** - Baixa chance
- **0-19%:** ⚫ **Muito Improvável** - Não recomendado

### Fatores que Aumentam o Score
- ✅ **Marca preferida** (cliente já comprou a marca)
- ✅ **Cor favorita** (histórico de compra da cor)
- ✅ **Tamanho certo** (compatível com perfil)
- ✅ **Faixa de preço** (similar ao que já gastou)
- ✅ **Cliente frequente** (3+ compras)

---

## 🎯 Casos de Uso Reais

### Caso 1: Produto Novo Chegou
**Situação:** Chegou um lote de Nike Air Max preto tamanho 42
**Ação:** Cadastre o produto e veja automaticamente os 5 melhores clientes
**Resultado:** Lista priorizada com botão direto para WhatsApp

### Caso 2: Promoção Direcionada  
**Situação:** Tênis azul em promoção
**Ação:** Cadastre como produto e filtre quem já comprou azul
**Resultado:** Marketing direcionado para público certo

### Caso 3: Estoque Parado
**Situação:** Tênis feminino tamanho 36 não está vendendo
**Ação:** Recadastre e veja se há clientes compatíveis
**Resultado:** Estratégia de vendas focada

### Caso 4: Cliente VIP
**Situação:** Produto premium chegou
**Ação:** Sistema mostra automaticamente clientes com maior ticket médio
**Resultado:** Oferta para quem tem poder de compra

---

## 📱 Testando o WhatsApp

1. **Configure números reais** nos clientes de teste
2. **Clique em "Enviar WhatsApp"** nas recomendações
3. **Mensagem personalizada** será criada automaticamente:

```
Olá [Nome]! Temos um novo [Marca] [Modelo] [Cor] 
tamanho [Tamanho] que achamos que você vai gostar! 
Preço: R$ [Valor]
```

---

## 🔧 Personalizando o Sistema

### Ajustar Pesos do Algoritmo
No arquivo `app.py`, função `gerar_recomendacoes()`:
```python
# Marca (40% do score)
score += 40 * (marcas.count(produto.marca) / len(marcas))

# Cor (30% do score)  
score += 30 * (cores.count(produto.cor) / len(cores))

# Tamanho (20% do score)
score += 20

# Preço (até 20% adicional)
score += 20

# Frequência (bonus 10%)
score += 10
```

### Adicionar Novas Cores
Nos templates, adicione na lista de cores:
```html
<option value="Nova_Cor">Nova Cor</option>
```

### Modificar Mensagem WhatsApp
No template `recomendacoes.html`, altere o link:
```html
?text=Sua mensagem personalizada aqui
```

---

## 📈 Relatórios Disponíveis

1. **Dashboard Principal:** Métricas gerais
2. **Vendas por Marca:** Ranking de marcas
3. **Cores Mais Vendidas:** Preferências dos clientes
4. **Distribuição por Gênero:** Perfil da clientela
5. **Ticket Médio:** Poder de compra

---

## 🎉 Próximos Passos

1. **Use com dados reais** - Substitua pelos seus clientes
2. **Refine o algoritmo** - Ajuste pesos conforme seu negócio
3. **Expanda funcionalidades** - Adicione desconto, estoque, etc.
4. **Automatize** - Configure notificações automáticas
5. **Analise resultados** - Use relatórios para tomar decisões

---

**💡 Dica Final:** O sistema fica mais inteligente com o tempo. Quanto mais vendas você registrar, melhores ficam as recomendações!