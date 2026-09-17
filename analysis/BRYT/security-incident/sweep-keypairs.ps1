# Read-only sweep: enumerate ALL EC2 key pairs across the bryt-inv-* read-only profiles.
#
# Purpose: turn "rotate everything" into a concrete worklist of EC2 key pairs that currently
# exist, per account and region. Key pairs are a REGIONAL resource, so this sweeps every
# enabled region in each account to avoid missing any.
#
# It ONLY calls read-only APIs (sts:GetCallerIdentity, ec2:DescribeRegions,
# ec2:DescribeKeyPairs). It changes nothing.
#
# Prereqs: AWS CLI v2 on PATH, bryt-inv-* profiles already configured (SSO).
#
# Example:
#   powershell -ExecutionPolicy Bypass -File .\sweep-keypairs.ps1

[CmdletBinding()]
param(
  [string[]] $Profiles = @(
    'bryt-inv-prod','bryt-inv-audit','bryt-inv-sage','bryt-inv-portal2',
    'bryt-inv-phidex','bryt-inv-dev','bryt-inv-logarchive','bryt-inv-logging',
    'bryt-inv-sagemaker','bryt-inv-test','bryt-inv-uat','bryt-inv-users'
  ),
  # If empty, each account's enabled regions are discovered via ec2:DescribeRegions.
  [string[]] $Regions = @()
)

$ErrorActionPreference = 'SilentlyContinue'
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$out   = Join-Path $PSScriptRoot "aws-audit-keypairs-$stamp"
New-Item -ItemType Directory -Path $out -Force | Out-Null

function Invoke-Aws {
  param([string]$Profile, [string[]]$AwsArgs)
  $json = & aws @AwsArgs --profile $Profile --output json 2>$null
  if ($LASTEXITCODE -ne 0 -or -not $json) { return $null }
  try { return ($json | ConvertFrom-Json) } catch { return $null }
}

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
    $kp = Invoke-Aws -Profile $profile -AwsArgs @('ec2','describe-key-pairs','--region',$region,'--query','KeyPairs[].{Name:KeyName,Id:KeyPairId,Type:KeyType,Created:CreateTime,Fingerprint:KeyFingerprint}')
    if ($kp) {
      foreach ($k in $kp) {
        $row = [pscustomobject]@{
          Profile     = $profile
          Account     = $acct
          Region      = $region
          Name        = $k.Name
          KeyPairId   = $k.Id
          Type        = $k.Type
          Created     = $k.Created
          Fingerprint = $k.Fingerprint
        }
        $all.Add($row)
        Write-Host ("  {0,-15} {1,-24} {2}" -f $region, $k.Name, $k.Id) -ForegroundColor Gray
      }
    }
  }
}

# Per-account/region breakdown + combined outputs
if ($all.Count) {
  $all = $all | Sort-Object Account, Region, Name
  $all | Export-Csv -Path (Join-Path $out 'keypairs.csv') -NoTypeInformation -Encoding utf8
  ($all | Format-Table Profile,Account,Region,Name,KeyPairId,Type,Created -Auto | Out-String -Width 400) |
    Out-File -FilePath (Join-Path $out 'keypairs.txt') -Encoding utf8 -Width 400
} else {
  'No EC2 key pairs found across the swept profiles/regions.' |
    Out-File -FilePath (Join-Path $out 'keypairs.txt') -Encoding utf8
}

# Summary
$byAcct = $all | Group-Object Account | Sort-Object Name |
  ForEach-Object { "  {0,-14} {1} key pair(s)" -f $_.Name, $_.Count }
$summary = @(
  "EC2 key-pair sweep  |  Run: $(Get-Date)",
  "Profiles: $($Profiles.Count)  |  Total key pairs found: $($all.Count)",
  "Distinct accounts with key pairs: $(($all | Select-Object -ExpandProperty Account -Unique).Count)",
  '',
  'Per account:',
  $byAcct
) | Where-Object { $_ -ne $null }
$summary | Out-File -FilePath (Join-Path $out '00-SUMMARY.txt') -Encoding utf8

Write-Host "`n$($summary -join "`n")" -ForegroundColor Yellow
Write-Host "`nResults: $out" -ForegroundColor Cyan
