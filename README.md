# Exchange API

Microsserviço responsável pela conversão de moedas, desenvolvido em **Python + FastAPI**. Busca cotações em tempo real a partir de uma API de terceiros e exige que as requisições sejam autenticadas via API Gateway.

---

## Arquitetura

```
Client → Gateway (Auth) → Exchange API → ExchangeRate-API (3rd party)
```

> A autenticação é responsabilidade da camada **Trusted Layer** (auth). O header `id-account` é encaminhado pelo gateway e deve estar presente em todas as requisições.

---

## Endpoint

### `GET /exchange/{from}/{to}`

Retorna a cotação atual entre duas moedas.

**Parâmetros de rota**

| Parâmetro | Tipo   | Descrição                              |
|-----------|--------|----------------------------------------|
| `from`    | string | Código da moeda de origem (ex: `USD`)  |
| `to`      | string | Código da moeda de destino (ex: `EUR`) |

**Headers**

| Header       | Obrigatório | Descrição                                  |
|--------------|-------------|--------------------------------------------|
| `id-account` | Sim         | UUID da conta, encaminhado pelo gateway    |

**Exemplo de requisição**

```
GET /exchange/USD/EUR
```

**Exemplo de resposta** — `200 OK`

```json
{
  "sell": 0.82,
  "buy": 0.80,
  "date": "2021-09-01 14:23:42",
  "id-account": "0195ae95-5be7-7dd3-b35d-7a7d87c404fb"
}
```

**Campos da resposta**

| Campo        | Tipo   | Descrição                                           |
|--------------|--------|-----------------------------------------------------|
| `sell`       | float  | Taxa de câmbio para venda da moeda de origem        |
| `buy`        | float  | Taxa de câmbio para compra da moeda de origem       |
| `date`       | string | Data e hora da conversão (`YYYY-MM-DD HH:MM:SS`)   |
| `id-account` | string | UUID da conta extraído do header da requisição      |

**Respostas de erro**

| Código | Descrição                                            |
|--------|------------------------------------------------------|
| `200`  | cotação disponível         |
| `404`  | Moeda não encontrada ou cotação indisponível         |
| `500`  | Erro interno ou falha na API de terceiros            |

---

## API de Terceiros

Este serviço utiliza a [ExchangeRate-API](https://www.exchangerate-api.com/) para buscar cotações em tempo real.

- **Endpoint utilizado:** `GET https://v6.exchangerate-api.com/v6/{API_KEY}/latest/{from}`
- **Plano gratuito:** até 1.500 requisições/mês
- **Documentação:** https://www.exchangerate-api.com/docs/overview

---

## Variáveis de Ambiente

| Variável           | Descrição                        |
|--------------------|----------------------------------|
| `EXCHANGE_API_KEY` | Chave de API do ExchangeRate-API |

---

## Executando Localmente

**Requisitos:** Python 3.10+

Crie um arquivo `.env` na raiz do projeto:

```env
EXCHANGE_API_KEY=sua_chave_aqui
```

Instale as dependências e suba o servidor:

```bash
pip install fastapi uvicorn requests python-dotenv

uvicorn main:app --reload --port 8000
```

**Testando o endpoint:**

```bash
curl -H "id-account: id_gerado_pelo_auth" \
     http://localhost:8080/exchange/USD/EUR
```

---

## Docker Compose

A variável `EXCHANGE_API_KEY` é lida automaticamente do arquivo `.env` na raiz do projeto:

```env
EXCHANGE_API_KEY=sua_chave_aqui  # ⚠️ Substitua pela sua chave real
```

O serviço no `docker-compose.yml` já está configurado para recebê-la:

```yaml
exchange:
  build:
    context: ./exchange
    dockerfile: Dockerfile
  hostname: exchange
  deploy:
    replicas: 1
  environment:
    EXCHANGE_API_KEY: ${EXCHANGE_API_KEY}
```

> **Atenção:** nunca suba o `.env` com a chave real para o repositório. Certifique-se de que ele está no `.gitignore`.

---

## Kubernetes

Os manifestos ficam na pasta `k8s/`. A chave da API é armazenada em um **Secret** para não ficar exposta em texto plano no Deployment.

**⚠️ Antes de aplicar os manifestos**, edite o arquivo do Secret e substitua o valor da chave:

```yaml
# k8s/secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: exchange-secret
type: Opaque
stringData:
  EXCHANGE_API_KEY: sua_chave_aqui  # ⚠️ Substitua pela sua chave real
```

Depois aplique todos os manifestos:

```bash
kubectl apply -f k8s/
```

Os recursos criados são:

| Recurso      | Nome                  | Descrição                                      |
|--------------|-----------------------|------------------------------------------------|
| `Secret`     | `exchange-secret`     | Armazena a `EXCHANGE_API_KEY`                  |
| `ConfigMap`  | `exchange-config`     | Define `APP_ENV=production` e `APP_PORT=8080`  |
| `Deployment` | `exchange-deployment` | Sobe 1 réplica da imagem `youcancallmegus/exchange:latest` |
| `Service`    | `exchange`            | Expõe o serviço internamente na porta `8080` via `ClusterIP` |

---

## Estrutura do Projeto

```
exchange/
├── k8s/                  # Manifestos Kubernetes (Deployment, Service, etc.)
├── .env                  # Variáveis de ambiente (não versionar)
├── .gitignore
├── Dockerfile
├── exchangeRouter.py     # Rota /exchange
├── Jenkinsfile           # Pipeline de CI/CD
├── LICENSE
├── main.py               # Entrypoint da aplicação FastAPI
├── README.md
└── requirements.txt      # Dependências Python
```

---

## Observações

- Os códigos de moeda seguem o padrão **ISO 4217** (ex: `USD`, `EUR`, `BRL`).
- Os campos `sell` e `buy` são derivados da mesma taxa retornada pela API de terceiros. Um spread pode ser aplicado conforme necessário.
- Este serviço **não realiza autenticação** — essa responsabilidade é de outra camada.