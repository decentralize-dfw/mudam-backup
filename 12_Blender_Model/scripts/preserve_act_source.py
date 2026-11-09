"""Preserve the imported, uncut ACT source scene as an exact independent copy."""
from pathlib import Path
import hashlib, json, shutil

root = Path(__file__).resolve().parents[1]
source = root / 'scenes/MUDAM_ACT2020_SOURCE_REVIEW_v002.blend'
target = root / 'scenes/MUDAM_ACT2020_DOKUNULMAMIS.blend'
def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()
original_hash = digest(source)
if not target.exists():
    shutil.copy2(source, target)
assert digest(target) == original_hash
receipt = {
    'source': str(source), 'preserved_copy': str(target),
    'sha256': original_hash, 'bytes': target.stat().st_size,
    'byte_identical': True,
    'scope': 'Uncut imported ACT 2020 source scene including its original museum; source coordinate conversion already applied. Raw downloaded source tiles remain separately preserved.',
    'working_scene': 'MUDAM_R151_ACT_CEVRE_ADAY_v002.blend'
}
(root / 'reports/ACT2020_preserved_source.json').write_text(json.dumps(receipt, indent=2), encoding='utf-8')
print(json.dumps(receipt, indent=2))
