# 🤖 Agente IPO - Sistema Inteligente de Codificação

> Sistema automatizado para codificação de pesquisas do Instituto Pesquisas de Opinião (IPO) com correção ortográfica, agrupamento inteligente e relatórios detalhados.

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

O **Agente IPO** é um sistema web desenvolvido especificamente para automatizar o processo de codificação de pesquisas de opinião. Ele resolve os principais desafios enfrentados pelos institutos de pesquisa:

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

## 🛠️ Tecnologias

### Backend
- **Python 3.8+** - Linguagem principal
- **Flask 2.3+** - Framework web
- **Pandas** - Manipulação de dados
- **OpenPyXL** - Processamento Excel

### Frontend
- **Bootstrap 5** - Framework CSS responsivo
- **Font Awesome** - Ícones profissionais
- **JavaScript ES6** - Interatividade
- **HTML5/CSS3** - Estrutura e estilo

### Deploy
- **Render** - Hospedagem gratuita
- **Gunicorn** - Servidor WSGI
- **Git** - Controle de versão

## 🚀 Instalação

### Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)
- Git (opcional)

### Instalação Local

```bash
# 1. Clonar repositório
git clone https://github.com/seu-usuario/agente-ipo.git
cd agente-ipo

# 2. Criar ambiente virtual (recomendado)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Executar aplicação
python web_interface_ipo.py

# 5. Acessar no navegador
# http://localhost:5000
```

### Variáveis de Ambiente

Crie um arquivo `.env` (opcional):

```env
FLASK_ENV=development
SECRET_KEY=sua_chave_secreta_aqui
MAX_CONTENT_LENGTH=52428800  # 50MB
PORT=5000
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

```
agente-ipo/
├── web_interface_ipo.py          # Aplicação Flask principal
├── final_ipo_agent_improved.py   # Agente de codificação
├── improved_coding_system.py     # Sistema de correção e agrupamento
├── templates/                    # Templates HTML
│   ├── base.html                # Template base
│   ├── index.html               # Página inicial
│   ├── questao_especifica.html  # Formulário principal
│   ├── upload.html              # Upload de arquivos
│   └── exemplo.html             # Página de exemplo
├── requirements.txt             # Dependências Python
├── render.yaml                  # Configuração Render
├── Procfile                     # Configuração Heroku
├── .gitignore                   # Arquivos ignorados
└── README.md                    # Este arquivo
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

- ✅ **Interface Web** - Completa e funcional
- ✅ **Sistema de Codificação** - Testado e validado
- ✅ **Deploy Automático** - Configurado para Render
- ✅ **Documentação** - Completa e atualizada
- ✅ **Testes** - Validado com dados reais

### Próximas Funcionalidades

- [ ] **API REST** completa
- [ ] **Autenticação** de usuários
- [ ] **Histórico** de processamentos
- [ ] **Exportação** em múltiplos formatos
- [ ] **Integração** com outros sistemas

---

**🤖 Agente IPO - Automatizando a codificação de pesquisas com inteligência artificial!**

