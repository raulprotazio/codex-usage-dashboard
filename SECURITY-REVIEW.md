# Revisão local — 9 de setembro de 2026

Base revisada: luyh7/codex-usage-dashboard,
commit `038d577c1bf55a5f138a025be58920f9cf7070e4`.

Revisão estática do servidor/parser Python, interface inline, APIs de importação
e scripts de inicialização/instalação. Não encontrei telemetria, envio automático
dos logs para serviços externos ou leitura de credenciais de autenticação do
Codex. A execução escolhida usa a biblioteca padrão do Python, sem instalar
dependências npm. Isso não é uma garantia de ausência de vulnerabilidades.

## Proteções adicionadas

- Servidor restrito a loopback; validação de Host e Origin e bloqueio de
  requisições cross-site. Escritas exigem JSON.
- Cabeçalhos contra framing, referer e carregamento de recursos externos.
  A interface original ainda exige scripts e estilos inline na CSP.
- Launcher próprio não encerra processos que ocupem a porta.
- Dados reais e configuração de máquina excluídos do Git.
- Importação SSH exige autenticação não interativa e host previamente conhecido.
  O destino é validado; somente nosso código é executado, nunca conteúdo dos logs.

## Compatibilidade

Corrigidos IDs de arquivo/dispositivo do Windows maiores que o INTEGER do SQLite,
estatísticas incompletas de DirEntry no Windows e otimização de leitura de CRLF.
IDs são armazenados como bytes decimais e reconstruídos sem perda de precisão.
Os testes também fecham conexões SQLite explicitamente e usam datas locais
quando o cenário é um filtro de calendário local.

## Limites

Validação: leitura real combinada de sessões Windows e de um snapshot SSH Ubuntu.
Os dois testes novos (barreira de origem HTTP e IDs de arquivo de 128 bits)
passaram. Na última execução da suíte completa: 89 testes, 87 passaram, 1 foi
ignorado e 1 falhou (`test_snapshot_token_keeps_list_and_detail_consistent`).
Também ocorreram falhas intermitentes de invalidação de cache em reescritas
muito rápidas de arquivos durante outras execuções no Windows. Não se declara
a suíte completamente aprovada; esse comportamento exige investigação adicional.
O reinício do servidor de verificação foi bloqueado pelo ambiente de execução,
portanto a interface servindo a última revisão ainda precisa ser verificada.

Qualquer programa executado como o mesmo usuário pode acessar o serviço local.
Caches e snapshots contêm informações privadas; não os compartilhe. A inspeção
cobre este commit e as mudanças do fork, não futuras atualizações do upstream.
O instalador npm original pode substituir skills existentes; ele não foi usado.
As estimativas financeiras e a atribuição de todos os formatos de logs não são
garantidas por esta revisão de segurança.
