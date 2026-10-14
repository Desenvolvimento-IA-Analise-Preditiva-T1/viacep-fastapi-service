import re
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI, HTTPException, Path, status
from pydantic import BaseModel, Field
import httpx


# Esquemas de Dados com Pydantic
class RespostaEndereco(BaseModel):
    """Esquema de saída com os campos exatos solicitados no exercício."""
    logradouro: str = Field(..., description="Nome da rua, avenida ou praça")
    bairro: str = Field(..., description="Bairro ou distrito")
    estado: str = Field(..., description="Sigla da Unidade Federativa (ex: SP, RJ)")
    regiao: str = Field(..., description="Região do país (ex: Sudeste, Nordeste)")

    model_config = {
        "json_schema_extra": {
            "example": {
                "logradouro": "Praça da Sé",
                "bairro": "Sé",
                "estado": "SP",
                "regiao": "Sudeste"
            }
        }
    }



# Gerenciamento do Ciclo de Vida da Aplicação (Lifespan)
# Cliente HTTP assíncrono compartilhado durante toda a execução da API
http_client: httpx.AsyncClient | None = None

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Gerencia a inicialização e o encerramento do cliente HTTP.
    Evita recriar pools de conexão a cada requisição de CEP.
    """
    global http_client
    http_client = httpx.AsyncClient(timeout=5.0)
    yield
    await http_client.aclose()


# Inicialização da Aplicação FastAPI
app = FastAPI(
    title="API de Consulta de Endereço (ViaCEP Proxy)",
    description="Microsserviço de consulta de endereço a partir de CEP utilizando FastAPI, Pydantic e HTTPX.",
    version="1.0.0",
    lifespan=lifespan
)


# Rota de Monitoramento (Healthcheck)
@app.get("/health", tags=["Monitoramento"])
async def verificar_saude():
    return {"status": "online", "servico": "consulta_cep"}


# Endpoint Principal: Consulta de CEP
@app.get(
    "/endereco/{cep}",
    response_model=RespostaEndereco,
    status_code=status.HTTP_200_OK,
    summary="Busca endereço pelo CEP",
    tags=["Endereço"]
)
async def buscar_endereco_por_cep(
    cep: str = Path(
        ...,
        description="CEP com 8 dígitos, com ou sem hífen (ex: 06420-130 ou 06420130)",
        examples=["06420-130", "01001000"]
    )
):
    # Higienização: remove traços, pontos ou espaços
    cep_limpo = re.sub(r"\D", "", cep)

    # Validação: confere se restaram exatamente 8 dígitos numéricos
    if len(cep_limpo) != 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Formato de CEP inválido: '{cep}'. O CEP deve conter exatamente 8 dígitos numéricos."
        )

    # Consumo da API externa com o cliente HTTP assíncrono
    url_viacep = f"https://viacep.com.br/ws/{cep_limpo}/json/"

    try:
        resposta = await http_client.get(url_viacep)
        resposta.raise_for_status()
    except httpx.HTTPError:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Não foi possível estabelecer comunicação com o provedor externo (ViaCEP)."
        )

    dados = resposta.json()

    # Verificação de CEP não encontrado (regra da API do ViaCEP)
    if dados.get("erro") is True or dados.get("erro") == "true":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"CEP '{cep_limpo}' não localizado na base nacional de endereços."
        )

    # Extração e mapeamento dos 4 campos obrigatórios
    # Obs.: o ViaCEP fornece 'uf' (ou 'estado') e o campo 'regiao'
    return RespostaEndereco(
        logradouro=dados.get("logradouro", ""),
        bairro=dados.get("bairro", ""),
        estado=dados.get("uf", dados.get("estado", "")),
        regiao=dados.get("regiao", "")
    )


# uvicorn main:app --reload --port 8000
