$ErrorActionPreference = 'Stop'
$taskRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
$manifestPath = Join-Path $PSScriptRoot 'FILE_MANIFEST.jsonl'
$checked = 0
$failures = [System.Collections.Generic.List[string]]::new()
foreach ($line in [System.IO.File]::ReadLines($manifestPath)) {
    $entry = $line | ConvertFrom-Json
    $relative = $entry.path.Substring(6).Replace('/', [IO.Path]::DirectorySeparatorChar)
    $target = [IO.Path]::GetFullPath((Join-Path $taskRoot $relative))
    if (-not $target.StartsWith($taskRoot + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) {
        throw "Manifest path leaves project root: $relative"
    }
    if (-not (Test-Path -LiteralPath $target -PathType Leaf)) {
        $failures.Add("MISSING $relative")
        continue
    }
    $item = Get-Item -LiteralPath $target
    if ($item.Length -ne $entry.bytes) {
        $failures.Add("SIZE $relative")
        continue
    }
    $hash = (Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($hash -ne $entry.sha256) { $failures.Add("HASH $relative") }
    $checked += 1
    if ($checked % 3000 -eq 0) { Write-Host "Checked $checked files..." }
}
if ($failures.Count -gt 0) {
    $failures | Set-Content -LiteralPath (Join-Path $PSScriptRoot 'RESTORE_FAILURES.txt') -Encoding utf8
    throw "$($failures.Count) verification failures; see RESTORE_FAILURES.txt"
}
Write-Host "PASS: $checked files match the original byte-for-byte SHA256 manifest."

