# 🚀 Instruções de Instalação

## Problema Atual

O erro que você está vendo é porque o `pyarrow` (dependência do Streamlit) precisa do `cmake` para compilar no Python 3.14.

## Solução 1: Instalar CMake (Recomendado)

### macOS
```bash
# Instalar cmake usando Homebrew
brew install cmake

# Depois instalar as dependências
uv pip install streamlit pandas
```

## Solução 2: Usar Python 3.11 ou 3.12

O pyarrow tem binários pré-compilados para versões mais antigas do Python:

```bash
# Criar novo ambiente com Python 3.12
uv venv --python 3.12

# Ativar o ambiente
source .venv/bin/activate

# Instalar dependências
uv pip install streamlit pandas
```

## Solução 3: Instalação Manual Simplificada

Se as opções acima não funcionarem, execute:

```bash
# Tentar instalar com pip tradicional
pip install streamlit pandas
```

## Executar a Aplicação

Após instalar com sucesso as dependências:

```bash
# Executar o app Streamlit
streamlit run app_sorteio.py
```

A aplicação abrirá automaticamente no seu navegador em `http://localhost:8501`

## Características da Aplicação

✅ Sorteio automático de grupos com 4 componentes  
✅ Garantia de pelo menos 1 calouro por grupo  
✅ Criação manual de grupos personalizados  
✅ Validação automática dos grupos  
✅ Exportação de resultados em CSV  
✅ Interface interativa e fácil de usar  

## Suporte

Se continuar com problemas de instalação, me avise qual solução você tentou!
