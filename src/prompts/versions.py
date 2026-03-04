"""
Versionamento de prompts para comparação de qualidade.

Define múltiplas versões de prompts para permitir análise
comparativa de resultados, seguindo o requisito de comparação
de qualidade entre diferentes versões.

Versão v1: Prompts básicos e diretos (baseline)
Versão v2: Prompts otimizados com técnicas avançadas
Versão v3: Prompts com few-shot examples e self-consistency
"""

from src.prompts.templates import PromptTemplates

# ============================================================
# VERSÃO v1 — Prompts Básicos (Baseline)
# ============================================================
# Prompts simples e diretos, sem técnicas avançadas.
# Servem como base de comparação para medir a eficácia
# das técnicas de engenharia de prompt na versão v2.
# ============================================================

V1_TEMPLATES = PromptTemplates(
    version="v1",
    description="Prompts básicos e diretos, sem técnicas avançadas de engenharia de prompt.",
    techniques=["instrução direta", "formatação simples"],
    persona=(
        "Você é um professor que ensina diversos assuntos para alunos "
        "de diferentes idades e níveis."
    ),
    conceptual=(
        "Explique o conceito de {topic} para um aluno com o seguinte perfil:\n"
        "{student_description}\n\n"
        "Faça uma explicação clara e adequada ao nível do aluno."
    ),
    practical=(
        "Dê exemplos práticos sobre {topic} para um aluno com o seguinte perfil:\n"
        "{student_description}\n\n"
        "Os exemplos devem ser adequados à idade e nível do aluno."
    ),
    reflection=(
        "Crie perguntas de reflexão sobre {topic} para um aluno com o seguinte perfil:\n"
        "{student_description}\n\n"
        "As perguntas devem estimular o pensamento crítico."
    ),
    visual_summary=(
        "Crie um resumo visual de {topic} para um aluno com o seguinte perfil:\n"
        "{student_description}\n\n"
        "Use diagramas ou mapas mentais em ASCII."
    ),
)


# ============================================================
# VERSÃO v2 — Prompts Otimizados
# ============================================================
# Prompts que utilizam técnicas avançadas de engenharia de prompt:
# - Persona Prompting detalhada
# - Context Setting com dados específicos do aluno
# - Chain-of-Thought para raciocínio passo a passo
# - Output Formatting com estrutura explícita da resposta
# - Few-shot examples implícitos
# ============================================================

