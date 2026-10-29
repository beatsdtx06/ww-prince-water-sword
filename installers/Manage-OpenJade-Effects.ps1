[CmdletBinding()]
param([ValidateSet('Install','Restore')][string]$Action, [Parameter(Mandatory=$true)][string]$GameDirectory)
$ErrorActionPreference='Stop'
Set-StrictMode -Version Latest
function Digest([string]$Path) {
    $hash=[Security.Cryptography.SHA256]::Create(); $stream=[IO.File]::OpenRead($Path)
    try { ([BitConverter]::ToString($hash.ComputeHash($stream))).Replace('-','').ToLowerInvariant() }
    finally { $stream.Dispose(); $hash.Dispose() }
}
function Require([bool]$Condition,[string]$Message) { if(-not $Condition){throw $Message} }
$baseHash='cb9424bf647d6a3eac08ab139dbc68ae4024378ef43c43f00f18c8ab8a1c4644'
$targetHash='3d4b138b0babfe026669db584b5bed29b25ddca94f23172cfa6c30f288c3409d'
$game=(Resolve-Path -LiteralPath $GameDirectory).ProviderPath
$archive=Join-Path $game 'pop3.bf'
$backupDir=Join-Path $game 'WWPrinceEffectsBackup'
$backup=Join-Path $backupDir 'pop3.bf.before-openjade-effects'
$temporary=Join-Path $backupDir 'pop3.bf.effects.tmp'
$ownsTemporary=$false
try {
    $current=Digest $archive
    Require ($current -in @($baseHash,$targetHash)) 'Unknown model archive; effects operation refused.'
    foreach($process in @(Get-Process -Name POP3,PrinceOfPersia,openjade -ErrorAction SilentlyContinue)) {
        $processPath=$null; try {$processPath=$process.Path} catch {}
        Require (-not [string]::IsNullOrWhiteSpace($processPath)) 'Close running games before changing effects.'
        Require (-not $processPath.StartsWith($game.TrimEnd('\')+'\',[StringComparison]::OrdinalIgnoreCase)) 'Close this game before changing effects.'
    }
    if($Action -eq 'Restore' -and $current -eq $baseHash) { Write-Output 'OpenJade effects already restored.'; exit 0 }
    if($Action -eq 'Install' -and $current -eq $targetHash) {
        Require ((Test-Path -LiteralPath $backup) -and (Digest $backup) -eq $baseHash) 'Effects are present but the verified baseline backup is missing. Restore the old model mod in Mod Manager and apply the universal package cleanly.'
        Write-Output 'OpenJade full effects already installed.'; exit 0
    }
    if(-not (Test-Path -LiteralPath $backupDir)) { New-Item -ItemType Directory -Path $backupDir | Out-Null }
    Require (-not (Test-Path -LiteralPath $temporary)) 'Previous effects temporary file exists; inspect recovery state before retrying.'
    if($Action -eq 'Restore') {
        Require ((Test-Path -LiteralPath $backup) -and (Digest $backup) -eq $baseHash) 'Verified effects backup required for restore.'
        $ownsTemporary=$true
        Copy-Item -LiteralPath $backup -Destination $temporary
        Require ((Digest $temporary) -eq $baseHash) 'Restore copy verification failed.'
    } else {
        if(Test-Path -LiteralPath $backup) { Require ((Digest $backup) -eq $baseHash) 'Existing effects backup does not match.' }
        else { Copy-Item -LiteralPath $archive -Destination $backup }
        Require ((Digest $backup) -eq $baseHash) 'Effects backup verification failed.'
        $compressed=$null; $gzip=$null; $reader=$null; $inputFile=$null; $outputFile=$null
        try {
            $compressed=[IO.File]::OpenRead((Join-Path $PSScriptRoot 'openjade-effects.delta.gz'))
            $gzip=New-Object IO.Compression.GZipStream($compressed,[IO.Compression.CompressionMode]::Decompress)
            $reader=New-Object IO.BinaryReader($gzip)
            Require ([Text.Encoding]::ASCII.GetString($reader.ReadBytes(8)) -eq 'WWBFDEL1') 'Invalid effects delta.'
            $expectedLength=$reader.ReadUInt64(); $count=$reader.ReadUInt32()
            Require ($expectedLength -eq 603050280 -and $count -lt 1000000) 'Invalid effects header.'
            $inputFile=[IO.File]::OpenRead($backup)
            $outputFile=[IO.File]::Open($temporary,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None)
            $ownsTemporary=$true
            $buffer=New-Object byte[] 1048576
            for($i=0;$i -lt $count;$i++) {
                $mode=$reader.ReadByte()
                if($mode -eq 0) {
                    $offset=$reader.ReadUInt64(); $remaining=[long]$reader.ReadUInt32()
                    Require ($offset+$remaining -le $inputFile.Length) 'Effects copy outside source.'
                    $inputFile.Position=[long]$offset
                } elseif($mode -eq 1) { $remaining=[long]$reader.ReadUInt32() }
                else { throw 'Unknown effects operation.' }
                Require ($outputFile.Position+$remaining -le $expectedLength) 'Effects output exceeds expected size.'
                while($remaining -gt 0) {
                    $wanted=[int][Math]::Min($remaining,$buffer.Length)
                    if($mode -eq 0) { $read=$inputFile.Read($buffer,0,$wanted) }
                    else { $read=$reader.Read($buffer,0,$wanted) }
                    Require ($read -gt 0) 'Truncated effects data.'
                    $outputFile.Write($buffer,0,$read); $remaining-=$read
                }
            }
            Require ($outputFile.Length -eq $expectedLength) 'Wrong effects output length.'
            Require ($reader.BaseStream.ReadByte() -eq -1) 'Unexpected trailing effects data.'
            $outputFile.Flush($true)
        } finally {
            foreach($stream in @($outputFile,$inputFile,$reader,$gzip,$compressed)) { if($null -ne $stream){$stream.Dispose()} }
        }
        Require ((Digest $temporary) -eq $targetHash) 'Effects output verification failed; installed archive was not changed.'
    }
    $rollback=Join-Path $backupDir ('before-'+$Action+'.'+[Guid]::NewGuid().ToString('N')+'.bf')
    [IO.File]::Replace($temporary,$archive,$rollback)
    Write-Output "OpenJade effects $Action complete; verified backup retained."
} catch {
    # Only our explicitly scoped unfinished output is removed; original and backup remain.
    if($ownsTemporary -and (Test-Path -LiteralPath $temporary)) { Remove-Item -LiteralPath $temporary }
    Write-Error $_; exit 1
}
