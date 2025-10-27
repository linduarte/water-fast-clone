def calcular_conta_agua(
    valor_fixo: float,
    valor_variavel: float,
    recursos_hidr_agua: float,
    recursos_hidr_esg: float
) -> dict[str, float | dict[str, float]]:
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

    total_corrigido = 0.0
    for apto, moradores in distribuicao_residentes.items():
        valor_total = valor_fixo_corrigido + valor_variavel_por_residente * moradores
        # round per-apartment value and accumulate the rounded amount
        valor_total_rounded = round(valor_total, 2)
        # pyrefly: ignore  # missing-attribute
        resultado["detalhes_por_apartamento"][apto] = valor_total_rounded
        total_corrigido += valor_total_rounded

    resultado["total_arrecadado"] = round(float(total_corrigido), 2)
    return resultado
