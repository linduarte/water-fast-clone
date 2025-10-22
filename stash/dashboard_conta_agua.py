import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os
import bcrypt

st.set_page_config(page_title="Dashboard: Conta de Água", layout="wide", page_icon="💧")

CONFIG_FILE = "config.json"


# Função para carregar dados de usuários
def carregar_usuarios():
    if not os.path.exists(CONFIG_FILE):
        return {}

    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f).get("users", {})
    except json.JSONDecodeError:
        st.error(
            "Erro ao ler o config.json. Verifique se o arquivo está formatado corretamente."
        )
        return {}


# Função para salvar novo usuário
def salvar_usuario(usuario, senha):
    usuarios = carregar_usuarios()
    hashed = bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()
    usuarios[usuario] = hashed
    with open(CONFIG_FILE, "w") as f:
        json.dump({"users": usuarios}, f, indent=4)


# Função para recriar config.json padrão
def criar_config_padrao():
    if not os.path.exists(CONFIG_FILE):
        salvar_usuario("admin", "admin123")
        st.info("Arquivo config.json criado com usuário padrão: admin/admin123")


# Tela de login
def autenticar_usuarios():
    usuarios = carregar_usuarios()

    st.title("🔐 Login")
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        if usuario in usuarios and bcrypt.checkpw(
            senha.encode(), usuarios[usuario].encode()
        ):
            st.session_state["autenticado"] = True
            st.session_state["usuario"] = usuario
            st.rerun()
        else:
            st.error("Usuário ou senha inválido.")


# Criar config inicial se não existir
criar_config_padrao()

# Verifica login
if "autenticado" not in st.session_state or not st.session_state["autenticado"]:
    autenticar_usuarios()
    st.stop()

# Logout
if st.sidebar.button("🚪 Logout"):
    st.session_state.clear()
    st.rerun()

# Se autenticado
st.success(f"Bem-vindo, {st.session_state['usuario']}!")

# Cadastro de novo usuário (somente para admin)
if st.session_state["usuario"] == "admin":
    with st.expander("➕ Cadastrar novo usuário"):
        novo_usuario = st.text_input("Novo usuário")
        nova_senha = st.text_input("Nova senha", type="password")
        if st.button("Cadastrar"):
            if novo_usuario and nova_senha:
                salvar_usuario(novo_usuario, nova_senha)
                st.success(f"Usuário '{novo_usuario}' cadastrado com sucesso!")
            else:
                st.warning("Preencha ambos os campos.")

    with st.expander("📋 Ver todos os usuários cadastrados"):
        usuarios = carregar_usuarios()
        if usuarios:
            # pyrefly: ignore  # bad-argument-type
            st.table(pd.DataFrame(usuarios.keys(), columns=["Usuários"]))
        else:
            st.info("Nenhum usuário encontrado.")

# Sidebar – Configuração de moradores
st.sidebar.header("🏢 Apartamentos")
modo_lista = st.sidebar.radio(
    "Como deseja definir os apartamentos?",
    ["Gerar automaticamente", "Importar de JSON"],
)

if modo_lista == "Gerar automaticamente":
    num_apts = st.sidebar.number_input(
        "Número de apartamentos:", min_value=1, max_value=100, value=8, step=1
    )
    # pyrefly: ignore  # no-matching-overload
    apartamentos = [f"{str(i + 1).zfill(2)}" for i in range(num_apts)]
else:
    json_text = st.sidebar.text_area(
        "Cole a lista JSON:", height=150, placeholder='Ex: ["101", "102", "201", "202"]'
    )
    try:
        apartamentos = json.loads(json_text)
        if not isinstance(apartamentos, list):
            raise ValueError
    except Exception:
        st.sidebar.error("Formato inválido. Forneça uma lista JSON válida.")
        apartamentos = []

st.sidebar.header("👥 Moradores por Apartamento")
distribuicao_residentes = {}
for apto in apartamentos:
    valor = st.sidebar.text_input(
        f"{apto}", value="2", placeholder="Digite o número de moradores"
    )
    if not valor.isdigit() or int(valor) < 0:
        st.sidebar.error(
            f"Número inválido para o apartamento {apto}. Use apenas inteiros positivos."
        )
    distribuicao_residentes[apto] = valor

