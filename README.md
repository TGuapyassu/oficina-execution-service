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

Porta **8002**. Stack: [`../oficina-os-service/docker-compose.stack.yml`](../oficina-os-service/docker-compose.stack.yml). K8s: `infra-k8s/manifests/app/`.

## Infraestrutura

- `infra-db/` — RDS `oficina_execution`
- `infra-k8s/manifests/app/` — Deploy Kubernetes
