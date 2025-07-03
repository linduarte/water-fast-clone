import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import json
import os
import bcrypt

CONFIG_FILE = "config.json"

# Função para carregar dados de usuários
def carregar_usuarios():
    if not os.path.exists(CONFIG_FILE):
        return {}
    with open(CONFIG_FILE, "r") as f:
        return json.load(f).get("users", {})

# Função para salvar novo usuário
def salvar_usuario(usuario, senha):
    usuarios = carregar_usuarios()
    hashed = bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()
    usuarios[usuario] = hashed
    with open(CONFIG_FILE, "w") as f:
        json.dump({"users": usuarios}, f, indent=4)

# Tela de login
def autenticar_usuarios():
    usuarios = carregar_usuarios()

    st.title("🔐 Login")
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        if usuario in usuarios and bcrypt.checkpw(senha.encode(), usuarios[usuario].encode()):
            st.session_state["autenticado"] = True
            st.session_state["usuario"] = usuario
            st.experimental_rerun()
        else:
            st.error("Usuário ou senha inválido.")

# Verifica login
if "autenticado" not in st.session_state or not st.session_state["autenticado"]:
    autenticar_usuarios()
    st.stop()

# Logout
if st.sidebar.button("🚪 Logout"):
    st.session_state.clear()
    st.experimental_rerun()

# Se autenticado
st.set_page_config(page_title="Dashboard: Conta de Água", layout="wide", page_icon="💧")
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

# Sidebar – Configuração de moradores
st.sidebar.header("👥 Moradores por Apartamento")
apartamentos = [
    f"apartamento {f}{u}" for f in ["", "1", "2", "3"] for u in ["01", "02"]
]
distribuicao_residentes = {
    apto: st.sidebar.number_input(apto, min_value=0, value=2, step=1)
    for apto in apartamentos
}

# Inputs principais
st.title("💧 Dashboard de Conta de Água e Esgoto")
with st.expander("📅 Preencha os dados da conta"):
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        valor_fixo = st.number_input(
            "Valor de esgoto (fixo)", min_value=0.0, format="%.2f"
        )
    with col2:
        valor_variavel = st.number_input(
            "Valor de água (variável)", min_value=0.0, format="%.2f"
        )
    with col3:
        recursos_hidr_agua = st.number_input(
            "Recursos hídricos (água)", min_value=0.0, format="%.2f"
        )
    with col4:
        recursos_hidr_esg = st.number_input(
            "Recursos hídricos (esgoto)", min_value=0.0, format="%.2f"
        )


# Cálculo principal
def calcular(distrib, valor_fixo, valor_variavel, rec_agua, rec_esg):
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

    # Gráficos
    colg1, colg2 = st.columns(2)

    with colg1:
        st.subheader("📊 Valor pago por apartamento")
        chart_data = df.set_index("Apartamento")["Valor Total (R$)"]
        st.bar_chart(chart_data)

    with colg2:
        st.subheader("🥧 Distribuição de moradores")
        moradores_data = df.set_index("Apartamento")["Moradores"]
        fig, ax = plt.subplots()
        ax.pie(
            moradores_data,
            labels=moradores_data.index,
            autopct="%1.1f%%",
            startangle=140,
        )
        ax.axis("equal")
        st.pyplot(fig)

    # Download
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "📅 Baixar resultado em CSV",
        csv,
        file_name="resultado_conta_agua.csv",
        mime="text/csv",
    )
