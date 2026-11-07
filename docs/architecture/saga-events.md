# Eventos Saga — Execution Service

## Consome

- `os.created` → work order + `execution.queued`, `execution.status_changed` (EM_DIAGNOSTICO), `execution.diagnosis_completed`
- `payment.confirmed` → execução + `execution.completed`

## Publica

`execution.queued`, `execution.status_changed`, `execution.diagnosis_completed`, `execution.started`, `execution.completed`

## NoSQL

Redis: chave `oficina:execution:queue` (prioridade por `os_id`).
