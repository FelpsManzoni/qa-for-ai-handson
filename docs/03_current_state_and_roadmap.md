# Estado Atual e Roadmap

## O que já existe neste repositório (checkpoint-0)

- Estrutura do projeto, documentação, `.env.example`, `requirements.txt`
- `data/golden_dataset.csv` — 12 perguntas de QA/conceitos de ML com respostas de referência, pontos-chave e uma
  resposta offline pré-executada para cada uma (de um modelo fixo e conhecido, para que o exercício offline nunca
  dependa de acesso à rede)
- Arquivos esqueleto em `src/` e `scripts/` com assinaturas de função e marcadores `TODO`, mas ainda sem lógica de
  pontuação

## O que é construído ao vivo, em ordem

Guiado pelos prompts do OpenCode em `docs/07_opencode_build_guide.md` — nada abaixo já está escrito neste
repositório:

| Incremento | O que é adicionado |
|---|---|
| 1 | `token_f1` + `keypoint_coverage` em `src/scorer.py` |
| 2 | `semantic_similarity` adicionado, contrato JSON completo, `overall` + `pass` |
| 3 | `src/offline_runner.py` consolidado, `scripts/evaluate.py --mode offline` roda o dataset inteiro → `data/results.csv` |

Depois da sessão (*continue daqui*, especificado em `docs/07_opencode_build_guide.md`):

| Melhoria | O que é adicionado |
|---|---|
| 1 | `src/local_runner.py` + `--mode local` — avaliar um modelo local via Ollama (`docs/05_local_models_optional.md`) |
| 2 | `src/online_runner.py` + `--mode online` — avaliar um modelo via API (OpenRouter) |

Se um incremento ao vivo não convergir a tempo, o apresentador narra sua própria implementação de referência
preparada para aquele arquivo específico, em vez de depurar ao vivo contra o relógio — veja a nota sobre isso em
`docs/07_opencode_build_guide.md`. Essa referência é preparação exclusiva do apresentador, não algo para publicar
junto com este repositório ou entregar aos alunos — o ponto do exercício é que a turma o constrói, não que o
recebe pronto.

## Limitações conhecidas (que vale a pena expor aos alunos, não esconder)

- **`keypoint_coverage` é intencionalmente ingênuo.** Ele procura a redação do ponto-chave (ou uma variante
  próxima) na resposta; uma resposta correta usando vocabulário totalmente diferente pode pontuar baixo aqui
  mesmo quando `semantic_similarity` pontua alto. Essa divergência é um *recurso* para a discussão de análise
  final, não um bug para corrigir silenciosamente.
- **`token_f1` recompensa a sobreposição literal**, então uma resposta concisa e correta pode pontuar mais baixo
  do que uma resposta inchada que repete a redação da referência. Essa é uma limitação padrão e bem conhecida das
  métricas de sobreposição lexical — vale a pena nomear explicitamente em vez de apresentar o scorer como se não
  tivesse nenhuma.
- **O golden dataset é pequeno (12 linhas) de propósito**, para caber no orçamento de tempo da sessão. Conjuntos
  de avaliação reais são maiores e mais diversos; `docs/01_overview.md` e o slide de análise final sinalizam isso.
- **O acesso gratuito às APIs de LLM muda com o tempo.** O modelo específico referenciado em `.env.example` é
  ilustrativo — verifique `openrouter.ai/models` para as opções de nível gratuito atuais e seus limites de taxa
  antes do evento, e atualize `OPENROUTER_MODEL` conforme necessário.

## Possíveis extensões (não obrigatórias para a sessão, ideias para depois)

- Adicionar uma quebra por subgrupo (ex.: por tópico da pergunta) ao `analyze.py`.
- Adicionar um arquivo de configuração para pesos/threshold em vez de flags de CLI, para que toda uma turma possa
  padronizar em uma única configuração.
- Trocar por `sentence-transformers` se sua equipe já depender dele em outro lugar (veja `docs/02_architecture.md`).
- Estender o golden dataset além de conceitos de ML/QA para um domínio mais específico ao currículo dos seus
  alunos.
