[CmdletBinding()]
param(
    [ValidateSet('Install', 'Restore', 'Status')]
    [string]$Action = 'Install',
    [string]$GameDirectory
)

$ErrorActionPreference = 'Stop'
$supportedHash = 'f42f721f1394894b87b4584ca1e9bc0c2be7af71cf39a1a3548925fa9eab7cfa'
$patchedHash = 'f6dd6820334918d915c8d6b70a60b799d3e85b3be9c5a3245d240768be734208'
$stockHash = 'febbabb37d355ebbe51c4e8cd4172ad825870c759b529421f361a13339aa0941'
$offset = 0x5E1380

function Get-Sha256([string]$Path) {
    return (Get-FileHash -Algorithm SHA256 -LiteralPath $Path).Hash.ToLowerInvariant()
}

function Resolve-GamePath {
    if ($GameDirectory) {
        $candidate = [IO.Path]::GetFullPath($GameDirectory)
        if (Test-Path -LiteralPath (Join-Path $candidate 'POP3.EXE')) { return $candidate }
        throw "POP3.EXE was not found in: $candidate"
    }
    $candidates = @(
        (Get-Location).Path,
        'C:\Program Files (x86)\Steam\steamapps\common\Prince of Persia Two Thrones',
        'C:\SteamLibrary\steamapps\common\Prince of Persia Two Thrones',
        'D:\SteamLibrary\steamapps\common\Prince of Persia Two Thrones',
        'E:\SteamLibrary\steamapps\common\Prince of Persia Two Thrones'
    )
    foreach ($candidate in $candidates) {
        if (Test-Path -LiteralPath (Join-Path $candidate 'POP3.EXE')) {
            return [IO.Path]::GetFullPath($candidate)
        }
    }
    throw 'Game folder not found. Pass -GameDirectory with the Prince of Persia Two Thrones folder.'
}

function Assert-GameClosed {
    if (Get-Process -Name 'POP3' -ErrorAction SilentlyContinue) {
        throw 'Close Prince of Persia: The Two Thrones before changing POP3.EXE.'
    }
}

$game = Resolve-GamePath
$exe = Join-Path $game 'POP3.EXE'
$managerBackup = Join-Path $game 'POP3.EXE.popmm.bak'
$backupDirectory = Join-Path $game 'WWPrinceWaterSwordBackup'
$backup = Join-Path $backupDirectory 'POP3.EXE.before-interpreter-patch'
$currentHash = Get-Sha256 $exe

if ($Action -eq 'Status') {
    [pscustomobject]@{
        GameDirectory = $game
        ExeSha256 = $currentHash
        State = if ($currentHash -eq $patchedHash) { 'Patched' } elseif ($currentHash -eq $supportedHash) { 'Ready' } else { 'UnsupportedOrChanged' }
        BackupPresent = Test-Path -LiteralPath $backup
    }
    exit 0
}

Assert-GameClosed

if ($Action -eq 'Install') {
    if ($currentHash -eq $patchedHash) {
        Write-Output 'Steam interpreter patch is already installed.'
        exit 0
    }
    if ($currentHash -ne $supportedHash) {
        throw "Unsupported POP3.EXE hash: $currentHash. Enable PoP Mod Manager Large assets first; this patch refuses unknown executables."
    }
    if (-not (Test-Path -LiteralPath $managerBackup) -or (Get-Sha256 $managerBackup) -ne $stockHash) {
        throw 'The verified PoP Mod Manager stock executable backup is missing or changed. Nothing was modified.'
    }
    New-Item -ItemType Directory -Path $backupDirectory -Force | Out-Null
    if (Test-Path -LiteralPath $backup) {
        if ((Get-Sha256 $backup) -ne $supportedHash) { throw 'Existing interpreter-patch backup is not the supported executable.' }
    } else {
        Copy-Item -LiteralPath $exe -Destination $backup
    }
    $bytes = [IO.File]::ReadAllBytes($exe)
    if ($bytes.Length -ne 6344704 -or [BitConverter]::ToUInt32($bytes, $offset) -ne 1) {
        throw 'Executable layout or interpreter flag is unexpected. Nothing was modified.'
    }
    [BitConverter]::GetBytes([uint32]0).CopyTo($bytes, $offset)
    $temporary = Join-Path $backupDirectory 'POP3.EXE.interpreter-patch.tmp'
    [IO.File]::WriteAllBytes($temporary, $bytes)
    if ((Get-Sha256 $temporary) -ne $patchedHash) { throw 'Patched executable verification failed.' }
    Move-Item -LiteralPath $temporary -Destination $exe -Force
    if ((Get-Sha256 $exe) -ne $patchedHash) { throw 'Installed executable verification failed.' }
    [pscustomobject]@{ Action = 'Install'; GameDirectory = $game; ExeSha256 = $patchedHash; Backup = $backup }
    exit 0
}

if ($currentHash -eq $supportedHash) {
    Write-Output 'Steam interpreter patch is already restored.'
    exit 0
}
if ($currentHash -ne $patchedHash) {
    throw "Refusing to restore over an unknown POP3.EXE hash: $currentHash"
}
if (-not (Test-Path -LiteralPath $backup) -or (Get-Sha256 $backup) -ne $supportedHash) {
    throw 'Verified interpreter-patch backup is missing or changed.'
}
$temporary = Join-Path $backupDirectory 'POP3.EXE.restore.tmp'
Copy-Item -LiteralPath $backup -Destination $temporary -Force
Move-Item -LiteralPath $temporary -Destination $exe -Force
if ((Get-Sha256 $exe) -ne $supportedHash) { throw 'Restored executable verification failed.' }
[pscustomobject]@{ Action = 'Restore'; GameDirectory = $game; ExeSha256 = $supportedHash; BackupRetained = $backup }
