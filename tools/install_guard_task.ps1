# Installs (or removes) a Windows scheduled task that starts tools\keylab_guard.py
# invisibly at logon with administrator rights (needed for the automatic USB reset).
# Run once from an *administrator* PowerShell:
#   powershell -ExecutionPolicy Bypass -File tools\install_guard_task.ps1
#   powershell -ExecutionPolicy Bypass -File tools\install_guard_task.ps1 -Uninstall
param([switch]$Uninstall)

$TaskName = "KeyLab Guard"
$Guard = Join-Path $PSScriptRoot "keylab_guard.py"

$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole(
    [Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) { Write-Error "Please run this from an administrator PowerShell."; exit 1 }

if ($Uninstall) {
    Stop-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue
    Write-Host "Task '$TaskName' removed."
    exit 0
}

# pyw.exe = Python launcher without console window (installed with Python for Windows)
$pyw = (Get-Command pyw.exe -ErrorAction SilentlyContinue).Source
if (-not $pyw) { Write-Error "pyw.exe (Python launcher) not found - install Python for Windows first."; exit 1 }

$user = "$env:USERDOMAIN\$env:USERNAME"
$action = New-ScheduledTaskAction -Execute $pyw -Argument "-3 `"$Guard`"" -WorkingDirectory $PSScriptRoot
$trigger = New-ScheduledTaskTrigger -AtLogOn -User $user
$principal = New-ScheduledTaskPrincipal -UserId $user -LogonType Interactive -RunLevel Highest
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
    -ExecutionTimeLimit ([TimeSpan]::Zero) -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1) `
    -MultipleInstances IgnoreNew

Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Principal $principal `
    -Settings $settings -Description "Detects and recovers the Arturia KeyLab mkII USB MIDI hang (keylab_guard.py)" `
    -Force | Out-Null
Start-ScheduledTask -TaskName $TaskName
Write-Host "Task '$TaskName' installed and started. Log: $(Join-Path $PSScriptRoot 'keylab_guard.log')"
