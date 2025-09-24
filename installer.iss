; Inno Setup script for NSE Streamlit App
[Setup]
AppName=NSE Streamlit App
AppVersion=1.0
DefaultDirName={pf}\NSEStreamlitApp
DefaultGroupName=NSE Streamlit App
OutputDir=.
OutputBaseFilename=NSEStreamlitAppInstaller
Compression=lzma
SolidCompression=yes

[Files]
Source: "dist\NSEStreamlitApp.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "stock_list.csv"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\NSE Streamlit App"; Filename: "{app}\NSEStreamlitApp.exe"

[Run]
Filename: "{app}\NSEStreamlitApp.exe"; Description: "Run NSE Streamlit App"; Flags: nowait postinstall skipifsilent
