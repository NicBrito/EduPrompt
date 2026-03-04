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
# Registro de versões disponíveis
# ============================================================

PROMPT_VERSIONS: dict[str, PromptTemplates] = {
    "v1": V1_TEMPLATES,
    "v2": V2_TEMPLATES,
}

# Tipo para referência
PromptVersion = str
# ============================================================
# Registro de versões disponíveis
# ============================================================

PROMPT_VERSIONS: dict[str, PromptTemplates] = {
    "v1": V1_TEMPLATES,
    "v2": V2_TEMPLATES,
}

# Tipo para referência
PromptVersion = str
