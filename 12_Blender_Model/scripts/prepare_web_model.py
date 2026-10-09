"""Publish one lossless web payload, only from the latest verified GLB."""
from pathlib import Path
import gzip, hashlib, json, struct

R = Path(__file__).resolve().parents[2]
B = R / '12_Blender_Model'

def prepare():
    read = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
    report = read(B / 'reports/P21_export_report.json')
    check = read(B / 'reports/P21_verification.json')
    board = read(R / '11_Blender_Modelleme_Plani/is_paketleri.json')
    assert report['source_scene'] == board['latest_scene'], 'Latest scene must be exported first'
    assert check['file'] == report['file'] and check['failures'] == [], 'GLB verification required'
    revision = Path(report['source_scene']).name.split('_')[1]
    entry = next(e for e in read(B / 'config/checkpoint_extensions.json') if e['id'] == revision)
    for name in entry['checks']:
        receipt = read(B / 'reports' / name)
        assert receipt['file'] == report['source_scene'] and receipt['failures'] == [], name
    source = (R / report['file']).resolve()
    assert source.is_relative_to(B / 'exports')
    raw = source.read_bytes()
    assert len(raw) == check['size_bytes']
    assert struct.unpack_from('<4sII', raw) == (b'glTF', 2, len(raw))
    compressed = gzip.compress(raw, compresslevel=9, mtime=0)
    assert gzip.decompress(compressed) == raw
    out = B / 'exports/current.glb.gz'
    release = dict(schema=1, revision=revision, source_scene=report['source_scene'],
                   source_glb=report['file'], url='../exports/current.glb.gz',
                   encoding='gzip', sha256=hashlib.sha256(raw).hexdigest(),
                   size_bytes=len(raw), download_bytes=len(compressed),
                   selected_mesh_count=report['selected_mesh_count'])
    # Replace payload first and manifest last; readers verify the uncompressed hash.
    temp = out.with_suffix('.tmp')
    temp.write_bytes(compressed)
    temp.replace(out)
    manifest = B / 'config/model_release.json'
    temp = manifest.with_suffix('.tmp')
    temp.write_text(json.dumps(release, ensure_ascii=False, indent=2)+'\n', encoding='utf8')
    temp.replace(manifest)
    print(f'{revision}: {len(raw):,} -> {len(compressed):,} bytes; lossless web model ready')
    return release

if __name__ == '__main__':
    prepare()
