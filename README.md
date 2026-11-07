# oficina-execution-service

**GitHub:** https://github.com/TGuapyassu/oficina-execution-service

## Cobertura

```bash
pip install -e ".[dev]"
pytest
```

Evidência local (≥80%): [`docs/evidencias/cobertura-local.txt`](docs/evidencias/cobertura-local.txt) · [`cobertura-resumo.svg`](docs/evidencias/cobertura-resumo.svg) · `docs/evidencias/htmlcov/` após o `pytest`. CI: artefato **coverage-report**.

## API (Swagger)

Stack local: **http://localhost:8002/docs**

## Documentação

[`docs/architecture/`](docs/architecture/)

Fila de execução, diagnóstico e reparos. Publica eventos `execution.*` para a coreografia Saga.

## Bancos

| Tipo | Uso |
|------|-----|
| PostgreSQL | `work_orders` |
| Redis | Fila priorizada (`oficina:execution:queue`) |

## Eventos

- Consome: `os.created`, `payment.confirmed`
- Publica: `execution.queued`, `execution.diagnosis_completed`, `execution.started`, `execution.completed`, `execution.status_changed`

## Deploy

Porta **8002**. Stack: [`../oficina-os-service/docker-compose.stack.yml`](../oficina-os-service/docker-compose.stack.yml). K8s: `infra-k8s/manifests/app/`.

## Infraestrutura

- `infra-db/` — RDS `oficina_execution`
- `infra-k8s/manifests/app/` — Deploy Kubernetes

## Postman

Collection mínima: [`docs/postman/oficina-execution-service.postman_collection.json`](docs/postman/oficina-execution-service.postman_collection.json).  
Fluxo E2E Saga: [`../oficina-os-service/docs/postman/oficina-fase4-microservices.postman_collection.json`](../oficina-os-service/docs/postman/oficina-fase4-microservices.postman_collection.json).
