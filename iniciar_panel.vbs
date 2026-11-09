Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

' Comprobar si el backend en puerto 8000 ya esta escuchando
Dim oExec, sOutput
Set oExec = WshShell.Exec("cmd /c netstat -ano | findstr :8000 | findstr LISTENING")
sOutput = oExec.StdOut.ReadAll()

If InStr(sOutput, "LISTENING") = 0 Then
    ' Iniciar backend FastAPI de forma 100% oculta en segundo plano (sin ventana CMD)
    WshShell.Run "cmd /c cd /d ""D:\PROYECTOS\limpiar pc"" && python main.py", 0, False
    WScript.Sleep 1500
End If

' Buscar navegador instalado para abrir como VENTANA DE APLICACIÓN DE ESCRITORIO DEDICADA
' (Sin barra de direcciones, sin pestanas, sin marcadores: experiencia 100% programa de escritorio)
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
    ' Fallback estandar
    WshShell.Run appUrl, 1, False
End If
