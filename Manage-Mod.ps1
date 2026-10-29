[CmdletBinding()]
param(
    [ValidateSet('Install','Check','Restore')][string]$Action,
    [ValidateSet('Steam','OpenJade')][string]$Edition,
    [string]$GameDirectory
)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
function Digest([string]$Path) {
    $hash = [Security.Cryptography.SHA256]::Create()
    $stream = [IO.File]::OpenRead($Path)
    try { return ([BitConverter]::ToString($hash.ComputeHash($stream))).Replace('-','').ToLowerInvariant() }
    finally { $stream.Dispose(); $hash.Dispose() }
}
function Require([bool]$Condition,[string]$Message) { if (-not $Condition) { throw $Message } }
function Invoke-Helper([string]$Script,[string[]]$Arguments) {
    & "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -ExecutionPolicy Bypass -File $Script @Arguments
    Require ($LASTEXITCODE -eq 0) "Helper failed: $Script. Stop here; see the error above. Backups are preserved."
}
try {
    if (-not $Action) { $Action = Read-Host 'Action: Install, Check, or Restore' }
    Require ($Action -in @('Install','Check','Restore')) 'Choose Install, Check, or Restore.'
    if (-not $Edition) { $Edition = Read-Host 'Edition: Steam or OpenJade' }
    Require ($Edition -in @('Steam','OpenJade')) 'Choose Steam or OpenJade.'
    if (-not $GameDirectory) { $GameDirectory = Split-Path -Parent $PSScriptRoot }
    $game = (Resolve-Path -LiteralPath $GameDirectory).ProviderPath
    Require (Test-Path -LiteralPath (Join-Path $game 'pop3.bf') -PathType Leaf) 'pop3.bf not found in this folder.'
    # Validate the whole distributed bundle before allowing a write.
    $package = Get-Content -Raw -LiteralPath (Join-Path $PSScriptRoot 'package-manifest.json') | ConvertFrom-Json
    Require ($package.version -eq '0.5.0') 'Unexpected bundle version.'
    foreach ($entry in $package.files) {
        Require ($entry.path -match '^[a-zA-Z0-9_. /-]+$' -and $entry.path -notmatch '(^|/)\.\.(/|$)' -and -not $entry.path.StartsWith('/')) 'Unsafe package path.'
        $file = Join-Path $PSScriptRoot $entry.path
        Require (Test-Path -LiteralPath $file -PathType Leaf) "Missing bundle file: $($entry.path). Reapply the complete universal JTMod."
        Require ((Digest $file) -eq $entry.sha256) "Changed bundle file: $($entry.path). Reapply a clean copy of the universal JTMod."
    }
    $voice = Get-Content -Raw -LiteralPath (Join-Path $PSScriptRoot 'voice/manifest.json') | ConvertFrom-Json
    $sound = Join-Path $game 'Sound/soundlocal.big'
    $fat = Join-Path $game 'Sound/soundlocal.fat'
    Require ((Digest $fat) -eq $voice.fatSha256) 'Unsupported soundlocal.fat. This voice preview supports the documented English sound bank only.'
    $soundHash = Digest $sound
    Require ($soundHash -in @($voice.baseSha256,$voice.patchedSha256)) 'Unsupported or modified soundlocal.big. No files were changed.'
    $voiceState = if ($soundHash -eq $voice.baseSha256) { 'Original' } else { 'Installed (93 lines)' }
    $baseModel = 'cb9424bf647d6a3eac08ab139dbc68ae4024378ef43c43f00f18c8ab8a1c4644'
    $expectedModel = if ($Edition -eq 'Steam') { $baseModel } else { '3d4b138b0babfe026669db584b5bed29b25ddca94f23172cfa6c30f288c3409d' }
    $modelHash = Digest (Join-Path $game 'pop3.bf')
    $modelOK = $modelHash -eq $expectedModel
    $exeState = 'Not required'
    $exeHash = ''
    if ($Edition -eq 'Steam') {
        $exeHash = Digest (Join-Path $game 'POP3.EXE')
        $exeState = switch ($exeHash) {
            'f42f721f1394894b87b4584ca1e9bc0c2be7af71cf39a1a3548925fa9eab7cfa' { 'Large assets ready' }
            'f6dd6820334918d915c8d6b70a60b799d3e85b3be9c5a3245d240768be734208' { 'Interpreter patch installed' }
            'febbabb37d355ebbe51c4e8cd4172ad825870c759b529421f361a13339aa0941' { 'Stock (large assets not enabled)' }
            default { 'Unsupported' }
        }
    }
    Write-Output "Edition: $Edition | Correct model/sword archive: $modelOK | Voice: $voiceState | Steam EXE: $exeState"
    if ($Action -eq 'Check') {
        if (-not $modelOK -or $soundHash -ne $voice.patchedSha256 -or ($Edition -eq 'Steam' -and $exeState -ne 'Interpreter patch installed')) {
            Write-Output 'Bundle is not fully installed in this folder. Follow README.md for this edition.'
            exit 2
        }
        Write-Output 'All three components match this bundle. This verifies files, not game playback.'
        exit 0
    }
    # Only block game processes belonging to this target folder. Unrelated
    # installations and disposable test copies must not interfere.
    foreach ($process in @(Get-Process -Name POP3,PrinceOfPersia,openjade -ErrorAction SilentlyContinue)) {
        $processPath = $null
        try { $processPath = $process.Path } catch {}
        Require (-not [string]::IsNullOrWhiteSpace($processPath)) 'Cannot identify a running game. Close it before continuing.'
        Require (-not $processPath.StartsWith($game.TrimEnd('\')+'\',[StringComparison]::OrdinalIgnoreCase)) 'Close the game in the selected folder before continuing.'
    }
    if ($Action -eq 'Install') {
        Require ($modelOK -or ($Edition -eq 'OpenJade' -and $modelHash -eq $baseModel)) 'Apply the universal JTMod with PoP Mod Manager first. Use the supported clean base without overlapping mods.'
        if ($Edition -eq 'Steam') {
            Require ($exeState -in @('Large assets ready','Interpreter patch installed')) 'Enable Large assets with PoP Mod Manager first. Unknown executables are refused.'
            if ($exeState -eq 'Large assets ready') {
                Require ((Digest (Join-Path $game 'POP3.EXE.popmm.bak')) -eq 'febbabb37d355ebbe51c4e8cd4172ad825870c759b529421f361a13339aa0941') 'Verified Mod Manager executable backup required.'
            }
        }
        # Voice validates all its payloads and rollback state before changing anything.
        Invoke-Helper (Join-Path $PSScriptRoot 'voice/Manage-Voice.ps1') @('-Action','Install','-GamePath',$game)
        if ($Edition -eq 'Steam') {
            Invoke-Helper (Join-Path $PSScriptRoot 'installers/Install-Steam-Water-Sword.ps1') @('-Action','Install','-GameDirectory',$game)
        } else {
            Invoke-Helper (Join-Path $PSScriptRoot 'installers/Manage-OpenJade-Effects.ps1') @('-Action','Install','-GameDirectory',$game)
        }
        Write-Output 'Model + Water Sword + 93-line voice preview installed. Start the selected edition and test a New Game.'
    } else {
        if ($Edition -eq 'Steam') {
            Require ($exeState -ne 'Unsupported') 'Unknown Steam executable: restore refused. Backups were not changed.'
            if ($exeState -eq 'Interpreter patch installed') {
                Require ((Digest (Join-Path $game 'WWPrinceWaterSwordBackup/POP3.EXE.before-interpreter-patch')) -eq 'f42f721f1394894b87b4584ca1e9bc0c2be7af71cf39a1a3548925fa9eab7cfa') 'Verified interpreter backup required.'
            }
        }
        if ($Edition -eq 'OpenJade') {
            Invoke-Helper (Join-Path $PSScriptRoot 'installers/Manage-OpenJade-Effects.ps1') @('-Action','Restore','-GameDirectory',$game)
        }
        Invoke-Helper (Join-Path $PSScriptRoot 'voice/Manage-Voice.ps1') @('-Action','Uninstall','-GamePath',$game)
        if ($Edition -eq 'Steam' -and $exeState -eq 'Interpreter patch installed') {
            Invoke-Helper (Join-Path $PSScriptRoot 'installers/Install-Steam-Water-Sword.ps1') @('-Action','Restore','-GameDirectory',$game)
        }
        Write-Output 'Voice and interpreter patch restored. Now use Restore original in PoP Mod Manager; on Steam also disable Large assets. Backups were retained.'
    }
} catch {
    Write-Error $_
    exit 1
}
