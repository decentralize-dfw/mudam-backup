$ErrorActionPreference='Stop'
$repo=(Resolve-Path '.').Path
$modelRoot=(Resolve-Path '12_Blender_Model').Path
$keep=@(
'scenes/MUDAM_R151_WEB_CLEAN_v002.blend',
'scenes/MUDAM_R151_ACT_CEVRE_ADAY_v011.blend',
'scenes/MUDAM_ACT2020_DOKUNULMAMIS.blend',
'scenes/MUDAM_R149_UST_DOLASIM_TAS_DOSEME_v001.blend',
'exports/MUDAM_R149_UST_DOLASIM_TAS_DOSEME_v001_preview_compact.glb',
'exports/current.glb.gz',
'exports/r151_web_v002/building.glb',
'exports/r151_web_clean/near_context.glb',
'exports/r151_web_v002/far_context.glb',
'exports/web_current/building.glb.gz',
'exports/web_current/near_context.glb.gz',
'exports/web_current/far_context.glb.gz'
) | ForEach-Object { [IO.Path]::GetFullPath((Join-Path $modelRoot $_)) }
foreach($p in $keep){if(-not(Test-Path -LiteralPath $p)){throw "Protected current file missing: $p"}}
$tracked=@(& git -c core.quotepath=false ls-files) | ForEach-Object {[IO.Path]::GetFullPath((Join-Path $repo $_))}
$roots=@('scenes','exports','.local_source_cache/act_context/clipped_glb','.local_source_cache/act_context/clipped_glb_v002','.local_source_cache/act_context/clipped_glb_v003','.local_source_cache/act_context/clipped_glb_v004','.local_source_cache/act_context/clipped_glb_v005','.local_source_cache/act_context/clipped_glb_v006','.local_source_cache/act_context/inner_ground_glb','.local_source_cache/r151_web_lod')
$files=@(foreach($r in $roots){Get-ChildItem -LiteralPath (Join-Path $modelRoot $r) -Recurse -File | Where-Object {$_.Name -match '\.(blend\d*|glb)(\.gz)?$'}}) | Sort-Object FullName -Unique
$targets=@($files | Where-Object {$_.FullName -notin $keep -and $_.FullName -notin $tracked})
foreach($f in $targets){$resolved=(Resolve-Path -LiteralPath $f.FullName).Path;if(-not $resolved.StartsWith($modelRoot+'\',[StringComparison]::OrdinalIgnoreCase)){throw 'Outside target scope'};if($f.Attributes -band [IO.FileAttributes]::ReparsePoint){throw 'Reparse point refused'}}
$record=[ordered]@{created_utc=[DateTime]::UtcNow.ToString('o');scope=$modelRoot;protected=$keep;count=$targets.Count;bytes=($targets|Measure-Object Length -Sum).Sum;files=@($targets|ForEach-Object {@{path=$_.FullName;bytes=$_.Length}});deleted=@();errors=@()}
$log=Join-Path $modelRoot 'reports/LOCAL_MODEL_CLEANUP.json'
$record|ConvertTo-Json -Depth 6|Set-Content -LiteralPath $log -Encoding utf8
Write-Output "CLEANUP_PLAN $($record.count) files, $([math]::Round($record.bytes/1GB,2)) GiB; $($keep.Count) current/source files protected."
if($args -contains '-Execute'){
 foreach($f in $targets){try{Remove-Item -LiteralPath $f.FullName -Force -ErrorAction Stop;$record.deleted+= $f.FullName}catch{$record.errors+= @{path=$f.FullName;error=$_.Exception.Message}}}
 $record|ConvertTo-Json -Depth 6|Set-Content -LiteralPath $log -Encoding utf8
 foreach($p in $keep){if(-not(Test-Path -LiteralPath $p)){throw "Protected file missing after cleanup: $p"}}
 Write-Output "DELETED $($record.deleted.Count); ERRORS $($record.errors.Count)"
}
