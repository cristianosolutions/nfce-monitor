# Guia da Interface — NFC-e Monitor

Este documento apresenta os principais campos e recursos da interface
do **NFC-e Monitor**.

O sistema foi desenvolvido para auxiliar na leitura e conferência de
arquivos XML de NFC-e e permitir a consulta da situação fiscal dos
documentos na SEFAZ/SVRS utilizando certificado digital A1.

---

## Tela inicial

![Tela inicial do NFC-e Monitor](images/tela-inicial.jpg)

A tela principal concentra as funções de carregamento dos XMLs,
consulta à SEFAZ, pesquisa, filtros e exportação dos resultados.

---

## 1. Arquivos XML

### Pasta dos XMLs

Exibe o diretório que contém os arquivos XML que serão analisados.

O botão **Selecionar pasta** abre uma janela para escolher a pasta
onde estão armazenados os documentos fiscais.

### Analisar XMLs

Após selecionar a pasta, clique em **Analisar XMLs**.

O NFC-e Monitor percorre os arquivos XML encontrados, interpreta
os documentos e apresenta os resultados na tabela principal.

---

## 2. Consulta SEFAZ / Certificado A1

Esta área é utilizada para consultar a situação atual de uma NFC-e
diretamente no serviço da SEFAZ/SVRS.

### Certificado PFX

Exibe o caminho do certificado digital A1 utilizado para autenticação.

O certificado deve estar no formato:

- `.pfx`
- `.p12`

Utilize o botão **Selecionar PFX** para localizar o certificado no
computador.

> **Segurança:** certificados digitais, chaves privadas e senhas não
> devem ser armazenados no repositório GitHub.

### Senha

Campo destinado à senha do certificado digital.

Os caracteres são ocultados durante a digitação.

### Consultar SEFAZ

Selecione uma NFC-e na tabela e clique em **Consultar SEFAZ**.

O sistema utiliza a chave de acesso da NFC-e selecionada para consultar
sua situação fiscal.

---

## 3. Indicadores

A parte superior da aplicação apresenta cinco indicadores.

### NFC-e carregadas

Quantidade total de NFC-e identificadas durante a análise dos XMLs.

### SEFAZ autorizadas

Quantidade de documentos consultados cuja situação retornada pela
SEFAZ foi **AUTORIZADA**.

### SEFAZ canceladas

Quantidade de documentos cuja consulta identificou situação de
cancelamento.

### Não consultadas

Quantidade de NFC-e carregadas que ainda não foram consultadas
na SEFAZ durante a execução atual.

### Outros / erros

Quantidade de consultas que retornaram outra situação ou apresentaram
erro durante o processamento.

---

## 4. Pesquisa e filtros

### Pesquisar

Permite localizar documentos entre os registros carregados.

### Status XML

Filtra os registros de acordo com a situação encontrada no próprio
arquivo XML.

Exemplos:

- AUTORIZADA
- CANCELADA
- DENEGADA
- REJEITADA / OUTRO
- SEM PROTOCOLO

### Situação SEFAZ

Filtra os documentos conforme o resultado obtido na consulta online.

Exemplos:

- NÃO CONSULTADA
- AUTORIZADA
- CANCELADA
- NÃO CONSTA
- OUTRO
- ERRO

### Limpar filtros

Remove os filtros aplicados e volta a apresentar todos os registros.

---

## 5. Tabela de NFC-e

A tabela principal apresenta os documentos encontrados.

| Campo | Descrição |
|---|---|
| Número | Número da NFC-e |
| Série | Série do documento fiscal |
| Emissão | Data e hora de emissão |
| CNPJ | CNPJ do emitente |
| Emitente | Nome do estabelecimento emitente |
| Valor | Valor total da NFC-e |
| Status XML | Situação registrada no arquivo XML |
| Situação SEFAZ | Situação encontrada na consulta online |
| cStat | Código de status retornado pela SEFAZ |
| Protocolo | Número do protocolo relacionado ao documento |
| Chave de acesso | Chave de acesso de 44 dígitos da NFC-e |

---

## 6. Status XML × Situação SEFAZ

É importante diferenciar essas duas informações.

**Status XML** representa a situação encontrada no arquivo armazenado
localmente.

**Situação SEFAZ** representa o resultado da consulta realizada no
serviço fiscal.

Por isso, o XML local não deve ser considerado sozinho como garantia
da situação fiscal atual do documento.

---

## 7. Abrir o XML

Ao dar **duplo clique** sobre uma NFC-e da tabela, o NFC-e Monitor
tenta abrir o arquivo XML correspondente utilizando o programa
associado ao formato XML no sistema operacional.

---

## 8. Exportar Excel

O botão **Exportar Excel** gera uma planilha `.xlsx` com os registros
processados pelo NFC-e Monitor.

O usuário escolhe o local onde o relatório será salvo.

---

## 9. Barra de progresso e status

Na parte inferior da aplicação existe uma barra utilizada para
acompanhar o processamento dos arquivos.

Ao lado também são apresentadas mensagens sobre a operação atual,
incluindo o resultado das consultas realizadas na SEFAZ.

---

