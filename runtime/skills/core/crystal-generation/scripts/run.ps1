$ErrorActionPreference = 'Stop'
if (-not $env:RM_CACHE_DIR) { $env:RM_CACHE_DIR = Join-Path $env:LOCALAPPDATA 'ResearchMind' }
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:PYTHONUTF8 = '1'
if (-not $env:UV_CACHE_DIR) { $env:UV_CACHE_DIR = Join-Path $env:RM_CACHE_DIR 'uv-cache' }
if (-not $env:UV_PYTHON_INSTALL_DIR) { $env:UV_PYTHON_INSTALL_DIR = Join-Path $env:RM_CACHE_DIR 'python' }
function Get-SkillUv {
    $existing = Get-Command uv -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($existing) { return $existing.Source }
    $bin = Join-Path $env:RM_CACHE_DIR 'bin'
    $installed = Join-Path $bin 'uv-0.13.9.exe'
    if (Test-Path -LiteralPath $installed) { return $installed }
    if ([Runtime.InteropServices.RuntimeInformation]::OSArchitecture -ne 'X64') { throw 'Install uv for this architecture.' }
    $temp = Join-Path $bin ([guid]::NewGuid().ToString())
    [void][IO.Directory]::CreateDirectory($temp)
    $zip = Join-Path $temp 'uv.zip'
    $exe = Join-Path $temp 'uv.exe'
    try {
        Invoke-WebRequest -UseBasicParsing 'https://github.com/astral-sh/uv/releases/download/0.13.9/uv-x86_64-pc-windows-msvc.zip' -OutFile $zip
        if ((Get-FileHash -LiteralPath $zip).Hash -ne 'edd61f7f5728a56cc62455386661860bdfc7bab65872f39b0c25bdcc1d8e1beb') { throw 'uv archive checksum mismatch' }
        Add-Type -AssemblyName System.IO.Compression.FileSystem
        $archive = [IO.Compression.ZipFile]::OpenRead($zip)
        try {
            $entry = $archive.Entries | Where-Object Name -eq 'uv.exe' | Select-Object -First 1
            [IO.Compression.ZipFileExtensions]::ExtractToFile($entry,$exe)
        } finally { $archive.Dispose() }
        try { [IO.File]::Move($exe,$installed) } catch { if (-not [IO.File]::Exists($installed)) { throw } }
    } finally {
        [IO.File]::Delete($zip)
        [IO.File]::Delete($exe)
        [IO.Directory]::Delete($temp)
    }
    return $installed
}
if ($args.Count -gt 0 -and $args[0] -eq '_ensure_uv') { Get-SkillUv; exit 0 }
foreach ($name in 'python','python3') {
    $py = Get-Command $name -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($py -and $py.Source -notmatch '\\WindowsApps\\python') {
        & $py.Source -c 'import sys; sys.exit(sys.version_info < (3,11))'
        if ($LASTEXITCODE -eq 0) { & $py.Source -B "$PSScriptRoot/runtime.py" @args; exit $LASTEXITCODE }
    }
}
$cachedUv = Join-Path $env:RM_CACHE_DIR 'bin/uv-0.13.9.exe'
$systemUv = Get-Command uv -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1
if ($systemUv) { $cachedUv = $systemUv.Source }
if (Test-Path -LiteralPath $cachedUv) {
    $managed = & $cachedUv python find --managed-python --no-python-downloads 3.12 2>$null
    if ($LASTEXITCODE -eq 0 -and $managed) { & $managed -B "$PSScriptRoot/runtime.py" @args; exit $LASTEXITCODE }
}
if ($args.Count -gt 0 -and $args[0] -eq 'doctor') { Write-Output '{"status":"missing","missing":["Python 3.11+; run prepares Python 3.12"]}'; exit 2 }
$uv = Get-SkillUv
& $uv run --no-project --managed-python --python 3.12 python -B "$PSScriptRoot/runtime.py" @args
exit $LASTEXITCODE