# Inputs principais
st.title("💧 Dashboard de Conta de Água e Esgoto")
with st.expander("📅 Preencha os dados da conta"):
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        val1 = st.text_input(
            "Valor de esgoto (fixo)", value="0.00", placeholder="Ex: 150.00"
        )
        valor_fixo = (
            float(val1) if val1.replace(",", ".").replace(".", "", 1).isdigit() else 0.0
        )
    with col2:
        val2 = st.text_input(
            "Valor de água (variável)", value="0.00", placeholder="Ex: 180.50"
        )
        valor_variavel = (
            float(val2) if val2.replace(",", ".").replace(".", "", 1).isdigit() else 0.0
        )
    with col3:
        val3 = st.text_input(
            "Recursos hídricos (água)", value="0.00", placeholder="Ex: 25.00"
        )
        recursos_hidr_agua = (
            float(val3) if val3.replace(",", ".").replace(".", "", 1).isdigit() else 0.0
        )
    with col4:
        val4 = st.text_input(
            "Recursos hídricos (esgoto)", value="0.00", placeholder="Ex: 30.00"
        )
        recursos_hidr_esg = (
            float(val4) if val4.replace(",", ".").replace(".", "", 1).isdigit() else 0.0
        )


# Cálculo principal
def calcular(distrib, valor_fixo, valor_variavel, rec_agua, rec_esg):
    distrib = {k: int(v) for k, v in distrib.items() if v.isdigit()}
    n_apts = len(distrib)
    n_residentes = sum(distrib.values()) or 1
    total = valor_fixo + valor_variavel + rec_agua + rec_esg

    v_fixo_base = valor_fixo / n_apts
    v_var_pessoa = valor_variavel / n_residentes

    inicial = sum(v_fixo_base + v_var_pessoa * r for r in distrib.values())
    ajuste = (total - inicial) / n_apts
    v_fixo_corrigido = v_fixo_base + ajuste

    detalhes = []
    total_pago = 0
    for apto, moradores in distrib.items():
        valor = round(v_fixo_corrigido + moradores * v_var_pessoa, 2)
        detalhes.append(
            {"Apartamento": apto, "Moradores": moradores, "Valor Total (R$)": valor}
        )
        total_pago += valor

    return {
        "df": pd.DataFrame(detalhes).sort_values("Apartamento"),
        "valor_fixo_corrigido": round(v_fixo_corrigido, 2),
        "valor_variavel_por_residente": round(v_var_pessoa, 2),
        "total_arrecadado": round(total_pago, 2),
        "valor_total_da_conta": round(total, 2),
        "total_residentes": n_residentes,
    }


if st.button("🚀 Calcular"):
    resultado = calcular(
        distribuicao_residentes,
        valor_fixo,
        valor_variavel,
        recursos_hidr_agua,
        recursos_hidr_esg,
    )
    df = resultado["df"]

    # Métricas
    col1, col2, col3 = st.columns(3)
    col1.metric("🔢 Valor fixo por apto", f"R$ {resultado['valor_fixo_corrigido']}")
    col2.metric(
        "👤 Valor variável por residente",
        f"R$ {resultado['valor_variavel_por_residente']}",
    )
    col3.metric("💰 Valor total da conta", f"R$ {resultado['valor_total_da_conta']}")

    # Tabela
    st.subheader("🏠 Distribuição por apartamento")
    st.dataframe(df, use_container_width=True)

    # Gráficos com Plotly
    colg1, colg2 = st.columns(2)

    with colg1:
        st.subheader("📊 Valor pago por apartamento")
        fig_bar = px.bar(df, x="Apartamento", y="Valor Total (R$)", text_auto=True)
        st.plotly_chart(fig_bar, use_container_width=True)

    with colg2:
        st.subheader("🥧 Distribuição de moradores")
        fig_pie = px.pie(df, values="Moradores", names="Apartamento", hole=0.3)
        st.plotly_chart(fig_pie, use_container_width=True)

    # Download
    # pyrefly: ignore  # missing-attribute
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "📅 Baixar resultado em CSV",
        csv,
        file_name="resultado_conta_agua.csv",
        mime="text/csv",
    )
