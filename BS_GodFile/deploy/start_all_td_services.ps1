# start_all_td_services.ps1
# Launches all autonomous TouchDesigner production services
# Branch: feature/touchdesigner-mcp-integration

param(
    [switch]$Stop,
    [switch]$Status
)

$ProjectRoot = "G:\EnvironmentPortfolio"
$AuditDir = "$ProjectRoot\BS_GodFile\Saved\Audit"

# Status check mode
if ($Status) {
    Write-Host "========================================"
    Write-Host "  TD Service Status"
    Write-Host "========================================"
    
    $services = @(
        @{Name="TD Orchestrator"; Sentinel="AGENT_LOOP_TICK_td_orch"},
        @{Name="OSC Monitor"; Sentinel="osc_monitor_state.json"},
        @{Name="Spout Watchdog"; Sentinel="spout_stream_state.json"}
    )
    
    foreach ($svc in $services) {
        $path = Join-Path $AuditDir $svc.Sentinel
        if (Test-Path $path) {
            $content = Get-Content $path -Raw | ConvertFrom-Json
            Write-Host "  [$($svc.Name)] ACTIVE — last tick: $($content.timestamp)"
        }
        else {
            Write-Host "  [$($svc.Name)] INACTIVE"
        }
    }
    exit 0
}

# Stop mode
if ($Stop) {
    Write-Host "Stopping all TD services..."
    New-Item -ItemType File -Force -Path "$AuditDir\td_loop_STOP" | Out-Null
    Write-Host "Stop signal written. Services will exit on next tick."
    exit 0
}

# Start mode (default)
New-Item -ItemType Directory -Force -Path $AuditDir | Out-Null

# Clear old stop signals
Remove-Item "$AuditDir\td_loop_STOP" -ErrorAction SilentlyContinue

Write-Host "========================================"
Write-Host "  TouchDesigner Autonomous Production"
Write-Host "  Environment Portfolio Platform"
Write-Host "========================================"
Write-Host ""

# Service 1: TD Orchestrator Loop (60s interval)
Write-Host "[1/3] Starting TD Orchestrator daemon (60s interval)..."
$proc1 = Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-File", "$ProjectRoot\BS_GodFile\deploy\start_td_loop.ps1",
    "-IntervalSeconds", "60"
) -WindowStyle Minimized -PassThru
Write-Host "       PID: $($proc1.Id)"

Start-Sleep -Seconds 1

# Service 2: OSC Bridge Monitor (10s interval)
Write-Host "[2/3] Starting OSC bridge health monitor (10s interval)..."
$proc2 = Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-File", "$ProjectRoot\BS_GodFile\deploy\start_osc_monitor.ps1",
    "-IntervalSeconds", "10"
) -WindowStyle Minimized -PassThru
Write-Host "       PID: $($proc2.Id)"

Start-Sleep -Seconds 1

# Service 3: Spout Stream Watchdog (5s interval)
Write-Host "[3/3] Starting Spout stream watchdog (5s interval)..."
$proc3 = Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-File", "$ProjectRoot\BS_GodFile\deploy\start_spout_watchdog.ps1",
    "-IntervalSeconds", "5"
) -WindowStyle Minimized -PassThru
Write-Host "       PID: $($proc3.Id)"

Write-Host ""
Write-Host "All TD services launched."
Write-Host ""
Write-Host "Monitor:"
Write-Host "  Get-Content '$AuditDir\AGENT_LOOP_TICK_td_orch'"
Write-Host "  Get-Content '$AuditDir\osc_monitor_state.json'"
Write-Host "  Get-Content '$AuditDir\spout_stream_state.json'"
Write-Host ""
Write-Host "Stop all:"
Write-Host "  .\start_all_td_services.ps1 -Stop"
Write-Host ""
Write-Host "Status:"
Write-Host "  .\start_all_td_services.ps1 -Status"
