# 🤖 Qualicode_IA - Sistema Inteligente de Codificação

> Plataforma automatizada para codificação de pesquisas com IA, correção ortográfica, agrupamento semântico e relatórios detalhados. Reduz tempo de codificação manual em 80% com custo 50% menor que plataformas proprietárias.

## 📋 Índice

- [Sobre o Projeto](#sobre-o-projeto)
- [Funcionalidades](#funcionalidades)
- [Tecnologias](#tecnologias)
- [Instalação](#instalação)
- [Deploy](#deploy)
- [Como Usar](#como-usar)
- [API](#api)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Contribuição](#contribuição)
- [Licença](#licença)

## 🎯 Sobre o Projeto

O **Qualicode_IA** é uma plataforma moderna para automatizar codificação de pesquisas qualitativas. Combina IA (OpenAI gpt-3.5-turbo), processamento de linguagem natural e interface interativa para oferecer precisão próxima a BTInsights com custo significativamente menor.

### 🔍 Problemas Resolvidos

- **Codificação manual demorada** → Automatização inteligente
- **Erros ortográficos nas respostas** → Correção automática
- **Agrupamento inconsistente** → Análise de sentido por IA
- **Relatórios desorganizados** → Formato padronizado IPO
- **Retrabalho constante** → Processo único e eficiente

### 🎯 Público-Alvo

- **Institutos de Pesquisa** - Codificação de questionários
- **Empresas de Consultoria** - Análise de feedback
- **Universidades** - Pesquisas acadêmicas
- **Órgãos Públicos** - Pesquisas de satisfação

## ⚡ Funcionalidades

### 🔧 Processamento Inteligente

- **Correção Ortográfica Automática**
  - Corrige erros comuns: "saude" → "saúde"
  - Padroniza acentuação e capitalização
  - Mantém contexto original das respostas

- **Agrupamento por Sentido**
  - Identifica respostas similares automaticamente
  - Agrupa por significado, não apenas por palavras
  - Preserva códigos F17 existentes

- **Codificação Inteligente**
  - Usa códigos existentes quando aplicável
  - Cria novos códigos a partir do 10
  - Respeita códigos reservados (55, 66, 77, 88, 99)

### 📊 Interface Web Moderna

- **Questão Específica**
  - Cole dados diretamente do Excel
  - Processamento em tempo real
  - Download automático dos resultados

- **Upload de Arquivos**
  - Suporte a Excel (.xlsx, .xls)
  - Processamento de pesquisas completas
  - Validação automática de formatos

- **Relatórios Detalhados**
  - Formato padrão IPO
  - Mostra todos os agrupamentos
  - Estatísticas completas

### 📁 Arquivos Gerados

1. **Banco Codificado** (.xlsx) - Duas colunas: Código | Resposta
2. **F17 Atualizado** (.xlsx) - Códigos organizados numericamente
3. **Relatório de Agrupamentos** (.txt) - Detalhamento completo
4. **Resumo Estatístico** (.txt) - Análise quantitativa

### 🛠️ Tecnologias

#### Backend
- **Python 3.10+** - Linguagem principal
- **FastAPI** - Framework assíncrono (em desenvolvimento)
- **OpenAI API** - gpt-3.5-turbo com function-calling
- **Pandas + openpyxl** - Processamento de dados e Excel
- **SQLAlchemy + PostgreSQL** - Persistência com auditoria
- **Pydantic** - Validação de esquemas

#### Frontend
- **React 18 + TypeScript** - UI moderna e type-safe
- **Vite** - Build rápido e dev server otimizado
- **React Router** - Navegação SPA
- **Axios** - HTTP client
- **CSS Modules** - Estilização escalável

#### Deploy & DevOps
- **Render** - Hospedagem (backend + frontend)
- **Uvicorn** - Servidor ASGI
- **Docker** - Containerização (planejado)
- **Git** - Controle de versão

## 🚀 Instalação

### Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)
- Git (opcional)

### Instalação Local

```bash
# 1. Clonar repositório
git clone https://github.com/Xande025/Qualicode_IA.git
cd Qualicode_IA

# 2. Criar ambiente virtual (recomendado)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# 3. Configurar variáveis de ambiente
cp .env.example .env
# Edite .env e adicione sua OPENAI_API_KEY

# 4. Instalar dependências
pip install -r requirements.txt

# 5. Executar aplicação (MVP - Flask)
python web_interface_ipo.py
# ou (futuro - FastAPI)
# uvicorn app.main:app --reload

# 6. Acessar no navegador
# http://localhost:5000 (Flask MVP)
# http://localhost:8000 (FastAPI futuro)
```

### Variáveis de Ambiente

Crie um arquivo `.env` a partir do template:

```env
# Backend
OPENAI_API_KEY=sk-...seu-api-key-aqui
FLASK_ENV=development
PORT=5000
RESULTS_FOLDER=./results

# Database (futuro)
DATABASE_URL=postgresql://user:password@localhost:5432/qualicode_ia

# Frontend (se separado)
REACT_APP_API_URL=http://localhost:5000
```

## 📖 Como Usar

### 1. Questão Específica (Recomendado)

#### Entrada de Dados
1. **Nome da Questão**: `QUESTÃO 15 - PRINCIPAL REALIZAÇÃO`
2. **Dados da Questão** (uma resposta por linha):
   ```
   Melhorou a saude
   Asfalto novo
   Nao fez nada
   Construiu escola
   ```
3. **Códigos F17** (formato: código | descrição):
   ```
   1 | Melhoria na área da saúde
   2 | Pavimentação/asfalto
   9 | Não fez nada
   ```

#### Processamento
- Sistema corrige ortografia automaticamente
- Agrupa respostas por sentido
- Gera códigos e relatórios

#### Resultados
- **Banco codificado** com duas colunas
- **F17 atualizado** com novos códigos
- **Relatório detalhado** de agrupamentos

### 2. Upload de Arquivos

#### Formatos Suportados
- **Banco de Codificação**: Excel (.xlsx, .xls)
- **F17**: Excel com códigos existentes
- **Tamanho máximo**: 50MB por arquivo

#### Processamento Automático
- Identifica questões F17 automaticamente
- Processa apenas questões que precisam
- Gera relatórios para toda a pesquisa

### 3. Exemplo Prático

Use a página "Exemplo" para testar com dados reais:
- Dados pré-carregados
- Resultado esperado mostrado
- Botão "Usar Este Exemplo" para teste rápido

## 🔌 API

### Endpoints Principais

#### POST /questao_especifica
Processa uma questão específica.

**Parâmetros:**
- `question_name` (string): Nome da questão
- `question_data` (text): Dados da questão (uma resposta por linha)
- `f17_codes` (text): Códigos F17 (formato: código | descrição)

**Resposta:**
```json
{
  "success": true,
  "question_name": "QUESTÃO 15",
  "total_responses": 16,
  "statistics": {
    "total_codes": 12,
    "new_codes_count": 3
  },
  "download_links": {
    "banco": "/download/banco.xlsx",
    "f17": "/download/f17.xlsx",
    "relatorio": "/download/relatorio.txt"
  }
}
```

#### POST /upload
Upload de arquivos completos.

**Parâmetros:**
- `banco_file` (file): Arquivo Excel do banco
- `f17_file` (file): Arquivo Excel do F17

#### GET /download/<filename>
Download de arquivos gerados.

## 📁 Estrutura do Projeto

### MVP Atual (Flask Monolítico)
```
Qualicode_IA/
├── improved_coding_system.py         # Core: canonicalize, fuzzy merge, ChatGPT
├── final_ipo_agent_improved.py       # Orchestrator: processa questões
├── openai_compat.py                  # Compatibility wrapper OpenAI
├── web_interface_ipo.py              # Flask app (rotas: upload, questao_especifica, export)
├── templates/                        # Templates HTML
│   ├── base.html
│   ├── index.html
│   ├── upload.html
│   ├── questao_especifica.html
│   └── exemplo.html
├── results/                          # Outputs gerados (XLSX, TXT, logs)
├── docs/                             # Documentação
│   ├── contexto.md
│   ├── fluxogramas.md
│   ├── logica_negocio.md
│   ├── componentes_principais.md
│   └── estrutura_de_pastas_sugerida.md
├── .venv/                            # Virtual environment
├── requirements.txt
├── render.yaml
├── Procfile
└── README.md
```

### Arquitetura Futura (FastAPI + React)
```
Qualicode_IA/
├── backend/                          # FastAPI + modular
│   ├── app/api/routes/
│   ├── app/core/
│   ├── app/models/
│   └── requirements.txt
├── frontend/                         # React 18 + TypeScript
│   ├── src/components/
│   ├── src/pages/
│   ├── src/api/
│   └── package.json
└── docs/
```

### Arquivos Principais

- **`web_interface_ipo.py`**: Servidor Flask com todas as rotas
- **`final_ipo_agent_improved.py`**: Lógica principal do agente
- **`improved_coding_system.py`**: Sistema de correção e agrupamento
- **`templates/`**: Interface web responsiva

## 🧪 Testes

### Teste Local
```bash
# Executar aplicação
python web_interface_ipo.py

# Acessar no navegador
http://localhost:5000

# Usar página de exemplo para teste rápido
```

### Teste de Produção
```bash
# Simular ambiente de produção
export FLASK_ENV=production
python web_interface_ipo.py
```

## 📊 Exemplos de Uso

### Exemplo 1: Questão sobre Governo

**Entrada:**
```
Nome: QUESTÃO xx - PRINCIPAL REALIZAÇÃO DO GOVERNO

Dados:
Melhorou a saude
Asfalto novo
Nao fez nada
Construiu escola nova

Códigos F17:
1 | Melhoria na área da saúde
2 | Pavimentação/asfalto
3 | Educação
9 | Não fez nada
```

**Resultado:**
```
Código 1 – Melhoria na área da saúde:
 - Melhorou a saude

Código 2 – Pavimentação/asfalto:
 - Asfalto novo

Código 3 – Educação:
 - Construiu escola nova

Código 9 – Não fez nada:
 - Nao fez nada
```

### Exemplo 2: Agrupamento Inteligente

**Entrada:**
```
Melhorou a saude
Saude melhorou muito
Melhorou os postos de saude
```

**Resultado:**
```
Código 1 – Melhoria na área da saúde:
 - Melhorou a saude
 - Saude melhorou muito
 - Melhorou os postos de saude
```

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.
## 🎯 Status do Projeto

### MVP (v0.1 - Atual)
- ✅ Interface web funcional (Flask)
- ✅ Sistema de codificação com ChatGPT + fallback local
- ✅ Agrupamento inteligente (canonicalize + fuzzy merge)
- ✅ Exportação XLSX/TXT
- ✅ Deploy automatizado (Render)
- ✅ Documentação técnica completa
- ✅ Compatibilidade com OpenAI nova API

### Sprint 1 (v0.2 - Esta semana)
- [ ] Detecção automática de tipo de questão
- [ ] Pré-visualização com confirmação obrigatória
- [ ] Logs/auditoria raw do ChatGPT
- [ ] Testes unitários básicos
- [ ] Tratamento de erro 429 (quota)

### Sprint 2 (v0.3 - Próxima semana)
- [ ] Expandir dicionário de sinônimos
- [ ] Ajustar thresholds (fuzzy 85%+)
- [ ] Marcar MANUAL_REVIEW para anomalias
- [ ] Validação E2E com ChatGPT

### v1.0 (Produção)
- [ ] Migração para FastAPI (async)
- [ ] Frontend React 18 + TypeScript
- [ ] PostgreSQL com auditoria completa
- [ ] Multi-usuário com autenticação
- [ ] Suporte SPSS/CSV/RDS

---

## 📞 Contato & Contribuição

**Desenvolvedor**: Xande025  
**Repository**: [Xande025/Qualicode_IA](https://github.com/Xande025/Qualicode_IA)  
**Issues & Sugestões**: [GitHub Issues](https://github.com/Xande025/Qualicode_IA/issues)

---

**🤖 Qualicode_IA - Inteligência artificial para pesquisas qualitativas!**

