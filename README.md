# 📚 EduPrompt — Plataforma Educativa com IA

Plataforma educativa que gera conteúdo personalizado para alunos de diferentes perfis usando técnicas avançadas de engenharia de prompt. Compara automaticamente diferentes versões de prompts com métricas quantitativas.

🔗 **Repositório:** https://github.com/NicBrito/EduPrompt
🌐 **Deploy:** https://edu-prompt-desafio.vercel.app

---

## 🎯 Funcionalidades

- **Perfis de Alunos:** 5 perfis pré-configurados com diferentes idades, níveis e estilos de aprendizado
- **4 Tipos de Conteúdo:**
  - Explicação Conceitual (chain-of-thought)
  - Exemplos Práticos (contextualizados por idade/nível)
  - Perguntas de Reflexão (Taxonomia de Bloom)
  - Resumo Visual (mapa mental/diagrama ASCII)
- **Engenharia de Prompt:** 3 versões evolutivas (v1 baseline → v2 otimizada → v3 few-shot avançada)
- **Análise Comparativa:** Gera mesmo conteúdo com todas as versões e produz relatório com métricas
- **Cache Inteligente:** Evita chamadas desnecessárias à API com TTL configurável
- **Histórico:** Salva todas as gerações em JSON com timestamp
- **Dupla Interface:** CLI interativa + interface web (Flask)
- **Multi-provedor:** Suporta OpenAI, Google Gemini e Anthropic Claude

---

## 🚀 Setup Rápido

### 1. Clone o repositório

```bash
git clone https://github.com/NicBrito/EduPrompt
cd EduPrompt
```

### 2. Crie um ambiente virtual

```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# ou: venv\Scripts\activate  # Windows
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure as variáveis de ambiente

```bash
cp .env.example .env
```

Edite o arquivo `.env` e configure:
- `AI_PROVIDER`: Escolha `openai`, `gemini` ou `anthropic`
- A chave de API correspondente ao provedor escolhido

### 5. Execute

**CLI (Interface de linha de comando):**
```bash
python -m src.main
# ou:
python -m src
```

**Interface Web (Flask):**
```bash
python -m src.app
```
Acesse: http://localhost:5001

---

## 📁 Estrutura do Projeto

```
DevIA/
├── .env.example                    # Template de variáveis de ambiente
├── .gitignore
├── requirements.txt                # Dependências Python
├── README.md                       # Este arquivo
├── PROMPT_ENGINEERING_NOTES.md     # Documentação das estratégias de prompt
│
├── src/                            # Código-fonte principal
│   ├── __init__.py
│   ├── __main__.py                 # Suporte a python -m src
│   ├── config.py                   # Configuração central (.env)
│   ├── main.py                     # Interface CLI
│   ├── app.py                      # Interface Web (Flask)
│   │
│   ├── models/
│   │   └── student.py              # Modelo de perfil de aluno (dataclass + enums)
│   │
│   ├── prompts/
│   │   ├── engine.py               # Motor de engenharia de prompt
│   │   ├── templates.py            # Estrutura dos templates
│   │   └── versions.py             # Versões v1, v2 e v3
│   │
│   ├── generators/
│   │   ├── base.py                 # Gerador base (abstrato + cache)
│   │   ├── conceptual.py           # Explicação conceitual
│   │   ├── practical.py            # Exemplos práticos
│   │   ├── reflection.py           # Perguntas de reflexão
│   │   └── visual.py               # Resumo visual ASCII
│   │
│   ├── services/
│   │   ├── ai_client.py            # Cliente unificado (OpenAI/Gemini/Claude)
│   │   ├── cache.py                # Sistema de cache com TTL (SHA256)
│   │   ├── comparison.py           # Análise comparativa entre versões
│   │   └── storage.py              # Persistência JSON e histórico
│   │
│   └── utils/
│       └── helpers.py              # Funções utilitárias
│
├── data/
│   ├── students.json               # Perfis dos 5 alunos
│   ├── outputs/                    # Conteúdos gerados (histórico)
│   └── cache/                      # Cache de respostas da API
│
├── templates/
│   └── index.html                  # Interface web Flask
│
├── tests/
│   ├── test_models.py              # Testes de modelos (11 testes)
│   ├── test_prompts.py             # Testes do motor de prompt (11 testes)
│   ├── test_cache.py               # Testes do cache (8 testes)
│   ├── test_generators.py          # Testes dos geradores (9 testes)
│   ├── test_app.py                 # Testes dos endpoints Flask (24 testes)
│   └── test_comparison.py          # Testes da análise comparativa (6 testes)
│
└── samples/
    └── ana_silva_fotossintese_example.json  # Exemplo de output
