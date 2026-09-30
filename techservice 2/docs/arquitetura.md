# Arquitetura — Iteração 1

Aplicação web em camadas, derivada da arquitetura proposta na elaboração.

`Navegador -> Controller Flask -> Service -> Repository -> SQLite`

## Implementação

- Interface: HTML/CSS e templates Jinja, em `frontend/templates/app.html`.
- Controller: rotas e autenticação em `backend/controller.py`.
- Service: regras de negócio em `backend/service.py`.
- Repository: transações e SQL parametrizado em `backend/repository.py`.
- Banco: arquivo `instance/techservice.sqlite3`, criado automaticamente na primeira inicialização.
- Servidor WSGI: Gunicorn, porta interna 8000.

## Implantação para demonstração

GitHub armazena o código. GitHub Codespaces executa o servidor Python em um ambiente remoto. O encaminhamento da porta 8000 fornece uma URL HTTPS para o navegador. Para compartilhar com o professor sem autenticação no GitHub, o proprietário deve configurar essa porta como pública, se a conta permitir.

O SQLite reside no sistema de arquivos do Codespace, fora do controle de versão. Não é um banco compartilhado entre Codespaces: cada ambiente tem os próprios dados. Excluir o ambiente apaga os dados. Parar o ambiente interrompe o site. Não equivale a uma hospedagem permanente.

## Segurança e limites

Senhas verificadas por hash, sessão com segredo persistente, formulários protegidos contra CSRF, HTML com escape automático, consultas parametrizadas e mitigação de fórmulas na exportação CSV. Conta única de demonstração; sem perfis de autorização separados, sem proteção dedicada contra tentativas repetidas de login e sem política automatizada de backup. Não usar em produção nem inserir dados pessoais reais.

Não há dependência de serviços externos para o front-end. A instalação inicial baixa dependências Python e a imagem do ambiente remoto.
