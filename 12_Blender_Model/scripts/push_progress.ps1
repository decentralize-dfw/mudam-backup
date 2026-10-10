param([switch]$Publish, [string]$Message = "Update verified Mudam production progress", [string[]]$IncludePaths = @())
$ErrorActionPreference = 'Stop'
$mudamRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
Push-Location -LiteralPath $mudamRoot
try {
    function Git-Checked { & git @args; if ($LASTEXITCODE -ne 0) { throw "Git failed: $args" } }
    $branch = (& git branch --show-current).Trim()
    if ($branch -ne 'main') { throw 'Progress publication requires main.' }
    $staged = @(& git diff --cached --name-only)
    if ($staged.Count) { throw 'Existing staged changes preserved. Review or commit them first.' }
    $board = Get-Content -Raw -LiteralPath '11_Blender_Modelleme_Plani/is_paketleri.json' | ConvertFrom-Json
    if ($board.latest_scene -notmatch '_R(\d+)_') { throw 'Verified checkpoint ID missing.' }
    $revision = [int]$Matches[1]
    $extensions = Get-Content -Raw -LiteralPath '12_Blender_Model/config/checkpoint_extensions.json' | ConvertFrom-Json
    $entry = $extensions | Where-Object { $_.id -eq "R$revision" }
    if (-not $entry) { throw 'Checkpoint validation list missing.' }
    foreach ($check in $entry.checks) {
        $receipt = Get-Content -Raw -LiteralPath "12_Blender_Model/reports/$check" | ConvertFrom-Json
        if ($receipt.file -ne $board.latest_scene -or $receipt.failures.Count) { throw "Unverified checkpoint: $check" }
    }
    $mudamPython = Join-Path $env:USERPROFILE '.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
    & $mudamPython -X utf8 '12_Blender_Model/scripts/prepare_web_model.py'
    if ($LASTEXITCODE -ne 0) { throw 'Verified web model preparation failed.' }
    $allowed = @('12_Blender_Model/exports/current.glb.gz','.gitignore','11_Blender_Modelleme_Plani/is_paketleri.json','11_Blender_Modelleme_Plani/00_MODELLEME_ANA_PLANI.md','12_Blender_Model/URETIM.html','12_Blender_Model/URETIM_DURUMU.html','12_Blender_Model/URETIM_DURUMU.md','12_Blender_Model/PLAN_KONTROL.html','12_Blender_Model/MODEL_INCELEME.html','12_Blender_Model/assets','12_Blender_Model/config','12_Blender_Model/reports','12_Blender_Model/renders','12_Blender_Model/references','12_Blender_Model/scripts','12_Blender_Model/textures')
    $allowed += @('12_Blender_Model/CEVRE_ADAY.html','12_Blender_Model/WEB_HAFIF.html','12_Blender_Model/exports/web_current')
    $modelPattern = '\.(blend\d*|glb|gltf|fbx|obj|stl|ply|usd[acz]?|abc|bin)(\.gz)?$'
    $webModel = '12_Blender_Model/exports/current.glb.gz'
    $webModels = @($webModel,'12_Blender_Model/exports/web_current/building.glb.gz','12_Blender_Model/exports/web_current/near_context.glb.gz','12_Blender_Model/exports/web_current/far_context.glb.gz')
    $paths = @(& git -c core.quotepath=false ls-files --modified --others --exclude-standard -- $allowed | Sort-Object -Unique | Where-Object { ($_ -notmatch $modelPattern -or $_ -in $webModels) -and $_ -notmatch 'initial_dark\.jpg$' -and ($_ -eq '12_Blender_Model/config/r151_web_lod.json' -or $_ -notmatch '/R(\d+)_' -or [int]$Matches[1] -le $revision) })
    if ($IncludePaths.Count) {
        foreach ($requested in $IncludePaths) {
            if ($requested -notin $paths) { throw "Requested path is unchanged or outside publication allowlist: $requested" }
        }
        $paths = @($paths | Where-Object { $_ -in $IncludePaths })
    }
    foreach ($path in $paths) {
        $limit = if ($path -in $webModels) { 100000000 } else { 50000000 }
        if ((Test-Path -LiteralPath $path) -and (Get-Item -LiteralPath $path).Length -gt $limit) { throw "Progress artifact too large: $path" }
    }
    if (-not $Publish) { Write-Output "DRY RUN: $($paths.Count) progress files; Blender and historical models excluded; current web preview included; R$revision verified."; $paths; return }
    Git-Checked fetch origin
    & git merge-base --is-ancestor origin/main HEAD
    if ($LASTEXITCODE -ne 0) { throw 'Remote main has new work. Preserve and integrate it before retrying.' }
    if ($paths.Count) {
        Git-Checked add -- $paths
        $blocked = @(& git diff --cached --name-only --diff-filter=ACMR | Where-Object { $_ -match $modelPattern -and $_ -notin $webModels })
        if ($blocked.Count) { throw "Model file staged; push refused: $blocked" }
        Git-Checked diff --cached --check
        Git-Checked commit -m $Message
    }
    $ahead = [int](& git rev-list --count origin/main..HEAD)
    if (-not $ahead) { Write-Output 'No new changes to publish.'; return }
    # Check all unpublished commits, not only the current index.
    $incoming = @(& git log --format= --name-only --diff-filter=ACMR origin/main..HEAD | Where-Object { $_ -match $modelPattern -and $_ -notin $webModels })
    if ($incoming.Count) { throw 'An unpublished commit contains model binaries. Push refused.' }
    Git-Checked push origin main
    $sha = (& git rev-parse HEAD).Trim()
    $remote = ((& git ls-remote origin refs/heads/main) -split '\s+')[0]
    if ($sha -ne $remote) { throw 'Remote main differs after push; receipt not written.' }
    $utc = [DateTime]::UtcNow.ToString('yyyy-MM-dd HH:mm:ss') + ' UTC'
    $receiptLine = "`n`n$utc — $sha origin/main normal push doğrulandı. Pano, renderlar, raporlar ve üretim betikleri gönderildi; Blender ve arşiv GLB dosyaları yerelde; tek güncel sıkıştırılmış web GLB gönderildi.`n"
    Add-Content -LiteralPath '12_Blender_Model/URETIM_DURUMU.md' -Value $receiptLine -Encoding utf8
    Git-Checked add -- '12_Blender_Model/URETIM_DURUMU.md'
    Git-Checked commit -m "Record $utc progress push"
    Git-Checked push origin main
    Write-Output "Published $sha at $utc; Blender stayed local; latest web preview published."
} finally { Pop-Location }
