# Read-only AWS activity audit for the Bryt security incident.
# Focus: anomalous activity by the (possibly compromised) identity "Rhys" over the last N days,
# plus high-signal persistence / evasion / exfil / compute-abuse events by ANY actor.
#
# It ONLY calls read-only APIs (sts:GetCallerIdentity, cloudtrail:LookupEvents,
# iam:Get*/List*/GenerateCredentialReport, guardduty:List*/Get*, ec2:Describe*). It changes nothing.
#
# Prereqs: AWS CLI v2 on PATH, named profiles already configured (SSO or keys).
#
# Example:
#   powershell -ExecutionPolicy Bypass -File .\audit-aws.ps1 `
#       -Profiles bryt-inv-prod,bryt-inv-phidex,bryt-inv-sagemaker `
#       -Identities rhys.jacob@d55.co.uk,rhys.jacob+unified-engineer@d55.co.uk `
#       -Days 30
#
# IMPORTANT: CloudTrail's Username lookup attribute is an EXACT match, not a substring.
# Under Identity Center the session Username is the full SSO login (incl. +persona variants),
# so pass every variant via -Identities. The script does one exact lookup per variant.
# -IdentityLabel is only used for reporting and for loose IAM-user name matching.

[CmdletBinding()]
param(
  [Parameter(Mandatory = $true)] [string[]] $Profiles,
  [Parameter(Mandatory = $true)] [string[]] $Identities,
  [string]   $IdentityLabel = 'rhys.jacob',
  [int]      $Days          = 30,
  [string[]] $Regions       = @('eu-west-1','eu-west-2','us-east-1'),
  [string]   $MgmtProfile   = '',
  [string]   $Prefix        = '',
  [switch]   $AllRegions
)

$ErrorActionPreference = 'SilentlyContinue'
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
# Optional folder prefix (e.g. -Prefix d55  ->  d55-aws-audit-<stamp>).
$folderName = if ($Prefix) { "$Prefix-aws-audit-$stamp" } else { "aws-audit-$stamp" }
$out   = Join-Path $PSScriptRoot $folderName
New-Item -ItemType Directory -Path $out -Force | Out-Null

$startTime = (Get-Date).ToUniversalTime().AddDays(-$Days).ToString('yyyy-MM-ddTHH:mm:ssZ')
$winStart  = (Get-Date).AddDays(-$Days)
$flags = New-Object System.Collections.Generic.List[string]
function Flag($msg) { $flags.Add($msg); Write-Host "FLAG: $msg" -ForegroundColor Red }
function Save {
  # Accepts data either positionally (Save $path $data) OR via the pipeline (X | Save $path).
  param(
    [Parameter(Mandatory)][string] $path,
    [Parameter(ValueFromPipeline)] $data
  )
  begin { $buf = New-Object System.Collections.Generic.List[object] }
  process { if ($null -ne $data) { $buf.Add($data) } }
  end { $buf | Out-File -FilePath $path -Width 500 -Encoding utf8 }
}

# High-signal event names to surface regardless of who did them.
$sigFlat = @(
  'CreateUser','CreateAccessKey','CreateLoginProfile','UpdateLoginProfile','AttachUserPolicy',
  'PutUserPolicy','AttachRolePolicy','PutRolePolicy','CreateRole','UpdateAssumeRolePolicy',
  'AddUserToGroup','CreateVirtualMFADevice','EnableMFADevice','DeactivateMFADevice',
  'CreatePolicyVersion','CreateServiceSpecificCredential',
  'StopLogging','DeleteTrail','UpdateTrail','PutEventSelectors','DeleteFlowLogs','DeleteDetector',
  'UpdateDetector','DisassociateFromMasterAccount','StopConfigurationRecorder','DeleteConfigRule',
  'DeleteLogGroup','PutRetentionPolicy',
  'GetSecretValue','BatchGetSecretValue','GetParameter','GetParameters','GetParametersByPath',
  'ModifySnapshotAttribute','ModifyImageAttribute','CreateImage','ModifyDBSnapshotAttribute',
  'CopyDBSnapshot','CreateDBSnapshot','PutBucketPolicy','PutBucketAcl','RestoreDBInstanceFromDBSnapshot',
  'RunInstances','RequestSpotInstances','CreateKeyPair','ImportKeyPair',
  'AuthorizeSecurityGroupIngress','ModifyInstanceAttribute'
) | Select-Object -Unique

function Invoke-Aws {
  param([string]$Profile, [string[]]$AwsArgs)
  $json = & aws @AwsArgs --profile $Profile --output json 2>$null
  if ($LASTEXITCODE -ne 0 -or -not $json) { return $null }
  try { return ($json | ConvertFrom-Json) } catch { return $null }
}

