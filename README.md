# 🤖 Qualicode_IA - Sistema Inteligente de Codificação

> Plataforma automatizada para codificação de pesquisas qualitativas com IA de última geração (**GPT-4o**), correção ortográfica contextual, agrupamento semântico avançado e relatórios de auditoria completa. Reduz o tempo de codificação manual em até **90%** com precisão superior a métodos tradicionais.

## 📋 Índice

- [Sobre o Projeto](#sobre-o-projeto)
- [Diferenciais Técnicos](#diferenciais-técnicos)
- [Tecnologias](#tecnologias)
- [Instalação](#instalação)
- [Como Usar](#como-usar)
- [Arquitetura e Fluxo](#arquitetura-e-fluxo)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Status e Roadmap](#status-e-roadmap)
- [Licença](#licença)

## 🎯 Sobre o Projeto

O **Qualicode_IA** revoluciona a codificação de perguntas abertas em pesquisas de opinião. Diferente de ferramentas que apenas buscam palavras-chave, nosso agente utiliza **LLMs avançados (GPT-4o)** para entender o *sentido* das respostas, agrupar variações semânticas (ex: "saude precaria" = "falta de médicos") e gerar codebooks profissionais automaticamente.

### 🔍 Problemas Resolvidos

- **Codificação manual demorada** → Automatização em segundos (milhares de respostas/minuto).
- **Inconsistência humana** → Critérios padronizados e imutáveis via prompt engineering.
- **Perda de nuances** → O modelo entende ironia, gírias e variações regionais.
- **"Respostas perdidas"** → Sistema de **Retry Inteligente** e **Última Milha** garante 100% de cobertura.
- **Conflito de Códigos** → Lógica blindada impede duplicação de IDs entre Codebook antigo e novo.

### 🎯 Público-Alvo

- **Institutos de Pesquisa** (IPO, Ipec, Datafolha, etc.)
- **Empresas de Consultoria e CX**
- **Universidades e Pesquisadores Acadêmicos**
- **Órgãos Públicos** (Ouvidorias e Pesquisas de Satisfação)

## ⚡ Diferenciais Técnicos

### 🧠 Core de Inteligência Híbrida
O sistema não depende apenas da IA. Ele utiliza uma arquitetura em camadas para garantir robustez:

1.  **Camada Semântica (GPT-4o):** Cria o Codebook inicial com base em amostras únicas, entendendo o contexto profundo.
2.  **Camada de Auditoria (Retry):** Verifica automaticamente se alguma resposta ficou sem código e faz chamadas recursivas para preencher lacunas.
3.  **Camada Determinística (Local):** Aplica regras rígidas do Codebook F17 existente (se houver) para garantir compatibilidade histórica.
4.  **Camada de Segurança (Auto-Coding):** Se tudo falhar, cria códigos provisórios automaticamente para que nenhuma resposta seja descartada.

### 🔧 Funcionalidades Chave

- **Detecção Automática de Tipo:** Identifica se a questão é Aberta, Fechada (apenas números) ou Semi-aberta e ajusta o processamento.
- **Correção Ortográfica Contextual:** "melhoria na saude" e "melhorias na saúde" são tratadas como idênticas antes mesmo de codificar.
- **Relatórios Exaustivos:** O relatório final lista **todas** as variações de escrita que caíram em cada código, permitindo auditoria visual linha a linha.
- **Resumo Estatístico Real:** Contagem precisa de frequências baseada no banco final classificado.

## 🛠️ Tecnologias

#### Backend & IA
- **Python 3.10+**
- **OpenAI API (GPT-4o)** - Modelo state-of-the-art para raciocínio complexo.
- **Flask** - Framework web leve e robusto.
- **Pandas + OpenPyXL** - Manipulação de alta performance de dados Excel.
- **FuzzyWuzzy** - Algoritmos de similaridade de string para matching local.

#### Frontend
- **HTML5 / CSS3 / JavaScript** - Interface limpa e responsiva (Jinja2 Templates).
- **Bootstrap** - Estilização moderna.

## 🚀 Instalação

### Pré-requisitos
- Python 3.8 ou superior
- Conta na OpenAI (API Key)

### Instalação Local

```bash
# 1. Clonar repositório
git clone https://github.com/Xande025/Qualicode_IA.git
cd Qualicode_IA

# 2. Criar ambiente virtual
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Configurar ambiente
# Crie um arquivo .env na raiz com:
OPENAI_API_KEY=sk-sua-chave-aqui
FLASK_ENV=development

# 5. Executar
python web_interface_ipo.py
```

Acesse em: `http://localhost:5000`

## 📖 Como Usar

### Fluxo "Questão Específica" (Recomendado para testes)

1.  **Nome da Questão**: Dê um título (ex: "Q15 - Pontos Positivos").
2.  **Dados**: Cole a coluna do Excel com as respostas abertas (uma por linha).
3.  **F17 (Opcional)**: Cole os códigos que já existem (ex: `1 | Bom atendimento`). Se não tiver, deixe em branco e a IA criará do zero.
4.  **Processar**: O sistema fará a mágica.
5.  **Download**: Baixe o pacote ZIP com:
    *   `banco_codificado.xlsx`: Sua planilha pronta.
    *   `f17_atualizado.xlsx`: Seu codebook novo.
    *   `relatorio.txt`: Explicação detalhada.

## 🏗️ Arquitetura e Fluxo

```mermaid
graph TD
    A[Input Excel] --> B{Detecção de Tipo};
    B -- Fechada --> C[Ignora (Retorna Original)];
    B -- Aberta/Semi --> D[Extrai Respostas Únicas];
    D --> E[GPT-4o: Criação de Codebook];
    E --> F{Sobrou Resposta sem Código?};
    F -- Sim --> G[Retry: Chama GPT para Resíduos];
    G --> H[Consolidação de Códigos (Blindagem contra Conflitos)];
    F -- Não --> H;
    H --> I[Classificação Total do Banco];
    I --> J[Geração de Relatórios e Arquivos];
```

## 📁 Estrutura do Projeto

```
Qualicode_IA/
├── improved_coding_system.py   # Cérebro: Lógica de IA, prompts e limpeza
├── final_ipo_agent_improved.py # Orquestrador: Gerencia fluxo, retry e arquivos
├── web_interface_ipo.py        # Servidor Web: Rotas e interface
├── templates/                  # Telas (Upload, Questão Específica)
├── results/                    # Pasta temporária de saídas
└── docs/                       # Documentação técnica detalhada
```

## 🎯 Status e Roadmap

### Versão Atual (v0.2 - Stable)
- ✅ Migração completa para **GPT-4o**.
- ✅ Sistema de Retry para cobertura de 100%.
- ✅ Consolidação de códigos sem conflitos (F17 vs Novos).
- ✅ Relatórios exaustivos com todas as variações.
- ✅ Detecção de tipo de questão.

### Próximos Passos (v0.3)
- [ ] Implementação da rota de Upload de Arquivo Completo (processamento em lote).
- [ ] Interface de revisão manual ("arrastar e soltar") antes de exportar.
- [ ] Suporte a arquivos .SAV (SPSS).

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

---

**🤖 Qualicode_IA** - Inteligência artificial aplicada à pesquisa de verdade.
