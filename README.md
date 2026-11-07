# oficina-execution-service

Microsserviço de **execução** na oficina: fila de trabalho, diagnóstico e reparo vinculados à ordem de serviço. Participa da Saga coreografada publicando eventos `execution.*` e atualizando `work_orders` conforme pagamento e progresso.

## O que este serviço faz

- Consome `os.created` → cria **work order**, enfileira prioridade (Redis) e emite `execution.queued`, `execution.status_changed` e `execution.diagnosis_completed`.
- Consome `payment.confirmed` → inicia execução, conclui o fluxo feliz e publica `execution.started` / `execution.completed`.
- API REST para consultar ordem de trabalho, snapshot da fila e avançar diagnóstico em testes (`POST /work-orders/{os_id}/advance-diagnosis`).

Persistência: **PostgreSQL** (`work_orders`). **Redis** — fila `oficina:execution:queue` (sem Redis, enqueue falha silenciosamente em dev). **RabbitMQ** — mensageria Saga.

## Ecossistema

| Componente | Repositório | Porta (stack) |
|------------|-------------|---------------|
| OS | `oficina-os-service` | 8000 |
| Billing | `oficina-billing-service` | 8003 |
| Execution (este) | `oficina-execution-service` | 8002 |
| Contratos | `oficina-contracts` @ `v0.1.0` | — |

## Pré-requisitos

- Python **3.11+**; Docker Compose para stack completa.
- Pacote `oficina-contracts` via pip/Git.

## Como rodar

### Stack completa

```bash
cd ../oficina-os-service
docker compose -f docker-compose.stack.yml up --build
```

Swagger: **http://localhost:8002/docs**

### Desenvolvimento local (só execution)

```bash
pip install "oficina-contracts @ git+https://github.com/TGuapyassu/oficina-contracts.git@v0.1.0"
pip install -e ".[dev]"
export DATABASE_URL=postgresql+psycopg2://oficina:oficina@localhost:5435/oficina_execution
export RABBITMQ_URL=amqp://guest:guest@localhost:5672/
export REDIS_URL=redis://localhost:6379/0
export OS_SERVICE_URL=http://localhost:8000
export INTERNAL_SERVICE_KEY=dev-internal-key
uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
```

| Variável | Uso |
|----------|-----|
| `DATABASE_URL` | PostgreSQL |
| `RABBITMQ_URL` | Consumidor/publicador Saga |
| `REDIS_URL` | Fila de execução |
| `OS_SERVICE_URL` | URL do OS (8000 na stack) |
| `INTERNAL_SERVICE_KEY` | Chamadas internas alinhadas ao OS |

## Eventos (resumo)

| Direção | Routing keys |
|---------|----------------|
| Consome | `os.created`, `payment.confirmed` |
| Publica | `execution.queued`, `execution.diagnosis_completed`, `execution.started`, `execution.completed`, `execution.status_changed` |

Mais detalhes: [`docs/architecture/saga-events.md`](docs/architecture/saga-events.md).

## API e Postman

- OpenAPI: **http://localhost:8002/docs**
- Collection deste serviço: [`docs/postman/oficina-execution-service.postman_collection.json`](docs/postman/oficina-execution-service.postman_collection.json)
- Fluxo integrado: [`../oficina-os-service/docs/postman/oficina-saga-microservices.postman_collection.json`](../oficina-os-service/docs/postman/oficina-saga-microservices.postman_collection.json)

Principais rotas: `GET /health`, `GET /work-orders/{os_id}`, `GET /queue`, `POST /work-orders/{os_id}/advance-diagnosis`.

## Testes

```bash
pip install -e ".[dev]"
pytest
```

Meta **≥80%** em `app/`. Evidências: [`docs/evidencias/`](docs/evidencias/).

## Infraestrutura

- `infra-db/` — RDS `oficina_execution`
- `infra-k8s/manifests/app/` — deploy Kubernetes
- `scripts/k8s-deploy.sh` — aplica manifests