function Get-CloudTrailEvents {
  # Regional lookup-events by Username (EXACT match) for each identity variant, over the window.
  param([string]$Profile, [string]$Region, [string[]]$Users)
  $events = @()
  foreach ($user in $Users) {
    $raw = & aws cloudtrail lookup-events --profile $Profile --region $Region --output json --start-time $startTime --lookup-attributes "AttributeKey=Username,AttributeValue=$user" --max-items 5000 2>$null
    if ($LASTEXITCODE -ne 0 -or -not $raw) { continue }
    try { $obj = $raw | ConvertFrom-Json } catch { continue }
    foreach ($e in $obj.Events) {
      $ct = $null
      try { $ct = $e.CloudTrailEvent | ConvertFrom-Json } catch { }
      $events += [pscustomobject]@{
        Time      = $e.EventTime
        Event     = $e.EventName
        User      = $e.Username
        Region    = $Region
        SourceIP  = $ct.sourceIPAddress
        UserAgent = $ct.userAgent
        ErrorCode = $ct.errorCode
        Account   = $ct.recipientAccountId
      }
    }
  }
  return $events
}

function Get-AnyActorEvent {
  param([string]$Profile, [string]$Region, [string]$EventName)
  $raw = & aws cloudtrail lookup-events --profile $Profile --region $Region --output json --start-time $startTime --lookup-attributes "AttributeKey=EventName,AttributeValue=$EventName" --max-items 500 2>$null
  if ($LASTEXITCODE -ne 0 -or -not $raw) { return @() }
  try { $obj = $raw | ConvertFrom-Json } catch { return @() }
  $rows = @()
  foreach ($e in $obj.Events) {
    $ct = $null
    try { $ct = $e.CloudTrailEvent | ConvertFrom-Json } catch { }
    $rows += [pscustomobject]@{ Time = $e.EventTime; Event = $e.EventName; User = $e.Username; Region = $Region; SourceIP = $ct.sourceIPAddress }
  }
  return $rows
}

if ($AllRegions) {
  $r = Invoke-Aws -Profile $Profiles[0] -AwsArgs @('ec2','describe-regions','--all-regions','--query','Regions[].RegionName')
  $regionList = if ($r) { $r } else { $Regions }
} else {
  $regionList = $Regions
}

Write-Host "Audit window: since $startTime  |  Identities: $($Identities.Count) variant(s) of '$IdentityLabel'  |  Regions: $($regionList -join ', ')" -ForegroundColor Cyan

