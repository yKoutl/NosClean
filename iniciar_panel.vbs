Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

Dim scriptDir
scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)

' 1. Si existe el ejecutable compilado NosClean.exe, ejecutarlo directamente (posee icono oficial y ventana nativa)
Dim exePath
exePath = scriptDir & "\NosClean.exe"
If fso.FileExists(exePath) Then
    WshShell.Run """" & exePath & """", 1, False
    WScript.Quit
End If

' 2. Comprobar si el servidor HTTP responde silenciosamente
Function IsServerRunning()
    On Error Resume Next
    Dim http
    Set http = CreateObject("MSXML2.ServerXMLHTTP.6.0")
    http.setTimeouts 500, 500, 500, 500
    http.open "GET", "http://127.0.0.1:8000/favicon.ico", False
    http.send
    If Err.Number = 0 Then
        If http.status = 200 Then
            IsServerRunning = True
            Exit Function
        End If
    End If
    IsServerRunning = False
    On Error GoTo 0
End Function

' Si el servidor no esta activo, arrancarlo con pythonw main.py (abre ventana nativa con icono NosClean)
If Not IsServerRunning() Then
    WshShell.Run "pythonw.exe """ & scriptDir & "\main.py""", 0, False
    WScript.Quit
End If

' Si el servidor ya estaba activo, abrir ventana nativa a traves de main.py
WshShell.Run "pythonw.exe """ & scriptDir & "\main.py""", 0, False
