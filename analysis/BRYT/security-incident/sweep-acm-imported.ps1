# Read-only sweep: enumerate IMPORTED ACM certificates across the bryt-inv-* read-only profiles.
#
# Why imported only: ACM-issued (AMAZON_ISSUED) certs keep their private key inside ACM and it is
# NOT exportable, so a credential-chain compromise does not expose that key. IMPORTED certs had
# their private key generated OUTSIDE AWS and uploaded, so the key existed somewhere the compromised
# endpoint could have reached (dev machine, repo, Secrets Manager, SSM). Those are the certs worth
# triaging for reissue + reimport. This sweep lists them per account/region with expiry and consumers.
#
# It ONLY calls read-only APIs (sts:GetCallerIdentity, ec2:DescribeRegions,
# acm:ListCertificates, acm:DescribeCertificate). It changes nothing.
#
# Prereqs: AWS CLI v2 on PATH, bryt-inv-* profiles already configured (SSO).
#
# Example:
#   powershell -ExecutionPolicy Bypass -File .\sweep-acm-imported.ps1

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
$out   = Join-Path $PSScriptRoot "aws-audit-acm-$stamp"
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
    # Server-side filter to IMPORTED certs; still describe each for expiry + consumers.
    $list = Invoke-Aws -Profile $profile -AwsArgs @('acm','list-certificates','--region',$region,'--includes','keyTypes=RSA_1024,RSA_2048,RSA_3072,RSA_4096,EC_prime256v1,EC_secp384r1,EC_secp521r1','--query','CertificateSummaryList[].CertificateArn')
    if (-not $list) { continue }
    foreach ($arn in $list) {
      $d = Invoke-Aws -Profile $profile -AwsArgs @('acm','describe-certificate','--region',$region,'--certificate-arn',$arn)
      $c = $d.Certificate
      if (-not $c -or $c.Type -ne 'IMPORTED') { continue }
      $inUse = @($c.InUseBy)
      $row = [pscustomobject]@{
        Profile      = $profile
        Account      = $acct
        Region       = $region
        DomainName   = $c.DomainName
        Status       = $c.Status
        KeyAlgorithm = $c.KeyAlgorithm
        ImportedAt   = $c.ImportedAt
        NotAfter     = $c.NotAfter
        InUseCount   = $inUse.Count
        InUseBy      = ($inUse -join '; ')
        SANs         = (@($c.SubjectAlternativeNames) -join '; ')
        CertificateArn = $arn
      }
      $all.Add($row)
      Write-Host ("  {0,-15} {1,-30} imported={2} expires={3} inUse={4}" -f $region, $c.DomainName, $c.ImportedAt, $c.NotAfter, $inUse.Count) -ForegroundColor Gray
    }
  }
}

# Combined outputs
if ($all.Count) {
  $all = $all | Sort-Object Account, Region, DomainName
  $all | Export-Csv -Path (Join-Path $out 'acm-imported.csv') -NoTypeInformation -Encoding utf8
  ($all | Format-Table Profile,Account,Region,DomainName,Status,ImportedAt,NotAfter,InUseCount -Auto | Out-String -Width 400) |
    Out-File -FilePath (Join-Path $out 'acm-imported.txt') -Encoding utf8 -Width 400
} else {
  'No IMPORTED ACM certificates found across the swept profiles/regions.' |
    Out-File -FilePath (Join-Path $out 'acm-imported.txt') -Encoding utf8
}

# Summary
$byAcct = $all | Group-Object Account | Sort-Object Name |
  ForEach-Object { "  {0,-14} {1} imported cert(s)" -f $_.Name, $_.Count }
$summary = @(
  "ACM imported-certificate sweep  |  Run: $(Get-Date)",
  "Profiles: $($Profiles.Count)  |  Total IMPORTED certs found: $($all.Count)",
  "Distinct accounts with imported certs: $(($all | Select-Object -ExpandProperty Account -Unique).Count)",
  '',
  'Per account:'
) + @($byAcct) + @(
  '',
  'NOTE: private keys for IMPORTED certs originated outside AWS - trace where each key was',
  'generated/stored; if that source was reachable from the compromised endpoint, reissue + reimport.'
) | Where-Object { $_ -ne $null }
$summary | Out-File -FilePath (Join-Path $out '00-SUMMARY.txt') -Encoding utf8

Write-Host "`n$($summary -join "`n")" -ForegroundColor Yellow
Write-Host "`nResults: $out" -ForegroundColor Cyan
