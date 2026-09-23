# Construindo o Sistema de LLM-Eval ao Vivo, com o OpenCode

Este é o hands-on de fato. Todo mundo tem este repositório clonado no estado checkpoint-0 (nada em
`src/scorer.py` implementado ainda — toda função levanta `NotImplementedError`). A turma trabalha através de
três prompts, em ordem, dando cada um ao OpenCode e verificando o resultado antes de avançar para o próximo.

## Como usar este guia

Para cada incremento abaixo:

1. **Leia o prompt em voz alta / projete-o** — o apresentador (ou um voluntário) o digita no OpenCode exatamente
   como está escrito, na raiz do repositório.
2. **Deixe o OpenCode propor a mudança** — revisem o diff juntos antes de aceitá-lo. Este é o ciclo "humano
   define, agente propõe, humano revisa, código roda" da abertura da sessão — não aprove o diff sem ler.
3. **Rode a verificação de aceite** — o comando exato é dado junto com cada prompt. Se passar, avance. Se não
   passar, este é um momento de discussão ("o que o OpenCode errou, e por quê?"), não um descarrilamento — alguns
   prompts de acompanhamento ao OpenCode ("o teste X está falhando porque Y, corrija") são normais e esperados,
   não um sinal de que algo deu errado.
4. **Se um incremento realmente não se resolver no tempo disponível**, o apresentador aplica sua própria
   implementação de referência preparada para aquele arquivo e narra o diff, e o grupo continua a partir dali.
   Não gaste o tempo compartilhado do grupo em um incremento travado.

Tenha em mente as próprias instruções do OpenCode: ele consegue ler o repositório inteiro, então já tem o
contexto nas docstrings de `src/scorer.py` e em `docs/02_architecture.md`. Em geral você não precisa reexplicar o
projeto — apenas dar o prompt do incremento específico.

---

## Incremento 1 — `token_f1` e `keypoint_coverage` (caso único)

**Prompt para dar ao OpenCode:**

```
Open src/scorer.py. Implement token_f1(reference, candidate) and
keypoint_coverage(key_points, candidate), replacing the NotImplementedError
placeholders. Use the existing _normalize() helper for tokenizing.

token_f1: SQuAD-style token-overlap F1.
- Use token *counts* (collections.Counter), not sets, so repeated words count.
- shared = sum of the per-token minimum count between reference and candidate
  (i.e. Counter intersection).
- precision = shared / number of candidate tokens
- recall = shared / number of reference tokens
- F1 = harmonic mean of precision and recall
- Return 0.0 if either text is empty, or if there's no overlap at all.

keypoint_coverage: for each string in key_points, normalize it into tokens
and check whether at least 60% of ITS OWN tokens appear anywhere in the
candidate's normalized tokens (a bag-of-words overlap check, not an exact
phrase match). Count how many key points clear that bar, divide by the
total number of key points. Return 1.0 if key_points is empty.

Do not touch semantic_similarity or score_pair yet.
```

**Verificação de aceite:**

```bash
python -m pytest tests/ -q
```

Os 4 testes em `tests/test_scorer.py` devem passar. Se `test_keypoint_coverage_partial` estiver instável, esse
teste está intencionalmente verificando uma pontuação *parcial* (`0.0 < coverage < 1.0`), não um número exato — o
ponto de discussão aqui é exatamente que "crédito parcial" é uma escolha de design, não um acidente.

**O que destacar para a turma:** pergunte ao OpenCode *por que* ele escolheu contagens de tokens em vez de
conjuntos de tokens, ou por que escolheu 60% como a barra de sobreposição (ele não escolheu — você escolheu, no
prompt) — este é um bom momento para deixar claro que o OpenCode está implementando uma especificação que os
humanos escreveram, não inventando os critérios de avaliação por conta própria.

---

## Incremento 2 — `semantic_similarity` + o contrato de pontuação completo

**Prompt para dar ao OpenCode:**

```
Open src/scorer.py. Implement semantic_similarity(reference, candidate):
import get_embedder from src.embeddings, call get_embedder(). If it returns
None, return None immediately (no embedding backend available). Otherwise
encode both texts and return their cosine similarity, clamped to [0, 1]
(cosine similarity can be negative; treat anything below 0 as 0 for this
signal since it isn't meaningful for near-duplicate sentence comparison).

Then rewrite score_pair() to:
1. Compute token_f1, keypoint_coverage, and semantic_similarity for the pair.
2. Combine them into `overall` using the WEIGHTS dict already defined at the
   top of the file: overall = WEIGHTS["token_f1"]*f1 + WEIGHTS["keypoint_coverage"]*coverage + WEIGHTS["semantic_similarity"]*similarity.
3. IMPORTANT: if semantic_similarity returned None, do NOT treat it as 0 in
   that formula — instead renormalize by dividing the two-signal weighted
   sum by (WEIGHTS["token_f1"] + WEIGHTS["keypoint_coverage"]).
4. Return a dict with token_f1, keypoint_coverage, semantic_similarity,
   overall (all rounded to 3 decimals), pass (overall >= THRESHOLD), mode,
   and latency_ms.
```

**Verificação de aceite:**

```bash
python scripts/evaluate.py --mode offline
```

Toda linha agora deve mostrar um valor real de `overall` e `pass` (não `null`) em `data/results.csv`. Se
`semantic_similarity` vier `null` para todas as linhas, isso é esperado na primeira vez em que o modelo do
`fastembed` ainda não terminou de baixar (veja `docs/02_architecture.md` — a primeira execução precisa de
internet) — o pipeline ainda deve produzir pontuações reais a partir dos outros dois sinais de qualquer forma.