foreach ($profile in $Profiles) {
  Write-Host "`n=== Profile: $profile ===" -ForegroundColor Green
  $ident = Invoke-Aws -Profile $profile -AwsArgs @('sts','get-caller-identity')
  if (-not $ident) {
    Flag "[$profile] could not authenticate / call sts:GetCallerIdentity - skipping"
    continue
  }
  $acct = $ident.Account
  $adir = Join-Path $out "$profile-$acct"
  New-Item -ItemType Directory -Path $adir -Force | Out-Null
  $ident | ConvertTo-Json | Save (Join-Path $adir 'caller-identity.json')

  # ---- 1. CloudTrail events by the identity, across regions ----
  $allEvents = @()
  foreach ($region in $regionList) {
    $ev = Get-CloudTrailEvents -Profile $profile -Region $region -Users $Identities
    if ($ev.Count) { $allEvents += $ev }
  }
  $allEvents = $allEvents | Sort-Object Time
  $allEvents | ConvertTo-Json -Depth 4 | Save (Join-Path $adir '01-cloudtrail-identity-raw.json')

  if ($allEvents.Count) {
    ($allEvents | Group-Object Event    | Sort-Object Count -Descending | Select-Object Count,Name | Format-Table -Auto | Out-String -Width 200) | Save (Join-Path $adir '01a-by-event.txt')
    ($allEvents | Group-Object SourceIP | Sort-Object Count -Descending | Select-Object Count,Name | Format-Table -Auto | Out-String -Width 200) | Save (Join-Path $adir '01b-by-sourceip.txt')
    ($allEvents | Group-Object Region   | Sort-Object Count -Descending | Select-Object Count,Name | Format-Table -Auto | Out-String -Width 200) | Save (Join-Path $adir '01c-by-region.txt')
    ($allEvents | Group-Object { ([datetime]$_.Time).ToString('yyyy-MM-dd') } | Select-Object Count,Name | Format-Table -Auto | Out-String -Width 200) | Save (Join-Path $adir '01d-by-day.txt')

    $hot = $allEvents | Where-Object { $sigFlat -contains $_.Event }
    if ($hot.Count) {
      ($hot | Format-Table Time,Event,User,Region,SourceIP,ErrorCode -Auto | Out-String -Width 300) | Save (Join-Path $adir '01e-HIGH-SIGNAL-by-identity.txt')
      Flag "[$profile] $($hot.Count) high-signal event(s) by '$IdentityLabel' (see 01e-HIGH-SIGNAL-by-identity.txt)"
    }
    $ips = $allEvents | Select-Object -ExpandProperty SourceIP | Sort-Object -Unique
    Save (Join-Path $adir '01f-distinct-source-ips.txt') $ips
  } else {
    Write-Host "  no CloudTrail events matched the supplied identities in window (check exact SSO session-name format)" -ForegroundColor Yellow
  }

  # ---- 2. High-signal events by ANY actor (persistence/evasion in the window) ----
  foreach ($region in $regionList) {
    foreach ($en in @('CreateUser','CreateAccessKey','CreateLoginProfile','StopLogging','DeleteTrail','CreateKeyPair','RunInstances')) {
      $rows = Get-AnyActorEvent -Profile $profile -Region $region -EventName $en
      if ($rows.Count) {
        ($rows | Format-Table -Auto | Out-String -Width 300) | Save (Join-Path $adir "02-anyactor-$region-$en.txt")
        Flag "[$profile/$region] $($rows.Count) x $en in window (see 02-anyactor-$region-$en.txt)"
      }
    }
  }

  # ---- 3. IAM current-state snapshot ----
  & aws iam generate-credential-report --profile $profile --output json 2>$null | Out-Null
  Start-Sleep -Seconds 2
  $cr = & aws iam get-credential-report --profile $profile --query Content --output text 2>$null
  if ($cr) {
    try { [System.Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($cr)) | Save (Join-Path $adir '03-credential-report.csv') } catch { }
  }
  $users = Invoke-Aws -Profile $profile -AwsArgs @('iam','list-users')
  if ($users) {
    $newUsers = $users.Users | Where-Object { [datetime]$_.CreateDate -ge $winStart }
    if ($newUsers) {
      ($newUsers | Format-Table UserName,CreateDate -Auto | Out-String) | Save (Join-Path $adir '03a-new-users.txt')
      Flag "[$profile] IAM user(s) created in window (see 03a-new-users.txt)"
    }
    $keyRows = foreach ($u in $users.Users) {
      $ak = Invoke-Aws -Profile $profile -AwsArgs @('iam','list-access-keys','--user-name',$u.UserName)
      foreach ($k in $ak.AccessKeyMetadata) {
        $lu = Invoke-Aws -Profile $profile -AwsArgs @('iam','get-access-key-last-used','--access-key-id',$k.AccessKeyId)
        [pscustomobject]@{
          User     = $u.UserName
          KeyId    = $k.AccessKeyId
          Status   = $k.Status
          Created  = $k.CreateDate
          LastUsed = $lu.AccessKeyLastUsed.LastUsedDate
          Svc      = $lu.AccessKeyLastUsed.ServiceName
          Region   = $lu.AccessKeyLastUsed.Region
        }
      }
    }
    ($keyRows | Sort-Object User | Format-Table -Auto | Out-String -Width 300) | Save (Join-Path $adir '03b-access-keys.txt')
    $newKeys = $keyRows | Where-Object { $_.Created -and [datetime]$_.Created -ge $winStart }
    if ($newKeys) { Flag "[$profile] access key(s) created in window (see 03b-access-keys.txt)" }
    $rhys = $users.Users | Where-Object { $_.UserName -match $IdentityLabel }
    foreach ($u in $rhys) {
      $mfa = Invoke-Aws -Profile $profile -AwsArgs @('iam','list-mfa-devices','--user-name',$u.UserName)
      $mfa | ConvertTo-Json -Depth 4 | Save (Join-Path $adir "03c-mfa-$($u.UserName).json")
    }
  }

  # ---- 4. GuardDuty findings in the window ----
  $gdSince = [DateTimeOffset]::UtcNow.AddDays(-$Days).ToUnixTimeMilliseconds()
  $gdCriteria = '{"Criterion":{"updatedAt":{"Gte":' + $gdSince + '}}}'
  foreach ($region in $regionList) {
    $det = Invoke-Aws -Profile $profile -AwsArgs @('guardduty','list-detectors','--region',$region)
    if (-not $det.DetectorIds) {
      Save (Join-Path $adir "04-guardduty-$region.txt") 'No GuardDuty detector in this region (coverage gap).'
      continue
    }
    foreach ($d in $det.DetectorIds) {
      $fids = Invoke-Aws -Profile $profile -AwsArgs @('guardduty','list-findings','--region',$region,'--detector-id',$d,'--finding-criteria',$gdCriteria)
      if ($fids.FindingIds.Count) {
        $f = Invoke-Aws -Profile $profile -AwsArgs (@('guardduty','get-findings','--region',$region,'--detector-id',$d,'--finding-ids') + $fids.FindingIds)
        $f | ConvertTo-Json -Depth 6 | Save (Join-Path $adir "04-guardduty-$region.json")
        ($f.Findings | Select-Object Type,Severity,Title,@{n='Updated';e={$_.UpdatedAt}} | Sort-Object Severity -Descending | Format-Table -Auto | Out-String -Width 300) | Save (Join-Path $adir "04-guardduty-$region.txt")
        Flag "[$profile/$region] $($fids.FindingIds.Count) GuardDuty finding(s) in window (see 04-guardduty-$region.txt)"
      }
    }
  }

  # ---- 5. EC2 recent launches / new key pairs (compute-abuse cue) ----
  foreach ($region in $regionList) {
    $inst = Invoke-Aws -Profile $profile -AwsArgs @('ec2','describe-instances','--region',$region,'--query','Reservations[].Instances[].{Id:InstanceId,Type:InstanceType,State:State.Name,Launch:LaunchTime,Key:KeyName,Az:Placement.AvailabilityZone}')
    if ($inst) {
      $recent = $inst | Where-Object { $_.Launch -and [datetime]$_.Launch -ge $winStart }
      if ($recent) {
        ($recent | Format-Table -Auto | Out-String -Width 300) | Save (Join-Path $adir "05-ec2-recent-$region.txt")
        Flag "[$profile/$region] EC2 instance(s) launched in window (see 05-ec2-recent-$region.txt)"
      }
    }
    $kp = Invoke-Aws -Profile $profile -AwsArgs @('ec2','describe-key-pairs','--region',$region,'--query','KeyPairs[].{Name:KeyName,Id:KeyPairId,Created:CreateTime}')
    if ($kp) {
      $newkp = $kp | Where-Object { $_.Created -and [datetime]$_.Created -ge $winStart }
      if ($newkp) {
        ($newkp | Format-Table -Auto | Out-String) | Save (Join-Path $adir "05-keypairs-new-$region.txt")
        Flag "[$profile/$region] EC2 key pair(s) created in window (see 05-keypairs-new-$region.txt)"
      }
    }
  }
}

