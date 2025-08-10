from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel
import httpx

app = FastAPI(
    title="API VipCoringaX - Nick Free Fire",
    description=(
        "API JSON criada por VipCoringa para consulta de Nickname Free Fire.\n"
        "Para usar, faça GET no endpoint /nickff?userId=SEU_USER_ID\n\n"
        "Exemplo: /nickff?userId=123456789\n"
        "Retorna o nickname, id e país do usuário.\n"
        "Criador: VipCoringa"
    ),
    version="1.0",
)

class NickFFResponse(BaseModel):
    username: str
    userId: str
    country: str

async def nickff(userId: str) -> NickFFResponse:
    if not userId:
        raise HTTPException(status_code=400, detail="Parâmetro userId é obrigatório")

    body = {
        "voucherPricePoint.id": 8050,
        "voucherPricePoint.price": "",
        "voucherPricePoint.variablePrice": "",
        "n": "",
        "email": "",
        "userVariablePrice": "",
        "order.data.profile": "",
        "user.userId": userId,
        "voucherTypeName": "FREEFIRE",
        "affiliateTrackingId": "",
        "impactClickId": "",
        "checkoutId": "",
        "tmwAccessToken": "",
        "shopLang": "in_ID"
    }

    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/58.0.3029.110 Safari/537.36")
    }

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post("https://order.codashop.com/id/initPayment.action",
                                     json=body,
                                     headers=headers)
            resp.raise_for_status()
            data = resp.json()
            confirmation = data.get("confirmationFields")
            if not confirmation:
                raise HTTPException(status_code=404, detail="Dados não encontrados na resposta")

            roles = confirmation.get("roles")
            if not roles or len(roles) == 0:
                raise HTTPException(status_code=404, detail="Usuário não possui roles")

            return NickFFResponse(
                username=roles[0].get("role", "Desconhecido"),
                userId=userId,
                country=confirmation.get("country", "Desconhecido")
            )
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"Erro na requisição externa: {str(e)}")
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code,
                                detail=f"Erro HTTP externo: {e.response.text}")

@app.get("/", tags=["Início"])
async def raiz():
    return {
        "mensagem": "Bem-vindo à API VipCoringaX para Nick Free Fire",
        "instrucoes": {
            "endpoint_consulta": "/nickff?userId=SEU_USER_ID",
            "exemplo": "/nickff?userId=123456789",
            "criador": "VipCoringa"
        }
    }

@app.get("/nickff", response_model=NickFFResponse, tags=["Nick Free Fire"])
async def consultar_nickff(userId: str = Query(..., description="ID do usuário Free Fire")):
    return await nickff(userId)
