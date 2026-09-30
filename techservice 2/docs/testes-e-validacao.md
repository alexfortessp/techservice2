# Plano de testes e validação

## Automatizados

Na aba Terminal do Codespace, execute:

`python -m unittest discover -s tests -v`

Foram preparados 15 testes cobrindo dados obrigatórios, edição de cliente, vínculo de equipamento, dinheiro, persistência, aprovação, entrega, histórico, mudanças de orçamento aprovado, acesso privado, login incorreto, CSRF, cadastro HTTP, relatório e escape HTML.

Resultado esperado: os testes listados terminam com `OK`. Resultado real: ainda não executado nesta preparação. Registre data, ambiente e saída real antes de declarar aprovação.

## Manual — preencher após executar

| Teste | Ação | Resultado esperado | Resultado real |
|---|---|---|---|
| M01 | Entrar com credenciais corretas | Painel abre | Pendente |
| M02 | Cadastrar e editar cliente | Alteração aparece na lista | Pendente |
| M03 | Cadastrar equipamento | Cliente aparece vinculado | Pendente |
| M04 | Abrir OS | Número e histórico são criados | Pendente |
| M05 | Registrar diagnóstico e orçamento | Dados aparecem ao reabrir | Pendente |
| M06 | Reparo sem aprovação | Mens