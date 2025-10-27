import json
import os
from typing import Dict, TypedDict

import bcrypt
import pandas as pd
import plotly.express as px
import streamlit as st

# TypedDict for calculation result
class CalculoResult(TypedDict):
    df: 'pd.DataFrame'
    valor_fixo_corrigido: float
    valor_variavel_por_residente: float
    total_arrecadado: float
    valor_total_da_conta: float
    total_residentes: int




st.set_page_config(page_title="Dashboard: Conta de Água", layout="wide", page_icon="💧")

CONFIG_FILE = "config.json"


# ---------------------- Helpers ----------------------
def parse_float(text: str, default: float = 0.0) -> float:
    """Safely parse a float from text (accepts comma as decimal)."""
    if not isinstance(text, str):
        return default
    t = text.strip().replace("\u00a0", "")
    t = t.replace(",", ".")
    try:
        return float(t)
    except Exception:
        return default


def to_positive_int(val: object) -> int | None:
    """Try to convert val to a non-negative int. Return None if invalid."""
    try:
        if isinstance(val, int):
            v = val
        else:
            v = int(str(val).strip())
        if v >= 0:
            return v
    except Exception:
        return None
    return None


def format_currency(value: float) -> str:
    return f"R$ {value:.2f}"


# Função para carregar dados de usuários
def carregar_usuarios() -> dict[str, str]:
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
def salvar_usuario(usuario: str, senha: str) -> None:
    usuarios = carregar_usuarios()
    hashed = bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()
    usuarios[usuario] = hashed
    with open(CONFIG_FILE, "w") as f:
        json.dump({"users": usuarios}, f, indent=4)


# Função para recriar config.json padrão
def criar_config_padrao() -> None:
    if not os.path.exists(CONFIG_FILE):
        salvar_usuario("admin", "admin123")
        st.info("Arquivo config.json criado com usuário padrão: admin/admin123")


# Tela de login
def autenticar_usuarios() -> None:
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

match modo_lista:
    case "Gerar automaticamente":
        num_apts = st.sidebar.number_input(
            "Número de apartamentos:", min_value=1, max_value=100, value=8, step=1
        )
        # pyrefly: ignore  # no-matching-overload
        apartamentos = [f"{str(i + 1).zfill(2)}" for i in range(num_apts)]
    case "Importar de JSON":
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
    case _:
        apartamentos = []

st.sidebar.header("👥 Moradores por Apartamento")
distribuicao_residentes = {}
for apto in apartamentos:
    valor = st.sidebar.text_input(
        f"{apto}", value="2", placeholder="Digite o número de moradores"
    )
    # store raw value; we'll validate/convert in calcular()
    distribuicao_residentes[apto] = valor


# Inputs principais
st.title("💧 Dashboard de Conta de Água e Esgoto")
with st.expander("📅 Preencha os dados da conta"):
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        val1 = st.text_input(
            "Valor de esgoto (fixo)", value="0.00", placeholder="Ex: 150.00"
        )
        valor_fixo = parse_float(val1)
    with col2:
        val2 = st.text_input(
            "Valor de água (variável)", value="0.00", placeholder="Ex: 180.50"
        )
        valor_variavel = parse_float(val2)
    with col3:
        val3 = st.text_input(
            "Recursos hídricos (água)", value="0.00", placeholder="Ex: 25.00"
        )
        recursos_hidr_agua = parse_float(val3)
    with col4:
        val4 = st.text_input(
            "Recursos hídricos (esgoto)", value="0.00", placeholder="Ex: 30.00"
        )
        recursos_hidr_esg = parse_float(val4)


