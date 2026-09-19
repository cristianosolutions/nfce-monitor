# Manual do Usuário — NFC-e Monitor

## 1. Finalidade

O NFC-e Monitor auxilia na conferência de NFC-e armazenadas em XML e permite consultar a situação fiscal de uma nota na SEFAZ/SVRS usando certificado digital A1.

## 2. Requisitos de uso

Tenha disponível:

- arquivos XML de NFC-e;
- certificado A1 `.pfx` ou `.p12`;
- senha do certificado;
- internet;
- autorização para utilizar o certificado e consultar os documentos.

## 3. Abrir o programa

Na versão instalada, abra **NFC-e Monitor** pelo Menu Iniciar ou atalho.

Em desenvolvimento:

```powershell
.\.venv\Scripts\Activate.ps1
python main.py
```

## 4. Analisar XMLs

1. Na seção **Arquivos XML**, clique em **Selecionar pasta**.
2. Escolha a pasta que contém os XMLs.
3. Clique em **Analisar XMLs**.
4. O programa também pesquisa subpastas.
5. Acompanhe a barra de progresso.
6. Aguarde a conclusão.

As NFC-e são deduplicadas pela chave de acesso de 44 dígitos.

## 5. Entender a tabela

- **Número:** número da NFC-e.
- **Série:** série fiscal.
- **Emissão:** data/hora.
- **CNPJ:** emitente.
- **Emitente:** estabelecimento.
- **Valor:** valor da nota.
- **Status XML:** situação encontrada localmente.
- **Situação SEFAZ:** resultado online.
- **cStat:** código fiscal retornado.
- **Protocolo:** protocolo associado.
- **Chave de acesso:** chave de 44 dígitos.

## 6. Pesquisa e filtros

O campo **Pesquisar** permite localizar informações como número, série, chave, CNPJ e emitente.

O filtro **Status XML** pode apresentar situações como:

```text
AUTORIZADA
CANCELADA
DENEGADA
REJEITADA / OUTRO
SEM PROTOCOLO
```

O filtro **Situação SEFAZ** possui:

```text
NÃO CONSULTADA
AUTORIZADA
CANCELADA
NÃO CONSTA
OUTRO
ERRO
```

Os filtros podem ser combinados.

## 7. Configurar o certificado

1. Clique em **Selecionar PFX**.
2. Escolha o `.pfx` ou `.p12`.
3. Digite a senha no campo **Senha**.
4. A senha ficará mascarada.

Nunca compartilhe o certificado e sua senha sem autorização.

## 8. Consultar uma NFC-e

1. Carregue os XMLs.
2. Selecione uma linha.
3. Selecione o PFX.
4. Informe a senha.
5. Clique em **Consultar SEFAZ**.
6. Aguarde.
7. Confira situação, cStat, motivo e protocolo.
8. A linha e os indicadores serão atualizados.

## 9. Status XML x SEFAZ

São informações diferentes.

Um cenário possível é:

```text
Status XML: AUTORIZADA
Situação SEFAZ: CANCELADA
```

Isso pode ocorrer quando o arquivo disponível é da autorização original, mas houve evento posterior.

## 10. Indicadores

Os cards mostram:

- NFC-e carregadas;
- SEFAZ autorizadas;
- SEFAZ canceladas;
- não consultadas;
- outros/erros.

## 11. Abrir o XML

Dê duplo clique em uma linha. Se o arquivo ainda existir no caminho original, ele será aberto pelo Windows.

## 12. Exportar Excel

1. Clique em **Exportar Excel**.
2. Escolha o destino.
3. Informe o nome.
4. Salve.

O relatório inclui dados locais e resultados SEFAZ disponíveis na sessão.

## 13. Se ocorrer erro

Verifique:

- conexão com internet;
- PFX selecionado;
- senha;
- validade do certificado;
- chave da NFC-e;
- disponibilidade do serviço fiscal.

## 14. Cuidados

- Não compartilhe PFX/senha.
- Não publique XMLs fiscais reais.
- Não altere XMLs originais.
- Mantenha backup dos documentos.
- Use a aplicação como apoio de conferência.

## 15. Ao encerrar

Na versão atual, resultados mantidos somente em memória podem ser perdidos ao fechar. Exporte para Excel quando precisar preservar o resultado da sessão. Persistência local está planejada para uma versão futura.
