# Notas de Engenharia de Prompt — EduPrompt

## Visão Geral

Este documento descreve as estratégias e técnicas de engenharia de prompt utilizadas no EduPrompt, uma plataforma educativa que gera conteúdo personalizado para alunos usando IA.

O sistema implementa **3 versões evolutivas de prompts** (v1, v2 e v3) com **10 técnicas** distintas, permitindo comparação quantitativa e qualitativa da eficácia de cada abordagem.

---

## Técnicas Utilizadas (10 técnicas)

### 1. Persona Prompting

**O que é:** Definir um papel/personalidade específica para a IA assumir, incluindo expertise, experiência e princípios de atuação.

**Evolução entre versões:**

- **v1:** `"Você é um professor que ensina diversos assuntos para alunos de diferentes idades e níveis."`
- **v2:** `"Você é um professor experiente em Pedagogia com mais de 15 anos de experiência adaptando conteúdo educacional para diferentes perfis de alunos..."` (inclui 5 princípios pedagógicos)
- **v3:** `"Você é um professor-pesquisador com PhD em Educação e mais de 20 anos de experiência adaptando conteúdo para diferentes perfis cognitivos. Você é especialista em Design Instrucional e domina a Taxonomia de Bloom, Aprendizagem Significativa de Ausubel e a teoria das Inteligências Múltiplas de Gardner..."` (inclui 7 princípios pedagógicos)

**Por que funciona:** A profundidade da persona afeta diretamente a qualidade e granularidade pedagógica das respostas. Na v3, citar teorias pedagógicas específicas (Bloom, Ausubel, Gardner) leva a IA a aplicar genuinamente esses frameworks.

### 2. Context Setting (Configuração de Contexto)

**O que é:** Fornecer informações detalhadas sobre o contexto — no caso, dados do perfil do aluno — para personalizar cada resposta.

**Como utilizamos:**

Cada prompt inclui dados específicos do aluno:
- Nome, idade, nível de conhecimento (iniciante/intermediário/avançado)
- Estilo de aprendizado (visual, auditivo, leitura-escrita, cinestésico)
- Interesses pessoais (variáveis por aluno)

**Exemplo real (trecho do prompt montado para Ana Silva):**
```
## Perfil do Aluno
Ana Silva tem 12 anos, está começando a aprender o assunto e
aprende melhor com imagens, diagramas e representações visuais.
Seus interesses incluem: jogos, desenho, animais.
- Idade: 12 anos
- Nível: iniciante
- Estilo de aprendizado: visual
```

**Por que funciona:** Com contexto detalhado, a IA adapta automaticamente vocabulário, exemplos e nível de complexidade. O mesmo tópico gera respostas fundamentalmente diferentes para Pedro (9 anos, cinestésico) e Maria (25 anos, leitura-escrita).

### 3. Chain-of-Thought (Cadeia de Pensamento)

**O que é:** Instruir a IA a pensar passo a passo antes de produzir a resposta final.

**Como utilizamos (trecho do prompt conceitual v2):**
```
Pense passo a passo antes de construir sua explicação:

1. Análise prévia: Primeiro, analise internamente quais são os
   conceitos-chave que este aluno precisa entender...
2. Conexão com conhecimento prévio: Identifique o que um aluno
   de nível [X] provavelmente já sabe...
3. Construção progressiva: Monte a explicação do mais simples
   para o mais complexo...
```

**Por que funciona:** O raciocínio passo a passo produz explicações mais estruturadas e logicamente sequenciadas. A IA "planeja" antes de escrever, resultando em conteúdo com melhor progressão pedagógica.

### 4. Output Formatting (Formatação de Saída)

**O que é:** Especificar exatamente a estrutura e formato da resposta esperada.

**Exemplos reais por tipo de conteúdo:**

