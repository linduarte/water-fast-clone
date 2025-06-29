from fastapi import FastAPI
from pydantic import BaseModel
from calculate import calcular_conta_agua

app = FastAPI()


class ContaRequest(BaseModel):
    valor_fixo: float
    valor_variavel: float
    recursos_hidr_agua: float
    recursos_hidr_esg: float


@app.post("/calcular-conta")
def calcular(request: ContaRequest):
    resultado = calcular_conta_agua(
        request.valor_fixo,
        request.valor_variavel,
        request.recursos_hidr_agua,
        request.recursos_hidr_esg,
    )
    return resultado