V2_TEMPLATES = PromptTemplates(
    version="v2",
    description=(
        "Prompts otimizados com persona detalhada, chain-of-thought, "
        "context setting avançado e output formatting estruturado."
    ),
    techniques=[
        "persona prompting",
        "chain-of-thought",
        "context setting",
        "output formatting",
        "constraint setting",
        "audience adaptation",
    ],
    persona=(
        "Você é um professor experiente em Pedagogia com mais de 15 anos de "
        "experiência adaptando conteúdo educacional para diferentes perfis de "
        "alunos. Você domina técnicas de ensino diferenciado e é especialista "
        "em tornar conceitos complexos acessíveis para qualquer público. "
        "Você sempre adapta sua linguagem, exemplos e abordagem de acordo "
        "com a idade, nível de conhecimento e estilo de aprendizado do aluno.\n\n"
        "Princípios que você segue:\n"
        "1. Use linguagem adequada à idade do aluno\n"
        "2. Conecte novos conceitos com o conhecimento prévio do aluno\n"
        "3. Use analogias e exemplos do cotidiano do aluno\n"
        "4. Adapte a complexidade ao nível de conhecimento\n"
        "5. Respeite o estilo de aprendizado preferido"
    ),
    conceptual=(
        "## Tarefa\n"
        "Elabore uma explicação conceitual completa sobre **{topic}**.\n\n"
        "## Perfil do Aluno\n"
        "{student_description}\n"
        "- Idade: {age} anos\n"
        "- Nível: {level}\n"
        "- Estilo de aprendizado: {style}\n\n"
        "## Instruções Detalhadas\n"
        "Pense passo a passo antes de construir sua explicação:\n\n"
        "1. **Análise prévia:** Primeiro, analise internamente quais são os "
        "conceitos-chave que este aluno precisa entender sobre {topic}, "
        "considerando seu nível ({level}) e idade ({age} anos).\n\n"
        "2. **Conexão com conhecimento prévio:** Identifique o que um aluno "
        "de nível {level} provavelmente já sabe e use isso como ponto de partida.\n\n"
        "3. **Construção progressiva:** Monte a explicação do mais simples "
        "para o mais complexo, garantindo que cada etapa seja compreensível.\n\n"
        "## Formato da Resposta\n"
        "Estruture sua resposta da seguinte forma:\n\n"
        "### O que é {topic}?\n"
        "[Definição clara e acessível]\n\n"
        "### Por que é importante?\n"
        "[Relevância e aplicações práticas]\n\n"
        "### Como funciona?\n"
        "[Explicação passo a passo com chain-of-thought]\n\n"
        "### Resumo\n"
        "[Recapitulação em 2-3 frases]\n\n"
        "**Importante:** Use linguagem adequada para {age} anos, nível {level}. "
        "Adapte exemplos e analogias ao estilo {style} de aprendizado."
    ),
    practical=(
        "## Tarefa\n"
        "Crie exemplos práticos e contextualizados sobre **{topic}**.\n\n"
        "## Perfil do Aluno\n"
        "{student_description}\n"
        "- Idade: {age} anos\n"
        "- Nível: {level}\n"
        "- Estilo de aprendizado: {style}\n"
        "- Interesses: {interests}\n\n"
        "## Instruções Detalhadas\n"
        "Crie **3 exemplos práticos** que:\n"
        "1. Sejam relevantes para o cotidiano de uma pessoa de {age} anos\n"
        "2. Conectem {topic} com os interesses do aluno ({interests})\n"
        "3. Aumentem gradualmente em complexidade\n"
        "4. Sejam adaptados ao estilo de aprendizado {style}\n\n"
        "## Formato da Resposta\n"
        "Para cada exemplo, use esta estrutura:\n\n"
        "### Exemplo [N]: [Título descritivo]\n"
        "**Contexto:** [Situação do cotidiano do aluno]\n"
        "**Aplicação:** [Como {topic} se aplica nesta situação]\n"
        "**Passo a passo:** [Demonstração prática]\n"
        "**O que aprendemos:** [Conceito reforçado]\n\n"
        "**Importante:** Os exemplos devem ser realistas e estimulantes, "
        "conectando {topic} com situações que uma pessoa de {age} anos "
        "de nível {level} encontraria no dia a dia."
    ),
    reflection=(
        "## Tarefa\n"
        "Crie perguntas de reflexão sobre **{topic}** que estimulem "
        "o pensamento crítico.\n\n"
        "## Perfil do Aluno\n"
        "{student_description}\n"
        "- Idade: {age} anos\n"
        "- Nível: {level}\n"
        "- Estilo de aprendizado: {style}\n\n"
        "## Instruções Detalhadas\n"
        "Pense passo a passo sobre os níveis de pensamento que deseja estimular:\n\n"
        "1. **Compreensão:** Perguntas que verificam se o aluno entendeu o conceito\n"
        "2. **Aplicação:** Perguntas que pedem para aplicar o conhecimento\n"
        "3. **Análise:** Perguntas que pedem para comparar, contrastar ou investigar\n"
        "4. **Avaliação:** Perguntas que pedem opinião fundamentada\n"
        "5. **Criação:** Perguntas que estimulam a imaginar soluções novas\n\n"
        "## Formato da Resposta\n"
        "Crie **5 perguntas**, uma para cada nível acima:\n\n"
        "### Pergunta [N] — [Nível: Compreensão/Aplicação/etc.]\n"
        "**Pergunta:** [A pergunta em si]\n"
        "**Por que essa pergunta é importante:** [Justificativa pedagógica]\n"
        "**Dica para reflexão:** [Uma dica que guie o aluno sem dar a resposta]\n\n"
        "**Importante:** Adapte a linguagem e complexidade das perguntas para "
        "um aluno de {age} anos, nível {level}. Evite perguntas que possam "
        "ser respondidas com sim/não."
    ),
    visual_summary=(
        "## Tarefa\n"
        "Crie um resumo visual sobre **{topic}** em formato de mapa mental "
        "ou diagrama usando caracteres ASCII.\n\n"
        "## Perfil do Aluno\n"
        "{student_description}\n"
        "- Idade: {age} anos\n"
        "- Nível: {level}\n"
        "- Estilo de aprendizado: {style}\n\n"
        "## Instruções Detalhadas\n"
        "1. Identifique os 4-6 conceitos principais de {topic}\n"
        "2. Organize-os hierarquicamente (do mais geral ao mais específico)\n"
        "3. Mostre as conexões entre os conceitos\n"
        "4. Adapte a quantidade de detalhes ao nível {level}\n\n"
        "## Formato da Resposta\n"
        "Estruture sua resposta em duas partes:\n\n"
        "### Mapa Mental / Diagrama ASCII\n"
        "```\n"
        "[Diagrama usando ─, │, ├, └, ┌, ┐, ┘, ┤, ┴, ┬, ╔, ═, ║ etc.]\n"
        "```\n\n"
        "### Legenda e Explicação\n"
        "Explique brevemente cada elemento do diagrama e como eles se conectam.\n\n"
        "**Importante:** O diagrama deve ser visualmente claro e legível em "
        "uma fonte monoespaçada. Use no máximo 80 caracteres de largura. "
        "Adapte a complexidade para nível {level} ({age} anos)."
    ),
)



