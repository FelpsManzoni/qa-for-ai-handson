# Arquitetura

## A ideia central

Uma função de pontuação, duas fontes de resposta:

```
                    ┌─────────────────────────┐
                    │  question, reference,    │
                    │  key_points               │
                    └────────────┬─────────────┘
                                 │
                 ┌───────────────┴────────────────┐
                 │                                 │
        modo ONLINE                        modo OFFLINE
   src/online_runner.py                src/offline_runner.py
   chamada ao vivo ao OpenRouter        lê a coluna model_answer_offline
   -> model_answer (+ latency_ms)       de golden_dataset.csv
                 │                                 │
                 └───────────────┬─────────────────┘
                                 │
                         model_answer
                                 │
                        src/scorer.py
                     score_pair(...) -> dict
                                 │
                        data/results.csv
```

Ambos os runners chamam exatamente a mesma `score_pair()`. Nada na lógica de pontuação se ramifica conforme o
modo; o único campo específico de modo na saída é `latency_ms` (presente no modo online, `null` no modo offline).

## Sinais de `score_pair()`

| Sinal | O que mede | Como é calculado |
|---|---|---|
| `token_f1` | Sobreposição lexical com a resposta de referência | Estilo SQuAD: precisão/recall sobre tokens de palavra normalizados (minúsculas, sem pontuação), média harmônica |
| `keypoint_coverage` | Se a resposta de fato cobre os pontos esperados | Fração de `key_points` cujo texto normalizado (ou uma variante próxima) aparece na resposta normalizada |
| `semantic_similarity` | Se a resposta significa a mesma coisa, mesmo que com outras palavras | Similaridade de cosseno entre embeddings de sentença da referência e da resposta (modelo local via `fastembed`) — **opcional**, veja o fallback abaixo |

## Combinando em `overall`

```python
overall = 0.4 * token_f1 + 0.3 * keypoint_coverage + 0.3 * semantic_similarity
```

Se a biblioteca de embeddings não estiver disponível (veja o fallback abaixo), os pesos são renormalizados sobre
os dois sinais restantes, em vez de silenciosamente zerar um deles:

```python
overall = (0.4 * token_f1 + 0.3 * keypoint_coverage) / 0.7
```

`overall >= threshold` (padrão `0.70`, configurável via `--threshold`) se torna `pass: true/false`.

Todos os pesos e o limiar (threshold) ficam em `src/scorer.py` como constantes nomeadas — altere-os em um único
lugar, não espalhados pela base de código, e eles também são expostos como flags de CLI do `evaluate.py` para
experimentos rápidos durante a sessão.

## Comportamento de fallback (a dependência de embedding é opcional)

`src/embeddings.py` tenta importar `fastembed` no carregamento. Se essa importação falhar por qualquer motivo
(máquina offline, problema de instalação, plataforma incompatível), `get_embedder()` retorna `None`,
`score_pair()` detecta isso e pula `semantic_similarity` completamente (definindo-o como `null` na saída e
renormalizando `overall` como acima). **O pipeline ainda roda de ponta a ponta de qualquer forma** — isso é
intencional, para que um contratempo de dependência no dia da instalação degrade o exercício em vez de bloqueá-lo.

## Por que `fastembed` e não `sentence-transformers`

Ambos fornecem embeddings de sentença a partir do mesmo tipo de modelo pequeno (ex.: `all-MiniLM-L6-v2`). O
`fastembed` roda sobre o ONNX Runtime e não tem dependência de `torch`, o que resulta em uma instalação muito mais
leve e rápida numa sala cheia de laptops com hardware variado. Se sua equipe já padroniza `sentence-transformers`
em outros lugares, trocar a implementação de `src/embeddings.py` é uma mudança pequena e contida — o resto do
sistema não sabe nem se importa com qual biblioteca produziu os vetores.

## Especificidades do modo online

`src/online_runner.py` lê `OPENROUTER_API_KEY`, `OPENROUTER_MODEL` e `OPENROUTER_BASE_URL` do `.env` (via
`python-dotenv`), envia cada `question` como uma única mensagem de usuário ao modelo configurado, e registra:

- `model_answer` — o texto bruto da resposta
- `latency_ms` — tempo de relógio (wall-clock) da chamada
- `status` — `"ok"` ou `"error"` (com a mensagem da exceção mantida em `error_detail` quando falha)

Uma chamada que falha não interrompe o lote: é registrada com `status: "error"` e `overall: null`, e o runner
segue para a próxima linha (veja `docs/04_handson_instructions.md` para o plano de contingência exato caso o
OpenRouter esteja lento ou com limite de taxa ao vivo diante da turma).

## Opcional: trocando por um modelo local

`docs/05_local_models_optional.md` cobre a substituição da chamada ao OpenRouter em `online_runner.py` por uma
chamada a um modelo hospedado localmente (por exemplo, via API HTTP local do Ollama). Como a função do runner é
apenas "produzir uma string `model_answer`", essa é uma troca contida que não toca em `scorer.py` de forma alguma.
