#define MyAppName "NFC-e Monitor"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "MERCANTIL MEDEIROS LTDA"
#define MyAppExeName "NFCe Monitor.exe"

[Setup]
AppId={{7C753C7A-78E1-4AA4-B39D-76D0B3B74D65}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}

DefaultDirName={autopf}\NFC-e Monitor
DefaultGroupName=NFC-e Monitor

OutputDir=output
OutputBaseFilename=NFCeMonitor_Setup_{#MyAppVersion}

SetupIconFile=..\assets\icone.ico
UninstallDisplayIcon={app}\{#MyAppExeName}

Compression=lzma2
SolidCompression=yes

WizardStyle=modern

PrivilegesRequired=admin

ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Tasks]
Name: "desktopicon"; Description: "Criar um atalho na Área de Trabalho"; GroupDescription: "Atalhos:"; Flags: unchecked

[Files]
Source: "..\dist\NFCe Monitor\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\NFC-e Monitor"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\NFC-e Monitor"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Executar NFC-e Monitor"; Flags: nowait postinstall skipifsilent