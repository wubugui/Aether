param(
    [ValidatePattern('^[a-zA-Z0-9_-]+$')][string]$Round = 'current',
    [switch]$ExportWindows,
    [switch]$CaptureViews
)
$ErrorActionPreference = 'Stop'
$workspace = [IO.Path]::GetFullPath((Split-Path -Parent $PSScriptRoot))
$driver = Join-Path $PSScriptRoot 'validation_manifest.py'
$driverArguments = @($driver, 'run', '--workspace', $workspace, '--round', $Round)
if ($ExportWindows) { $driverArguments += '--export-windows' }
if ($CaptureViews) { $driverArguments += '--capture-views' }
# The driver owns one run ID, exclusive lock, hidden subprocesses, unique
# evidence directory, dependency freeze and positive report checks.
$portablePython = Join-Path $workspace 'MIGRATION_20260906\python-portable.cmd'
if (Test-Path -LiteralPath $portablePython -PathType Leaf) {
    & $portablePython @driverArguments
} else {
    & python @driverArguments
}
if ($LASTEXITCODE -ne 0) {
    throw 'Technical validation failed. Inspect the unique run directory printed above; previous results are not a fallback.'
}
