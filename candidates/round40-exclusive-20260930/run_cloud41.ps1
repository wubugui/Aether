param(
    [ValidatePattern('^[a-z0-9-]+$')][string]$RunName,
    [ValidateSet('verify','no-hud','no-sky','normal','clear-font-cache')][string]$Mode='verify'
)
$round40Base=$PSScriptRoot
$env:APPDATA=Join-Path $round40Base 'evidence\userdata'
$round40Output=Join-Path $round40Base ('evidence\'+$RunName)
if(Test-Path -LiteralPath ($round40Output+'.stdout.log')){throw 'Preserve previous run logs: use a new RunName'}
New-Item -ItemType Directory -Path $round40Output -Force | Out-Null
$round40Tool=if($Mode -eq 'verify'){'res://tools/verify_cloud41.gd'}else{'res://tools/probe_shutdown40.gd'}
$round40Args=@('--path',(Join-Path $round40Base 'project'),'--script',$round40Tool,'--log-file',($round40Output+'.log'),'--',('--output-dir='+$round40Output))
if($Mode -ne 'verify'){$round40Args+=('--mode='+$Mode)}
$round40Engine=Join-Path $round40Base '..\..\.tools\godot\Godot_v4.5.1-stable_win64_console.exe'
$round40Proc=Start-Process -FilePath $round40Engine -ArgumentList $round40Args -WindowStyle Hidden -RedirectStandardOutput ($round40Output+'.stdout.log') -RedirectStandardError ($round40Output+'.stderr.log') -PassThru
Write-Output $round40Proc.Id
