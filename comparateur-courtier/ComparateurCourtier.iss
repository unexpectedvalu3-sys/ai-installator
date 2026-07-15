; ComparateurCourtier.iss — Script Inno Setup, appelé par make_client.py.
; Empaquette l'exe GÉNÉRIQUE (dist\ComparateurCourtier.exe) + un .env client.
; Défines passés par make_client.py : ClientName, AppVersion, ClientEnv.
;   ISCC.exe /DClientName=sophie /DAppVersion=1.1.0 /DClientEnv=dist\_client.env ComparateurCourtier.iss
;
; L'installateur :
;   - copie l'exe (générique, sans secret) dans %LOCALAPPDATA%\ComparateurCourtier ;
;   - dépose le .env client (clés + identifiants) À CÔTÉ, seulement s'il n'existe pas
;     déjà (onlyifdoesntexist) -> les mises à jour préservent le .env + data/ ;
;   - crée les raccourcis Bureau + Menu Démarrer.

#ifndef ClientName
  #define ClientName "ComparateurCourtier"
#endif
#ifndef AppVersion
  #define AppVersion "0.0.0"
#endif

#define MyAppName "Comparateur Courtier"
#define MyAppExeName "ComparateurCourtier.exe"
#define MyAppVersion AppVersion
#define MyAppPublisher "AI Installator"

[Setup]
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={localappdata}\ComparateurCourtier
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
DisableDirPage=yes
OutputDir=dist
OutputBaseFilename=setup_{#ClientName}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64
ArchitecturesAllowed=x64
PrivilegesRequired=lowest
SetupIconFile=static\mascotte.ico
UninstallDisplayIcon={app}\{#MyAppExeName}

[Languages]
Name: "french"; MessagesFile: "compiler:Languages\French.isl"

[Tasks]
Name: "desktopicon"; Description: "Créer un raccourci sur le Bureau"; GroupDescription: "Icônes:"

[Files]
; L'exe générique (toujours écrasé lors des mises à jour).
Source: "dist\ComparateurCourtier.exe"; DestDir: "{app}"; Flags: ignoreversion
; Le .env client (clés + identifiants) : déposé UNIQUEMENT s'il n'existe pas déjà,
; pour que les réinstallations / mises à jour préservent la config + le SECRET_KEY.
#ifdef ClientEnv
Source: "{#ClientEnv}"; DestDir: "{app}"; DestName: ".env"; Flags: onlyifdoesntexist
#endif

[Dirs]
Name: "{app}\data"; Flags: uninsneveruninstall

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; IconFilename: "{app}\{#MyAppExeName}"
Name: "{group}\Désinstaller {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; IconFilename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; Description: "Lancer le Comparateur Courtier"; Flags: nowait postinstall skipifsilent