**O que destacar para a turma:** este é o momento exato de perguntar "por que não simplesmente tratar um sinal
ausente como zero?" — um bom scorer deve degradar graciosamente quando uma dependência está indisponível, não
penalizar silenciosamente toda resposta por um problema de infraestrutura que nada tem a ver com a qualidade da
resposta.

---

## Incremento 3 — Consolidar o pipeline offline

**Prompt para dar ao OpenCode:**

```
Open src/offline_runner.py. Review run_offline(): it should read
data/golden_dataset.csv, call score_pair() per row using the
model_answer_offline column as the candidate answer, and write
data/results.csv. Make sure a single row's failure (any exception from
score_pair) is caught and recorded as a row with overall=None and an
"error" field, WITHOUT stopping the rest of the batch. Confirm the output
CSV has one column per field across all rows (some rows may have an
"error" key that others don't — handle that when building the CSV header).
```

**Verificação de aceite:**

```bash
python scripts/evaluate.py --mode offline
python scripts/analyze.py
```

`analyze.py` deve imprimir uma pontuação geral média/mediana real e a taxa de aprovação, além da quebra por
sinal. Salve uma cópia como backup agora, enquanto ela é conhecidamente boa:

```bash
cp data/results.csv data/results_backup.csv
```

---

## Depois dos três incrementos: análise e investigação do avaliador

Com o sistema offline pronto, siga o bloco de análise em `docs/04_handson_instructions.md` — qualidade geral,
onde falha, se a média esconde algo, se os sinais concordam, a comparação com uma execução sem o sinal semântico
(`python scripts/evaluate.py --mode offline --no-semantic --out data/results_2sinais.csv`) e, por fim, a
investigação de um caso na fronteira do limiar que aparece nessa execução (uma linha com `overall` igual a 0.7 e
`pass` igual a `False`). Esse caso **não é corrigido em aula**: ele é
reproduzido, explicado e registrado como um bug do avaliador.

---

## Continue daqui (depois da sessão)

O sistema construído em aula avalia respostas **pré-geradas** (coluna `model_answer_offline`). As duas melhorias
abaixo trocam apenas a **fonte** do `model_answer` — o scorer, o dataset e o `analyze.py` continuam iguais. Faça
nesta ordem.

### Continue daqui 1 — Avaliar um modelo local com Ollama

Pré-requisito: [Ollama](https://ollama.com) instalado e um modelo pequeno baixado (`ollama pull llama3.2:3b`).
Detalhes de hardware e contexto em `docs/05_local_models_optional.md`.

**Prompt para dar ao OpenCode:**

```
Create src/local_runner.py, modeled on src/offline_runner.py. It must:
- read OLLAMA_BASE_URL (default http://localhost:11434) and OLLAMA_MODEL
  (default llama3.2:3b) from .env via python-dotenv;
- implement call_local_model(question) that POSTs to
  {OLLAMA_BASE_URL}/api/generate with JSON {"model": OLLAMA_MODEL,
  "prompt": question, "stream": false}, reads the "response" field as the
  answer, measures latency with time.perf_counter(), and on any exception
  returns status="error" with the message in error_detail — never raise;
- implement run_local(dataset_path, results_path): for each row of
  data/golden_dataset.csv call call_local_model(question); if status is "ok"
  call score_pair() with the live answer (mode="local", passing latency_ms);
  if "error", record a row with overall=None and the error, and continue.
Then add "local" to the --mode choices in scripts/evaluate.py and route it to
run_local(). Add OLLAMA_BASE_URL and OLLAMA_MODEL to .env.example.
Do not change src/scorer.py.
```

**Verificação de aceite:**

```bash
python scripts/evaluate.py --mode local
python scripts/analyze.py
```

`data/results.csv` deve ter `mode = local` e `latency_ms` preenchido. Compare com a execução offline: o ranking de
qualidade que o avaliador produz combina com a sua intuição sobre o modelo local? Se não, é o modelo ou o scorer?

### Continue daqui 2 — Avaliar um modelo via API (OpenRouter)

Pré-requisito: uma `OPENROUTER_API_KEY` no `.env` (veja `.env.example`) e um modelo disponível em
`openrouter.ai/models`.

**Prompt para dar ao OpenCode:**

```
Open src/online_runner.py. Review call_model(): it should POST to
{OPENROUTER_BASE_URL}/chat/completions with the OPENROUTER_API_KEY from
.env as a Bearer token, sending `question` as a single user message to
OPENROUTER_MODEL. Measure latency with time.perf_counter(). On any
exception, return status="error" with the exception message in
error_detail — never raise. Then review run_online(): for each dataset
row, call call_model(), and if status is "ok" call score_pair() with the
live answer (mode="online", passing latency_ms through); if status is
"error", record a row with overall=None and the error, and continue to the
next row regardless.
```

**Verificação de aceite:**

```bash
python scripts/evaluate.py --mode online
python scripts/analyze.py
```

Se o OpenRouter estiver lento, com limite de taxa, ou o modelo de nível gratuito estiver indisponível, algumas
linhas mostrarão `status: error` — isso é esperado; o sistema deve continuar processando as demais linhas.

Com as três execuções (offline, local e API) em mãos, compare as médias por sinal e as distribuições: o avaliador
separa os modelos de forma coerente?
