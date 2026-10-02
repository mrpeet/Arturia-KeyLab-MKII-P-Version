# KeyLab mkII USB watchdog
# Logs (with timestamp) whenever the KeyLab appears, disappears or changes status
# on the USB bus. Run it in the background while working in FL Studio; when the
# keyboard stops responding, check the log:
#   - device vanished / status changed  -> USB, cable or power problem
#   - device stayed "OK" the whole time -> firmware, driver or script side
#
# Usage:  powershell -ExecutionPolicy Bypass -File tools\usb_watch.ps1
# Stop with Ctrl+C. Log: tools\usb_watch.log

param(
    [int]$IntervalSec = 2,
    [string]$LogFile = (Join-Path $PSScriptRoot 'usb_watch.log')
)

$ArturiaVid = 'VID_1C75'

function Get-KeyLabState {
    $devs = Get-PnpDevice -PresentOnly -ErrorAction SilentlyContinue |
        Where-Object { $_.InstanceId -match $ArturiaVid -or $_.FriendlyName -match 'KeyLab' }
    if (-not $devs) { return 'NOT CONNECTED' }
    ($devs | Sort-Object FriendlyName, InstanceId |
        ForEach-Object { '{0} [{1}]' -f $_.FriendlyName, $_.Status }) -join '; '
}

function Write-Log([string]$text) {
    $line = '{0}  {1}' -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $text
    Write-Host $line
    Add-Content -Path $LogFile -Value $line -Encoding utf8
}

Write-Log "--- usb_watch started (interval ${IntervalSec}s) ---"
$last = $null
while ($true) {
    $state = Get-KeyLabState
    if ($state -ne $last) {
        Write-Log $state
        $last = $state
    }
    Start-Sleep -Seconds $IntervalSec
}