# ---- Management account: SSO / console sign-in events ----
if ($MgmtProfile) {
  Write-Host "`n=== Mgmt profile (sign-in/SSO): $MgmtProfile ===" -ForegroundColor Green
  $mdir = Join-Path $out "MGMT-$MgmtProfile"
  New-Item -ItemType Directory -Path $mdir -Force | Out-Null
  foreach ($region in (@($regionList) + 'us-east-1' | Select-Object -Unique)) {
    $login = Get-CloudTrailEvents -Profile $MgmtProfile -Region $region -Users $Identities
    if ($login.Count) {
      ($login | Where-Object { $_.Event -match 'ConsoleLogin|Authenticate|Federate|AssumeRole' } | Format-Table Time,Event,Region,SourceIP,ErrorCode -Auto | Out-String -Width 300) | Save (Join-Path $mdir "signin-$region.txt")
    }
  }
}

# ---- Summary ----
if ($flags.Count -eq 0) {
  $summary = "NO FLAGS: no high-signal activity surfaced for '$IdentityLabel' or by any actor in the last $Days days across the scanned profiles/regions."
} else {
  $summary = "FLAGS FOUND ($($flags.Count)):`r`n" + ($flags -join "`r`n")
}
Save (Join-Path $out '00-SUMMARY.txt') @(
  "AWS activity audit  |  Run: $(Get-Date)  |  Window: last $Days days (since $startTime)",
  "Identity: '$IdentityLabel' ($($Identities.Count) variants)  |  Profiles: $($Profiles -join ', ')",
  '',
  $summary,
  '',
  'NOTE: lookup-events covers management events for the last 90 days only.',
  'Bulk S3 GetObject exfil is NOT visible here unless S3 data events are captured on a trail (then query via Athena / CloudTrail Lake).'
)
Write-Host "`n$summary" -ForegroundColor Yellow
Write-Host "`nResults: $out" -ForegroundColor Cyan
