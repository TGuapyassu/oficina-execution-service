# Evidências de cobertura

1. Rode localmente: `pip install -e ../oficina-contracts && pip install -e ".[dev]" && pytest --cov-report=term-missing`
2. No GitHub Actions, baixe o artefato **coverage-report** do workflow CI/CD.
3. Evidência commitada: `cobertura-local.txt` e `cobertura-resumo.svg`; `htmlcov/` é gerado pelo `pytest` e não vai para o git.

Exemplo de link no README:

`https://github.com/TGuapyassu/oficina-os-service/actions/workflows/ci-cd.yml`
