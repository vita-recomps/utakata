# Memory watch for long test runs: every N seconds, the game's private bytes and working set,
# the system's free memory, and the five processes using the most private memory, as CSV.
#   powershell -NoProfile -File tools\memwatch.ps1 -Out build\mem.csv [-Seconds 15] [-Minutes 30] [-Process shinobido2]
param(
    [Parameter(Mandatory)][string]$Out,
    [int]$Seconds = 15,
    [int]$Minutes = 30,
    [string]$Process = 'shinobido2'
)
$end = (Get-Date).AddMinutes($Minutes)
'time,game_private_mb,game_ws_mb,game_handles,free_mb,commit_mb,top5' | Set-Content -Encoding utf8 $Out
while ((Get-Date) -lt $end) {
    $os = Get-CimInstance Win32_OperatingSystem
    $g = Get-Process $Process -ErrorAction SilentlyContinue | Select-Object -First 1
    $gp = if ($g) { [math]::Round($g.PrivateMemorySize64 / 1MB) } else { '' }
    $gw = if ($g) { [math]::Round($g.WorkingSet64 / 1MB) } else { '' }
    $gh = if ($g) { $g.HandleCount } else { '' }
    $commit = [math]::Round(($os.TotalVirtualMemorySize - $os.FreeVirtualMemory) / 1KB)
    $top = Get-Process | Sort-Object PrivateMemorySize64 -Descending | Select-Object -First 5 |
        ForEach-Object { '{0}={1}' -f $_.ProcessName, [math]::Round($_.PrivateMemorySize64 / 1MB) }
    '{0},{1},{2},{3},{4},{5},"{6}"' -f (Get-Date -Format 'HH:mm:ss'), $gp, $gw, $gh,
        [math]::Round($os.FreePhysicalMemory / 1KB), $commit, ($top -join ' ') | Add-Content -Encoding utf8 $Out
    Start-Sleep -Seconds $Seconds
}