# ============================================================
# VERSÃO v3 — Prompts com Few-Shot e Self-Consistency
# ============================================================
# Prompts que combinam TODAS as técnicas da v2 com adições:
# - Few-shot examples: Exemplos concretos de resposta ideal
# - Self-consistency: Pede à IA avaliar a própria resposta
# - Metacognição: Pede à IA explicar suas escolhas pedagógicas
# - Scaffolding: Instrui construção progressiva explícita
# ============================================================

V3_TEMPLATES = PromptTemplates(
    version="v3",
    description=(
        "Prompts avançados com few-shot examples, self-consistency, "
        "metacognição e scaffolding pedagógico."
    ),
    techniques=[
        "persona prompting",
        "chain-of-thought",
        "context setting",
        "output formatting",
        "constraint setting",
        "audience adaptation",
        "few-shot examples",
        "self-consistency",
        "metacognição",
        "scaffolding",
    ],
    persona=(
        "Você é um professor-pesquisador com PhD em Educação e mais de 20 anos de "
        "experiência adaptando conteúdo para diferentes perfis cognitivos. Você é "
        "especialista em Design Instrucional e domina a Taxonomia de Bloom, "
        "Aprendizagem Significativa de Ausubel e a teoria das Inteligências Múltiplas "
        "de Gardner.\n\n"
        "Você segue rigorosamente estes princípios pedagógicos:\n"
        "1. Sempre crie pontes entre o novo conteúdo e o conhecimento prévio do aluno\n"
        "2. Use a linguagem e o vocabulário adequados à faixa etária\n"
        "3. Priorize exemplos do universo do aluno (interesses e cotidiano)\n"
        "4. Construa explicações do concreto ao abstrato (scaffolding)\n"
        "5. Adapte profundidade e estilo ao perfil de aprendizado específico\n"
        "6. Sempre inclua ao menos uma analogia ou metáfora relativa ao cotidiano\n"
        "7. Ao final, faça uma auto-avaliação pedagógica das suas escolhas"
    ),
    conceptual=(
        "## Tarefa\n"
        "Elabore uma explicação conceitual completa sobre **{topic}**.\n\n"
        "## Perfil do Aluno\n"
        "{student_description}\n"
        "- Idade: {age} anos\n"
        "- Nível: {level}\n"
        "- Estilo de aprendizado: {style}\n\n"
        "## Exemplo de Resposta Ideal (Few-Shot)\n"
        "Aqui está um exemplo de como estruturar uma explicação conceitual sobre "
        "'Gravidade' para uma aluna de 10 anos, nível iniciante, estilo visual:\n\n"
        "---\n"
        "### O que é Gravidade?\n"
        "Gravidade é a força invisível que puxa tudo em direção ao chão. "
        "Imagine que a Terra é como um ímã gigante que atrai tudo para ela — "
        "quando você joga uma bola para cima, ela sempre volta para baixo por causa "
        "da gravidade!\n\n"
        "### Por que é importante?\n"
        "Sem gravidade, estaríamos flutuando como astronautas no espaço! A gravidade "
        "mantém a água nos rios, nossos pés no chão e até a Lua girando ao redor da Terra.\n\n"
        "### Como funciona?\n"
        "Passo 1: Tudo que tem massa (peso) exerce gravidade.\n"
        "Passo 2: Quanto maior o objeto, mais forte a gravidade — por isso a Terra nos puxa.\n"
        "Passo 3: Quanto mais perto do objeto, mais forte a atração.\n\n"
        "### Resumo\n"
        "Gravidade é a força que puxa objetos uns para os outros. A Terra, por ser enorme, "
        "puxa tudo para baixo, mantendo-nos no chão e a Lua no céu.\n\n"
        "### Auto-avaliação pedagógica\n"
        "Usei analogia do ímã (concreta e visual), linguagem simples para 10 anos, "
        "e construí do mais familiar (bola caindo) ao mais abstrato (movimento da Lua).\n"
        "---\n\n"
        "## Instruções Detalhadas\n"
        "Agora, seguindo o mesmo padrão de qualidade, pense passo a passo:\n\n"
        "1. **Análise prévia:** Quais conceitos-chave sobre {topic} este aluno de "
        "nível {level} e {age} anos precisa entender primeiro?\n\n"
        "2. **Ponte cognitiva:** O que esse aluno provavelmente já sabe? Parta desse "
        "ponto para construir a explicação.\n\n"
        "3. **Scaffolding:** Monte a explicação do concreto ao abstrato, do simples "
        "ao complexo, verificando que cada etapa sustenta a próxima.\n\n"
        "## Formato da Resposta\n"
        "### O que é {topic}?\n"
        "[Definição clara com analogia do cotidiano do aluno]\n\n"
        "### Por que é importante?\n"
        "[Relevância e aplicações que o aluno possa reconhecer]\n\n"
        "### Como funciona?\n"
        "[Explicação passo a passo — chain-of-thought]\n\n"
        "### Resumo\n"
        "[Recapitulação em 2-3 frases]\n\n"
        "### Auto-avaliação pedagógica\n"
        "[Explique brevemente: quais técnicas pedagógicas você usou e por quê]\n\n"
        "**Restrições:** Linguagem para {age} anos, nível {level}, estilo {style}. "
        "Use ao menos uma analogia do cotidiano do aluno. "
        "Ao final, releia sua resposta e verifique se é coerente e progressiva."
    ),
    practical=(
        "## Tarefa\n"
        "Crie exemplos práticos contextualizados sobre **{topic}**.\n\n"
        "## Perfil do Aluno\n"
        "{student_description}\n"
        "- Idade: {age} anos | Nível: {level} | Estilo: {style}\n"
        "- Interesses: {interests}\n\n"
        "## Exemplo de Resposta Ideal (Few-Shot)\n"
        "Exemplo de um bom exemplo prático sobre 'Frações' para um aluno de 11 anos "
        "que gosta de pizza e futebol:\n\n"
        "---\n"
        "### Exemplo 1: Dividindo a Pizza\n"
        "**Contexto:** Você pediu uma pizza com 8 fatias para dividir com 3 amigos.\n"
        "**Aplicação:** Cada pessoa come 8 ÷ 4 = 2 fatias. Cada pessoa come 2/8 = 1/4 da pizza.\n"
        "**Passo a passo:** 1) Conte as fatias (8). 2) Conte as pessoas (4). 3) Divida: 8/4 = 2 fatias cada.\n"
        "**O que aprendemos:** Fração é uma divisão! 2/8 e 1/4 são a mesma coisa.\n"
        "---\n\n"
        "## Instruções Detalhadas\n"
        "Crie **3 exemplos práticos** que:\n"
        "1. Usem situações reais do dia a dia de alguém de {age} anos\n"
        "2. Conectem {topic} com os interesses do aluno ({interests})\n"
        "3. Aumentem progressivamente em complexidade (scaffolding)\n"
        "4. Sejam adaptados ao estilo de aprendizado {style}\n"
        "5. Tenham vocabulário adequado ao nível {level}\n\n"
        "## Formato da Resposta\n"
        "Para cada exemplo:\n\n"
        "### Exemplo [N]: [Título descritivo]\n"
        "**Contexto:** [Situação real do cotidiano do aluno]\n"
        "**Aplicação:** [Como {topic} se aplica nesta situação]\n"
        "**Passo a passo:** [Demonstração detalhada]\n"
        "**O que aprendemos:** [Conceito reforçado]\n\n"
        "### Auto-avaliação pedagógica\n"
        "[Explique por que escolheu esses exemplos para esse perfil]\n\n"
        "**Restrições:** Exemplos devem ser realistas para {age} anos, nível {level}. "
        "Não use jargão técnico além do que o nível {level} permite."
    ),
    reflection=(
        "## Tarefa\n"
        "Crie perguntas de reflexão sobre **{topic}** que estimulem o "
        "pensamento crítico em diferentes níveis cognitivos.\n\n"
        "## Perfil do Aluno\n"
        "{student_description}\n"
        "- Idade: {age} anos | Nível: {level} | Estilo: {style}\n\n"
        "## Exemplo de Resposta Ideal (Few-Shot)\n"
        "Exemplo de uma boa pergunta de reflexão sobre 'Poluição' para nível intermediário:\n\n"
        "---\n"
        "### Pergunta 1 — Nível: Análise\n"
        "**Pergunta:** Se uma fábrica gera empregos para 500 famílias mas polui o rio "
        "da cidade, como você avaliaria essa situação? Existe uma solução que "
        "beneficie todos?\n"
        "**Por que essa pergunta é importante:** Desenvolve pensamento sistêmico — "
        "o aluno precisa considerar múltiplos stakeholders e trade-offs.\n"
        "**Dica para reflexão:** Pense nas consequências de curto e longo prazo para "
        "cada grupo: trabalhadores, moradores, meio ambiente.\n"
        "---\n\n"
        "## Instruções Detalhadas\n"
        "Use a Taxonomia de Bloom como guia para cobrir diferentes níveis cognitivos:\n\n"
        "1. **Compreensão:** Verificar entendimento do conceito\n"
        "2. **Aplicação:** Pedir para usar o conhecimento em situação nova\n"
        "3. **Análise:** Comparar, contrastar, investigar relações\n"
        "4. **Avaliação:** Formar opinião fundamentada com argumentos\n"
        "5. **Criação:** Imaginar soluções novas ou cenários hipotéticos\n\n"
        "## Formato da Resposta\n"
        "Crie **5 perguntas**, uma para cada nível:\n\n"
        "### Pergunta [N] — Nível: [Compreensão/Aplicação/Análise/Avaliação/Criação]\n"
        "**Pergunta:** [Pergunta aberta — nunca de sim/não]\n"
        "**Por que essa pergunta é importante:** [Justificativa pedagógica]\n"
        "**Dica para reflexão:** [Orientação sem revelar a resposta]\n\n"
        "### Auto-avaliação pedagógica\n"
        "[Explique como as perguntas progridem em complexidade cognitiva]\n\n"
        "**Restrições:** Linguagem para {age} anos, nível {level}. "
        "Zero perguntas de sim/não. Todas devem exigir raciocínio."
    ),
    visual_summary=(
        "## Tarefa\n"
        "Crie um resumo visual sobre **{topic}** em formato de mapa mental "
        "ou diagrama usando caracteres ASCII/Unicode.\n\n"
        "## Perfil do Aluno\n"
        "{student_description}\n"
        "- Idade: {age} anos | Nível: {level} | Estilo: {style}\n\n"
        "## Exemplo de Resposta Ideal (Few-Shot)\n"
        "Exemplo de diagrama ASCII sobre 'Ciclo da Água' para nível iniciante:\n\n"
        "---\n"
        "```\n"
        "              ☀️ SOL (energia)\n"
        "                   │\n"
        "                   ▼\n"
        "    ┌──────────────────────────┐\n"
        "    │       EVAPORAÇÃO         │\n"
        "    │   (água → vapor)         │\n"
        "    └────────────┬─────────────┘\n"
        "                 │\n"
        "                 ▼\n"
        "    ┌──────────────────────────┐\n"
        "    │      CONDENSAÇÃO         │\n"
        "    │   (vapor → nuvens)       │\n"
        "    └────────────┬─────────────┘\n"
        "                 │\n"
        "                 ▼\n"
        "    ┌──────────────────────────┐\n"
        "    │      PRECIPITAÇÃO        │\n"
        "    │   (chuva / neve)         │\n"
        "    └────────────┬─────────────┘\n"
        "                 │\n"
        "                 ▼\n"
        "        🌊 Rios, Lagos, Oceanos\n"
        "              (volta ao início)\n"
        "```\n"
        "---\n\n"
        "## Instruções Detalhadas\n"
        "1. Identifique 4-6 conceitos principais de {topic}\n"
        "2. Organize hierarquicamente (geral → específico)\n"
        "3. Mostre conexões e relações entre conceitos\n"
        "4. Adapte detalhamento ao nível {level}\n"
        "5. Use Unicode box-drawing: ─ │ ├ └ ┌ ┐ ┘ ┤ ┬ ┴ ╔ ═ ║\n\n"
        "## Formato da Resposta\n\n"
        "### Mapa Mental / Diagrama ASCII\n"
        "```\n"
        "[Seu diagrama aqui — máx. 80 colunas de largura]\n"
        "```\n\n"
        "### Legenda e Explicação\n"
        "[Descreva cada elemento e as conexões entre eles]\n\n"
        "### Auto-avaliação pedagógica\n"
        "[Explique suas escolhas de organização visual para este perfil]\n\n"
        "**Restrições:** Máximo 80 caracteres de largura. Fonte monoespaçada. "
        "Complexidade adequada para {level} ({age} anos)."
    ),
)


# ============================================================
# Registro de versões disponíveis
# ============================================================

PROMPT_VERSIONS: dict[str, PromptTemplates] = {
    "v1": V1_TEMPLATES,
    "v2": V2_TEMPLATES,
    "v3": V3_TEMPLATES,
}

# Tipo para referência
PromptVersion = str
