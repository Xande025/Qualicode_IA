# 📡 API Documentation - Agente IPO

## Endpoints

### POST /questao_especifica
Processa uma questão específica com dados e códigos F17.

**Request:**
```json
{
  "question_name": "QUESTÃO 15 - PRINCIPAL REALIZAÇÃO",
  "question_data": "Melhorou a saude\nAsfalto novo\nNao fez nada",
  "f17_codes": "1 | Melhoria na área da saúde\n2 | Pavimentação/asfalto\n9 | Não fez nada"
}
```

**Response:**
```json
{
  "success": true,
  "question_name": "QUESTÃO 15 - PRINCIPAL REALIZAÇÃO",
  "total_responses": 3,
  "valid_responses": 3,
  "statistics": {
    "total_codes": 3,
    "new_codes_count": 0,
    "groups_with_multiple": 0,
    "largest_group_size": 1
  },
  "download_links": {
    "banco": "/download/banco_20250812_123456.xlsx",
    "f17": "/download/f17_20250812_123456.xlsx",
    "relatorio": "/download/relatorio_20250812_123456.txt",
    "resumo": "/download/resumo_20250812_123456.txt"
  },
  "detailed_report": "RELATÓRIO DE AGRUPAMENTOS..."
}
```

### GET /download/<filename>
Download de arquivos gerados.

**Response:** Arquivo binário (Excel ou texto)

### POST /upload
Upload de arquivos completos (Banco + F17).

**Request:** Multipart form data
- `banco_file`: Arquivo Excel
- `f17_file`: Arquivo Excel

**Response:** Redirecionamento ou mensagem de status