**Explicação conceitual (v2+):**
```
### O que é {topic}?
[Definição clara e acessível]

### Por que é importante?
[Relevância e aplicações práticas]

### Como funciona?
[Explicação passo a passo]

### Resumo
[Recapitulação em 2-3 frases]
```

**Exemplos práticos (v2+):**
```
### Exemplo [N]: [Título descritivo]
**Contexto:** [Situação do cotidiano do aluno]
**Aplicação:** [Como o tópico se aplica]
**Passo a passo:** [Demonstração]
**O que aprendemos:** [Conceito reforçado]
```

**Por que funciona:** Formatos estruturados garantem consistência e completude nas respostas. O conteúdo fica organizado, padronizado e fácil de consumir.

### 5. Constraint Setting (Configuração de Restrições)

**O que é:** Definir limites e regras claras para a resposta.

**Exemplos de restrições aplicadas:**
```
Importante: Use linguagem adequada para 12 anos, nível iniciante.
Adapte exemplos e analogias ao estilo visual de aprendizado.
```
```
O diagrama deve usar no máximo 80 caracteres de largura.
Zero perguntas de sim/não. Todas devem exigir raciocínio.
```

**Por que funciona:** Restrições claras evitam conteúdo inadequado ao público-alvo e forçam a IA a se manter dentro de parâmetros pedagógicos adequados.

### 6. Audience Adaptation (Adaptação de Público)

**O que é:** Adaptar todos os elementos do prompt ao público-alvo específico.

**Como utilizamos (trecho do prompt de exemplos práticos):**
```
Crie 3 exemplos práticos que:
1. Sejam relevantes para o cotidiano de uma pessoa de {age} anos
2. Conectem {topic} com os interesses do aluno ({interests})
3. Aumentem gradualmente em complexidade
4. Sejam adaptados ao estilo de aprendizado {style}
```

**Por que funciona:** A personalização por público cria conteúdo mais engajante. Um aluno que gosta de "animais" recebe exemplos com animais; um que gosta de "programação" recebe exemplos com código.

### 7. Few-Shot Prompting (v3)

**O que é:** Fornecer exemplos concretos de respostas ideais antes de pedir a tarefa.

**Como utilizamos (trecho do prompt conceitual v3):**
```
## Exemplo de Resposta Ideal (Few-Shot)
Aqui está um exemplo de como estruturar uma explicação conceitual
sobre 'Gravidade' para uma aluna de 10 anos, nível iniciante, estilo visual:

---
### O que é Gravidade?
Gravidade é a força invisível que puxa tudo em direção ao chão.
Imagine que a Terra é como um ímã gigante que atrai tudo para ela...

### Por que é importante?
Sem gravidade, estaríamos flutuando como astronautas! A gravidade
mantém a água nos rios, nossos pés no chão...
---
```

**Por que funciona:** Exemplos concretos demonstram o padrão de qualidade esperado, incluindo tom de voz, profundidade, uso de analogias e nível de linguagem. Essa é a técnica de maior impacto na v3.

### 8. Self-Consistency (v3)

**O que é:** Instruir a IA a verificar e avaliar sua própria resposta quanto à coerência e adequação.

**Como utilizamos:**
```
Ao final, releia sua resposta e verifique se é coerente e progressiva.
```

A persona v3 também inclui o princípio:
```
7. Ao final, faça uma auto-avaliação pedagógica das suas escolhas
```

**Por que funciona:** Estimula a IA a revisar e corrigir inconsistências antes de finalizar, melhorando a coerência geral do conteúdo.

### 9. Metacognição (v3)

**O que é:** Pedir à IA que explique suas próprias escolhas pedagógicas, promovendo transparência no raciocínio.

**Como utilizamos (seção final do formato de saída v3):**
```
### Auto-avaliação pedagógica
[Explique brevemente: quais técnicas pedagógicas você usou e por quê]
```

**Exemplo real de auto-avaliação gerada pela v3:**
```
### Auto-avaliação pedagógica
Usei analogia do ímã (concreta e visual), linguagem simples para 10 anos,
e construí do mais familiar (bola caindo) ao mais abstrato (movimento da Lua).
```

