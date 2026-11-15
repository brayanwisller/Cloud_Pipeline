# Cloud Tasks API — Pipeline CI/CD e Deploy na AWS

API REST desenvolvida em Python com **Flask** para gestão de tarefas (CRUD), conteinerizada com **Docker** e implantada de forma automatizada numa instância **AWS EC2 (Ubuntu)** através de pipelines de **CI/CD no GitHub Actions**.

## Integrantes do Grupo

| Nome Completo | RA | 
| ----- | ----- | 
| Brayan Wisller | 22303778 | 
| Lucas Araújo de Paula | 22300800 | 
| Matheus de Tassi Alves Fagundes Gomes | 22308947 | 

## Arquitetura e Tecnologias

* **Linguagem & Framework:** Python 3.11 + Flask

* **Servidor WSGI:** Gunicorn (exposto na porta `8000`)

* **Testes Automatizados:** Pytest (`tests/test_api.py`)

* **Conteinerização:** Docker (imagem publicada no GitHub Container Registry - GHCR)

* **Persistência de Dados:** Armazenamento em ficheiro JSON (`data/tasks.json`) mapeado via volume nomeado do Docker (`cloud-tasks-data:/app/data`), garantindo que os dados sobrevivam ao reinício ou recriação do contentor.

* **CI/CD:** GitHub Actions:

  * **CI (`ci.yml`):** Executa os testes unitários e valida o build da imagem Docker em Pull Requests e pushes na `main`. Publica a imagem no GHCR após merges na `main`.

  * **CD (`cd.yml`):** Aguarda a conclusão com sucesso da CI, liga-se via SSH à instância AWS EC2, executa o script `scripts/deploy.sh` para atualizar o contentor com a imagem imutável e valida o endpoint `/health`.

* **Infraestrutura Cloud:** AWS EC2 (`t3.micro`) com Security Group configurado para acesso HTTP na porta `8000` e SSH restrito.

## Estrutura do Projeto

```
Cloud_Pipeline/
├── .github/workflows/
│   ├── ci.yml                # Pipeline de Integração Contínua e publicação de imagem
│   └── cd.yml                # Pipeline de Entrega Contínua via SSH na EC2
├── app/
│   └── main.py               # Código principal da API Flask e lógica de persistência
├── scripts/
│   ├── deploy.sh             # Script executado na EC2 para atualizar o contentor
│   └── setup-ec2-ubuntu.sh   # Script de provisionamento inicial do Docker na EC2
├── tests/
│   └── test_api.py           # Suíte de testes automatizados com Pytest
├── Dockerfile                # Definição da imagem Docker de produção
├── compose.yaml              # Orquestração local com Docker Compose
├── pytest.ini                # Configurações do Pytest
├── requirements.txt          # Dependências de produção (Flask, Gunicorn)
└── requirements-dev.txt      # Dependências de desenvolvimento/testes (Pytest)

```

## Endpoints Disponíveis

| Método | Rota | Descrição | 
| ----- | ----- | ----- | 
| `GET` | `/health` | Verifica o estado de saúde da API (usado pelo *health check* do deploy). | 
| `GET` | `/tasks` | Lista todas as tarefas registadas (suporta filtro por status, se aplicável). | 
| `POST` | `/tasks` | Cria uma nova tarefa. | 
| `GET` | `/tasks/<id>` | Obtém os detalhes de uma tarefa específica. | 
| `PUT` | `/tasks/<id>` | Atualiza os dados ou o estado de uma tarefa existente. | 
| `DELETE` | `/tasks/<id>` | Remove uma tarefa do sistema. | 

## Como Executar Localmente

### 1. Via Python (Ambiente Virtual)

```
# Instalar dependências
pip install -r requirements.txt -r requirements-dev.txt

# Executar os testes automatizados
python -m pytest -q

# Iniciar a aplicação localmente
python -m flask --app app.main run --port 8000

```

### 2. Via Docker

```
# Construir a imagem
docker build -t cloud-tasks-api .

# Executar o contentor com persistência de dados
docker run -d \
  --name cloud-tasks-api \
  -p 8000:8000 \
  -v cloud-tasks-data:/app/data \
  -e DATA_DIR=/app/data \
  cloud-tasks-api

```

A API estará acessível em `http://localhost:8000/health`.