```

---

## 💻 Uso

### CLI — Menu Principal

```
┌─────────────────────────────────┐
│        MENU PRINCIPAL           │
├─────────────────────────────────┤
│  1. Gerar conteúdo específico   │
│  2. Gerar todos os conteúdos    │
│  3. Listar perfis de alunos     │
│  4. Comparar versões de prompt  │
│  5. Ver histórico de geração    │
│  6. Gerenciar cache             │
│  7. Trocar versão de prompts    │
│  8. Análise comparativa completa│
│  0. Sair                        │
└─────────────────────────────────┘
```

### Exemplo de Uso via CLI

1. Execute `python -m src.main`
2. Escolha opção `2` (Gerar todos os conteúdos)
3. Selecione um aluno (ex: Ana Silva — 12 anos, iniciante)
4. Digite o tópico (ex: "Fotossíntese")
5. O sistema gera os 4 tipos de conteúdo e salva em JSON

### Análise Comparativa

Use a opção `8` do CLI ou o endpoint `/api/compare` para gerar o mesmo conteúdo com todas as versões de prompt (v1, v2, v3) e obter um relatório com:

- Conteúdo gerado por cada versão
- Métricas quantitativas (palavras, linhas, estrutura)
- Evolução das técnicas aplicadas
- Observações automáticas sobre diferenças

### API Web — Endpoints

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/` | Interface web |
| POST | `/api/generate` | Gerar conteúdo específico |
| POST | `/api/generate-all` | Gerar todos os 4 tipos |
| POST | `/api/compare` | Análise comparativa entre versões |
| GET | `/api/students` | Listar alunos |
| GET | `/api/history` | Ver histórico |
| GET | `/api/cache/stats` | Estatísticas do cache |
| POST | `/api/cache/clear` | Limpar cache |

---

## 🧪 Testes

```bash
# Rodar todos os testes (69 testes)
pytest

# Com cobertura
pytest --cov=src

# Testes específicos
pytest tests/test_prompts.py -v
pytest tests/test_app.py -v
```

---

## 🧠 Engenharia de Prompt

O sistema implementa **10 técnicas** de engenharia de prompt, organizadas em 3 versões evolutivas:

### v1 — Baseline (2 técnicas)
- **Persona Prompting** — Papel de professor
- **Context Setting** — Dados do aluno

### v2 — Otimizada (6 técnicas)
1. **Persona Prompting** — Definição detalhada do papel do professor
2. **Context Setting** — Dados específicos do aluno incluídos no prompt
3. **Chain-of-Thought** — Raciocínio passo a passo para explicações
4. **Output Formatting** — Estrutura explícita da resposta esperada
5. **Constraint Setting** — Limites claros de linguagem e complexidade
6. **Audience Adaptation** — Personalização por público-alvo

### v3 — Avançada com Few-Shot (10 técnicas)
7. **Few-Shot Prompting** — Exemplos concretos de entrada/saída
8. **Self-Consistency** — Instrução para verificação e revisão
9. **Metacognição** — Estímulo ao pensamento reflexivo
10. **Scaffolding** — Construção progressiva de complexidade

Detalhes completos e exemplos em [PROMPT_ENGINEERING_NOTES.md](PROMPT_ENGINEERING_NOTES.md).

---

## 📊 Comparação de Versões

O sistema permite gerar o mesmo conteúdo com 3 versões de prompt para comparação:

| Versão | Técnicas | Foco |
|--------|----------|------|
| v1 | 2 | Prompts diretos e simples |
| v2 | 6 | Todas as técnicas avançadas |
| v3 | 10 | Few-shot, metacognição, scaffolding |

Use a opção 8 do menu CLI, a opção 4 para comparação rápida, ou o endpoint `/api/compare` na interface web.

---

## 🔧 Configuração

### Provedores Suportados

| Provedor | Modelos Sugeridos | Variável |
|----------|-------------------|----------|
| Google | gemini-flash-latest, gemini-2.0-flash | `GEMINI_API_KEY` |
| OpenAI | gpt-4o, gpt-4o-mini | `OPENAI_API_KEY` |
| Anthropic | claude-3-haiku, claude-3-sonnet | `ANTHROPIC_API_KEY` |

### Cache

O cache é armazenado em `data/cache/` com TTL configurável via `CACHE_TTL` no `.env`. Padrão: 1 hora (3600 segundos).

### Porta

A interface web roda na porta 5001 por padrão (configurável via `FLASK_PORT` no `.env`).

---

## 📄 Licença

Projeto desenvolvido como desafio técnico para vaga de Estágio em IA e Engenharia de Prompt.
