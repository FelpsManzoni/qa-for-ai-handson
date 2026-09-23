# QA for AI — Hands-On: Construindo um Sistema de LLM-Eval

**Sessão:** QA for AI (Hands-On) — 60 minutos, construção ao vivo
**Apresentador:** Felipe Sonntag Manzoni
**Repo:** [github.com/FelpsManzoni/qa-for-ai-handson](https://github.com/FelpsManzoni/qa-for-ai-handson)

Este repositório é o **ponto de partida** que os alunos clonam no início do hands-on — um esqueleto, não um
projeto finalizado. A lógica de pontuação em `src/scorer.py` ainda não está implementada (toda função levanta
`NotImplementedError`). **A turma a constrói ao vivo, em conjunto, dando prompts para o [OpenCode](https://opencode.ai)** —
veja `docs/07_opencode_build_guide.md` para o texto exato dos prompts, um por incremento de construção.

Ao final, isso se torna um pequeno **sistema de LLM-eval** determinístico: algo que avalia as respostas de uma LLM
em relação a um golden dataset usando métricas transparentes, baseadas em código — nenhuma LLM julga a saída de
outra LLM aqui.

## O que "sistema de LLM-eval" significa neste repositório

Toda resposta é avaliada da mesma forma, pelo mesmo código, independentemente de onde a resposta veio:

1. **Token F1** — precisão/recall de sobreposição de palavras entre a resposta do modelo e a resposta de referência.
2. **Cobertura de pontos-chave** — quantos dos pontos-chave esperados de fato aparecem na resposta.
3. **Similaridade semântica** *(sinal opcional)* — similaridade de cosseno entre embeddings de sentença da referência e da resposta, calculada localmente, para que uma paráfrase correta não seja injustamente penalizada pela sobreposição pura de palavras.

Esses sinais se combinam em uma **pontuação geral** (overall) transparente e um limiar de **aprovado/reprovado**.
Veja `docs/02_architecture.md` para a fórmula exata e `docs/06_glossary.md` caso algum desses termos seja novo.

## Um scorer, várias fontes de resposta

| Modo | De onde vem `model_answer` | Precisa de |
|---|---|---|
| `offline` (o que construímos e rodamos em aula) | Coluna pré-preenchida em `data/golden_dataset.csv` | Nada — totalmente local, sem rede |
| `local` (*continue daqui 1*) | Um modelo rodando na sua máquina via [Ollama](https://ollama.com) | Ollama instalado + um modelo baixado |
| `online` (*continue daqui 2*) | Uma chamada a uma LLM via [OpenRouter](https://openrouter.ai) | Uma `OPENROUTER_API_KEY` no `.env` |

Todos os modos chamam exatamente a mesma função `score_pair()` em `src/scorer.py`. Nada na lógica de pontuação
muda entre eles.

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env               # necessário apenas para os modos local/online
python scripts/evaluate.py --mode offline   # roda sem erros, tudo pontua como "não implementado ainda"
# (sempre com a venv ativada: sem ela, o sinal semântico não roda e as notas mudam)
python -m pytest tests/ -q                  # os 4 testes FALHAM — isso é esperado, antes da construção
```

Esse é o estado checkpoint-0 do qual todo mundo parte. Faça isso *antes* do evento (veja
`docs/04_handson_instructions.md`) para que problemas de setup sejam pegos em casa, não em aula.

## Construindo ao vivo com o OpenCode

`docs/07_opencode_build_guide.md` tem a sequência exata de prompts para dar ao OpenCode, um por incremento, cada
um com uma verificação de aceite (um comando de teste) para rodar antes de avançar para o próximo prompt. Este é
o hands-on de fato — siga-o em ordem durante a sessão.

## Estrutura do repositório

```
slides/          as duas apresentações da sessão (abra os .html no navegador)
docs/            documentação do projeto — leia 01 e 04 primeiro
data/            golden dataset, respostas offline pré-executadas, resultados, backups
src/             scorer.py, embeddings.py, runner offline (e o esqueleto do runner online)
scripts/         evaluate.py (ponto de entrada CLI), analyze.py (métricas + gráficos)
tests/           alguns testes de sanidade para o scorer
```

## Incrementos de construção

A turma constrói isso em três incrementos, cada um guiado por um prompt do OpenCode em
`docs/07_opencode_build_guide.md` e verificado com um comando antes de seguir adiante:

| Incremento | O que é construído | Verificado com |
|---|---|---|
| 1 | `token_f1` + `keypoint_coverage` para um único caso | `pytest tests/ -q` |
| 2 | `semantic_similarity` + contrato de pontuação completo (`overall`, `pass`) | `python scripts/evaluate.py --mode offline` pontua cada linha |
| 3 | Pipeline offline em lote consolidado (tratamento de erro por linha, `results.csv` real) | `python scripts/analyze.py` imprime números reais |

Depois da sessão, continue daqui: avaliar um **modelo local com Ollama** (`docs/05_local_models_optional.md`) e,
em seguida, um **modelo via API com o OpenRouter** (`docs/07_opencode_build_guide.md`, *Continue daqui 2*).

**Se o OpenCode produzir algo quebrado e o grupo não conseguir corrigir ao vivo em um tempo razoável**, não gaste
os minutos limitados do grupo depurando — o apresentador deve ter sua própria implementação de referência privada
(construída com antecedência, da mesma forma que você prepararia qualquer demo de live-coding) para usar como
fallback naquele incremento específico, e seguir em frente. Essa referência, por si só, não é algo para distribuir
aos alunos antes ou durante o exercício — isso transformaria um exercício de construção em um exercício de
copiar e colar.

## Por que não LLM-as-a-Judge?

O bloco teórico antes deste hands-on apresenta LLM-as-a-Judge como um dos mecanismos possíveis de avaliação. Este
hands-on deliberadamente **não** constrói um: em vez de pedir a outra LLM para julgar a qualidade (e depois ter
que perguntar "quem julga o juiz?"), toda pontuação aqui vem de código determinístico e inspecionável. Veja
`docs/01_overview.md` para o raciocínio completo.
