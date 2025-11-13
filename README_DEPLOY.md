# Sistema de Sorteio de Grupos 🎲

Aplicação web para sorteio automático de grupos com garantia de distribuição equilibrada de calouros e veteranos.

## 🚀 Demo

[Link da aplicação](seu-link-aqui)

## ✨ Funcionalidades

### 🔓 Acesso Público
- **Consultar Grupos**: Busque alunos e visualize grupos salvos sem necessidade de login

### 🔐 Área Administrativa (Login Necessário)
- **Sorteio Automático**: Crie grupos automaticamente garantindo pelo menos 1 calouro por grupo
- **Grupos Manuais**: Monte grupos personalizados manualmente
- **Visualizar Dados**: Acesse e filtre os dados completos dos alunos
- **Exportação**: Exporte grupos para CSV
- **Histórico**: Salve e consulte sorteios anteriores

## 📋 Pré-requisitos

- Python 3.12+
- pip ou uv

## 🛠️ Instalação Local

```bash
# Clone o repositório
git clone <seu-repositorio>
cd sorteio

# Crie um ambiente virtual
python -m venv .venv
source .venv/bin/activate  # No Windows: .venv\Scripts\activate

# Instale as dependências
pip install -r requirements.txt

# Execute a aplicação
streamlit run app_sorteio.py
```

## 🔑 Credenciais de Acesso

- **Usuário**: pharmabio
- **Senha**: pharmabio

> ⚠️ **Importante**: Altere as credenciais antes de fazer deploy em produção!

## 📊 Formato dos Dados

Os dados dos alunos devem estar em formato CSV com ponto e vírgula como separador:

```csv
Nome;Turma;;;;;
João Silva;1;;;;;
Maria Santos;2;;;;;
```

Onde:
- **Turma 1**: Calouros
- **Turma 2**: Veteranos

## 🎯 Como Usar

1. Faça upload do arquivo CSV com os dados dos alunos
2. Configure o tamanho dos grupos (2-6 alunos)
3. Execute o sorteio automático ou crie grupos manualmente
4. Salve e exporte os resultados
5. Consulte grupos salvos pela aba de consulta (pública)

## 🔒 Segurança

- Sistema de autenticação com sessão
- Área pública separada da administrativa
- Validação de grupos (garantia de pelo menos 1 calouro)

## 📝 Tecnologias

- **Streamlit**: Framework web
- **Pandas**: Manipulação de dados
- **Python 3.12**: Linguagem base

## 📄 Licença

MIT License - veja LICENSE para mais detalhes

## 👨‍💻 Autor

Desenvolvido para PharmaBio
