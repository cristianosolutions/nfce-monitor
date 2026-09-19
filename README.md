NFC-e Monitor

Aplicação desktop em Python para análise, conferência e consulta fiscal de NFC-e (modelo 65) a partir de arquivos XML, com consulta de situação na SEFAZ/SVRS utilizando certificado digital A1.

Necessidade real

A aplicação foi desenvolvida para facilitar a conferência de grandes volumes de NFC-e armazenadas em XML. Um XML local pode mostrar que uma nota foi originalmente autorizada, mas isso não garante, sozinho, que ela permaneça autorizada: pode existir um evento posterior, como cancelamento, cujo XML não esteja na pasta analisada.

Por isso o NFC-e Monitor mantém duas informações separadas:

Status XML: situação encontrada nos arquivos locais.

Situação SEFAZ: situação obtida pela consulta fiscal online.

Assim, milhares de documentos podem ser analisados sem abertura manual de cada XML.

A ferramenta auxilia a conferência fiscal e não substitui procedimentos contábeis/fiscais oficiais nem a validação das regras vigentes.

Funcionalidades

Seleção de pasta e busca recursiva de XMLs.

Leitura de grandes volumes de NFC-e.

Extração de número, série, emissão, CNPJ, emitente, valor, protocolo e chave.

Deduplicação pela chave de acesso de 44 dígitos.

Identificação de eventos presentes nos XMLs.

Processamento em segundo plano sem bloquear a interface.

Barra de progresso.

Consulta individual na SEFAZ/SVRS.

Certificado digital A1 PFX/P12.

Pesquisa e filtros por Status XML e Situação SEFAZ.

Indicadores de autorizadas, canceladas, não consultadas e outros/erros.

Exportação para Excel.

Abertura do XML original com duplo clique.

Executável Windows via PyInstaller.

Tecnologias

Tecnologia

Uso

Python 3.12

Linguagem principal

Tkinter / ttk

Interface gráfica

ElementTree

Leitura dos XMLs

Requests

HTTPS/SOAP

Cryptography

Certificado A1

Truststore

Cadeia de confiança do Windows

OpenPyXL

Excel

Threading + Queue

Processamento em segundo plano

pathlib

Arquivos e diretórios

PyInstaller

Executável Windows

Inno Setup

Instalador

Estrutura

verificador-nfce/
├── app/
│   ├── __init__.py
│   ├── certificado_service.py
│   ├── excel_service.py
│   ├── interface.py
│   ├── nfce_service.py
│   └── xml_reader.py
├── assets/
│   ├── icone.ico
│   └── logo.png
├── doc/
│   ├── MANUAL_USUARIO.md
│   └── DESENVOLVIMENTO.md
├── instalador/
│   └── NFCeMonitor.iss
├── main.py
├── requirements.txt
├── teste_certificado.py
└── teste_sefaz.py

Desenvolvimento local

git clone URL_DO_REPOSITORIO
cd verificador-nfce
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python main.py

Dependências principais:

requests
cryptography
openpyxl
truststore

Como usar

Abra o NFC-e Monitor.

Clique em Selecionar pasta e escolha a pasta dos XMLs.

Clique em Analisar XMLs e aguarde.

Use pesquisa e filtros para localizar documentos.

Para consulta online, selecione o certificado A1 PFX/P12.

Informe a senha.

Selecione uma NFC-e na tabela.

Clique em Consultar SEFAZ.

Confira Situação SEFAZ, cStat, motivo e protocolo.

Use Exportar Excel quando necessário.

Consulte doc/MANUAL_USUARIO.md para o manual completo.

Status XML x Situação SEFAZ

Status XML      = informação existente no arquivo local
Situação SEFAZ  = resultado da consulta fiscal online

Essa separação é intencional.

Segurança

Nunca publique:

certificados .pfx/.p12;

chaves .pem/.key;

senhas;

XMLs fiscais reais;

.env com segredos;

relatórios fiscais reais.

Build Windows

Build validado em --onedir:

python -m PyInstaller `
  --noconfirm `
  --clean `
  --windowed `
  --onedir `
  --name "NFCe Monitor" `
  --icon "assets\icone.ico" `
  --add-data "assets;assets" `
  main.py

Resultado:

dist\NFCe Monitor\NFCe Monitor.exe

Estado atual

Já validados: análise de dezenas de milhares de XMLs, deduplicação, interface responsiva, certificado A1, TLS, SOAP, consulta NFC-e na SVRS, retorno cStat 100, filtros, Excel e executável PyInstaller.

Ainda deve ser validado, quando houver exemplo disponível, o comportamento completo com uma NFC-e real cancelada posteriormente.

Próximas evoluções

Consulta em lote controlada.

Botão para interromper consulta.

Persistência local das consultas.

Histórico.

SQLite.

Painel de detalhes.

Finalização do instalador.

Releases versionadas.

Documentação

doc/MANUAL_USUARIO.md — utilização passo a passo.

doc/DESENVOLVIMENTO.md — histórico técnico e decisões do projeto.

Publicação

Antes de tornar o repositório público, confirme que a identidade visual e demais recursos podem ser publicados. Para uso exclusivamente interno, prefira um repositório privado.