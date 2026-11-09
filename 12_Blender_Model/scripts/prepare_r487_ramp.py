from pathlib import Path
R=Path('12_Blender_Model');s=(R/'scripts/fit_r487_passage.py').read_text().replace('q[:,1]-24]','q[:,1]-24,np.minimum(0,q[:,1]-17)]').replace('three-coefficient plane','four-coefficient continuous plane/ramp with source-observed south break at y17');(R/'scripts/fit_r487_passage_ramp.py').write_text(s)
