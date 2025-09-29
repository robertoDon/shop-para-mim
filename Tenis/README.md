# 👟 Shop Pra Mim

Sistema completo de gestão de loja de tênis com **recomendações inteligentes** baseadas no histórico de compras.

## 🚀 Deploy no Render.com

Este repositório está otimizado para deploy direto no Render.com:

1. **Fork** este repositório
2. **Conecte** ao Render.com
3. **Deploy automático!**

### ⚙️ Configuração no Render:
```
Name: shop-pra-mim
Runtime: Python 3
Build Command: pip install -r requirements.txt  
Start Command: gunicorn app:app
```

## 🔐 Credenciais padrão:
- **Usuário:** admin
- **Senha:** 123456

## ✨ Funcionalidades:
- 🔐 Sistema de login
- 👥 Gestão de clientes
- 🛒 Registro de vendas
- 📦 Controle de estoque
- 🎯 **Recomendações inteligentes**
- 📊 Relatórios e analytics

## 🎯 Sistema de Recomendação:
Quando você adiciona um produto novo, o sistema automaticamente:
- Analisa histórico de compras
- Calcula scores por cliente
- Recomenda os 5 melhores clientes
- Gera links do WhatsApp

---

**Desenvolvido com ❤️ para a Shop Pra Mim!**