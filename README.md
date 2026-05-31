# 🚀 Automação Excel & Sheets -> ClickUp

Este repositório contém uma solução modular em Python focada em automação de processos, engenharia de dados e integração de sistemas. O objetivo principal é extrair informações de planilhas (locais e em nuvem), tratá-las com o suporte de Inteligência Artificial (API do Gemini) e gerenciar de forma automatizada o fluxo de tarefas no **ClickUp**.

O projeto foi desenhado de forma incremental, evoluindo de scripts locais simples até integrações de APIs em fluxo bidirecional.

---

## 🛠️ Tecnologias e Ferramentas

* **Python 3.14**
* **Pandas** (Manipulação e limpeza de dados)
* **Google Generative AI SDK** (Processamento de linguagem natural com Gemini)
* **Requests** (Consumo de APIs REST)
* **ClickUp API v2** (Gerenciamento de workspaces e tasks)

---

## ⚙️ Como Configurar o Ambiente

1. **Clonar o repositório:**

    ```bash
    git clone https://github.com/seu-usuario/seu-repositorio.git
    cd seu-repositorio
    ```
2. **Criar e ativar o ambiente virtual (opcional, mas recomendado)**

    ```bash
    python -m venv venv
    # No Windows:
    .\venv\Scripts\activate
    # No Mac/Linux:
    source venv/bin/activate
    ```

3. **Instalar as dependências:**

    ```bash
    pip install pandas openpyxl google-generativeai requests
    ```
    
4. **Variáveis de Ambiente:**
    
    Certifique-se de configurar suas chaves de acesso antes de rodar os scripts:
    
    - `GEMINI_API_KEY` (Obtida no Google AI Studio)
    - `CLICKUP_TOKEN` (Seu Personal Token do ClickUp)
    - `CLICKUP_LIST_ID` (O ID da lista alvo no ClickUp)

## 🗺️ Roadmap de Desenvolvimento

Abaixo está o plano de evolução do projeto. Sinta-se à vontade para acompanhar o progresso:

- [x]  **Fase 1:** Extração e limpeza simples de arquivos Excel (`.xlsx`) localizados diretamente na pasta do projeto.
- [ ]  **Fase 2:** Varredura automática de uma pasta local para extração e limpeza de múltiplos arquivos, conectando com a API do ClickUp para inserção das tarefas no Board.
- [ ]  **Fase 3:** Migração para nuvem. Extração e tratamento de dados diretamente do Google Sheets via API oficial do Google e inserção automatizada no ClickUp.
- [ ]  **Fase 4 (Fluxo Reverso):** Sincronização reversa. Monitorar o Board do ClickUp e exportar/atualizar as informações das tarefas de volta para o Google Sheets.