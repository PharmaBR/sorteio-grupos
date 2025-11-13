# 🎲 Sistema de Sorteio de Grupos

## Descrição

Aplicação Streamlit para realizar sorteio de grupos de alunos com as seguintes características:

- **Grupos com 4 componentes** (tamanho configurável)
- **Garantia de pelo menos 1 calouro por grupo**
- **Criação manual de grupos personalizados**
- **Exportação de resultados em CSV**

## Funcionalidades

### 1. 🎲 Sorteio Automático
- Sorteio aleatório respeitando a regra de pelo menos 1 calouro por grupo
- Possibilidade de usar seed para resultados reproduzíveis
- Integração com grupos manuais (alunos em grupos manuais são excluídos do sorteio)
- Exportação dos resultados

### 2. ✏️ Grupos Manuais
- Criação de grupos personalizados
- Seleção manual de alunos
- Validação automática (verifica se há calouro no grupo)
- Gerenciamento de grupos (adicionar/remover)

### 3. 📋 Visualizar Dados
- Listagem de todos os alunos
- Filtros por turma
- Busca por nome
- Estatísticas gerais

## Como Usar

### Instalação

```bash
# Instalar dependências
pip install streamlit pandas
```

### Executar a Aplicação

```bash
# A partir do diretório do projeto
streamlit run app_sorteio.py
```

### Uso da Interface

1. **Carregar dados**: O sistema usa automaticamente o arquivo `dados_chamada/dados_manha.csv` ou você pode fazer upload de outro arquivo CSV

2. **Configurar**: Use a barra lateral para ajustar:
   - Tamanho dos grupos
   - Seed para reprodutibilidade

3. **Sortear**: 
   - Vá para a aba "Sorteio Automático"
   - Clique em "Sortear Grupos"
   - Os grupos serão gerados automaticamente

4. **Grupos Manuais**:
   - Vá para a aba "Grupos Manuais"
   - Selecione os alunos desejados
   - Clique em "Adicionar Grupo"

5. **Exportar**: Após o sorteio, use o botão "Exportar Grupos (CSV)" para baixar os resultados

## Formato do Arquivo CSV

O arquivo CSV deve ter o seguinte formato:

```csv
Nome;Turma
JOÃO SILVA;1
MARIA SANTOS;2
...
```

Onde:
- **Turma 1** = Calouros
- **Turma 2** = Veteranos

## Regras do Sorteio

1. Cada grupo deve ter exatamente 4 alunos (ou o número configurado)
2. Cada grupo DEVE ter pelo menos 1 calouro (Turma 1)
3. Grupos manuais são respeitados e seus alunos não entram no sorteio automático
4. A distribuição é feita de forma a balancear os grupos

## Tecnologias Utilizadas

- **Streamlit**: Interface web interativa
- **Pandas**: Manipulação de dados
- **Python**: Lógica de sorteio e validação
