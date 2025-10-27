
import pandas as pd
from typing import TypedDict

class CalculoResult(TypedDict):
    df: pd.DataFrame
    valor_fixo_corrigido: float
    valor_variavel_por_residente: float
    total_arrecadado: float
    valor_total_da_conta: float
    total_residentes: int

def calcular_conta_agua(
    distribuicao_residentes: dict[str, int],
    valor_fixo: float,
    valor_variavel: float,
    recursos_hidr_agua: float,
    recursos_hidr_esg: float
) -> CalculoResult:

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

    detalhes = []
    total_corrigido = 0.0
    for apto, moradores in distribuicao_residentes.items():
        valor_total = valor_fixo_corrigido + valor_variavel_por_residente * moradores
        valor_total_rounded = round(valor_total, 2)
        detalhes.append({
            "Apartamento": apto,
            "Moradores": moradores,
            "Valor Total (R$)": valor_total_rounded
        })
        total_corrigido += valor_total_rounded

    df = pd.DataFrame(detalhes).sort_values("Apartamento")

    return CalculoResult(
        df=df,
        valor_fixo_corrigido=round(valor_fixo_corrigido, 2),
        valor_variavel_por_residente=round(valor_variavel_por_residente, 2),
        total_arrecadado=round(float(total_corrigido), 2),
        valor_total_da_conta=round(total_conta_agua, 2),
        total_residentes=numero_residentes,
    )
