# Cursor-monitored Surreal Architecture tier-B wake loop
param(
    [int]$IntervalSeconds = 300
)

$ErrorActionPreference = "Continue"
$deploy = $PSScriptRoot
$pidFile = Join-Path $deploy "SURREAL_TIERB_LOOP.pid"
$stopFile = Join-Path $deploy "SURREAL_TIERB_LOOP_STOP"
$tickPrompt = "Surreal Architecture micro-cycle: read SURREAL_ARCH_LOOP_STATE.md, pick one slice from Next loop targets, node design + taxonomy before code if new kit; sync; verify; update LOOP_STATE. Do NOT edit plan files."

$PID | Out-File -FilePath $pidFile -Encoding ascii -Force
Write-Output "AGENT_LOOP_START_surreal_tierb pid=$PID interval=${IntervalSeconds}s"

if (Test-Path $stopFile) {
    Remove-Item $stopFile -Force
}

$tick = 0
while ($true) {
    try {
        Start-Sleep -Seconds $IntervalSeconds
    } catch {
        Write-Output "sleep interrupted: $_"
        continue
    }

    if (Test-Path $stopFile) {
        Write-Output "AGENT_LOOP_STOP_surreal_tierb stop sentinel detected"
        break
    }

    $tick++
    $json = @{ prompt = $tickPrompt } | ConvertTo-Json -Compress
    Write-Output "AGENT_LOOP_TICK_surreal_tierb $json"
}

if (Test-Path $pidFile) { Remove-Item $pidFile -Force }
Write-Output "AGENT_LOOP_EXIT_surreal_tierb"