# Cálculo principal
def calcular(
    distrib: dict[str, object],
    valor_fixo: float,
    valor_variavel: float,
    rec_agua: float,
    rec_esg: float
) -> CalculoResult:
    # Convert inputs to valid integers; ignore invalid entries
    distrib_clean: Dict[str, int] = {}
    for k, v in distrib.items():
        iv = to_positive_int(v)
        if iv is not None:
            distrib_clean[k] = iv

    n_apts = len(distrib_clean)
    total = valor_fixo + valor_variavel + rec_agua + rec_esg

    # If there are no valid apartments, return an empty, safe result
    if n_apts == 0:
        # explicit empty DataFrame with typed Series avoids static-type warnings
        empty_df = pd.DataFrame(
            {
                "Apartamento": pd.Series(dtype=object),
                "Moradores": pd.Series(dtype=int),
                "Valor Total (R$)": pd.Series(dtype=float),
            }
        )
        return CalculoResult(
            df=empty_df,
            valor_fixo_corrigido=0.0,
            valor_variavel_por_residente=0.0,
            total_arrecadado=0.0,
            valor_total_da_conta=round(float(total), 2),
            total_residentes=0,
        )

    n_residentes = sum(distrib_clean.values())

    v_fixo_base = valor_fixo / n_apts if n_apts > 0 else 0.0
    v_var_pessoa = valor_variavel / n_residentes if n_residentes > 0 else 0.0

    inicial = sum(v_fixo_base + v_var_pessoa * r for r in distrib_clean.values())
    ajuste = (total - inicial) / n_apts if n_apts > 0 else 0.0
    v_fixo_corrigido = v_fixo_base + ajuste

    detalhes = []
    for apto, moradores in distrib_clean.items():
        # ensure plain python types so static analysis is happy
        moradores_int = int(moradores)
        valor = round(v_fixo_corrigido + moradores_int * v_var_pessoa, 2)
        valor = float(valor)
        detalhes.append(
            {"Apartamento": apto, "Moradores": moradores_int, "Valor Total (R$)": valor}
        )

    # compute total as a pure python float (avoid incremental += type issues)
    total_pago = float(sum(d["Valor Total (R$)"] for d in detalhes))

    return CalculoResult(
        df=pd.DataFrame(detalhes).sort_values("Apartamento"),
        valor_fixo_corrigido=round(v_fixo_corrigido, 2),
        valor_variavel_por_residente=round(v_var_pessoa, 2),
        total_arrecadado=round(float(total_pago), 2),
        valor_total_da_conta=round(float(total), 2),
        total_residentes=n_residentes,
    )


if st.button("🚀 Calcular"):
    resultado = calcular(
        distribuicao_residentes,
        valor_fixo,
        valor_variavel,
        recursos_hidr_agua,
        recursos_hidr_esg,
    )
    df = resultado["df"]
    if not isinstance(df, pd.DataFrame):
        st.error("Erro interno: resultado['df'] não é um DataFrame.")
        st.stop()

    # If result is empty (no valid apartments), show a helpful message
    if isinstance(df, pd.DataFrame) and df.empty:
        st.warning(
            "Nenhum apartamento válido encontrado. Verifique os valores informados no painel lateral."
        )
        # still show total account value
        st.metric(
            "💰 Valor total da conta",
            format_currency(resultado["valor_total_da_conta"]),
        )
    else:
        # Métricas
        col1, col2, col3 = st.columns(3)
        col1.metric(
            "🔢 Valor fixo por apto", format_currency(resultado["valor_fixo_corrigido"])
        )
        col2.metric(
            "👤 Valor variável por residente",
            format_currency(resultado["valor_variavel_por_residente"]),
        )
        col3.metric(
            "💰 Valor total da conta",
            format_currency(resultado["valor_total_da_conta"]),
        )

        # Tabela
        st.subheader("🏠 Distribuição por apartamento")
        st.dataframe(df, width='stretch')

        # Gráficos com Plotly
        colg1, colg2 = st.columns(2)

        with colg1:
            st.subheader("📊 Valor pago por apartamento")
            fig_bar = px.bar(df, x="Apartamento", y="Valor Total (R$)", text_auto=True)
            st.plotly_chart(fig_bar, width='stretch')

        with colg2:
            st.subheader("🥧 Distribuição de moradores")
            fig_pie = px.pie(df, values="Moradores", names="Apartamento", hole=0.3)
            st.plotly_chart(fig_pie, width='stretch')

        # Download
        if isinstance(df, pd.DataFrame):
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "📅 Baixar resultado em CSV",
                csv,
                file_name="resultado_conta_agua.csv",
                mime="text/csv",
            )
