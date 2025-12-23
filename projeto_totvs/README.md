# 🏭 Projeto Portal Manufatura (Integração TOTVS Protheus)

Sistema web desenvolvido em **Python (Flask)** para visualização e controle de Projetos, Células Robóticas e Produtos, integrado diretamente ao ERP **TOTVS Protheus**.

## 🚀 Funcionalidades

* **Autenticação Segura:** Login validado diretamente no Protheus (Basic Auth + OAuth2).
* **Gestão de Sessão:** Uso de Tokens JWT com Cookies seguros (`HttpOnly`).
* **Dashboards:** Visualização de status de produção (Necessidade vs. Entregue).
* **Integração SQL:** Consultas otimizadas diretamente no banco de dados do Protheus.
* **Auditoria:** Logs detalhados de todas as ações dos usuários e tentativas de acesso.

---

## 📋 Pré-requisitos

* Python 3.10 ou superior
* Acesso de rede ao servidor SQL Server e à API REST do Protheus
* Driver ODBC para SQL Server 17 ou superior

---

## ⚙️ Instalação

1.  **Clone ou baixe o projeto** para sua máquina.
2.  **Crie um ambiente virtual** (opcional, mas recomendado):
    ```bash
    python -m venv .venv
    # Windows:
    .venv\Scripts\activate
    # Linux/Mac:
    source .venv/bin/activate
    ```
3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

---

## 🔒 Configuração de Segurança (.env)

Este projeto utiliza variáveis de ambiente para proteger senhas. **Você deve criar um arquivo chamado `.env` na raiz do projeto** com o seguinte conteúdo:

```ini


▶️ Como Rodar
Com o ambiente ativado e as configurações feitas, execute:

Bash

python app.py
O sistema estará disponível em: 👉 http://localhost:5000

📂 Estrutura do Projeto
Plaintext

projeto_totvs/
├── controllers/       # Lógica de negócio (auth e projetos)
├── models/            # Acesso a dados (SQL e API Protheus)
├── static/            # Arquivos CSS, JS e Imagens
├── templates/         # Arquivos HTML (Login e Dashboard)
├── views/             # Rotas e Endpoints da API
├── app.py             # Arquivo principal de inicialização
├── config.py          # Carregamento das configurações do .env
├── requirements.txt   # Lista de bibliotecas Python
└── sistema.log        # Arquivo de log gerado automaticamente
🛠️ Tecnologias Utilizadas

Backend: Flask, PyODBC, Requests, PyJWT

Frontend: HTML5, CSS3, JavaScript (Fetch API)

Banco de Dados: Microsoft SQL Server

ERP: TOTVS Protheus (Microsiga)