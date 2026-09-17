# Read-only sweep: inventory Secrets Manager secrets across the bryt-inv-* read-only profiles.
#
# Purpose: turn "rotate everything" into a concrete worklist of Secrets Manager secrets, with the
# metadata needed to prioritise: whether rotation is enabled, when each was last changed/rotated,
# when last accessed (are there live consumers?), and whether it has been rotated since the incident.
#
# IMPORTANT: this is METADATA ONLY. It does NOT call GetSecretValue / BatchGetSecretValue and never
# reads secret material. It ONLY calls read-only APIs (sts:GetCallerIdentity, ec2:DescribeRegions,
# secretsmanager:ListSecrets). It changes nothing.
#
# Prereqs: AWS CLI v2 on PATH, bryt-inv-* profiles already configured (SSO).
#
# Example:
#   powershell -ExecutionPolicy Bypass -File .\sweep-secrets.ps1 -RotateSince 2026-09-15

[CmdletBinding()]
param(
  [string[]] $Profiles = @(
    'bryt-inv-prod','bryt-inv-audit','bryt-inv-sage','bryt-inv-portal2',
    'bryt-inv-phidex','bryt-inv-dev','bryt-inv-logarchive','bryt-inv-logging',
    'bryt-inv-sagemaker','bryt-inv-test','bryt-inv-uat','bryt-inv-users'
  ),
  # If empty, each account's enabled regions are discovered via ec2:DescribeRegions.
  [string[]] $Regions = @(),
  # Secrets NOT changed/rotated on or after this date are flagged as "needs rotation".
  # Default to the incident window; adjust once the true malware-landing date is confirmed.
  [datetime] $RotateSince = '2026-09-15'
)

$ErrorActionPreference = 'SilentlyContinue'
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$out   = Join-Path $PSScriptRoot "aws-audit-secrets-$stamp"
New-Item -ItemType Directory -Path $out -Force | Out-Null

function Invoke-Aws {
  param([string]$Profile, [string[]]$AwsArgs)
  $json = & aws @AwsArgs --profile $Profile --output json 2>$null
  if ($LASTEXITCODE -ne 0 -or -not $json) { return $null }
  try { return ($json | ConvertFrom-Json) } catch { return $null }
}

function Parse-Date($v) { if ($v) { try { return [datetime]$v } catch { return $null } } return $null }

$all = New-Object System.Collections.Generic.List[object]

foreach ($profile in $Profiles) {
  Write-Host "`n=== Profile: $profile ===" -ForegroundColor Green
  $ident = Invoke-Aws -Profile $profile -AwsArgs @('sts','get-caller-identity')
  if (-not $ident) {
    Write-Host "  could not authenticate / call sts:GetCallerIdentity - skipping" -ForegroundColor Yellow
    continue
  }
  $acct = $ident.Account

  if ($Regions.Count) {
    $regionList = $Regions
  } else {
    $r = Invoke-Aws -Profile $profile -AwsArgs @('ec2','describe-regions','--query','Regions[].RegionName')
    $regionList = if ($r) { $r | Sort-Object } else { @('eu-west-1','eu-west-2','us-east-1') }
  }

  foreach ($region in $regionList) {
    $secrets = Invoke-Aws -Profile $profile -AwsArgs @('secretsmanager','list-secrets','--region',$region,'--query','SecretList[].{Name:Name,Arn:ARN,RotationEnabled:RotationEnabled,LastChanged:LastChangedDate,LastRotated:LastRotatedDate,LastAccessed:LastAccessedDate,NextRotation:NextRotationDate,RotationDays:RotationRules.AutomaticallyAfterDays,Owning:OwningService,Kms:KmsKeyId,Created:CreatedDate}')
    if (-not $secrets) { continue }
    foreach ($s in $secrets) {
      $changed  = Parse-Date $s.LastChanged
      $rotated  = Parse-Date $s.LastRotated
      $accessed = Parse-Date $s.LastAccessed
      # "Rotated since incident" = value changed OR rotated on/after the cutoff.
      $ref = @($changed, $rotated) | Where-Object { $_ } | Sort-Object -Descending | Select-Object -First 1
      $rotatedSince = if ($ref) { $ref -ge $RotateSince } else { $false }
      $row = [pscustomobject]@{
        Profile        = $profile
        Account        = $acct
        Region         = $region
        Name           = $s.Name
        RotationEnabled= [bool]$s.RotationEnabled
        RotationDays   = $s.RotationDays
        LastChanged    = if ($changed)  { $changed.ToString('yyyy-MM-dd') } else { '' }
        LastRotated    = if ($rotated)  { $rotated.ToString('yyyy-MM-dd') } else { 'never' }
        LastAccessed   = if ($accessed) { $accessed.ToString('yyyy-MM-dd') } else { '' }
        RotatedSinceIncident = $rotatedSince
        OwningService  = $s.Owning
        KmsKeyId       = $s.Kms
        Arn            = $s.Arn
      }
      $all.Add($row)
      $mark = if ($rotatedSince) { 'ok ' } else { 'ROT' }
      Write-Host ("  [{0}] {1,-12} {2,-40} rotEnabled={3} lastChanged={4}" -f $mark, $region, $s.Name, [bool]$s.RotationEnabled, $row.LastChanged) -ForegroundColor Gray
    }
  }
}

