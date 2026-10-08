"""Resolve the task board's current scene only when saved-file QA exists."""
from pathlib import Path
import json
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model'
def verified_current_scene():
 scene=json.loads((R/'11_Blender_Modelleme_Plani/is_paketleri.json').read_text(encoding='utf8'))['latest_scene']
 assert (R/scene).is_file(),scene
 checks=[]
 for p in (B/'reports').glob('*verification.json'):
  q=json.loads(p.read_text(encoding='utf8'))
  if q.get('file')==scene and q.get('failures')==[]:checks.append(p.name)
 assert checks,('No saved-file QA for current scene',scene)
 return dict(file=scene,verification_reports=checks)
