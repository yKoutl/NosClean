Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

' Comprobar si el backend en puerto 8000 ya esta escuchando
Dim oExec, sOutput
Set oExec = WshShell.Exec("cmd /c netstat -ano | findstr :8000 | findstr LISTENING")
sOutput = oExec.StdOut.ReadAll()

If InStr(sOutput, "LISTENING") = 0 Then
    ' Iniciar backend FastAPI de forma 100% oculta en segundo plano (sin ventana CMD)
    WshShell.Run "cmd /c cd /d ""D:\PROYECTOS\limpiar pc"" && python main.py", 0, False
    
    ' Polling activo de puerto: abre inmediatamente al responder (max 2 segs)
    Dim attempt
    For attempt = 1 To 20
        WScript.Sleep 100
        Set oExec = WshShell.Exec("cmd /c netstat -ano | findstr :8000 | findstr LISTENING")
        If InStr(oExec.StdOut.ReadAll(), "LISTENING") > 0 Then Exit For
    Next
End If

' Buscar navegador instalado para abrir como VENTANA DE APLICACIÓN DE ESCRITORIO DEDICADA
' Con perfil independiente para fijar icono corporativo en barra de tareas de Windows
Dim appUrl, profileDir, edgePath, chromePath, appOpened
appUrl = "http://127.0.0.1:8000"
profileDir = "D:\PROYECTOS\limpiar pc\.nosclean_profile"
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
    WshShell.Run """" & edgePath & """ --user-data-dir=""" & profileDir & """ --app=""" & appUrl & """ --window-size=1280,820", 1, False
    appOpened = True
ElseIf fso.FileExists(chromePath) Then
    WshShell.Run """" & chromePath & """ --user-data-dir=""" & profileDir & """ --app=""" & appUrl & """ --window-size=1280,820", 1, False
    appOpened = True
End If

If Not appOpened Then
    ' Fallback estandar
    WshShell.Run appUrl, 1, False
End If
