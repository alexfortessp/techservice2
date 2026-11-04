# TechService

Sistema web de gerenciamento de ordens de serviço para assistências técnicas. Centraliza clientes, equipamentos, diagnósticos, orçamentos e o acompanhamento de cada ordem de serviço (OS), do recebimento do equipamento até a entrega.

Projeto da disciplina **Prática Profissional em Análise e Desenvolvimento de Sistemas** — Universidade Presbiteriana Mackenzie.

**Versão:** Iteração 2 da construção (tag `v2`).

---

## Tecnologias

- **Python 3 + Flask** — interface web e controle das requisições
- **SQLite** — banco de dados relacional (arquivo criado automaticamente)
- **Jinja + HTML/CSS** — telas do sistema
- **Gunicorn** — servidor WSGI opcional (somente Linux/macOS)

## Estrutura do repositório

```
techservice 2/
├── app.py                  # ponto de entrada da aplicação
├── requirements.txt        # dependências Python
├── start.sh                # inicialização com Gunicorn em segundo plano (usado no Codespaces)
├── backend/
│   ├── controller.py       # rotas HTTP, sessão de acesso e proteção CSRF
│   ├── service.py          # validações e regras de negócio
│   └── repository.py       # consultas parametrizadas e persistência no SQLite
├── frontend/templates/     # telas do sistema
├── tests/test_app.py       # testes automatizados
└── docs/                   # requisitos, casos de uso, arquitetura, backlog e guia do usuário
```

> **Atenção:** a pasta do projeto se chama `techservice 2`, com espaço no nome. Nos comandos, use aspas: `cd "techservice 2"`.

---

## Como executar no seu computador

### 1. Pré-requisitos

- **Python 3.9 ou superior.** Confira com `python3 --version` (Linux/macOS) ou `python --version` (Windows). No Windows, ao instalar o Python, marque a opção *Add Python to PATH*.
- **Git**, para clonar o repositório.
- Um navegador moderno (Chrome, Edge ou Firefox).

### 2. Clonar o repositório

```bash
git clone https://github.com/alexfortessp/techservice2.git
cd techservice2
git checkout v2
cd "techservice 2"
```

O comando `git checkout v2` posiciona o código exatamente na versão entregue na Iteração 2. O Git vai avisar que você está em *detached HEAD*; isso é esperado e não atrapalha a execução.

### 3. Criar e ativar um ambiente virtual

**Linux / macOS**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows (PowerShell)**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Se o PowerShell bloquear a ativação, rode antes `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` e tente de novo.

**Windows (Prompt de Comando)**

```bat
python -m venv .venv
.venv\Scripts\activate.bat
```

Com o ambiente ativado, o terminal mostra `(.venv)` no início da linha.

### 4. Instalar as dependências

```bash
pip install -r requirements.txt
```

### 5. Iniciar a aplicação

**Opção A — qualquer sistema operacional (recomendada para desenvolvimento)**

```bash
python app.py
```

**Opção B — Linux/macOS com Gunicorn**

```bash
gunicorn --bind 127.0.0.1:8000 app:app
```

Nas duas opções, abra no navegador: **http://localhost:8000**

Para parar o servidor, pressione `Ctrl + C` no terminal.

> O script `start.sh` foi feito para o GitHub Codespaces: ele inicia o Gunicorn em segundo plano e grava o log em `.server.log`. Para uso local, prefira as opções A ou B.

### 6. Entrar no sistema

Credenciais de demonstração (públicas, do próprio projeto):

| Usuário | Senha |
|---|---|
| `admin` | `TechService123!` |

Para usar outras credenciais, defina as variáveis de ambiente **antes** de iniciar o servidor:

**Linux / macOS**

```bash
export ADMIN_USER="meu_usuario"
export ADMIN_PASSWORD="minha_senha"
```

**Windows (PowerShell)**

```powershell
$env:ADMIN_USER="meu_usuario"
$env:ADMIN_PASSWORD="minha_senha"
```

Opcionalmente, defina também `SECRET_KEY`. Se ela não for definida, a aplicação gera uma chave automaticamente e a guarda em `instance/.session-secret`.

### 7. Banco de dados

O banco SQLite é criado automaticamente na primeira execução, no arquivo `techservice 2/instance/techservice.sqlite3`. Não é preciso instalar nem configurar nenhum servidor de banco.

Para conferir por consulta direta que um cadastro feito pela aplicação foi gravado, rode (na pasta `techservice 2`):

```bash
python -c "import sqlite3; print(sqlite3.connect('instance/techservice.sqlite3').execute('SELECT id, name FROM clients').fetchall())"
```

Para começar com o banco vazio, pare o servidor e apague a pasta `instance`.

### 8. Executar os testes automatizados

Na pasta `techservice 2`, com o ambiente virtual ativado:

```bash
python -m unittest discover -s tests -v
```

---

## Uso rápido

1. Faça login.
2. Em **Clientes**, cadastre um cliente.
3. Em **Equipamentos**, cadastre um equipamento vinculado a esse cliente.
4. Em **Ordens → Nova OS**, abra uma ordem de serviço informando o defeito relatado.
5. Abra a OS e registre técnico, diagnóstico, orçamento e a decisão do cliente.
6. Atualize o status até **Concluída** e depois **Entregue**.
7. Baixe o relatório CSV com todas as ordens.

O passo a passo completo está em [`techservice 2/docs/guia-do-usuario.md`](techservice%202/docs/guia-do-usuario.md).

## Problemas comuns

| Problema | Solução |
|---|---|
| `python` ou `python3` não é reconhecido | Instale o Python 3.9+ e, no Windows, marque *Add Python to PATH*. No macOS/Linux, use `python3`. |
| `No module named flask` | O ambiente virtual não está ativado ou as dependências não foram instaladas. Repita os passos 3 e 4. |
| Porta 8000 já está em uso | Encerre o outro processo ou rode em outra porta: `flask --app app run --port 5000` e acesse http://localhost:5000. |
| Gunicorn não funciona no Windows | O Gunicorn não é compatível com Windows. Use a opção A (`python app.py`). |
| Mensagem "Formulário expirado" | Atualize a página e envie o formulário novamente. |
| Usuário ou senha incorretos | Confira as credenciais da seção 6 e se as variáveis `ADMIN_USER`/`ADMIN_PASSWORD` foram alteradas. |

## Documentação do projeto

- [Requisitos](techservice%202/docs/requisitos.md)
- [Casos de uso](techservice%202/docs/casos-de-uso.md)
- [Arquitetura](techservice%202/docs/arquitetura.md)
- [Backlog](techservice%202/docs/backlog.md)
- [Guia do usuário](techservice%202/docs/guia-do-usuario.md)
- [Testes e validação](techservice%202/docs/testes-e-validacao.md)

## Controle de versão

- `main` — branch principal do repositório
- `iteracao2` — branch usado no desenvolvimento da Iteração 2
- Tag `v1` — código entregue na Iteração 1 da construção
- Tag `v2` — código entregue na Iteração 2 da construção

## Autores

Alexandre Eliezer Fortes e Ramon Henrique de Godoy