**Por que funciona:** Forçar explicitação das escolhas pedagógicas leva a IA a fazer escolhas mais deliberadas e fundamentadas, em vez de simplesmente gerar texto fluente.

### 10. Scaffolding (v3)

**O que é:** Instruir a IA a construir conhecimento progressivamente, do concreto ao abstrato, do simples ao complexo.

**Como utilizamos:**
```
Scaffolding: Monte a explicação do concreto ao abstrato, do simples
ao complexo, verificando que cada etapa sustenta a próxima.
```

Nos exemplos práticos:
```
Aumentem progressivamente em complexidade (scaffolding)
```

**Por que funciona:** O scaffolding reflete uma prática pedagógica comprovada — construir conceitos sobre fundamentos sólidos. O resultado é conteúdo que o aluno pode acompanhar sem se perder.

---

## Comparação Detalhada v1 vs v2 vs v3

### Diferenças Estruturais

| Aspecto | v1 (Baseline) | v2 (Otimizada) | v3 (Avançada) |
|---------|---------------|----------------|---------------|
| Persona | Genérica ("um professor") | Detalhada (15 anos, 5 princípios) | Especialista (PhD, 7 princípios, teorias nomeadas) |
| Contexto | Texto simples | Dados estruturados + narrativa | Dados estruturados + narrativa |
| Estrutura | "Faça uma explicação clara" | Template com seções definidas | Template + few-shot example completo |
| Chain-of-thought | Não utiliza | 3 passos explícitos | 3 passos com scaffolding explícito |
| Restrições | Mínimas | Específicas (idade, nível, estilo) | Específicas + auto-verificação |
| Few-shot | Não utiliza | Não utiliza | Exemplo completo por tipo |
| Self-consistency | Não | Não | Sim — releitura e verificação |
| Metacognição | Não | Não | Sim — auto-avaliação pedagógica |
| Nº de técnicas | 2 | 6 | 10 |
| Tamanho aprox. | ~50 palavras | ~200 palavras | ~450 palavras |

### Impacto Observado

**v1 → v2:**
- Respostas significativamente mais longas e detalhadas
- Melhor estrutura e organização
- Melhor adaptação ao perfil do aluno
- Inclusão de analogias relevantes

**v2 → v3:**
- Respostas com qualidade pedagógica superior
- Inclusão de seção de auto-avaliação
- Exemplos mais contextualizados ao universo do aluno
- Maior progressividade (scaffolding) nas explicações
- Consistência de formato ancorada nos few-shot examples

---

## Arquitetura do Sistema de Prompts

```
PromptEngine(version)
  ├── build_system_prompt(student)     → Persona + Context Setting
  ├── build_conceptual_prompt()        → Chain-of-Thought + Output Formatting + [Few-Shot v3]
  ├── build_practical_prompt()         → Context Setting + Output Formatting + [Few-Shot v3]
  ├── build_reflection_prompt()        → Chain-of-Thought + Constraint Setting + [Few-Shot v3]
  └── build_visual_prompt()            → Output Formatting + Constraint Setting + [Few-Shot v3]
```

O `system_prompt` contém a persona e o perfil do aluno — compartilhado entre todas as chamadas para manter consistência. O `user_prompt` contém a tarefa específica com técnicas combinadas.

### Fluxo de Montagem

```
1. Carrega templates da versão selecionada (v1/v2/v3)
2. Monta system_prompt: persona + describe(student)
3. Monta user_prompt: template.format(topic, age, level, style, interests)
4. Envia [system_prompt, user_prompt] à API
5. Salva resultado com metadados (versão, prompt usado, timestamp)
```

---

## Decisões de Design

1. **Separação persona/conteúdo:** O system prompt (persona + contexto) é separado do user prompt (tarefa específica), permitindo reutilização e consistência.

