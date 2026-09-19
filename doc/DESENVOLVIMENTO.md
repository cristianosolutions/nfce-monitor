Histórico de Desenvolvimento — NFC-e Monitor

1. Origem

O projeto começou como um leitor de XMLs de NFC-e para conferir grandes quantidades de documentos. A necessidade evoluiu quando se percebeu que o XML local não garante, sozinho, a situação fiscal atual.

Princípio central:

XML local ≠ necessariamente situação fiscal atual

2. Ambiente Python

O Windows possuía múltiplos Pythons. Foi adotado Python 3.12 com .venv.

py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
where.exe python

Com o ambiente ativo, o Python da .venv deve ter prioridade.

3. Leitura dos XMLs

Foi criado app/xml_reader.py com ElementTree e o namespace fiscal:

{"nfe": "http://www.portalfiscal.inf.br/nfe"}

O leitor passou a extrair chave, número, série, modelo, emissão, CNPJ, emitente, fantasia, valor, protocolo, cStat e motivo.

4. Eventos

O leitor passou a reconhecer eventos, especialmente:

tpEvento = 110111

relacionado ao cancelamento.

A interpretação foi mantida conservadora para evitar classificação fiscal incorreta.

5. Grandes volumes

Para evitar travamento do Tkinter foram usados:

threading.Thread
queue.Queue
root.after

Foram realizados testes com aproximadamente 62 mil documentos e posteriormente mais de 54 mil registros na interface.

6. Deduplicação

A chave de acesso de 44 dígitos foi escolhida como identificador. O número nNF isolado não é suficiente.

7. Consulta online

A ausência de eventos locais mostrou a necessidade de consultar a SEFAZ para separar:

Status XML
Situação SEFAZ

8. Certificado A1

certificado_service.py utiliza cryptography para abrir PFX/P12.

Como requests não utiliza diretamente o PFX da forma necessária, certificado e chave são extraídos para PEMs temporários, utilizados na conexão e apagados no finally.

9. TLS

Um erro de cadeia de certificados foi resolvido com:

import truststore
truststore.inject_into_ssl()

Não foi usado verify=False.

10. SOAP/SVRS

Namespace:

http://www.portalfiscal.inf.br/nfe/wsdl/NFeConsultaProtocolo4

SOAPAction:

http://www.portalfiscal.inf.br/nfe/wsdl/NFeConsultaProtocolo4/nfeConsultaNF

Um teste no endpoint de NF-e retornou cStat 450, evidenciando que aquele serviço esperava modelo 55.

O endpoint adotado para NFC-e foi:

https://nfce.svrs.rs.gov.br/ws/NfeConsulta/NfeConsulta4.asmx

11. Payload

<consSitNFe xmlns="http://www.portalfiscal.inf.br/nfe" versao="4.00">
  <tpAmb>1</tpAmb>
  <xServ>CONSULTAR</xServ>
  <chNFe>CHAVE</chNFe>
</consSitNFe>

tpAmb=1 corresponde à produção.

12. Primeira consulta válida

Foi obtido retorno:

cStat: 100
xMotivo: Autorizado o uso da NF-e
Status: AUTORIZADA

Confirmando:

PFX → TLS → SOAP → SVRS → resposta fiscal

13. Parser fiscal

Foi evitado usar .//cStat indiscriminadamente, pois a resposta pode conter:

retConsSitNFe
protNFe
procEventoNFe

O parser foi estruturado para considerar protocolo e eventos separadamente.

14. Interface

interface.py evoluiu para conter cabeçalho, identidade visual, pasta dos XMLs, PFX, senha mascarada, cards, pesquisa, filtros, Treeview, cores, progresso, consulta e exportação.

15. Excel

excel_service.py utiliza OpenPyXL para exportar dados locais e resultados de consulta.

16. Identidade visual

Foram adicionados:

assets/logo.png
assets/icone.ico

Para PyInstaller, os caminhos de recursos foram adaptados para execução normal e congelada (sys._MEIPASS).

17. PyInstaller

Foi validado PyInstaller 6.22.3 em --onedir:

python -m PyInstaller `
  --noconfirm `
  --clean `
  --windowed `
  --onedir `
  --name "NFCe Monitor" `
  --icon "assets\icone.ico" `
  --add-data "assets;assets" `
  main.py

O executável em dist\NFCe Monitor\NFCe Monitor.exe foi testado com sucesso.

18. Instalador

Foi escolhido Inno Setup para gerar um Setup.exe, copiar a distribuição PyInstaller, criar atalhos e permitir desinstalação.

19. GitHub e segurança

Antes do primeiro commit deve existir .gitignore.

Nunca versionar certificados, senhas, chaves privadas, XMLs fiscais reais, relatórios reais, .venv, build ou dist.

20. Estado atual

Validado:

leitura XML;

grandes volumes;

deduplicação;

interface responsiva;

certificado A1;

TLS;

SOAP;

SVRS;

cStat 100;

filtros;

Excel;

logo/ícone;

executável.

Pendente de validação real: NFC-e cancelada posteriormente.

21. Roadmap

consulta em lote controlada;

selecionadas/filtradas;

intervalo entre requisições;

botão Parar;

persistência imediata;

SQLite;

histórico;

painel de detalhes;

instalador final;

releases e changelog.

22. Regra de manutenção

Mudanças em cStat, tpEvento, protNFe e procEventoNFe devem ser baseadas em respostas reais/documentação fiscal, nunca apenas para produzir um resultado visual esperado.

23. Retomada futura

Use este arquivo como contexto:

Continuar o NFC-e Monitor a partir de doc/DESENVOLVIMENTO.md. Leitura XML, certificado A1, consulta individual SVRS, filtros, Excel e build PyInstaller já foram validados.