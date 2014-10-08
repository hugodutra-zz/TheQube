; The Qube install script
; InnoSetup v5.5.5 unicode
; Copyright © Andre Polykanine A.K.A. Menelion Elensúlë, 2014
; Last modified: October 05, 2014

#define MyAppName "The Qube"
#define MyAppVersion "1.0 Beta 6"
#define MyAppPublisher "Andre Polykanine A.K.A. Menelion Elensúlë"
#define MyAppURL "http://theqube.oire.org"
#define MyAppExeName "The Qube.exe"

[Setup]
AppId={{45E90244-4E13-41FF-B351-C387F444965E}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={pf}\{#MyAppName}
DefaultGroupName={#MyAppName}
; LicenseFile=dist\Documentation\license.txt
OutputDir=setup
OutputBaseFilename=The Qube-setup 1.0 Beta 6
Compression=lzma2
SolidCompression=true
VersionInfoCompany=The Qube dev team
SetupLogging=true
ShowLanguageDialog=yes
AlwaysShowDirOnReadyPage=yes

[Languages]
Name: english; MessagesFile: compiler:Default.isl
Name: Portuguese (Brazil); MessagesFile: compiler:languages\BrazilianPortuguese.isl
Name: Dutch; MessagesFile: compiler:Languages\\Dutch.isl
Name: French; MessagesFile: compiler:languages\\French.isl
Name: German; MessagesFile: compiler:Languages\\German.isl
Name: Italian; MessagesFile: compiler:languages\\Italian.isl
Name: Polish; MessagesFile: compiler:languages\Polish.isl
Name: Russian; MessagesFile: compiler:Languages\russian.isl
Name: Spanish; MessagesFile: compiler:languages\Spanish.isl

[Tasks]
Name: desktopicon; Description: {cm:CreateDesktopIcon}; GroupDescription: {cm:AdditionalIcons}; Flags: unchecked

[Files]
Source: IssProc.dll; DestDir: {tmp}; Flags: dontcopy
Source: IssProcLanguage.ini; DestDir: {tmp}; Flags: dontcopy
Source: IssProc.dll; DestDir: {app}
Source: IssProcLanguage.ini; DestDir: {app}

Source: dist\*; Excludes: The Qube.iss; DestDir: {app}; Flags: ignoreversion createallsubdirs recursesubdirs
source: sounds\*; DestDir: {app}\sounds; Flags: ignoreversion createallsubdirs recursesubdirs
source: locale\*; DestDir: {app}\locale; Flags: ignoreversion createallsubdirs recursesubdirs
Source: dist\documentation\readme.html; DestDir: {app}\documentation; Flags: ignoreversion isreadme

[Icons]
Name: {group}\{#MyAppName}; Filename: {app}\{#MyAppExeName}
Name: {group}\The Qube Readme ; Filename: {app}\Documentation\readme.html
Name: {group}\The Qube Changelog ; Filename: {app}\Documentation\changelog.html
Name: {group}\Sign up for Twitter ; Filename: http://www.twitter.com/signup
Name: {group}\{cm:ProgramOnTheWeb,{#MyAppName}}; Filename: {#MyAppURL}
Name: {group}\{cm:UninstallProgram,{#MyAppName}}; Filename: {uninstallexe}
Name: {commondesktop}\{#MyAppName}; Filename: {app}\{#MyAppExeName}; Tasks: desktopicon

[Run]
Filename: {app}\{#MyAppExeName}; Description: {cm:LaunchProgram,{#MyAppName}}; Flags: nowait postinstall skipifsilent

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
      sModuleName :=ExpandConstant('*The Qube.exe;');                        { searched modules. Tip: separate multiple modules with semicolon Ex: '*mymodule.dll;*mymodule2.dll;*myapp.exe'}

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
     sModuleName := ExpandConstant('*The Qube.exe;');          { searched module. Tip: separate multiple modules with semicolon Ex: '*mymodule.dll;*mymodule2.dll;*myapp.exe'}

     nCode:=IssFindModuleU(0,sModuleName,'enu',false,false); { search for module and display files-in-use window if found  }

     if (nCode=0) or (nCode=2) then begin                    { no module found or ignored pressed}
          Result := true;                                    { continue setup  }
     end;

    // Unload the extension, otherwise it will not be deleted by the uninstaller
    UnloadDLL(ExpandConstant('{app}\IssProc.dll'));

end;
