# Execução local deste fork

Mantém a interface, parser, agrupamentos, filtros e snapshots do projeto original.
Não precisa de npm, Vite, serviço de nuvem ou instalação de skill. Requer Python
compatível com o projeto (validado com Python 3.12 no Windows) e, para importar
outro computador, OpenSSH e Python 3 nesse computador.

1. Copie `local-config.example.json` para `local-config.json`.
2. Ajuste o executável Python e o destino SSH no arquivo local.
3. No PowerShell, execute `./start-local.ps1`.
4. Acesse http://127.0.0.1:8765/.

Para atualizar também o Ubuntu antes de abrir:

```powershell
./start-local.ps1 -SyncUbuntu
```

Para executar em primeiro plano e encerrar com Ctrl+C:

```powershell
python scripts/local_dashboard.py
```

O Windows é lido diretamente das origens locais descobertas pelo projeto.
O Ubuntu aparece como dispositivo remoto, com o rótulo Ubuntu, usando o snapshot
nativo. A atualização SSH é manual neste estágio; não há novo agendamento.
O adaptador usa autenticação SSH já configurada, exige chave do host conhecida,
executa o parser revisado via stdin e não instala arquivos no Ubuntu.

Os logs originais são somente leitura. Cache SQLite, snapshots e logs do servidor
ficam em `local-data/`. Essa pasta e `local-config.json` estão no `.gitignore`.
O cache pode conter títulos, trechos de conversas e caminhos locais; não publique
essa pasta. Snapshots SSH omitem os campos de prompt inicial e prévia da resposta,
mas ainda contêm metadados e títulos. Não são dados anônimos.

Este fork utiliza os filtros e o histórico completos do upstream. Não importa
automaticamente as seleções de tarefas nem a data de corte do dashboard anterior.
Também não altera nem desativa o coletor anterior.

O servidor escuta apenas em loopback. O launcher verifica a versão em execução
e recusa reutilizar uma versão antiga. Não encerra processos automaticamente;
feche a instância anterior antes de atualizar. Mantenha este serviço local.

Os custos exibidos são estimativas segundo as tabelas do projeto, não uma fatura
da assinatura Codex. Esta adaptação não constitui nova auditoria das tarifas.
