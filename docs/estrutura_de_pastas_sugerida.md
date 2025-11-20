# Estrutura de Pastas do Projeto

## Estrutura Atual (MVP - Monolítico)

```
agente_codificador_ipo/
│
├── improved_coding_system.py          # Core: canonicalize, fuzzy merge, ChatGPT integration
├── final_ipo_agent_improved.py        # Orchestrator: processa questões, gera relatórios
├── openai_compat.py                   # Compatibility wrapper para OpenAI (legacy + novo)
├── web_interface_ipo.py               # Flask app (rotas: upload, questao_especifica, export)
│
├── templates/                         # HTML para Flask
│   ├── base.html
│   ├── index.html
│   ├── upload.html
│   ├── questao_especifica.html
│   └── exemplo.html
│
├── results/                           # Output gerado (XLSX, TXT, raw responses)
│
├── .venv/                             # Virtual environment
├── .env                               # Vars: OPENAI_API_KEY, RESULTS_FOLDER
├── requirements.txt                   # Deps: flask, pandas, openai, fuzzywuzzy, openpyxl, dotenv
├── Procfile                           # Deploy: Heroku/Render
├── render.yaml                        # Config: Render deploy
│
├── docs/                              # Documentação
│   ├── contexto.md
│   ├── fluxogramas.md
│   ├── logica_negocio.md
│   ├── estrutura_de_pastas_sugerida.md
│   ├── arquitetura.md (planejado)
│   ├── prompts.md (planejado)
│   └── mvp_checklist.md (planejado)
│
└── README.md                          # Entry point do projeto
```

## Arquitetura para Refactor (Futuro - Modular)

```
agente_codificador_ipo/
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                          # Flask app instance
│   │   │
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── routes/
│   │   │   │   ├── upload.py               # POST /upload
│   │   │   │   ├── questao_especifica.py   # POST /questao_especifica
│   │   │   │   └── export.py               # POST /export
│   │   │   └── handlers.py                 # Error handling
│   │   │
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── coding_system.py            # Refator: ImprovedIPOCodingSystem
│   │   │   ├── orchestrator.py             # Refator: FinalIPOAgentImproved
│   │   │   ├── openai_client.py            # Wrapper: compatibility + retries
│   │   │   └── config.py                   # Settings, env vars
│   │   │
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── codebook.py                 # Dataclass: Codebook, Code, GroupedResponse
│   │   │   └── request_response.py         # Request/Response schemas
│   │   │
│   │   ├── utils/
│   │   │   ├── __init__.py
│   │   │   ├── text_processing.py          # normalize, canonicalize, correct
│   │   │   ├── file_handlers.py            # XLSX/TXT I/O
│   │   │   └── logging.py                  # Structured logging
│   │   │
│   │   └── templates/                      # HTML templates (Flask)
│   │       ├── base.html
│   │       ├── upload.html
│   │       ├── questao_especifica.html
│   │       └── export.html
│   │
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_coding_system.py
│   │   ├── test_orchestrator.py
│   │   ├── test_api.py
│   │   └── fixtures.py
│   │
│   ├── requirements.txt
│   ├── .env.example
│   └── README.md
│
├── frontend/ (React + TypeScript)
│   ├── src/
│   │   ├── components/
│   │   │   ├── UploadForm.tsx
│   │   │   ├── CodebookPreview.tsx
│   │   │   ├── CodebookEditor.tsx
│   │   │   ├── ClassificationReview.tsx
│   │   │   ├── ExportPanel.tsx
│   │   │   └── common/
│   │   │       ├── Button.tsx
│   │   │       ├── Modal.tsx
│   │   │       └── Spinner.tsx
│   │   │
│   │   ├── pages/
│   │   │   ├── UploadPage.tsx
│   │   │   ├── PreviewPage.tsx
│   │   │   ├── ReviewPage.tsx
│   │   │   └── ExportPage.tsx
│   │   │
│   │   ├── api/
│   │   │   ├── client.ts
│   │   │   └── types.ts
│   │   │
│   │   ├── hooks/
│   │   │   ├── useUpload.ts
│   │   │   ├── useClassification.ts
│   │   │   └── useExport.ts
│   │   │
│   │   ├── styles/
│   │   │   ├── global.css
│   │   │   └── components.module.css
│   │   │
│   │   ├── App.tsx
│   │   └── main.tsx
│   │
│   ├── public/
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── package.json
│   ├── .env.example
│   └── README.md
│
├── docs/
│   ├── contexto.md
│   ├── fluxogramas.md
│   ├── logica_negocio.md
│   ├── arquitetura.md
│   ├── prompts.md
│   ├── api_reference.md
│   └── mvp_checklist.md
│
├── .gitignore
├── .env.example
├── Procfile
├── render.yaml
├── requirements.txt
└── README.md
```

## Status Atual

- ✅ **MVP funcional**: Monolítico, rápido de iterar, fácil de debugar
- 📋 **Próximo passo**: Refatorar para modular conforme cresce a complexidade
- 🎯 **Meta**: Estrutura em `backend/app/` quando sair da fase MVP
