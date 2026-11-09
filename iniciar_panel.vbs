Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

' Comprobar si el servidor HTTP responde silenciosamente (100% en memoria, cero ventanas CMD)
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

Dim scriptDir
scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)

' Si el servidor no esta activo, arrancarlo con pythonw de forma 100% invisible (sin consola)
If Not IsServerRunning() Then
    WshShell.Run "pythonw.exe """ & scriptDir & "\main.py""", 0, False
    
    ' Esperar silenciosamente hasta que el servidor responda
    Dim i
    For i = 1 To 20
        WScript.Sleep 100
        If IsServerRunning() Then Exit For
    Next
End If

' Lanzar aplicacion en ventana de escritorio limpia dedicada
Dim appUrl, edgePath, chromePath, appOpened
appUrl = "http://127.0.0.1:8000"
appOpened = False

edgePath = "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
If Not fso.FileExists(edgePath) Then
    edgePath = "C:\Program Files\Microsoft\Edge\Application\msedge.exe"
End If

chromePath = "C:\Program Files\Google\Chrome\Application\chrome.exe"
If Not fso.FileExists(chromePath) Then
    chromePath = "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
End If

If fso.FileExists(edgePath) Then
    WshShell.Run """" & edgePath & """ --app=""" & appUrl & """ --window-size=1280,820", 1, False
    appOpened = True
ElseIf fso.FileExists(chromePath) Then
    WshShell.Run """" & chromePath & """ --app=""" & appUrl & """ --window-size=1280,820", 1, False
    appOpened = True
End If

If Not appOpened Then
    WshShell.Run appUrl, 1, False
End If
