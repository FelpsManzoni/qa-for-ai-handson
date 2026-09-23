# Visão Geral do Projeto

## O que é isto

Um pequeno **sistema de LLM-eval** funcional, construído ao vivo durante a sessão hands-on de QA for AI. Ele avalia
as respostas de uma LLM a um conjunto de perguntas em relação a um **golden dataset** — um conjunto curado de
perguntas, respostas de referência e os pontos-chave que uma boa resposta precisa cobrir.

## Objetivos

1. Mostrar, em código, como uma noção vaga de "qualidade" se torna algo verificável.
2. Construir um scorer transparente de ponta a ponta: todo número que ele produz pode ser explicado lendo o
   código que o gerou.
3. Avaliar respostas pré-geradas (modo offline) em aula e deixar especificadas as extensões para avaliar um modelo
   local (Ollama) e um modelo via API (OpenRouter) — mantendo a lógica de pontuação idêntica entre elas.
4. Usar as métricas resultantes como base para uma discussão real de QA: o que é "bom o suficiente", onde o
   modelo falha, se a média esconde algo, e se os próprios sinais do avaliador concordam entre si.

## Por que isto *não* é LLM-as-a-Judge

A apresentação teórica imediatamente anterior a este hands-on (`AI_Quality_Engineering` / *Evaluating AI Models &
Agents*) apresenta LLM-as-a-Judge como um mecanismo de avaliação legítimo, e uma versão anterior deste hands-on
foi construída em torno dele. Deliberadamente nos afastamos disso para a *construção voltada ao aluno*:

- Um juiz LLM é, ele mesmo, um sistema de IA que precisa ser avaliado — "quem avalia o avaliador" é um problema
  real, não uma nota de rodapé, e resolvê-lo adequadamente exige mais do que 60 minutos.
- Um scorer baseado em regras é totalmente inspecionável: toda pontuação pode ser rastreada até uma linha
  específica de código, o que combina com a forma como uma audiência de QA está acostumada a pensar sobre
  oráculos de teste.
- Isso remove qualquer dependência de uma segunda chamada de LLM (e seu custo/latência/limites de taxa) só para
  avaliar a saída da primeira.

Nada disso significa que LLM-as-a-Judge seja uma má ideia — é uma ferramenta boa exatamente para os casos em que
um scorer baseado em regras lida mal (qualidade criativa aberta, tom, correção sutil). Simplesmente está fora do
escopo do que é *construído* nesses 60 minutos. Veja `docs/06_glossary.md` para uma comparação entre as duas
abordagens.

## Para quem é isto

Estudantes e profissionais participando do hands-on de QA for AI, com a apresentação teórica de fundamentos e a
apresentação *Evaluating AI Models & Agents* como contexto prévio (não um requisito estrito para acompanhar este
repositório, mas que explica o vocabulário usado ao longo dele).

## Como é o "pronto" para a sessão

Ao final da hora, o grupo terá:

- uma função `score_pair()` funcional (token F1 + cobertura de pontos-chave + similaridade semântica opcional),
- uma execução em lote offline produzindo `results.csv` a partir do golden dataset,
- uma análise em grupo sobre o que os números resultantes dizem e não dizem — incluindo a investigação de um bug
  do próprio avaliador,
- e as especificações para continuar depois da sessão: modelo local com Ollama (`docs/05_local_models_optional.md`)
  e modelo via API (`docs/07_opencode_build_guide.md`, *Continue daqui 2*).

Veja `docs/03_current_state_and_roadmap.md` para exatamente o que já vem pronto neste repositório versus o que é
construído ao vivo.
