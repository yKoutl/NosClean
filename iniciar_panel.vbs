Set WshShell = CreateObject("WScript.Shell")

' Comprobar si el puerto 8000 esta respondiendo
Dim oExec, sOutput
Set oExec = WshShell.Exec("cmd /c netstat -ano | findstr :8000 | findstr LISTENING")
sOutput = oExec.StdOut.ReadAll()

If InStr(sOutput, "LISTENING") = 0 Then
    ' Ejecutar python de forma completamente oculta (0 = Oculto, sin ventana negra)
    WshShell.Run "cmd /c cd /d ""D:\PROYECTOS\limpiar pc"" && python main.py", 0, False
    WScript.Sleep 1500
End If

' Abrir en navegador
WshShell.Run "http://127.0.0.1:8000", 1, False

