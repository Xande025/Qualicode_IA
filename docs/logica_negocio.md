# Lógica de Negócio Completa

## Fluxo Lógico

### 1. Upload de Dados
**O usuário envia uma planilha de respostas abertas** (XLSX com questões e respostas)

### 2. Pré-Processamento
**O backend limpa e padroniza os textos**
- Remove acentuação desnecessária (mantém contexto)
- Normaliza espaçamento e pontuação
- Remove duplicatas óbvias

### 3. Geração de Codebook Inicial
**O sistema seleciona uma amostra e envia para gpt-3.5-turbo**
- Amostra: até 30 respostas únicas por questão
- Usa function-calling para garantir JSON estruturado
- Output esperado: `{grupos: [{codigo, titulo, respostas}]}`

**O modelo gera um codebook com categorias e descrições**
- Agrupa respostas semanticamente similares
- Cria títulos descritivos para cada grupo
- Padroniza frases para relatório (F17)

### 4. Revisão e Ajuste do Codebook
**O analista revisa e ajusta o codebook no frontend**
- Confirma/rejeita agrupamentos propostos
- Edita títulos e descrições
- **Confirmação obrigatória** antes de prosseguir (requisito IPO)

### 5. Aplicação do Codebook
**O backend aplica o codebook final a todas as respostas**
- Usa o agrupador local aprimorado (canonicalize + fuzzy merge)
- Fallback automático se ChatGPT indisponível
- Padroniza descrições via `standardize_with_chatgpt` ou `correct_text`

### 6. Revisão Final
**O analista revisa cada resposta, confirmando ou alterando códigos**
- Interface interativa com sugestão de código
- Permite ajuste manual quando necessário
- Rastreia alterações para auditoria

### 7. Exportação
**O sistema exporta tudo em XLSX e TXT**
- XLSX com abas: Codebook, Respostas Codificadas, Relatório de Agrupamento
- TXT com relatório detalhado (F17)
- Pronto para análise downstream (SPSS, R, Python)

## Métricas de Sucesso

- **Velocidade**: 1000 respostas em < 2 minutos (vs. 8h manual)
- **Custo**: < $0.50 por 1000 respostas (vs. $50+ em plataformas)
- **Qualidade**: Concordância humana > 85% sem revisão