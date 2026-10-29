[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)][ValidateSet('Check','Install','Uninstall')][string]$Action,
    [Parameter(Mandatory=$true)][string]$GamePath
)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

function Get-BytesHash([byte[]]$Bytes) {
    $hasher = [System.Security.Cryptography.SHA256]::Create()
    try { return ([BitConverter]::ToString($hasher.ComputeHash($Bytes))).Replace('-','').ToLowerInvariant() }
    finally { $hasher.Dispose() }
}
function Get-FileDigest([string]$Path) {
    $hasher = [System.Security.Cryptography.SHA256]::Create()
    $inputFile = [IO.File]::OpenRead($Path)
    try { return ([BitConverter]::ToString($hasher.ComputeHash($inputFile))).Replace('-','').ToLowerInvariant() }
    finally { $inputFile.Dispose(); $hasher.Dispose() }
}
function Require([bool]$Condition,[string]$Message) {
    if (-not $Condition) { throw $Message }
}
function Confirm-NoGameRunning {
    $running = @(Get-Process -Name POP3,PrinceOfPersia,openjade -ErrorAction SilentlyContinue)
    foreach ($gameProcess in $running) {
        $processPath = $null
        try { $processPath = $gameProcess.Path } catch { }
        Require (-not [string]::IsNullOrWhiteSpace($processPath)) 'Cannot verify a running game process path. Close the game first.'
        $insideTarget = $processPath.StartsWith($gameRoot.TrimEnd('\')+'\',[StringComparison]::OrdinalIgnoreCase)
        Require (-not $insideTarget) 'Close Prince of Persia and OpenJade before changing sound files.'
    }
}

$packageRoot = [IO.Path]::GetFullPath($PSScriptRoot)
$manifestPath = Join-Path $packageRoot 'manifest.json'
$manifest = Get-Content -Raw -LiteralPath $manifestPath | ConvertFrom-Json
Require ($manifest.formatVersion -eq 1) 'Unsupported package format.'
$gameRoot = (Resolve-Path -LiteralPath $GamePath).ProviderPath
$soundRoot = Join-Path $gameRoot 'Sound'
$archivePath = Join-Path $soundRoot 'soundlocal.big'
$fatPath = Join-Path $soundRoot 'soundlocal.fat'
Require (Test-Path -LiteralPath $archivePath -PathType Leaf) 'Missing soundlocal.big.'
Require (Test-Path -LiteralPath $fatPath -PathType Leaf) 'Missing soundlocal.fat.'
Require ((Get-Item -LiteralPath $archivePath).Length -eq $manifest.archiveBytes) 'Unexpected archive size.'
Require ((Get-FileDigest $fatPath) -eq $manifest.fatSha256) 'Unsupported sound FAT. Nothing was changed.'
$currentHash = Get-FileDigest $archivePath
$state = if ($currentHash -eq $manifest.baseSha256) { 'Original' }
         elseif ($currentHash -eq $manifest.patchedSha256) { 'ThisPreviewInstalled' }
         else { 'UnsupportedOrModified' }
$backupRoot = Join-Path $soundRoot 'WW-Prince-Voice-Backups'
$backupPath = Join-Path $backupRoot ('soundlocal.' + $manifest.baseSha256 + '.big')
$receiptPath = Join-Path $soundRoot 'ww-prince-voice-install.json'
if ($Action -eq 'Check') {
    [pscustomobject]@{gamePath=$gameRoot;state=$state;currentSha256=$currentHash;
        replacementCount=@($manifest.patches).Count;backupExists=(Test-Path -LiteralPath $backupPath);
        runtimeTested=$false} | ConvertTo-Json
    exit 0
}
Confirm-NoGameRunning
Require ($state -ne 'UnsupportedOrModified') 'Archive differs from both supported states. Nothing was changed.'
if (($Action -eq 'Install' -and $state -eq 'ThisPreviewInstalled') -or
    ($Action -eq 'Uninstall' -and $state -eq 'Original')) {
    Write-Output "Already in requested state: $state"
    exit 0
}

if ($Action -eq 'Install') {
    Require (-not (Test-Path -LiteralPath $receiptPath)) 'An existing installation receipt needs review before installing.'
    $data = [IO.File]::ReadAllBytes($archivePath)
    Require ((Get-BytesHash $data) -eq $manifest.baseSha256) 'Archive changed during preparation.'
    $cursor = [long]0
    foreach ($patch in @($manifest.patches | Sort-Object start)) {
        Require ($patch.file -match '^patches/[0-9]+\.bin$') 'Unsafe patch filename.'
        $start = [long]$patch.start
        $length = [long]$patch.length
        Require ($start -ge $cursor -and $length -gt 0 -and $start -le ($data.LongLength - $length)) 'Invalid or overlapping patch range.'
        $payloadPath = Join-Path $packageRoot $patch.file
        $payload = [IO.File]::ReadAllBytes($payloadPath)
        Require ($payload.LongLength -eq $length) 'Patch length mismatch.'
        Require ((Get-BytesHash $payload) -eq $patch.sha256) 'Patch checksum mismatch.'
        $old = New-Object byte[] $length
        [Buffer]::BlockCopy($data,[int]$start,$old,0,[int]$length)
        Require ((Get-BytesHash $old) -eq $patch.originalSha256) 'Original patch range does not match.'
        [Buffer]::BlockCopy($payload,0,$data,[int]$start,[int]$length)
        $cursor = $start + $length
    }
    Require ((Get-BytesHash $data) -eq $manifest.patchedSha256) 'Combined patched archive checksum mismatch.'
    if (-not (Test-Path -LiteralPath $backupRoot)) { $null = New-Item -ItemType Directory -Path $backupRoot }
    if (-not (Test-Path -LiteralPath $backupPath)) { Copy-Item -LiteralPath $archivePath -Destination $backupPath }
    Require ((Get-FileDigest $backupPath) -eq $manifest.baseSha256) 'Backup verification failed.'
    $desiredHash = $manifest.patchedSha256
} else {
    Require (Test-Path -LiteralPath $backupPath -PathType Leaf) 'Original backup is missing. Refusing to guess a restore source.'
    Require ((Get-FileDigest $backupPath) -eq $manifest.baseSha256) 'Original backup checksum mismatch.'
    $data = [IO.File]::ReadAllBytes($backupPath)
    $desiredHash = $manifest.baseSha256
    if (Test-Path -LiteralPath $receiptPath) {
        $receipt = Get-Content -Raw -LiteralPath $receiptPath | ConvertFrom-Json
        Require ($receipt.patchedSha256 -eq $manifest.patchedSha256) 'Installation receipt belongs to a different preview.'
    }
}

# The temporary archive is adjacent to the destination, allowing atomic replace.
# Keep recovery files on failure; never delete or recursively remove user paths.
$temporaryPath = Join-Path $soundRoot ('soundlocal.wwvoice.'+[guid]::NewGuid().ToString('N')+'.tmp')
$stream = [IO.File]::Open($temporaryPath,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None)
try { $stream.Write($data,0,$data.Length); $stream.Flush($true) }
finally { $stream.Dispose() }
Require ((Get-FileDigest $temporaryPath) -eq $desiredHash) 'Temporary archive checksum mismatch.'
Confirm-NoGameRunning
Require ((Get-FileDigest $archivePath) -eq $currentHash) 'Game archive changed before replacement. Recovery files were preserved.'
$rollbackPath = Join-Path $backupRoot ('before-'+$Action+'.'+[guid]::NewGuid().ToString('N')+'.big')
[IO.File]::Replace($temporaryPath,$archivePath,$rollbackPath)
Require ((Get-FileDigest $archivePath) -eq $desiredHash) 'Final archive verification failed. Original backup remains available.'
Require ((Get-FileDigest $fatPath) -eq $manifest.fatSha256) 'FAT unexpectedly changed.'
if ($Action -eq 'Install') {
    [pscustomobject]@{package=$manifest.package;patchedSha256=$manifest.patchedSha256;
        baseSha256=$manifest.baseSha256;backupPath=$backupPath;installedAt=[DateTimeOffset]::Now.ToString('o');
        replacementCount=@($manifest.patches).Count;runtimeTested=$false} |
        ConvertTo-Json | Set-Content -LiteralPath $receiptPath -Encoding UTF8
} elseif (Test-Path -LiteralPath $receiptPath) {
    # Only this package's verified receipt is removed. Original backup is kept.
    Remove-Item -LiteralPath $receiptPath
}
[pscustomobject]@{action=$Action;status='VERIFIED';gamePath=$gameRoot;
    archiveSha256=$desiredHash;backupPath=$backupPath;rollbackPath=$rollbackPath;
    fatUnchanged=$true;runtimeTested=$false} | ConvertTo-Json
