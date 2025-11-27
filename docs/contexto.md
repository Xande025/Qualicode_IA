# Contexto do Projeto

## Problema

Analistas de pesquisa passam muito tempo codificando respostas abertas, o que torna o processo:
- **Lento**: dias de trabalho manual para centenas de respostas
- **Caro**: custo elevado com recursos humanos
- **Pouco escalável**: difícil aumentar volume sem aumentar custo

## Solução

Automatizar o processo de codificação usando modelos de IA (OpenAI GPT-4o), permitindo:

### Fluxo Principal

1. **Geração automática de codebook** → Análise de amostra de respostas via function-calling
2. **Classificação automática** → Agrupamento inteligente com fallback local
3. **Padronização de frases** → Correção de texto para F17/relatório
4. **Revisão humana** → Interface para confirmar/ajustar códigos
5. **Exportação pronta** → Gera XLSX e TXT para análise downstream

## Alinhamento Técnico

- **Modelo**: gpt-3.5-turbo (custo-efetivo)
- **Estrutura**: function-calling para saída JSON garantida
- **Fallback**: agrupador local (canonicalize + fuzzy merge) quando API indisponível
- **Robustez**: parse tolerante, tratamento de quota (429), retry automático

## Objetivos

- Qualidade próxima a plataformas como BTInsights
- Custo **50-80% mais baixo** (vs. SDKs proprietários)
- Foco em operações brasileiras (suporte a português, acentuação, contexto local)
- Flexibilidade: usar ChatGPT ou agrupador local conforme necessário