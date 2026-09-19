Manual do Usuário — NFC-e Monitor

1. Finalidade

O NFC-e Monitor auxilia na conferência de NFC-e armazenadas em XML e permite consultar a situação fiscal de uma nota na SEFAZ/SVRS usando certificado digital A1.

2. Requisitos de uso

Tenha disponível:

arquivos XML de NFC-e;

certificado A1 .pfx ou .p12;

senha do certificado;

internet;

autorização para utilizar o certificado e consultar os documentos.

3. Abrir o programa

Na versão instalada, abra NFC-e Monitor pelo Menu Iniciar ou atalho.

Em desenvolvimento:

.\.venv\Scripts\Activate.ps1
python main.py

4. Analisar XMLs

Na seção Arquivos XML, clique em Selecionar pasta.

Escolha a pasta que contém os XMLs.

Clique em Analisar XMLs.

O programa também pesquisa subpastas.

Acompanhe a barra de progresso.

Aguarde a conclusão.

As NFC-e são deduplicadas pela chave de acesso de 44 dígitos.

5. Entender a tabela

Número: número da NFC-e.

Série: série fiscal.

Emissão: data/hora.

CNPJ: emitente.

Emitente: estabelecimento.

Valor: valor da nota.

Status XML: situação encontrada localmente.

Situação SEFAZ: resultado online.

cStat: código fiscal retornado.

Protocolo: protocolo associado.

Chave de acesso: chave de 44 dígitos.

6. Pesquisa e filtros

O campo Pesquisar permite localizar informações como número, série, chave, CNPJ e emitente.

O filtro Status XML pode apresentar situações como:

AUTORIZADA
CANCELADA
DENEGADA
REJEITADA / OUTRO
SEM PROTOCOLO

O filtro Situação SEFAZ possui:

NÃO CONSULTADA
AUTORIZADA
CANCELADA
NÃO CONSTA
OUTRO
ERRO

Os filtros podem ser combinados.

7. Configurar o certificado

Clique em Selecionar PFX.

Escolha o .pfx ou .p12.

Digite a senha no campo Senha.

A senha ficará mascarada.

Nunca compartilhe o certificado e sua senha sem autorização.

8. Consultar uma NFC-e

Carregue os XMLs.

Selecione uma linha.

Selecione o PFX.

Informe a senha.

Clique em Consultar SEFAZ.

Aguarde.

Confira situação, cStat, motivo e protocolo.

A linha e os indicadores serão atualizados.

9. Status XML x SEFAZ

São informações diferentes.

Um cenário possível é:

Status XML: AUTORIZADA
Situação SEFAZ: CANCELADA

Isso pode ocorrer quando o arquivo disponível é da autorização original, mas houve evento posterior.

10. Indicadores

Os cards mostram:

NFC-e carregadas;

SEFAZ autorizadas;

SEFAZ canceladas;

não consultadas;

outros/erros.

11. Abrir o XML

Dê duplo clique em uma linha. Se o arquivo ainda existir no caminho original, ele será aberto pelo Windows.

12. Exportar Excel

Clique em Exportar Excel.

Escolha o destino.

Informe o nome.

Salve.

O relatório inclui dados locais e resultados SEFAZ disponíveis na sessão.

13. Se ocorrer erro

Verifique:

conexão com internet;

PFX selecionado;

senha;

validade do certificado;

chave da NFC-e;

disponibilidade do serviço fiscal.

14. Cuidados

Não compartilhe PFX/senha.

Não publique XMLs fiscais reais.

Não altere XMLs originais.

Mantenha backup dos documentos.

Use a aplicação como apoio de conferência.

15. Ao encerrar

Na versão atual, resultados mantidos somente em memória podem ser perdidos ao fechar. Exporte para Excel quando precisar preservar o resultado da sessão. Persistência local está planejada para uma versão futura.