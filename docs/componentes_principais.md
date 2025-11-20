# Componentes Principais do Sistema

## Stack Tecnológico Recomendado

| Componente | Função | Tecnologia | Justificativa |
|-----------|--------|-----------|---------------|
| **Backend** | Gerenciar fluxo, integrar OpenAI, processar planilhas | Python + FastAPI | Async, performance, simples de debugar |
| **Módulo de IA** | Enviar prompts, controlar modelos, registrar logs | OpenAI API (gpt-3.5-turbo) | Function-calling, custo-efetivo, fallback local |
| **Frontend** | Revisão do codebook, classificações, export | React 18 + TypeScript + Vite | UX moderna, type-safe, performance |
| **Banco de Dados** | Armazenar respostas, categorias, decisões, auditoria | PostgreSQL | Escalável, JSONB para flexibilidade, backup |
| **Exportador** | Criar arquivos CSV, XLSX, SPSS, TXT | Pandas + openpyxl + pyreadstat | Compatibilidade total, documentado |

## Detalhamento dos Componentes

### 1. Backend (Python + FastAPI)

**Responsabilidades:**
- ✅ Receber uploads XLSX
- ✅ Orquestrar fluxo: pré-processamento → agrupamento → validação
- ✅ Integrar OpenAI com function-calling
- ✅ Fallback local (canonicalize + fuzzy merge)
- ✅ Gerenciar estado (upload → preview → confirmação → export)
- ✅ Servir frontend estático (React build)

**Estrutura:**
```
app/
├── api/
│   ├── routes/upload.py
│   ├── routes/classify.py
│   ├── routes/preview.py
│   ├── routes/export.py
│   └── routes/health.py
├── core/
│   ├── coding_system.py (ImprovedIPOCodingSystem)
│   ├── orchestrator.py (FinalIPOAgentImproved)
│   ├── openai_client.py (wrapper + retry)
│   └── config.py
├── models/
│   └── schemas.py (Pydantic)
├── db/
│   └── models.py (SQLAlchemy)
└── main.py
```

**Endpoints:**
- `POST /api/v1/upload` → Recebe XLSX, retorna lista de questões
- `POST /api/v1/classify` → Processa questão, retorna grupos propostos
- `GET /api/v1/preview/<questao_id>` → Retorna preview para confirmação
- `POST /api/v1/confirm` → Confirma e salva códigos
- `POST /api/v1/export` → Gera XLSX/CSV/SPSS final

---

### 2. Módulo de IA (OpenAI Integration)

**Responsabilidades:**
- ✅ Enviar prompts estruturados com function-calling
- ✅ Parsear JSON retornado
- ✅ Controlar temperatura/tokens/modelo
- ✅ Registrar raw responses para auditoria
- ✅ Implementar retry com backoff exponencial (429, 500)
- ✅ Timeout (30s max)

**Fluxo:**
```
Prompt → Function-calling Schema
  ↓
OpenAI gpt-3.5-turbo
  ↓
Raw JSON Response (salvo em DB/arquivo)
  ↓
Parse Tolerante + Validação Pydantic
  ↓
Fallback Local (se parse falhar)
```

**Função Principal:**
```python
async def group_with_chatgpt(
    responses: list[str],
    existing_codes: dict,
    timeout: int = 30
) -> dict:
    # Function-calling → Retorna {codigo, titulo, respostas}
    # Fallback: group_responses_intelligent()
```

---

### 3. Frontend (React 18 + TypeScript + Vite)

**Responsabilidades:**
- ✅ Upload XLSX
- ✅ Listagem de questões
- ✅ Preview de agrupamentos com confirmação obrigatória
- ✅ Edição manual de códigos/descrições
- ✅ Export com opções (XLSX/CSV/SPSS)
- ✅ Visualização de logs/auditoria

**Componentes Principais:**
- `UploadForm.tsx` → Recebe arquivo
- `QuestionList.tsx` → Lista questões
- `CodebookPreview.tsx` → Preview + confirmação (OBRIGATÓRIA)
- `CodebookEditor.tsx` → Editar códigos
- `ExportPanel.tsx` → Download XLSX/CSV/SPSS

**Estado Global:**
```typescript
interface AppState {
  uploadId: string;
  questions: Question[];
  selectedQuestion: Question | null;
  groupedResponses: GroupedResponse[];
  exportStatus: 'idle' | 'processing' | 'ready' | 'error';
}
```

---

### 4. Banco de Dados (PostgreSQL)

**Tabelas Principais:**
- `uploads` → Arquivo enviado + metadata
- `questions` → Questões extraídas
- `responses` → Respostas originais
- `codes` → Dicionário de códigos
- `classifications` → Resposta → Código (histórico)
- `audit_logs` → Raw OpenAI responses + decisões

**Justificativa PostgreSQL:**
- ✅ JSONB para armazenar respostas raw do ChatGPT
- ✅ Full-text search para auditoria
- ✅ Transações ACID para garantir consistência
- ✅ Backup/restore simples

---

### 5. Exportador (Pandas + openpyxl + pyreadstat)

**Formatos Suportados:**
- ✅ **XLSX** → Abas: Codebook, Respostas Codificadas, Relatório
- ✅ **CSV** → Resposta, Código, Descrição (UTF-8)
- ✅ **SPSS** → SAV format (pyreadstat)
- ✅ **TXT** → Relatório formatado (F17)

**Output Esperado:**
```
Resultado_Codificacao_YYYYMMDD.xlsx
├── Codebook (id, código, descrição, # respostas)
├── Respostas_Codificadas (id, resposta, código, confiança)
└── Relatório (sumário + estatísticas)
```

---

## Decisões de Design

| Decisão | Razão | Trade-off |
|---------|-------|-----------|
| FastAPI (não Flask) | Async nativo, validação automática, performance | Migração futura do Flask atual |
| PostgreSQL (não SQLite) | Escalabilidade, JSONB, backup robusto | Setup inicial mais complexo |
| React (não templates Jinja) | UX moderna, state management, componentização | Separação frontend/backend |
| Vite (não Create React App) | Build rápido, dev server otimizado, módulos ES6 | Comunidade menor que CRA |
| Fallback Local Obrigatório | Robustez quando ChatGPT indisponível | Custo de manutenção maior |

---

## Dependências Críticas

### Backend
```
fastapi==0.104.1
uvicorn==0.24.0
openai==1.3.0 (nova API)
pandas==2.1.0
openpyxl==3.11.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
python-dotenv==1.0.0
pydantic==2.4.0
```

### Frontend
```json
{
  "react": "^18.2.0",
  "typescript": "^5.2.0",
  "vite": "^5.0.0",
  "axios": "^1.6.0",
  "react-router-dom": "^6.18.0"
}
```

---

## Roadmap de Implementação

### MVP (Semana 1-2)
- ✅ Backend: FastAPI com endpoints básicos
- ✅ Frontend: Upload + Preview + Export simples
- ✅ DB: Estrutura mínima

### v1.0 (Semana 3-4)
- 🔄 Editor de códigos interativo
- 🔄 Suporte SPSS/CSV
- 🔄 Audit logs completo

### v1.1+ (Futuro)
- 📌 Dashboard de estatísticas
- 📌 Multi-usuário com permissões
- 📌 Embeddings para clustering semântico