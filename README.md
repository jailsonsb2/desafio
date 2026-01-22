# Detector Inteligente de Dados Pessoais (LGPD/LAI)
### 1º Hackathon em Controle Social: Desafio Participa DF
**Categoria 1:** Acesso à Informação

---

## 📌 1. Visão Geral e Objetivo
Este projeto consiste em uma solução automatizada para **identificar e classificar pedidos de Acesso à Informação** que contenham dados pessoais, garantindo conformidade com a LGPD.

A solução utiliza uma abordagem híbrida (Regex + NLP/spaCy + Análise de Contexto) para diferenciar dados sensíveis (CPFs, Nomes, E-mails Pessoais) de dados públicos (Processos SEI, Matrículas, E-mails Institucionais), resolvendo o problema de falsos positivos.

---

## 📂 2. Estrutura do Projeto 
A organização dos arquivos segue uma lógica clara de separação entre documentação, dependências e código-fonte:

```text
/ (Raiz do Projeto)
│
├── main.py              # Script principal (CLI e Lógica de Detecção)
├── api.py               # (Opcional) Interface API REST para integração web
├── requirements.txt     # Lista de dependências para instalação automatizada
└── README.md            # Documentação completa do projeto

```

---

## ⚙️ 3. Instruções de Instalação e Dependência 

### Pré-requisitos

* **Linguagem:** Python 3.9 ou superior.
* **Sistema Operacional:** Windows, Linux ou macOS.
* **Acesso à Internet:** Para baixar pacotes e modelos de NLP.

### Instalação Passo a Passo

Siga os comandos abaixo sequencialmente para configurar o ambiente:

**1. Criar e ativar um Ambiente Virtual (Recomendado):**
Isso isola as dependências do projeto.

```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate

```

**2. Instalar Dependências:**
Utilize o gerenciador de pacotes `pip` com o arquivo fornecido.

```bash
pip install -r requirements.txt

```

**3. Baixar o Modelo de Processamento de Linguagem (NLP):**
Necessário para a biblioteca `spaCy` identificar nomes de pessoas.

```bash
python -m spacy download pt_core_news_lg

```

---

## 🚀 4. Instruções de Execução (Critério 2)

O script suporta execução via linha de comando (CLI) e aceita arquivos **CSV** ou **Excel (.xlsx)**.

### Comando Básico (Detecção Automática)

Basta colocar o arquivo de dados na mesma pasta do script e rodar:

```bash
python main.py

```

*O script encontrará automaticamente o primeiro arquivo compatível na pasta.*

### Comando Avançado (Argumentos Específicos)

Para especificar arquivos de entrada e saída:

```bash
python main.py --input "AMOSTRA_DADOS.csv" --output "RELATORIO_FINAL.csv"

```

| Argumento | Descrição | Exemplo |
| --- | --- | --- |
| `--input` | Define o arquivo a ser analisado. | `--input dados_2025.xlsx` |
| `--output` | Define o nome do arquivo de resultado. | `--output resultado.csv` |

---

## 💾 5. Formato dos Dados

### Entrada (Input)

O script aceita arquivos `.csv` (separados por vírgula ou ponto e vírgula) ou `.xlsx`.

* **Requisito:** O arquivo deve conter ao menos uma coluna com texto livre (ex: "Pedido", "Descrição", "Texto Mascarado"). O script detecta essa coluna automaticamente.

### Saída (Output)

Será gerado um arquivo `.csv` contendo as colunas originais acrescidas de:

1. **Classificacao:** "Público" ou "Restrito (Dados Pessoais)".
2. **Dados_Encontrados:** Lista dos tipos detectados (ex: "CPF, NOME_PESSOA, EMAIL").
3. **Texto_Snippet:** Trecho inicial do texto para conferência.

---

## 🧠 6. Lógica Implementada

O código-fonte (`main.py`) possui comentários detalhados explicativo a lógica. Destaques:

* **Filtro de Contexto (Lookbehind):** Implementado para ignorar números de 8/9 dígitos precedidos por palavras como "Processo SEI", "Matrícula" ou "Inscrição", evitando falsos positivos.
* **Blacklist de E-mails:** Ignora e-mails de serviço (`ouvidoria@`, `sac@`) para focar apenas em e-mails de cidadãos.
* **NLP Híbrido:** Combina Regex (para padrões exatos) com IA (para nomes subjetivos).

---

## 🌟 7. Diferencial: API Rest (FastAPI)

Além do script de execução local, o projeto inclui uma **API Rest pronta para produção** (`api.py`), demonstrando como esta solução pode ser integrada a um portal como um microserviço.

### Funcionalidades da API:
1.  **POST /analisar_texto:** Recebe um JSON e valida em tempo real (útil para alertar o cidadão enquanto ele digita).
2.  **POST /analisar_arquivo:** Recebe upload de CSV/XLSX e retorna o relatório processado.

### Como testar a API (Opcional):
1. Instale o servidor: `pip install fastapi uvicorn python-multipart`
2. Rode: `uvicorn api:app --reload`
3. Acesse a documentação interativa: `http://127.0.0.1:8000/docs`