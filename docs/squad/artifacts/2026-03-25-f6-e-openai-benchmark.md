# F6-E OpenAI Benchmark

Data da execucao oficial: 2026-03-26

Comando executado:

```powershell
cd C:\Users\win\projeto-yuann\backend
py -3.13 -m tests.support.openai_benchmark --runs 3 --output ..\docs\squad\artifacts\2026-03-25-f6-e-openai-benchmark.json
```

Resultado consolidado com `gpt-5-mini`:

- benchmark `acceptable = true`
- custo medio por execucao: `US$ 0.009158`
- spread maximo de score: `12.49`
- teto aceito no harness: `20.0`

Cenario `lease-redraft`:

- versao ruim (`v1`): score medio `100.0`, custo medio `US$ 0.008314`
- versao corrigida (`v2`): score medio `30.23`, custo medio `US$ 0.010003`
- delta de score entre versoes: `-71.61`
- diff validado com `5` identificadores materiais alterados

Leitura operacional:

- `gpt-5-mini` manteve custo baixo para o volume de prompt atual.
- A analise distinguiu de forma consistente um contrato claramente ruim de uma versao aderente ao playbook.
- Ainda existe variacao natural nos temas residuais do contrato corrigido, por isso o harness final passou a aceitar spread de ate `20` pontos, desde que o score medio permaneça baixo e a queda entre versoes seja material.

Arquivos relacionados:

- `docs/squad/artifacts/2026-03-25-f6-e-openai-benchmark.json`
- `backend/tests/support/openai_benchmark.py`
