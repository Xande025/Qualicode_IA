# Fluxograma Principal (IPO)

```
[upload de planilha]
    ↓
[pré-processamento + normalização]
    ↓
[amostra → gpt-4o (function-calling)]
    ↓
[agrupamento com códigos + fallback local]
    ↓
[correo de frases (F17/relatório)]
    ↓
[revisão humana (confirmação)]
    ↓
[exportação xlsx/txt]
    ↓
[download de arquivos]
```

## Fluxo das Chamadas de API

### Rota: `/questao_especifica` (Processamento com ChatGPT)

```
frontend → backend: POST /questao_especifica
  {questão, respostas[], códigos_existentes{}}
  ↓
backend → openai (group_with_chatgpt):
  - input: function-calling schema para return_groups
  - output: JSON estruturado {grupos: [{codigo, titulo, respostas}]}
  - fallback: agrupador local (canonicalize + fuzzy merge)
  ↓
backend → openai (standardize_with_chatgpt):
  - correo de frases para F17/relatório
  - fallback: correção local (correct_text)
  ↓
frontend ← backend: 
  {new_codes{}, final_codes{}, grouping_report}
```

### Rota: `/upload` (UI Flask)

```
frontend → backend: POST /upload (arquivo xlsx)
  ↓
backend:
  - extrai questões e respostas
  - carrega códigos existentes
  ↓
frontend ← backend: lista de questões para processar
```

### Rota: `/export` (Exportação)

```
frontend → backend: POST /export
  {dados_agrupados, formato: xlsx/txt}
  ↓
backend → pandas:
  - gera arquivo xlsx com abas
  - gera relatório txt
  ↓
frontend ← backend: download link
```

## Tratamento de Erros

- **429 (Quota insuficiente)**: Marca `chatgpt_available = False`, usa fallback local
- **Falha de parsing JSON**: Parse tolerante + regex extraction + fallback
- **API indisponível**: Sistema continua com agrupador local (sem bloqueios longos)  
