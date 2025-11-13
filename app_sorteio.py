import streamlit as st
import pandas as pd
import random
from pathlib import Path
import json
from datetime import datetime

st.set_page_config(page_title="Sorteio de Grupos", page_icon="🎲", layout="wide")

# Arquivo para armazenar grupos
GRUPOS_FILE = Path(__file__).parent / "grupos_salvos.json"

# Credenciais de autenticação
CREDENTIALS = {
    "username": "pharmabio",
    "password": "pharmabio"
}

# Função de autenticação
def check_password():
    """Retorna True se o usuário está autenticado"""
    
    # Verificar se já está autenticado na sessão
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    if st.session_state.authenticated:
        return True
    
    # Criar formulário de login
    with st.sidebar:
        st.markdown("---")
        st.subheader("🔐 Login")
        
        with st.form("login_form"):
            username = st.text_input("Usuário")
            password = st.text_input("Senha", type="password")
            submit = st.form_submit_button("Entrar")
            
            if submit:
                if username == CREDENTIALS["username"] and password == CREDENTIALS["password"]:
                    st.session_state.authenticated = True
                    st.success("✅ Login realizado com sucesso!")
                    st.rerun()
                else:
                    st.error("❌ Usuário ou senha incorretos!")
    
    return False

def logout():
    """Faz logout do usuário"""
    st.session_state.authenticated = False
    st.rerun()