# Combined outputs
if ($all.Count) {
  $all = $all | Sort-Object Account, Region, Name
  $all | Export-Csv -Path (Join-Path $out 'secrets.csv') -NoTypeInformation -Encoding utf8
  ($all | Format-Table Account,Region,Name,RotationEnabled,LastChanged,LastRotated,LastAccessed,RotatedSinceIncident -Auto | Out-String -Width 500) |
    Out-File -FilePath (Join-Path $out 'secrets.txt') -Encoding utf8 -Width 500
  # Worklist: secrets not rotated/changed since the incident cutoff (customer-managed only).
  $worklist = $all | Where-Object { -not $_.RotatedSinceIncident -and -not $_.OwningService }
  ($worklist | Format-Table Account,Region,Name,RotationEnabled,LastChanged,LastRotated -Auto | Out-String -Width 500) |
    Out-File -FilePath (Join-Path $out 'worklist-needs-rotation.txt') -Encoding utf8 -Width 500
} else {
  'No Secrets Manager secrets found across the swept profiles/regions.' |
    Out-File -FilePath (Join-Path $out 'secrets.txt') -Encoding utf8
}

# Summary
$needsRotation = @($all | Where-Object { -not $_.RotatedSinceIncident -and -not $_.OwningService })
$rotationOff   = @($all | Where-Object { -not $_.RotationEnabled -and -not $_.OwningService })
$awsManaged    = @($all | Where-Object { $_.OwningService })
$byAcct = $all | Group-Object Account | Sort-Object Name |
  ForEach-Object { "  {0,-14} {1} secret(s)" -f $_.Name, $_.Count }
$summary = @(
  "Secrets Manager sweep  |  Run: $(Get-Date)  |  Rotate-since cutoff: $($RotateSince.ToString('yyyy-MM-dd'))",
  "Profiles: $($Profiles.Count)  |  Total secrets found: $($all.Count)",
  "Distinct accounts with secrets: $(($all | Select-Object -ExpandProperty Account -Unique).Count)",
  "Customer-managed, NOT rotated since cutoff (rotate these): $($needsRotation.Count)",
  "Rotation disabled (customer-managed): $($rotationOff.Count)",
  "AWS-managed secrets (OwningService set, rotate via owning service): $($awsManaged.Count)",
  '',
  'Per account:'
) + @($byAcct) + @(
  '',
  'NOTE: metadata only - no secret values were read. "RotatedSinceIncident" is based on',
  'LastChangedDate/LastRotatedDate vs the cutoff; confirm the true malware-landing date and rerun.'
) | Where-Object { $_ -ne $null }
$summary | Out-File -FilePath (Join-Path $out '00-SUMMARY.txt') -Encoding utf8

Write-Host "`n$($summary -join "`n")" -ForegroundColor Yellow
Write-Host "`nResults: $out" -ForegroundColor Cyan
