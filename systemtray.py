# Iniciar el proceso de Uvicorn en segundo plano
$job = Start-Process py -ArgumentList "-3.12 -m uvicorn app.main:app --host 127.0.0.1 --port 9080" -WindowStyle Hidden -PassThru

# Crear el menú en la bandeja (usando un objeto COM de Windows)
Add-Type -AssemblyName System.Windows.Forms
$notifyIcon = New-Object System.Windows.Forms.NotifyIcon
$notifyIcon.Icon = [System.Drawing.SystemIcons]::Application
$notifyIcon.Text = "Servidor FastAPI (9080)"
$notifyIcon.Visible = $true

# Crear menú contextual
$menu = New-Object System.Windows.Forms.ContextMenu
$item1 = $menu.MenuItems.Add("Abrir en Web", { Start-Process "http://127.0.0.1:9080" })
$item2 = $menu.MenuItems.Add("Apagar Servidor", { 
    Stop-Process -Id $job.Id -Force
    $notifyIcon.Visible = $false
    [System.Windows.Forms.Application]::Exit()
})

$notifyIcon.ContextMenu = $menu

# Mantener el script corriendo
[System.Windows.Forms.Application]::Run()