import streamlit as st


# Função de cálculo reaproveitada
def calcular_conta_agua(
    valor_fixo, valor_variavel, recursos_hidr_agua, recursos_hidr_esg
):
    distribuicao_residentes = {
        "apartamento 01": 3,
        "apartamento 02": 3,
        "apartamento 101": 2,
        "apartamento 102": 2,
        "apartamento 201": 2,
        "apartamento 202": 2,
        "apartamento 301": 1,
        "apartamento 302": 2,
    }

    numero_apartamentos = len(distribuicao_residentes)
    numero_residentes = sum(distribuicao_residentes.values())
    total_conta_agua = (
        valor_fixo + valor_variavel + recursos_hidr_agua + recursos_hidr_esg
    )

    valor_fixo_por_apartamento = valor_fixo / numero_apartamentos
    valor_variavel_por_residente = valor_variavel / numero_residentes

    total_pago_inicial = sum(
        valor_fixo_por_apartamento + valor_variavel_por_residente * r
        for r in distribuicao_residentes.values()
    )

    diferenca = total_conta_agua - total_pago_inicial
    ajuste_por_apartamento = diferenca / numero_apartamentos
    valor_fixo_corrigido = valor_fixo_por_apartamento + ajuste_por_apartamento

    resultado = {
        "valor_fixo_corrigido": round(valor_fixo_corrigido, 2),
        "valor_variavel_por_residente": round(valor_variavel_por_residente, 2),
        "detalhes_por_apartamento": {},
        "total_arrecadado": 0.0,
        "valor_total_da_conta": round(total_conta_agua, 2),
    }

    total_corrigido = 0
    for apto, moradores in distribuicao_residentes.items():
        valor_total = valor_fixo_corrigido + valor_variavel_por_residente * moradores
        resultado["detalhes_por_apartamento"][apto] = round(valor_total, 2)
        total_corrigido += valor_total

    resultado["total_arrecadado"] = round(total_corrigido, 2)
    return resultado


# Interface com o usuário
st.title("💧 Calculadora de Conta de Água e Esgoto")

valor_fixo = st.number_input(
    "Valor de esgoto dinâmico (fixo): R$", min_value=0.0, format="%.2f"
)
valor_variavel = st.number_input(
    "Valor de abastecimento de água (variável): R$", min_value=0.0, format="%.2f"
)
recursos_hidr_agua = st.number_input(
    "Valor de recursos hídricos - água: R$", min_value=0.0, format="%.2f"
)
recursos_hidr_esg = st.number_input(
    "Valor de recursos hídricos - esgoto: R$", min_value=0.0, format="%.2f"
)

if st.button("Calcular"):
    resultado = calcular_conta_agua(
        valor_fixo, valor_variavel, recursos_hidr_agua, recursos_hidr_esg
    )

    st.subheader("🔍 Resultado")
    st.write(
        f"**Valor fixo ajustado por apartamento:** R$ {resultado['valor_fixo_corrigido']}"
    )
    st.write(
        f"**Valor variável por residente:** R$ {resultado['valor_variavel_por_residente']}"
    )

    st.subheader("🏠 Valores por apartamento")
    for apto, valor in resultado["detalhes_por_apartamento"].items():
        st.write(f"{apto}: R$ {valor}")

    st.subheader("📊 Totais")
    st.write(f"**Total arrecadado:** R$ {resultado['total_arrecadado']}")
    st.write(f"**Valor total da conta:** R$ {resultado['valor_total_da_conta']}")
