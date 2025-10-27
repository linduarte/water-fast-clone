
from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Dict
from calculate import calcular_conta_agua, CalculoResult

app = FastAPI()



class ContaRequest(BaseModel):
    distribuicao_residentes: Dict[str, int] = Field(..., description="Mapa de apartamento para número de moradores")
    valor_fixo: float
    valor_variavel: float
    recursos_hidr_agua: float
    recursos_hidr_esg: float




@app.post("/calcular-conta")
def calcular(request: ContaRequest) -> CalculoResult:
    resultado = calcular_conta_agua(
        request.distribuicao_residentes,
        request.valor_fixo,
        request.valor_variavel,
        request.recursos_hidr_agua,
        request.recursos_hidr_esg,
    )
    return resultado
