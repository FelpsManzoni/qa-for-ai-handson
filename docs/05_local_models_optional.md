# Continue Daqui 1: Avaliar um Modelo Local com Ollama

Esta é a **primeira melhoria sugerida depois da sessão** — não faz parte do que é construído em aula. O sistema
construído em aula avalia respostas pré-geradas (coluna `model_answer_offline` de `data/golden_dataset.csv`); aqui
você passa a avaliar respostas geradas **ao vivo por um modelo rodando na sua máquina**, com o mesmo scorer.

A segunda melhoria (avaliar um modelo via API, com o OpenRouter) está em `docs/07_opencode_build_guide.md`, seção
*Continue daqui 2*.

## Requisitos de máquina

Rodar um modelo local bem o suficiente para responder 12 perguntas em tempo razoável tipicamente exige pelo menos
8–16GB de RAM e se beneficia bastante de uma GPU (a memória unificada da Apple Silicon também funciona bem).

## Como se encaixa

O scorer (`src/scorer.py`), o runner offline e o `analyze.py` não sabem nem se importam com a origem da string
`model_answer`. A melhoria adiciona apenas uma nova fonte:

1. Instale o [Ollama](https://ollama.com) e baixe um modelo pequeno: `ollama pull llama3.2:3b` (ou outro modelo
   pequeno ajustado para instrução que caiba na sua máquina).
2. O Ollama expõe uma API HTTP local (padrão `http://localhost:11434/api/generate`).
3. Dê ao OpenCode o prompt *Continue daqui 1* de `docs/07_opencode_build_guide.md`: ele cria `src/local_runner.py`,
   adiciona `--mode local` ao `scripts/evaluate.py` e as variáveis `OLLAMA_BASE_URL` / `OLLAMA_MODEL` ao
   `.env.example`. Nenhuma chave de API é necessária.
4. Rode `python scripts/evaluate.py --mode local` e depois `python scripts/analyze.py`.

## O que esperar

Modelos locais pequenos geralmente pontuarão mais baixo em `token_f1` e `keypoint_coverage` do que um modelo
hospedado maior — isso é esperado e, em si, um ponto de discussão legítimo: o ranking de "melhor" e "pior" do
sistema de avaliação corresponde à sua intuição sobre qual modelo é de fato mais capaz? Se não, é culpa do modelo
ou do scorer?
