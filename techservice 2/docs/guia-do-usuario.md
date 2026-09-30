# TechService — Guia do usuário

## 1. Identificação e finalidade

Projeto acadêmico da disciplina Prática Profissional em Análise e Desenvolvimento de Sistemas. Primeira iteração da fase de construção. O sistema centraliza clientes, equipamentos e ordens de serviço de uma assistência técnica.

Os integrantes e o endereço real da aplicação devem ser informados pelo grupo no envio. Esta versão fornece acesso a um único funcionário de demonstração; não implementa perfis separados.

## 2. Acesso

Abra o endereço HTTPS encaminhado pela porta 8000 do Codespace, após o grupo iniciar o ambiente. Credenciais iniciais de demonstração: usuário **admin**, senha **TechService123!**. São credenciais públicas do projeto, não uma senha pessoal. Use somente dados fictícios. O administrador pode definir `ADMIN_USER` e `ADMIN_PASSWORD` no ambiente antes de iniciar o servidor.

Para disponibilizar o endereço a quem não está autenticado no GitHub, configure a porta como pública, se permitido pela conta. O sistema não funciona no GitHub Pages. Ele fica indisponível se o Codespace parar ou expirar.

## 3. Painel inicial

O painel mostra quantidades de clientes, equipamentos e OS, contadores por status e as últimas ordens. Os menus superiores dão acesso a Clientes, Equipamentos e Ordens. Sair encerra a sessão. O relatório CSV reúne todas as OS.

## 4. Clientes

Entre em Clientes. Preencha Nome (obrigatório), Telefone e E-mail (opcionais) e clique em Salvar cliente. A lista permite busca por nome ou contato. Para corrigir dados, clique em Editar, altere os campos e salve. Nomes repetidos são permitidos; confira os contatos antes de abrir uma OS.

## 5. Equipamentos

Entre em Equipamentos. Selecione um cliente já cadastrado, informe Tipo (obrigatório), Marca/modelo e Número de série (opcionais). Clique em Cadastrar equipamento. A lista apresenta o proprietário de cada equipamento. Nesta iteração não há edição ou exclusão de equipamentos.

## 6. Abrir uma OS

Entre em Ordens e clique em Nova OS. Selecione cliente/equipamento, descreva o defeito relatado e informe o nome do técnico, se conhecido. Clique em Abrir ordem de serviço. O sistema gera o número da OS, registra data/hora em UTC e abre o acompanhamento.

## 7. Consultar e acompanhar

Na lista de Ordens, pesquise por número, cliente, equipamento ou defeito. O filtro de status pode ser combinado com a pesquisa. Clique em Abrir para ver a ordem. Informe técnico, diagnóstico e orçamento total em reais. A versão usa valor total, sem detalhamento de peças e serviços.

A decisão do cliente é registrada pelo funcionário como Pendente, Aprovado ou Recusado. Não há portal do cliente. Salve a alteração pelo botão Salvar acompanhamento.

Estados disponíveis: Aberta; Em diagnóstico; Aguardando aprovação; Em reparo; Concluída; Entregue; Cancelada. Reparo, conclusão e entrega exigem diagnóstico, técnico e aprovação. Para entregar, primeiro salve como Concluída; depois salve como Entregue. OS Entregue ou Cancelada não pode ser alterada. Orçamento ou diagnóstico modificado após aprovação exige nova decisão: salve Pendente em estado compatível, antes de registrar nova aprovação.

## 8. Histórico e relatórios

O histórico registra abertura e alterações de técnico, diagnóstico, orçamento, aprovação e status. As datas são UTC. O relatório CSV pode ser aberto em uma planilha; contém número da OS, cliente, equipamento, status, decisão, orçamento, técnico e abertura. Ele exporta todas as OS, independentemente do filtro da lista.

Em uma OS, Imprimir / salvar em PDF abre a impressão do navegador para obter uma ficha. Dados não salvos no formulário não representam registro oficial: salve antes de imprimir.

## 9. Exemplo de uso

1. Cadastre Cliente Demonstração, com telefone fictício.
2. Cadastre Notebook, marca Modelo Demonstração, série DEMO001.
3. Abra OS com defeito Não liga e técnico Técnico Demonstração.
4. Registre diagnóstico Fonte danificada, orçamento 150,00, aprovação Pendente e status Aguardando aprovação. Salve.
5. Registre Aprovado e Em reparo. Salve.
6. Registre Concluída. Salve.
7. Registre Entregue. Salve.
8. Consulte histórico e baixe relatório.

## 10. Armazenamento e resolução de problemas

O banco SQLite é criado automaticamente em `instance/techservice.sqlite3`. Fechar a aba não apaga dados. Parar e reabrir o mesmo Codespace preserva o diretório; excluir ou reconstruir sem preservar esse diretório pode perder dados. Antes de excluir, faça uma cópia do banco com o servidor parado. Cada novo Codespace tem um banco próprio.

Se aparecer formulário expirado, atualize a página e tente novamente. Se uma validação impedir salvar, leia a mensagem, corrija os campos e repita. Se a URL não responder, confirme que o Codespace está ativo e que o processo da porta 8000 está funcionando. Se a URL pedir login no GitHub, confira a visibilidade pública da porta.

## 11. Limites da entrega

A publicação e os testes devem ser realizados pelo grupo. O pacote contém testes, mas não comprova que foram executados. Acesso temporário por Codespaces não garante disponibilidade contínua para avaliação. O vídeo de oito minutos solicitado no enunciado continua pendente. A rubrica completa e o escopo aprovado pelo professor não foram verificados nesta preparação.
