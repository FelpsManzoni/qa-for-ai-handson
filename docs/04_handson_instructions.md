# Instruções do Hands-On

## Antes do evento (fazer em casa, não em aula)

1. Instale Python 3.10+, git e o [OpenCode](https://opencode.ai), com um provedor de modelo configurado
   (instruções em `opencode.ai/docs`).
2. Clone este repositório: `git clone https://github.com/FelpsManzoni/qa-for-ai-handson.git && cd qa-for-ai-handson`
3. `python -m venv .venv && source .venv/bin/activate` (Windows: `.venv\Scripts\activate`)
4. `pip install -r requirements.txt`
5. `cp .env.example .env` — você só precisa preencher `OPENROUTER_API_KEY` para a melhoria *continue daqui 2*
   (modelo via API); o exercício em aula não precisa disso.
6. Rode o smoke test: `python scripts/evaluate.py --mode offline` deve completar sem erros e criar
   `data/results.csv` (mesmo antes de você ter escrito qualquer lógica de pontuação — o esqueleto do
   checkpoint-0 termina de forma limpa com pontuações placeholder, para você confirmar que seu ambiente
   funciona).
7. Confirme o sinal semântico (a primeira execução baixa o modelo de embedding e precisa de internet):
   `python -c "from src.embeddings import get_embedder; print(get_embedder())"` deve imprimir um objeto
   `Embedder`. Se imprimir `None`, o sistema funciona com os outros dois sinais, mas seus números vão diferir de
   quem tem o sinal semântico. A causa mais comum é rodar fora da venv: ative-a (passo 3) e rode de
   novo; se continuar `None`, tente `pip install fastembed` novamente ou verifique proxy/firewall.
8. Se o passo 6 ou 7 falhar, corrija-o *antes* do evento — o objetivo inteiro de fazer isso com antecedência é não
   gastar tempo de aula com configuração de ambiente.

## Durante a sessão

Acompanhe o apresentador e dê ao OpenCode os mesmos prompts que ele der — veja
`docs/07_opencode_build_guide.md` para o texto exato, um prompt por incremento:

1. `src/scorer.py` — a lógica de pontuação (incrementos 1–2)
2. `src/offline_runner.py` — o pipeline em lote (incremento 3)
3. `scripts/analyze.py` — já fornecido; você só vai rodá-lo, não escrevê-lo

Se sua própria tentativa em um incremento não estiver convergindo, não gaste o tempo limitado do grupo
depurando sozinho — acompanhe a tela do apresentador para aquele incremento e continue a partir dali assim que
ele resolver, depois atualize sua própria cópia dando ao OpenCode o mesmo prompt novamente, com a correção do
apresentador como contexto adicional, se necessário.

## Rodando o pipeline

```bash
python scripts/evaluate.py --mode offline
python scripts/analyze.py
```

`scripts/analyze.py` imprime a pontuação geral média/mediana, a taxa de aprovação, a quebra por sinal, e salva um
histograma em `data/score_distribution.png`.

Se algo travar durante a sessão, o apresentador usa a execução de referência dele e a análise continua a partir
dali — acompanhe pela tela.

## Discussão de análise (em grupo)

Trabalhe estes pontos em ordem, usando seu próprio `results.csv`:

1. **Qualidade geral** — qual é a pontuação geral média/mediana e a taxa de aprovação no limiar padrão? Isso é
   "bom"? O que mudaria sua resposta?
2. **Onde falha** — qual dos três sinais é o mais baixo em média? O que isso sugere sobre as respostas do modelo
   (ex.: baixa cobertura + alta similaridade = "soa certo, mas perde pontos obrigatórios")?
3. **A média esconde algo** — observe a distribuição, não só a média. As falhas estão concentradas em poucas
   perguntas ou distribuídas igualmente?
4. **Os sinais concordam** — encontre uma linha em que `token_f1` e `semantic_similarity` discordem fortemente. O
   que isso diz sobre o próprio scorer, não apenas sobre o modelo sendo testado?

5. **Mesmo modelo, outro avaliador** — rode de novo com o sinal semântico desligado e compare:

   ```bash
   python scripts/evaluate.py --mode offline --no-semantic --out data/results_2sinais.csv
   python scripts/analyze.py data/results_2sinais.csv
   ```

   As respostas do modelo são as mesmas; só o avaliador mudou. Sem o sinal semântico, o peso dele é
   redistribuído para token F1 e cobertura — dois sinais que punem paráfrases corretas. (É também o que acontece
   se você rodar fora da venv, sem o `fastembed` instalado.)
6. **Investigar o avaliador** — em `data/results_2sinais.csv`, procure uma linha com `overall` igual a 0.7 e
   `pass` igual a `False`. Refaça a conta com os valores da própria linha: o número exibido é arredondado, mas a
   decisão foi tomada sobre o valor sem arredondar. Não corrija em aula: reproduza, explique e registre como um
   bug do avaliador (título, passos para reproduzir, esperado, obtido, impacto).

## Continue daqui (depois da sessão)

1. **Modelo local com Ollama** — `docs/05_local_models_optional.md`.
2. **Modelo via API (OpenRouter)** — `docs/07_opencode_build_guide.md`, seção *Continue daqui 2*.
