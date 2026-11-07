# oficina-execution-service

**GitHub:** https://github.com/TGuapyassu/oficina-execution-service

## Cobertura

`pytest --cov-report=html` · artefato **coverage-report** no CI · [`docs/evidencias/`](docs/evidencias/)

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

Porta **8002**. Ver [`../docker-compose.microservices.yml`](../docker-compose.microservices.yml) e manifests em `oficina-infra-k8s/manifests/microservices/`.
