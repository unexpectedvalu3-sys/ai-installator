; ComparateurCourtier.iss — Script Inno Setup pour générer setup.exe
; Compiler : ISCC.exe ComparateurCourtier.iss
; Produit : dist\setup_ComparateurCourtier.exe (~40 Mo)
;
; L'installateur :
;   - copie ComparateurCourtier.exe dans %LOCALAPPDATA%\ComparateurCourtier
;     (pas de droits admin requis, mises à jour faciles)
;   - le .env et data/ vivent dans le même dossier
;   - crée les raccourcis Bureau + Menu Démarrer
;   - Au 1er lancement, l'exe affiche un assistant (clés API + mot de passe)
;   - Les mises à jour (réinstallation) préservent le .env + data/.

#define MyAppName "Comparateur Courtier"
#define MyAppExeName "ComparateurCourtier.exe"
#define MyAppVersion "1.0.9"
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
OutputBaseFilename=setup_ComparateurCourtier
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
; L'exe (toujours écrasé lors des mises à jour). Le .env et data/ ne sont PAS touchés.
Source: "dist\ComparateurCourtier.exe"; DestDir: "{app}"; Flags: ignoreversion

[Dirs]
Name: "{app}\data"; Flags: uninsneveruninstall

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; IconFilename: "{app}\{#MyAppExeName}"
Name: "{group}\Désinstaller {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; IconFilename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; Description: "Lancer le Comparateur Courtier"; Flags: nowait postinstall skipifsilent