# Funções para salvar e carregar grupos
def salvar_grupos(grupos, nome_sorteio, grupos_manuais=None):
    """Salva os grupos em arquivo JSON"""
    dados = []
    if GRUPOS_FILE.exists():
        with open(GRUPOS_FILE, 'r', encoding='utf-8') as f:
            dados = json.load(f)
    
    # Criar novo registro
    registro = {
        'id': len(dados) + 1,
        'nome': nome_sorteio,
        'data': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'grupos_automaticos': grupos,
        'grupos_manuais': grupos_manuais if grupos_manuais else []
    }
    
    dados.append(registro)
    
    with open(GRUPOS_FILE, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    
    return registro['id']

def carregar_grupos():
    """Carrega todos os sorteios salvos"""
    if GRUPOS_FILE.exists():
        with open(GRUPOS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def buscar_aluno(nome_parcial):
    """Busca em qual grupo um aluno está"""
    sorteios = carregar_grupos()
    resultados = []
    
    nome_parcial = nome_parcial.lower().strip()
    
    for sorteio in sorteios:
        # Buscar nos grupos automáticos
        for idx, grupo in enumerate(sorteio['grupos_automaticos']):
            for aluno in grupo:
                if nome_parcial in aluno.lower():
                    resultados.append({
                        'sorteio_id': sorteio['id'],
                        'sorteio_nome': sorteio['nome'],
                        'data': sorteio['data'],
                        'tipo_grupo': 'Automático',
                        'numero_grupo': idx + 1,
                        'aluno': aluno,
                        'grupo_completo': grupo
                    })
        
        # Buscar nos grupos manuais
        for idx, grupo in enumerate(sorteio['grupos_manuais']):
            for aluno in grupo:
                if nome_parcial in aluno.lower():
                    resultados.append({
                        'sorteio_id': sorteio['id'],
                        'sorteio_nome': sorteio['nome'],
                        'data': sorteio['data'],
                        'tipo_grupo': 'Manual',
                        'numero_grupo': idx + 1,
                        'aluno': aluno,
                        'grupo_completo': grupo
                    })
    
    return resultados

def deletar_sorteio(sorteio_id):
    """Deleta um sorteio salvo"""
    sorteios = carregar_grupos()
    sorteios = [s for s in sorteios if s['id'] != sorteio_id]
    
    with open(GRUPOS_FILE, 'w', encoding='utf-8') as f:
        json.dump(sorteios, f, ensure_ascii=False, indent=2)
    
    return True

# Função para carregar dados
@st.cache_data
def carregar_dados(arquivo):
    df = pd.read_csv(arquivo, sep=';', encoding='utf-8')
    df = df[['Nome', 'Turma']].copy()
    df['Nome'] = df['Nome'].str.strip()
    df['Turma'] = df['Turma'].astype(int)
    return df

# Função para validar grupos
def validar_grupo(grupo, df):
    """Verifica se o grupo tem pelo menos 1 calouro (Turma 1)"""
    turmas = df[df['Nome'].isin(grupo)]['Turma'].values
    return 1 in turmas

# Função para realizar sorteio automático
def sortear_grupos(df, tamanho_grupo=4, grupos_manuais=None):
    """Sorteia grupos garantindo que cada grupo tenha pelo menos 1 calouro
    e que nenhum calouro fique sozinho"""
    
    # Separar alunos em calouros e veteranos
    calouros = df[df['Turma'] == 1]['Nome'].tolist()
    veteranos = df[df['Turma'] == 2]['Nome'].tolist()
    
    # Remover alunos que já estão em grupos manuais
    if grupos_manuais:
        alunos_manuais = [aluno for grupo in grupos_manuais for aluno in grupo]
        calouros = [c for c in calouros if c not in alunos_manuais]
        veteranos = [v for v in veteranos if v not in alunos_manuais]
    
    # Embaralhar listas
    random.shuffle(calouros)
    random.shuffle(veteranos)
    
    grupos = []
    total_grupos = len(calouros)
    
    # Criar grupos começando com um calouro em cada
    for i in range(total_grupos):
        grupo = [calouros[i]]
        
        # Adicionar veteranos até completar o grupo
        while len(grupo) < tamanho_grupo and veteranos:
            grupo.append(veteranos.pop(0))
        
        grupos.append(grupo)
    
    # Distribuir veteranos restantes nos grupos
    idx = 0
    while veteranos:
        if len(grupos[idx]) < tamanho_grupo:
            grupos[idx].append(veteranos.pop(0))
        idx = (idx + 1) % len(grupos)
    
    # Verificar e redistribuir grupos muito pequenos (menos de 2 pessoas)
    # Calouros sozinhos devem ser redistribuídos
    grupos_finais = []
    calouros_sozinhos = []
    
    for grupo in grupos:
        if len(grupo) == 1:
            # Se é um calouro sozinho, guardar para redistribuir
            calouros_sozinhos.append(grupo[0])
        else:
            grupos_finais.append(grupo)
    
    # Redistribuir calouros que ficaram sozinhos
    # Adicionar aos grupos existentes, priorizando os menores
    for calouro in calouros_sozinhos:
        # Ordenar grupos por tamanho (menores primeiro)
        grupos_finais.sort(key=lambda x: len(x))
        # Adicionar ao menor grupo
        if grupos_finais:
            grupos_finais[0].append(calouro)
        else:
            # Se não houver grupos, criar um novo (caso extremo)
            grupos_finais.append([calouro])
    
    return grupos_finais

# Função para exibir grupos
def exibir_grupos(grupos, df, titulo="Grupos Formados"):
    st.subheader(titulo)
    
    cols = st.columns(min(3, len(grupos)))
    
    for idx, grupo in enumerate(grupos):
        with cols[idx % 3]:
            st.markdown(f"### 🎯 Grupo {idx + 1}")
            
            for aluno in grupo:
                turma = df[df['Nome'] == aluno]['Turma'].values[0]
                emoji = "🆕" if turma == 1 else "👤"
                turma_text = "Calouro" if turma == 1 else "Veterano"
                st.markdown(f"{emoji} **{aluno}** ({turma_text})")
            
            # Validação
            tem_calouro = validar_grupo(grupo, df)
            tamanho = len(grupo)
            
            if tem_calouro and tamanho >= 2:
                st.success(f"✅ Grupo válido ({tamanho} membros)")
            elif not tem_calouro:
                st.error("❌ Grupo sem calouro!")
            elif tamanho == 1:
                # Verificar se é veterano
                turma = df[df['Nome'] == grupo[0]]['Turma'].values[0]
                if turma == 2:
                    st.warning(f"⚠️ Veterano sozinho ({tamanho} membro)")
                else:
                    st.error(f"❌ Calouro sozinho! ({tamanho} membro)")
            else:
                st.info(f"ℹ️ Grupo pequeno ({tamanho} membros)")
            
            st.markdown("---")

# Interface Principal
def main():
    st.title("🎲 Sistema de Sorteio de Grupos")
    st.markdown("### Sorteio com garantia de pelo menos 1 calouro por grupo")
    
    # Carregar dados (necessário para todas as abas)
    arquivo_padrao = Path(__file__).parent / "dados_chamada" / "dados_manha.csv"
    
    if arquivo_padrao.exists():
        df = carregar_dados(arquivo_padrao)
    else:
        st.error("Arquivo de dados não encontrado!")
        return
    
    # Verificar autenticação
    is_authenticated = check_password()
    
    # Mostrar botão de logout se autenticado
    if is_authenticated:
        with st.sidebar:
            st.markdown("---")
            st.success(f"✅ Logado como: **{CREDENTIALS['username']}**")
            if st.button("🚪 Sair", use_container_width=True):
                logout()
    
    # Sidebar para configurações (apenas para usuários autenticados)
    if is_authenticated:
        st.sidebar.header("⚙️ Configurações")
        
        uploaded_file = st.sidebar.file_uploader(
            "Carregar arquivo CSV (opcional)", 
            type=['csv'],
            help="Se não carregar, usará o arquivo padrão"
        )
        
        if uploaded_file:
            df = carregar_dados(uploaded_file)
    
    # Mostrar estatísticas
    st.sidebar.markdown("### 📊 Estatísticas")
    st.sidebar.metric("Total de Alunos", len(df))
    st.sidebar.metric("Calouros (Turma 1)", len(df[df['Turma'] == 1]))
    st.sidebar.metric("Veteranos (Turma 2)", len(df[df['Turma'] == 2]))
    
    # Tamanho do grupo
    tamanho_grupo = st.sidebar.slider(
        "Tamanho do grupo",
        min_value=2,
        max_value=6,
        value=4,
        help="Número de alunos por grupo"
    )
    
    # Seed para reprodutibilidade
    usar_seed = st.sidebar.checkbox("Usar seed (reproduzível)")
    if usar_seed:
        seed = st.sidebar.number_input("Seed", min_value=0, value=42)
        random.seed(seed)
    
    st.sidebar.markdown("---")
    
    # Tabs para diferentes funcionalidades
    tab1, tab2, tab3, tab4 = st.tabs(["🎲 Sorteio Automático", "✏️ Grupos Manuais", "� Consultar Grupos", "📋 Visualizar Dados"])
    
    with tab1:
        if not is_authenticated:
            st.warning("🔒 Por favor, faça login para acessar a funcionalidade de sorteio automático.")
        else:
            st.header("Sorteio Automático")
            st.markdown("Clique no botão abaixo para sortear os grupos automaticamente.")
            
            col1, col2 = st.columns([1, 4])
            with col1:
                sortear = st.button("🎲 Sortear Grupos", type="primary", use_container_width=True)
            
            # Incluir grupos manuais no sorteio
            grupos_manuais_para_sorteio = None
            if 'grupos_manuais' in st.session_state and st.session_state.grupos_manuais:
                incluir_manuais = st.checkbox(
                    "Incluir grupos manuais criados (eles serão excluídos do sorteio)",
                    value=True
                )
                if incluir_manuais:
                    grupos_manuais_para_sorteio = st.session_state.grupos_manuais
            
            if sortear:
                grupos = sortear_grupos(df, tamanho_grupo, grupos_manuais_para_sorteio)
                st.session_state.grupos_sorteados = grupos
                st.balloons()
            
            # Exibir grupos manuais primeiro
            if grupos_manuais_para_sorteio:
                exibir_grupos(grupos_manuais_para_sorteio, df, "📌 Grupos Manuais")
                st.markdown("---")
            
            # Exibir grupos sorteados
            if 'grupos_sorteados' in st.session_state:
                exibir_grupos(st.session_state.grupos_sorteados, df, "🎲 Grupos Sorteados")
                
                # Botões de ação
                st.markdown("---")
                col1, col2 = st.columns(2)
                
                with col1:
                    # Salvar sorteio
                    with st.form("salvar_sorteio"):
                        nome_sorteio = st.text_input(
                            "Nome do sorteio",
                            value=f"Sorteio {datetime.now().strftime('%d/%m/%Y %H:%M')}",
                            help="Dê um nome para identificar este sorteio"
                        )
                        
                        if st.form_submit_button("💾 Salvar Sorteio", type="primary"):
                            sorteio_id = salvar_grupos(
                                st.session_state.grupos_sorteados,
                                nome_sorteio,
                                grupos_manuais_para_sorteio
                            )
                            st.success(f"✅ Sorteio '{nome_sorteio}' salvo com sucesso! (ID: {sorteio_id})")
                
                with col2:
                    # Exportar CSV
                    if st.button("📥 Exportar Grupos (CSV)", use_container_width=True):
                        resultado = []
                        
                        # Adicionar grupos manuais
                        if grupos_manuais_para_sorteio:
                            for idx, grupo in enumerate(grupos_manuais_para_sorteio):
                                for aluno in grupo:
                                    turma = df[df['Nome'] == aluno]['Turma'].values[0]
                                    resultado.append({
                                        'Grupo': f'Manual {idx + 1}',
                                        'Nome': aluno,
                                        'Turma': turma
                                    })
                        
                        # Adicionar grupos sorteados
                        for idx, grupo in enumerate(st.session_state.grupos_sorteados):
                            for aluno in grupo:
                                turma = df[df['Nome'] == aluno]['Turma'].values[0]
                                resultado.append({
                                    'Grupo': f'Grupo {idx + 1}',
                                    'Nome': aluno,
                                    'Turma': turma
                                })
                        
                        df_resultado = pd.DataFrame(resultado)
                        csv = df_resultado.to_csv(index=False, encoding='utf-8')
                        
                        st.download_button(
                            label="⬇️ Download CSV",
                            data=csv,
                            file_name="grupos_sorteados.csv",
                            mime="text/csv"
                        )
    
    with tab2:
        if not is_authenticated:
            st.warning("🔒 Por favor, faça login para criar grupos manualmente.")
        else:
            st.header("Criar Grupos Manualmente")
            st.markdown("Selecione os alunos para criar grupos personalizados.")
            
            # Inicializar session state
            if 'grupos_manuais' not in st.session_state:
                st.session_state.grupos_manuais = []
            
            # Obter alunos já alocados
            alunos_alocados = [aluno for grupo in st.session_state.grupos_manuais for aluno in grupo]
            alunos_disponiveis = df[~df['Nome'].isin(alunos_alocados)]['Nome'].tolist()
            
            st.markdown(f"**Alunos disponíveis:** {len(alunos_disponiveis)}")
            
            # Formulário para criar novo grupo
            with st.form("novo_grupo_manual"):
                st.subheader(f"Criar Grupo {len(st.session_state.grupos_manuais) + 1}")
                
                # Multiselect para escolher alunos
                alunos_selecionados = st.multiselect(
                    "Selecione os alunos (máximo 6)",
                    options=sorted(alunos_disponiveis),
                    max_selections=6,
                    help="Escolha os alunos que farão parte deste grupo"
                )
                
                # Mostrar preview
                if alunos_selecionados:
                    st.markdown("**Preview do grupo:**")
                    for aluno in alunos_selecionados:
                        turma = df[df['Nome'] == aluno]['Turma'].values[0]
                        emoji = "🆕" if turma == 1 else "👤"
                        turma_text = "Calouro" if turma == 1 else "Veterano"
                        st.text(f"{emoji} {aluno} ({turma_text})")
                    
                    # Validação
                    tem_calouro = any(df[df['Nome'] == aluno]['Turma'].values[0] == 1 
                                     for aluno in alunos_selecionados)
                    if tem_calouro:
                        st.success("✅ Grupo válido (tem calouro)")
                    else:
                        st.warning("⚠️ Grupo sem calouro!")
                
                submitted = st.form_submit_button("➕ Adicionar Grupo", type="primary")
                
                if submitted and alunos_selecionados:
                    st.session_state.grupos_manuais.append(alunos_selecionados)
                    st.success(f"Grupo {len(st.session_state.grupos_manuais)} adicionado!")
                    st.rerun()
            
            # Exibir grupos manuais criados
            if st.session_state.grupos_manuais:
                st.markdown("---")
                exibir_grupos(st.session_state.grupos_manuais, df, "📌 Grupos Manuais Criados")
                
                # Botões de ação
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🗑️ Limpar Todos os Grupos Manuais", type="secondary"):
                        st.session_state.grupos_manuais = []
                        st.rerun()
                
                with col2:
                    if st.button("❌ Remover Último Grupo"):
                        if st.session_state.grupos_manuais:
                            st.session_state.grupos_manuais.pop()
                            st.rerun()
    
    with tab3:
        st.header("🔍 Consultar Grupos Salvos")
        
        # Buscar aluno
        st.subheader("Buscar Aluno")
        col1, col2 = st.columns([3, 1])
        
        with col1:
            nome_busca = st.text_input(
                "Digite parte do nome do aluno",
                placeholder="Ex: João, Maria, Silva...",
                help="Digite qualquer parte do nome para buscar"
            )
        
        with col2:
            buscar_btn = st.button("🔍 Buscar", type="primary", use_container_width=True)
        
        if buscar_btn and nome_busca:
            resultados = buscar_aluno(nome_busca)
            
            if resultados:
                st.success(f"✅ Encontrado(s) {len(resultados)} resultado(s)")
                
                for resultado in resultados:
                    with st.expander(
                        f"📌 {resultado['aluno']} - {resultado['sorteio_nome']} (Grupo {resultado['numero_grupo']})",
                        expanded=True
                    ):
                        # Mostrar informações básicas
                        if is_authenticated:
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.metric("Sorteio", resultado['sorteio_nome'])
                            with col2:
                                st.metric("Data", resultado['data'])
                            with col3:
                                st.metric("Tipo", resultado['tipo_grupo'])
                        else:
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.metric("Sorteio", resultado['sorteio_nome'])
                            with col2:
                                st.metric("Grupo", resultado['numero_grupo'])
                        
                        st.markdown(f"### 🎯 Grupo {resultado['numero_grupo']}")
                        st.markdown("**Membros do grupo:**")
                        
                        for membro in resultado['grupo_completo']:
                            turma = df[df['Nome'] == membro]['Turma'].values[0] if membro in df['Nome'].values else '?'
                            emoji = "🆕" if turma == 1 else "👤" if turma == 2 else "❓"
                            turma_text = "Calouro" if turma == 1 else "Veterano" if turma == 2 else "Desconhecido"
                            
                            # Destacar o aluno buscado
                            if membro == resultado['aluno']:
                                st.markdown(f"**{emoji} {membro}** ({turma_text}) ⭐")
                            else:
                                st.markdown(f"{emoji} {membro} ({turma_text})")
            else:
                st.warning(f"❌ Nenhum resultado encontrado para '{nome_busca}'")
        
        # Listar todos os sorteios salvos - APENAS PARA AUTENTICADOS
        if is_authenticated:
            st.markdown("---")
            st.subheader("📋 Todos os Sorteios Salvos")
            
            sorteios = carregar_grupos()
            
            if sorteios:
                st.info(f"Total de sorteios salvos: {len(sorteios)}")
                
                for sorteio in reversed(sorteios):  # Mostrar os mais recentes primeiro
                    with st.expander(f"📁 {sorteio['nome']} - {sorteio['data']}", expanded=False):
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.markdown(f"**ID:** {sorteio['id']}")
                            st.markdown(f"**Data:** {sorteio['data']}")
                            
                            total_grupos = len(sorteio['grupos_automaticos']) + len(sorteio['grupos_manuais'])
                            total_alunos = sum(len(g) for g in sorteio['grupos_automaticos']) + sum(len(g) for g in sorteio['grupos_manuais'])
                            
                            st.markdown(f"**Total de grupos:** {total_grupos}")
                            st.markdown(f"**Total de alunos:** {total_alunos}")
                        
                        with col2:
                            if st.button(f"🗑️ Deletar", key=f"del_{sorteio['id']}", type="secondary"):
                                deletar_sorteio(sorteio['id'])
                                st.success(f"Sorteio '{sorteio['nome']}' deletado!")
                                st.rerun()
                        
                        # Mostrar grupos manuais
                        if sorteio['grupos_manuais']:
                            st.markdown("### 📌 Grupos Manuais")
                            for idx, grupo in enumerate(sorteio['grupos_manuais']):
                                st.markdown(f"**Grupo Manual {idx + 1}:** {', '.join(grupo)}")
                        
                        # Mostrar grupos automáticos
                        if sorteio['grupos_automaticos']:
                            st.markdown("### 🎲 Grupos Automáticos")
                            for idx, grupo in enumerate(sorteio['grupos_automaticos']):
                                st.markdown(f"**Grupo {idx + 1}:** {', '.join(grupo)}")
            else:
                st.info("📭 Nenhum sorteio salvo ainda. Faça um sorteio e clique em 'Salvar Sorteio'!")
    
    with tab4:
        if not is_authenticated:
            st.warning("🔒 Por favor, faça login para visualizar os dados dos alunos.")
        else:
            st.header("📋 Visualizar Dados dos Alunos")
            
            # Filtros
            col1, col2 = st.columns(2)
            with col1:
                filtro_turma = st.multiselect(
                    "Filtrar por turma",
                    options=[1, 2],
                    default=[1, 2],
                    format_func=lambda x: "Turma 1 (Calouros)" if x == 1 else "Turma 2 (Veteranos)"
                )
            
            with col2:
                busca = st.text_input("🔍 Buscar por nome")
            
            # Aplicar filtros
            df_filtrado = df[df['Turma'].isin(filtro_turma)]
            if busca:
                df_filtrado = df_filtrado[df_filtrado['Nome'].str.contains(busca, case=False)]
            
            # Mostrar dados
            st.dataframe(
                df_filtrado,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Nome": st.column_config.TextColumn("Nome do Aluno", width="large"),
                    "Turma": st.column_config.NumberColumn("Turma", width="small")
                }
            )
            
            st.metric("Total filtrado", len(df_filtrado))

if __name__ == "__main__":
    main()
