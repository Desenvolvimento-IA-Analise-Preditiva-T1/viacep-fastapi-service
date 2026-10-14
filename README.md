# 📍 API de Consulta de Endereço (ViaCEP Proxy)

Microsserviço RESTful construído em Python com **FastAPI**, **Pydantic** e **HTTPX**. A aplicação atua como um *Proxy Reverso*, consumindo os dados da API pública do ViaCEP, higienizando os parâmetros de entrada e devolvendo uma resposta limpa e padronizada apenas com os campos essenciais de endereço.

---

## 🎯 Objetivo e Problema Resolvido

Aplicações cliente (front-end web e mobile) não devem consultar provedores públicos externos diretamente por motivos de segurança, padronização de erros e desperdício de banda (*over-fetching* de dados como IBGE, SIAFI e DDD). 

Esta API resolve esse problema ao:
* Atuar como intermediário seguro e assíncrono.
* Higienizar formatos de CEP (aceitando `06420-130` ou `06420130`).
* Validar a integridade dos dados antes da consulta externa.
* Filtrar e retornar estritamente os campos: `logradouro`, `bairro`, `estado` e `regiao`.
* Traduzir inconsistências de resposta externa para códigos de status HTTP semânticos (`200`, `400`, `404`, `502`).

---

## 🛠️ Tecnologias e Bibliotecas

* **[Python 3.10+](https://www.python.org/)**
* **[FastAPI](https://fastapi.tiangolo.com/)**: Framework moderno para construção de APIs assíncronas de alta performance.
* **[Uvicorn](https://www.uvicorn.org/)**: Servidor web ASGI para execução concorrente e não bloqueante.
* **[Pydantic v2](https://docs.pydantic.dev/)**: Modelagem, validação estrita de tipos e serialização de dados.
* **[HTTPX](https://www.python-httpx.org/)**: Cliente HTTP assíncrono com suporte a pool de conexões persistentes.

---

## 📂 Estrutura de Arquivos

```text
api-consulta-cep/
│
├── main.py              # Código-fonte da aplicação FastAPI
├── requirements.txt     # Dependências e versões do projeto
├── .gitignore           # Arquivos e diretórios ignorados pelo Git
└── README.md            # Documentação da solução

```

---

## 🚀 Como Executar o Projeto Localmente

### 1. Clonar o repositório e acessar a pasta:

```bash
git clone [https://github.com/seu-usuario/api-consulta-cep.git](https://github.com/seu-usuario/api-consulta-cep.git)
cd api-consulta-cep

```

### 2. Criar e ativar o ambiente virtual:

* **Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate

```


* **Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1

```



### 3. Instalar as dependências:

Crie o arquivo `requirements.txt` (caso ainda não exista) com:

```text
annotated-doc==0.0.5
annotated-types==0.8.0
anyio==4.15.1
certifi==2026.7.22
click==8.5.0
fastapi==0.143.1
h11==0.16.0
httpcore==1.0.9
httpx==0.28.1
idna==3.20
opentelemetry-api==1.45.1
pydantic==2.14.1
pydantic_core==2.50.1
starlette==1.8.0
typing-inspection==0.4.4
typing_extensions==4.16.0
uvicorn==0.54.0

```

Em seguida, execute:

```bash
pip install -r requirements.txt

```

### 4. Iniciar o servidor da API:

```bash
uvicorn main:app --reload --port 8000

```

O servidor estará disponível em: `http://127.0.0.1:8000`

---

## 📖 Documentação Interativa (Swagger UI)

Com o servidor em execução, abra o navegador e acesse:

* **Swagger UI:** [http://127.0.0.1:8000/docs](https://www.google.com/search?q=http://127.0.0.1:8000/docs)
* **ReDoc:** [http://127.0.0.1:8000/redoc](https://www.google.com/search?q=http://127.0.0.1:8000/redoc)

---

## 🔌 Endpoints da API

### 1. Verificação de Saúde

* **Rota:** `GET /health`
* **Descrição:** Monitoramento operacional do serviço (healthcheck).
* **Resposta de Sucesso (`200 OK`):**
```json
{
  "status": "online",
  "servico": "consulta_cep"
}

```



---

### 2. Consulta de Endereço por CEP

* **Rota:** `GET /endereco/{cep}`
* **Parâmetro de Rota:** `cep` (com ou sem máscara/hífen).

#### Exemplo de Requisição:

```bash
curl -X GET "[http://127.0.0.1:8000/endereco/06420-130](http://127.0.0.1:8000/endereco/06420-130)"

```

#### Resposta de Sucesso (`200 OK`):

```json
{
  "logradouro": "Avenida Marginal Esquerda",
  "bairro": "Jardim Belval",
  "estado": "SP",
  "regiao": "Sudeste"
}

```

---

## ⚠️ Códigos de Status HTTP Tratados

| Código HTTP | Motivo / Situação | Exemplo de Retorno |
| --- | --- | --- |
| **`200 OK`** | Consulta efetuada e endereço encontrado. | Objeto JSON com os 4 campos mapeados. |
| **`400 Bad Request`** | CEP informado com formato inválido (diferente de 8 dígitos numéricos). | `{"detail": "Formato de CEP inválido: '123'..."}` |
| **`404 Not Found`** | CEP possui 8 dígitos, porém não existe na base nacional dos Correios. | `{"detail": "CEP '00000000' não localizado..."}` |
| **`502 Bad Gateway`** | Falha de rede ou indisponibilidade momentânea no serviço do ViaCEP. | `{"detail": "Não foi possível estabelecer comunicação..."}` |
