# Detector de Dados Pessoais (LGPD) - Desafio Participa DF
### Categoria 1: Acesso à Informação

Esta solução implementa um sistema automatizado para identificar e classificar pedidos de acesso à informação que contenham dados pessoais, garantindo a conformidade com a **LGPD (Lei Geral de Proteção de Dados)** sem comprometer a transparência pública exigida pela **LAI**.

---

## 🎯 Motivação e Abordagem

O maior desafio na anonimização de pedidos de LAI é o **falso positivo**. Sistemas tradicionais baseados apenas em Regex tendem a classificar números de processos (SEI), matrículas funcionais e inscrições imobiliárias erroneamente como telefones ou documentos pessoais.

Nossa solução utiliza uma **Abordagem Híbrida e Contextual**:
1.  **Regex de Alta Precisão:** Para padrões rígidos (CPF, E-mail).
2.  **NLP (Processamento de Linguagem Natural):** Utilizando `spaCy` para identificar nomes de pessoas, onde não há padrão numérico.
3.  **Análise de Contexto (Context Lookbehind):** Uma camada lógica que analisa as palavras *anteriores* a um número para decidir se ele é um dado sensível (ex: telefone) ou um dado público (ex: número de processo ou matrícula).

---

## 🚀 Funcionalidades Principais

* **Suporte Multi-Formato:** Aceita nativamente arquivos **.CSV** (com detecção automática de separador `;` ou `,`) e planilhas Excel (** .XLSX, .XLS**).
* **Execução Flexível:** Pode ser executado via linha de comando (CLI) ou em modo de detecção automática (varre a pasta).
* **Tratamento de Codificação:** Lida automaticamente com arquivos UTF-8 e Latin-1 (comuns em exportações de sistemas antigos).
* **Filtro de "Ruído" Corporativo:** Ignora e-mails institucionais genéricos (ex: `ouvidoria@`, `sac@`) para focar na proteção do cidadão.

---

## 🛠️ Instalação

### Pré-requisitos
* Python 3.9 ou superior.

### 1. Instalar Dependências
Execute o comando abaixo para instalar as bibliotecas necessárias (`pandas`, `spacy`, `openpyxl`):

```bash
pip install -r requirements.txt

```

### 2. Baixar o Modelo de NLP

A solução utiliza o modelo de linguagem em português do spaCy. Recomendamos a versão `large` (lg) para maior precisão na detecção de nomes próprios.

```bash
python -m spacy download pt_core_news_lg

```

*(O sistema fará fallback automático para o modelo `sm` caso o `lg` não esteja disponível).*

---

## 💻 Como Executar

A solução foi desenhada para ser flexível. Você pode rodar de duas formas:

### Modo 1: Detecção Automática (Mais Simples)

Basta colocar seu arquivo (CSV ou Excel) na mesma pasta do script e rodar. O sistema encontrará o arquivo automaticamente.

```bash
python main.py

```

### Modo 2: Linha de Comando (Avançado)

Ideal para integração com pipelines ou para especificar arquivos exatos.

```bash
python main.py --input "meu_arquivo.xlsx" --output "resultado_final.csv"

```

| Argumento | Descrição | Padrão |
| --- | --- | --- |
| `--input` | Caminho do arquivo de entrada (.csv ou .xlsx). | Automático (primeiro da pasta) |
| `--output` | Caminho para salvar o resultado. | `resultado_analise.csv` |

---

## 🧠 Detalhes da Implementação Técnica

Para fins de avaliação e futura incorporação ao ecossistema do GDF, detalhamos abaixo a lógica de cada componente:

### 1. Detecção de Telefones com "Context Lookbehind"

* **Problema:** Bases governamentais contêm muitos números de 8 ou 9 dígitos que não são telefones (Processos SEI, Matrículas, NIRE, Inscrições).
* **Solução:** Implementamos uma verificação que "olha para trás" no texto. Se o número for precedido por termos como *"Processo"*, *"Matrícula"* ou *"Inscrição"*, ele é **ignorado**.
* **Resultado:** Eliminação quase total de falsos positivos em pedidos técnicos.

### 2. Tratamento de E-mails (Blacklist Inteligente)

* **Lógica:** Nem todo e-mail é dado pessoal sensível. E-mails como `atendimento@empresa.com` ou `sic@df.gov.br` são públicos.
* **Solução:** O algoritmo verifica o prefixo do e-mail. Se contiver termos de serviço (`sac`, `noreply`, `admin`), não é marcado como restrito, aumentando a precisão da classificação.

### 3. Detecção de Nomes (NLP)

* **Lógica:** Regex não consegue distinguir "Maria Silva" de "Rua das Flores".
* **Solução:** Utilizamos o modelo de Entidades Nomeadas (NER) do `spaCy`. Filtramos a entidade `PER` (Pessoa) e aplicamos regras extras (ex: ignorar nomes com apenas 1 palavra) para garantir que estamos protegendo cidadãos reais.

---

## 📂 Estrutura do Projeto

* `main.py`: Código fonte principal contendo a classe `DataProtector` e lógica de execução.
* `requirements.txt`: Lista de dependências.
* `README.md`: Documentação do projeto.

---

## 🔮 Roadmap (Sugestão de Incorporação)

A classe `DataProtector` foi construída de forma modular. Para transformar esta solução em uma API (Microserviço) para o Participa DF, basta instanciar a classe e expor o método `.analyze_text(str)` via **FastAPI** ou **Flask**, permitindo validação em tempo real durante a digitação do cidadão.

## 🌟 Diferencial: API Rest (FastAPI)

Além do script de execução local, o projeto inclui uma **API Rest pronta para produção** (`api.py`), demonstrando como esta solução pode ser integrada a um portal como um microserviço.

### Funcionalidades da API:
1.  **POST /analisar_texto:** Recebe um JSON e valida em tempo real (útil para alertar o cidadão enquanto ele digita).
2.  **POST /analisar_arquivo:** Recebe upload de CSV/XLSX e retorna o relatório processado.

### Como testar a API (Opcional):
1. Instale o servidor: `pip install fastapi uvicorn python-multipart`
2. Rode: `uvicorn api:app --reload`
3. Acesse a documentação interativa: `http://127.0.0.1:8000/docs`