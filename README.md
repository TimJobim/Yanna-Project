# 📊 Sistema de Monitoramento de Feminicídios // CE

Um sistema web interativo desenvolvido com **Streamlit** para o monitoramento, extração de dados e análise espacial de casos de feminicídio no estado do Ceará. A ferramenta processa textos não estruturados (como notícias ou boletins de ocorrência) e os transforma em painéis analíticos para direcionamento de políticas públicas.

## ✨ Funcionalidades

* **Smart Extractor (Regex):** Extração automatizada de dados a partir de textos brutos, identificando: Data, Município, Idade (números ou por extenso), Cor da Pele e Motivação/Causa do crime.
* **Mapeamento Geopolítico:** Classificação automática dos municípios nas **14 Regiões de Planejamento do IPECE**.
* **Entrada Multimodal:** Suporte para análise em lote via upload de arquivos `.CSV`, inserção de texto manual ou **Gravação de Áudio (Voice-to-Text)**.
* **🚨 Sistema de Alerta de Políticas Públicas:** Cálculo automático do **Índice de Concentração Regional (ICR)**. O sistema identifica as zonas de maior risco e sugere diretrizes de intervenção primária (ex: implantação de Delegacia da Mulher ou Patrulha Maria da Penha).
* **Dashboard Interativo:** Geração de gráficos dinâmicos com *Plotly* (Distribuição de Causas, Evolução Temporal, Demografia e Ranking de Cidades).
* **Exportação de Dados:** Download dos relatórios processados em formatos `.CSV` e `.XLSX`.

## 🛠️ Tecnologias Utilizadas

* **Linguagem:** Python 3.x
* **Interface Web:** Streamlit
* **Processamento de Dados:** Pandas, RegEx (Expressões Regulares)
* **Visualização:** Plotly Express
* **Recursos de Áudio:** `streamlit-mic-recorder`

## 🚀 Como Executar o Projeto

### 1. Pré-requisitos
Certifique-se de ter o Python instalado. Em seguida, instale as bibliotecas necessárias executando o comando abaixo no seu terminal:

```bash
pip install streamlit pandas plotly streamlit-mic-recorder XlsxWriter
