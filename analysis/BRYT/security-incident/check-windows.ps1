# Read-only check of a Windows PC for the "Healthcare-Medical-Supply-Plan" lure and its loader.
# Run in PowerShell AS ADMINISTRATOR:
#   powershell -ExecutionPolicy Bypass -File "$env:USERPROFILE\Downloads\check-windows.ps1"
# It does not run git, npm, node or anything from the repo, and changes nothing.

$ErrorActionPreference = 'SilentlyContinue'
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$out = Join-Path ([Environment]::GetFolderPath('Desktop')) "win-check-$env:COMPUTERNAME-$stamp"
New-Item -ItemType Directory -Path $out -Force | Out-Null
function Save($name, $data) { $data | Out-File -FilePath (Join-Path $out $name) -Width 400 -Encoding utf8 }
$flags = New-Object System.Collections.Generic.List[string]
function Flag($msg) { $flags.Add($msg); Write-Host "FLAG: $msg" -ForegroundColor Red }

Write-Host "[1] Tools the malware needs"
$tools = foreach ($t in 'git','node','code','curl') { $p = (Get-Command $t -All).Source; "{0,-5} {1}" -f $t, ($(if ($p) { $p -join '; ' } else { 'not found' })) }
Save '01-tools.txt' $tools

Write-Host "[2] Lure files and folders"
$roots = @($env:USERPROFILE, 'C:\Users\Public') + (Get-ChildItem 'C:\Users' -Directory | ForEach-Object FullName)
$roots = $roots | Select-Object -Unique
$lure = foreach ($r in $roots) {
  Get-ChildItem -Path $r -Recurse -Force -ErrorAction SilentlyContinue -Attributes !Offline `
    -Include '*Healthcare-Medical-Supply*','*Infosytech*','*Blockchain*Pharma*','*imindstechnology*' |
    Select-Object FullName, CreationTime, LastWriteTime, Length
}
Save '02-lure-files.txt' ($lure | Format-Table -AutoSize | Out-String -Width 400)
if ($lure) { Flag "Lure files found (see 02-lure-files.txt)" }

Write-Host "[3] Git hooks inside any copy of the repo (read only)"
foreach ($d in ($lure | Where-Object { Test-Path (Join-Path $_.FullName '.git') })) {
  $h = Join-Path $d.FullName '.git\hooks'
  $hooks = Get-ChildItem $h -File | Where-Object Name -notlike '*.sample'
  if ($hooks) { Flag "Non-sample git hooks in $h"; Save "03-hooks-$($d.CreationTime.ToString('yyyyMMddHHmm')).txt" ($hooks | Select-Object Name, CreationTime, LastWriteTime, Length | Out-String) }
  if (Test-Path (Join-Path $d.FullName '.git\logs\HEAD')) {
    Save "03-githead-$($d.CreationTime.ToString('yyyyMMddHHmm')).txt" (Get-Content (Join-Path $d.FullName '.git\logs\HEAD'))
    Flag "Git has been used in $($d.FullName) (checkout history exists)"
  }
}

Write-Host "[4] Loader code anywhere in user folders (text search)"
$markers = 'fetchPastebinContent','===END===','LENGTH_MARKER_LENGTH','pastebin.com/m5phAFf6','/api/w | cmd','cleverstack-ext30341','vercel.app/api/w','vercel.app/api/m'
$hits = foreach ($r in $roots) {
  Get-ChildItem -Path $r -Recurse -Force -File -Attributes !Offline -ErrorAction SilentlyContinue |
    Where-Object { $_.Length -lt 2MB -and $_.FullName -notmatch '\\(node_modules|\.git\\objects|WinSxS)\\' } |
    Select-String -Pattern $markers -SimpleMatch -List -ErrorAction SilentlyContinue |
    Select-Object Path, Line
}
Save '04-loader-hits.txt' ($hits | Format-List | Out-String -Width 400)
if ($hits) { Flag "Loader code markers found (see 04-loader-hits.txt)" }

Write-Host "[4b] Malicious git hooks in every repo"
$hookHits = foreach ($r in $roots) {
  Get-ChildItem -Path $r -Recurse -Force -Directory -Filter hooks -ErrorAction SilentlyContinue |
    Where-Object { $_.Parent.Name -eq '.git' } |
    ForEach-Object { Get-ChildItem $_.FullName -File | Where-Object Name -notlike '*.sample' } |
    Where-Object { Select-String -Path $_.FullName -Pattern 'vercel.app/api','api/w','curl.exe -s','| cmd' -SimpleMatch -Quiet } |
    Select-Object FullName, CreationTime, LastWriteTime
}
Save '04b-malicious-hooks.txt' ($hookHits | Format-Table -AutoSize | Out-String -Width 400)
if ($hookHits) { Flag "MALICIOUS GIT HOOKS FOUND (see 04b-malicious-hooks.txt). Do not run git in those repos." }

Write-Host "[5] Persistence: scheduled tasks, Run keys, Startup folders, WMI"
$tasks = Get-ScheduledTask | ForEach-Object {
  $a = ($_.Actions | ForEach-Object { "$($_.Execute) $($_.Arguments)" }) -join ' ; '
  [pscustomobject]@{ Path = $_.TaskPath + $_.TaskName; Action = $a; Author = $_.Author; Date = $_.Date }
}
$badTasks = $tasks | Where-Object { $_.Action -match 'node|curl|pastebin|api/w|wscript|mshta|powershell.*-enc|\\AppData\\' }
Save '05-tasks-all.txt' ($tasks | Format-Table -AutoSize | Out-String -Width 400)
Save '05-tasks-suspicious.txt' ($badTasks | Format-List | Out-String -Width 400)
if ($badTasks) { Flag "Suspicious scheduled tasks (see 05-tasks-suspicious.txt)" }

$runKeys = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run','HKCU:\Software\Microsoft\Windows\CurrentVersion\RunOnce',
           'HKLM:\Software\Microsoft\Windows\CurrentVersion\Run','HKLM:\Software\Microsoft\Windows\CurrentVersion\RunOnce',
           'HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Run'
$run = foreach ($k in $runKeys) { $p = Get-ItemProperty $k; if ($p) { $p.PSObject.Properties | Where-Object Name -notlike 'PS*' | ForEach-Object { "$k | $($_.Name) = $($_.Value)" } } }
Save '05-run-keys.txt' $run
if ($run -match 'node|curl|pastebin|api/w') { Flag "Suspicious Run key entries" }

$startup = Get-ChildItem "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup","$env:ProgramData\Microsoft\Windows\Start Menu\Programs\Startup" -Force |
  Select-Object FullName, CreationTime, LastWriteTime
Save '05-startup-folders.txt' ($startup | Format-Table -AutoSize | Out-String -Width 400)

$wmi = Get-CimInstance -Namespace root\subscription -ClassName CommandLineEventConsumer | Select-Object Name, CommandLineTemplate
Save '05-wmi-consumers.txt' ($wmi | Format-List | Out-String)
if ($wmi) { Flag "WMI command-line event consumers exist (unusual)" }

Write-Host "[6] Files created in AppData around the lure dates"
$recent = Get-ChildItem "$env:APPDATA","$env:LOCALAPPDATA","$env:ProgramData" -Recurse -Force -File -ErrorAction SilentlyContinue |
  Where-Object { $_.CreationTime -ge [datetime]'2026-07-20' -and $_.CreationTime -le [datetime]'2026-08-20' -and $_.Extension -in '.js','.cjs','.mjs','.cmd','.bat','.ps1','.vbs','.exe','.dll','' -and $_.FullName -notmatch '\\(Microsoft\\Edge|Google\\Chrome|Packages|Temp\\.*\.tmp|node_modules|npm-cache)\\' } |
  Select-Object CreationTime, Length, FullName | Sort-Object CreationTime
Save '06-appdata-new-files.txt' ($recent | Format-Table -AutoSize | Out-String -Width 400)

Write-Host "[7] Command history and Defender"
Save '07-powershell-history.txt' (Get-Content "$env:APPDATA\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt" | Select-String 'git|node|npm|curl|pixeldrain|Healthcare|pastebin')
Save '07-defender-detections.txt' (Get-MpThreatDetection | Select-Object InitialDetectionTime, ProcessName, Resources, ThreatID | Format-List | Out-String -Width 400)
Save '07-defender-status.txt' (Get-MpComputerStatus | Select-Object AMRunningMode, RealTimeProtectionEnabled, AntivirusSignatureLastUpdated | Format-List | Out-String)

Write-Host "[8] Browser history for the lure links"
foreach ($hist in (Get-ChildItem "$env:LOCALAPPDATA\Google\Chrome\User Data\*\History","$env:LOCALAPPDATA\Microsoft\Edge\User Data\*\History" -Force)) {
  $tmp = Join-Path $env:TEMP ("h-" + [guid]::NewGuid() + ".db"); Copy-Item $hist.FullName $tmp
  $txt = [System.Text.Encoding]::ASCII.GetString([IO.File]::ReadAllBytes($tmp))
  $m = [regex]::Matches($txt, 'https?://[\x21-\x7e]*(pixeldrain|imindstechnology|pastebin)[\x21-\x7e]*') | ForEach-Object Value | Select-Object -Unique
  if ($m) { Flag "Lure links in browser history: $($hist.FullName)"; Save "08-browser-$([guid]::NewGuid().ToString().Substring(0,6)).txt" (@($hist.FullName) + $m) }
  Remove-Item $tmp -Force
}

Write-Host ""
if ($flags.Count -eq 0) { $summary = "NO FLAGS: no sign of the lure repo, loader code or persistence was found." }
else { $summary = "FLAGS FOUND:`r`n" + ($flags -join "`r`n") }
Save '00-SUMMARY.txt' @("Computer: $env:COMPUTERNAME  User: $env:USERNAME  Run: $(Get-Date)", $summary)
Compress-Archive -Path $out -DestinationPath "$out.zip" -Force
Write-Host $summary -ForegroundColor Yellow
Write-Host "Results: $out.zip"
