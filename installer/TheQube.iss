; TheQube install script
; InnoSetup v5.5.5 unicode
; Copyright © TheQube developers team, 2014

#define MyAppName "TheQube"
#define MyAppVersion "0.7"
#define MyAppPublisher "TheQube developers team"
#define MyAppURL "http://theqube.oire.org"
#define MyAppExeName "TheQube.exe"
#define MyAppDescription "An accessible social networking client developed mainly for the blind."
#define MyAppCopyrightYear "2014"

[Setup]
AppId={{45E90244-4E13-41FF-B351-C387F444965E}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppCopyright=Copyright © {#MyAppCopyrightYear} {#MyAppPublisher}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={pf}\{#MyAppName}
DefaultGroupName={#MyAppName}
; LicenseFile=..\src\dist\Documentation\license.txt
OutputDir=setup
OutputBaseFilename=TheQube-{#MyAppVersion}-setup
Compression=lzma2
SolidCompression=true
DisableStartupPrompt=true
AlwaysShowDirOnReadyPage=true
AlwaysShowGroupOnReadyPage=true
ShowLanguageDialog=yes
DisableProgramGroupPage=true
DisableReadyPage=false
DisableFinishedPage=false
ArchitecturesAllowed=x86 x64
VersionInfoCompany={#MyAppPublisher}
VersionInfoCopyright=Copyright © {#MyAppCopyrightYear} {#MyAppPublisher}
VersionInfoDescription={#MyAppDescription}
VersionInfoProductName={#MyAppName}
VersionInfoProductVersion={#MyAppVersion}
VersionInfoVersion={#MyAppVersion}
AppModifyPath={app}
AppContact=theqube@lists.oire.org
PrivilegesRequired=lowest

[Languages]
Name: en; MessagesFile: compiler:Default.isl,languages\DefaultCustom.islu
Name: pt_BR; MessagesFile: compiler:Languages\BrazilianPortuguese.isl,languages\DefaultCustom.islu
Name: ru; MessagesFile: compiler:Languages\russian.isl,languages\RussianCustom.islu
Name: es; MessagesFile: compiler:languages\Spanish.isl,languages\SpanishCustom.islu

[Tasks]
Name: desktopicon; Description: {cm:CreateDesktopIcon}; GroupDescription: {cm:AdditionalIcons}; Flags: unchecked

[Files]
Source: IssProc.dll; DestDir: {tmp}; Flags: dontcopy
Source: IssProcLanguage.ini; DestDir: {tmp}; Flags: dontcopy
Source: IssProc.dll; DestDir: {app}
Source: IssProcLanguage.ini; DestDir: {app}

Source: ..\src\dist\*; DestDir: {app}; Permissions: users-readexec; Flags: ignoreversion createallsubdirs recursesubdirs
source: ..\src\sounds\*; DestDir: {app}\sounds; Flags: ignoreversion createallsubdirs recursesubdirs
source: ..\src\locale\*; Excludes: *.po; DestDir: {app}\locale; Flags: ignoreversion createallsubdirs recursesubdirs
Source: ..\src\dist\documentation\*; DestDir: {app}\documentation; Flags: ignoreversion createallsubdirs recursesubdirs

[Icons]
Name: {group}\{#MyAppName}; Filename: {app}\{#MyAppExeName}
Name: {group}\{cm:ReadManual,{#MyAppName}}; Filename: {app}\Documentation\{language}\readme.html
Name: {group}\{cm:WhatsNew,{#MyAppName}}; Filename: {app}\Documentation\{language}\changelog.html
Name: {group}\{cm:JoinTwitter}; Filename: https://twitter.com/signup
Name: {group}\{cm:ProgramOnTheWeb,{#MyAppName}}; Filename: {#MyAppURL}
Name: {group}\{cm:UninstallProgram,{#MyAppName}}; Filename: {uninstallexe}
Name: {commondesktop}\{#MyAppName}; Filename: {app}\{#MyAppExeName}; Tasks: desktopicon

[Run]
Filename: {app}\{#MyAppExeName}; Description: {cm:LaunchProgram,{#MyAppName}}; Flags: nowait postinstall skipifsilent
filename: {app}\documentation\{language}\readme.html; Description: {cm:ReadManual,{#MyAppName}}; Flags: shellexec runasoriginaluser nowait postinstall skipifsilent unchecked
filename: {app}\documentation\{language}\changelog.html; Description: {cm:WhatsNew,{#MyAppName}}; Flags: shellexec runasoriginaluser nowait postinstall skipifsilent unchecked

[Code]
function IssFindModule(hWnd: Integer; Modulename: PAnsiChar; Language: PAnsiChar; Silent: Boolean; CanIgnore: Boolean ): Integer;
external 'IssFindModule@files:IssProc.dll stdcall setuponly';

function IssFindModuleU(hWnd: Integer; Modulename: PAnsiChar; Language: PAnsiChar; Silent: Boolean; CanIgnore: Boolean ): Integer;
external 'IssFindModule@{app}\IssProc.dll stdcall uninstallonly';

function NextButtonClick(CurPage: Integer): Boolean;
var
  hWnd: Integer;
  sModuleName: String;
  nCode: Integer;  {IssFindModule returns: 0 if no module found; 1 if cancel pressed; 2 if ignore pressed; -1 if an error occured }
begin
  Result := true;

 if CurPage = wpReady then
   begin
      Result := false;
      ExtractTemporaryFile('IssProcLanguage.ini');                          { extract extra language file - you don't need to add this line if you are using english only }
      hWnd := StrToInt(ExpandConstant('{wizardhwnd}'));                     { get main wizard handle }
      sModuleName :=ExpandConstant('*TheQube.exe;');                        { searched modules. Tip: separate multiple modules with semicolon Ex: '*mymodule.dll;*mymodule2.dll;*myapp.exe'}

     nCode:=IssFindModule(hWnd,sModuleName,'en',false,true);                { search for module and display files-in-use window if found  }
     //sModuleName:=IntToStr(nCode);
    // MsgBox ( sModuleName, mbConfirmation, MB_YESNO or MB_DEFBUTTON2);

     if nCode=1 then  begin                                                 { cancel pressed or files-in-use window closed }
          PostMessage (WizardForm.Handle, $0010, 0, 0);                     { quit setup, $0010=WM_CLOSE }
     end else if (nCode=0) or (nCode=2) then begin                          { no module found or ignored pressed}
          Result := true;                                                   { continue setup  }
     end;

  end;

end;


function InitializeUninstall(): Boolean;
var
  sModuleName: String;
  nCode: Integer;  {IssFindModule returns: 0 if no module found; 1 if cancel pressed; 2 if ignore pressed; -1 if an error occured }

begin
    Result := false;
     sModuleName := ExpandConstant('*TheQube.exe;');          { searched module. Tip: separate multiple modules with semicolon Ex: '*mymodule.dll;*mymodule2.dll;*myapp.exe'}

     nCode:=IssFindModuleU(0,sModuleName,'enu',false,false); { search for module and display files-in-use window if found  }

     if (nCode=0) or (nCode=2) then begin                    { no module found or ignored pressed}
          Result := true;                                    { continue setup  }
     end;

    // Unload the extension, otherwise it will not be deleted by the uninstaller
    UnloadDLL(ExpandConstant('{app}\IssProc.dll'));

end;