2. **Versionamento explícito:** 3 versões permitem comparação A/B/C e demonstram evolução iterativa das técnicas. Cada versão tem técnicas documentadas.

3. **Templates parametrizados:** Variáveis `{topic}`, `{age}`, `{level}`, `{style}`, `{interests}` permitem montar prompts dinamicamente sem duplicação de código.

4. **Técnicas combinadas:** Cada prompt combina 2-5 técnicas simultaneamente, pois técnicas isoladas têm impacto menor do que combinações calibradas.

5. **Taxonomia de Bloom:** As perguntas de reflexão seguem os 5 níveis da Taxonomia de Bloom (Compreensão → Aplicação → Análise → Avaliação → Criação), promovendo desenvolvimento cognitivo progressivo.

6. **Few-shot com domínio diferente:** Os exemplos da v3 usam tópicos diferentes do solicitado (ex: exemplo sobre "Gravidade" quando o aluno pede "Fotossíntese"), evitando que a IA copie o exemplo ao invés de genuinamente adaptar.

7. **Auto-avaliação obrigatória:** A v3 exige seção de auto-avaliação pedagógica, forçando a IA a refletir sobre suas escolhas e tornando o processo mais transparente.

---

## Análise Comparativa — Ferramenta

O projeto inclui um módulo dedicado de análise comparativa (`src/services/comparison.py`) que:

1. Gera o mesmo conteúdo com todas as versões de prompt
2. Calcula métricas quantitativas (palavras, linhas, títulos, tópicos, perguntas, emojis)
3. Compara evolução de técnicas entre versões
4. Produz observações automáticas sobre diferenças
5. Salva relatório completo em JSON

### Métricas Calculadas

| Métrica | O que mede |
|---------|-----------|
| total_words | Volume de conteúdo |
| total_lines | Extensão da resposta |
| headings | Estruturação hierárquica |
| bullet_points | Uso de listas organizadas |
| questions | Engajamento com perguntas |
| example_markers | Presença de exemplos |
| emoji_count | Elementos visuais |
| avg_words_per_line | Densidade do texto |

---

## Perfis de Alunos e Estratégia de Diversidade

Os 5 perfis foram desenhados para cobrir extremos e intermediários:

| Aluno | Idade | Nível | Estilo | Desafio principal |
|-------|-------|-------|--------|-------------------|
| Ana Silva | 12 | Iniciante | Visual | Criança + visual: precisa de analogias concretas e diagramas |
| Carlos Oliveira | 17 | Avançado | Leitura-escrita | Adolescente avançado: pode receber conteúdo técnico e denso |
| Maria Santos | 25 | Intermediário | Auditivo | Adulta: precisa de linguagem formal e aplicações profissionais |
| Pedro Costa | 9 | Iniciante | Cinestésico | Criança pequena + cinestésico: precisa de atividades práticas |
| Lúcia Ferreira | 20 | Intermediário | Visual | Estudante universitária: equilíbrio entre teoria e prática |

**Justificativa:** A diversidade de perfis testa se as técnicas de prompt realmente se adaptam, ao invés de gerar conteúdo genérico com variação superficial.

---

## Referências Pedagógicas

- **Taxonomia de Bloom:** BLOOM, B. S. (1956). *Taxonomy of Educational Objectives*. Framework usado nas perguntas de reflexão.
- **Aprendizagem Significativa:** AUSUBEL, D. P. (1968). *Educational Psychology: A Cognitive View*. Princípio de pontes cognitivas usado na v3.
- **Inteligências Múltiplas:** GARDNER, H. (1983). *Frames of Mind*. Base para adaptação por estilo de aprendizado.
- **Scaffolding:** VYGOTSKY, L. S. (1978). *Mind in Society*. Construção progressiva de conhecimento na v3.
- **Few-Shot Prompting:** BROWN, T. et al. (2020). *Language Models are Few-Shot Learners*. Técnica central da v3.
