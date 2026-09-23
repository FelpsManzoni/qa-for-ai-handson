# Glossário

**Golden dataset** — Um conjunto curado de exemplos (pergunta, resposta de referência, pontos-chave esperados)
tratado como verdade fundamental (ground truth) para avaliação. Pequeno e verificado manualmente, ao contrário
do tráfego de produção.

**Ponto-chave (key point)** — Um fato ou conceito específico que uma boa resposta precisa conter, redigido de
forma a ser verificável mecanicamente (uma palavra-chave ou frase curta), em oposição a um critério de qualidade
vago como "deve estar completa".

**Token F1** — A média harmônica de precisão e recall calculada sobre as palavras (tokens) que se sobrepõem entre
dois textos. Tomada emprestada da avaliação de compreensão de leitura (ex.: SQuAD); recompensa a sobreposição
lexical, não o significado.

**Similaridade semântica** — Quão próximos dois trechos de texto estão em significado, estimada aqui via
similaridade de cosseno entre embeddings de sentença (representações vetoriais numéricas) produzidas por um
modelo local pequeno.

**Pontuação geral / limiar / aprovado-reprovado (overall score / threshold / pass-fail)** — A combinação
ponderada dos sinais individuais em um único número, e o ponto de corte acima do qual uma resposta é considerada
aceitável. Mesma ideia de um limiar de aprovação de testes de build: um número só se torna uma decisão quando
alguém define onde fica a linha.

**Modo online** — A resposta avaliada é produzida ao vivo, via uma chamada de API a uma LLM (neste repositório,
via OpenRouter), durante a execução.

**Modo offline** — A resposta avaliada já existe como um valor estático no dataset (pré-gerada anteriormente, por
um modelo conhecido, em um momento conhecido), então a pontuação não precisa de acesso à rede.

**LLM-as-a-Judge** — Uma abordagem de avaliação em que uma LLM separada é instruída a avaliar a resposta de outro
modelo, tipicamente retornando uma pontuação e uma justificativa. Abordada nas apresentações teóricas; **não** é
o que este repositório constrói (veja `docs/01_overview.md` para o motivo).

**Sistema de LLM-eval (LLM-eval system)** — A categoria mais ampla à qual o scorer deste repositório pertence:
qualquer sistema que avalia a saída de uma LLM em relação a critérios definidos. LLM-as-a-Judge é uma
implementação possível de um sistema de LLM-eval; o scorer baseado em regras aqui é outra.

**Limite de taxa (rate limit)** — Um teto que um provedor de API impõe a quantas requisições você pode fazer em
uma janela de tempo. Relevante para o modo online: uma chave de nível gratuito compartilhada pode se esgotar
rapidamente com muitos usuários simultâneos, e é exatamente por isso que o exercício obrigatório da turma roda
offline e o online é uma demo exclusiva do apresentador.
