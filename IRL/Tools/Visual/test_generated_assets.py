from pathlib import Path
from PIL import Image
import hashlib, json, numpy as np, subprocess, sys, tempfile

root=Path(__file__).parent
with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
    for path in [a,b]:
        subprocess.run([sys.executable,str(root/'generate_irl_showcase.py'),'--out',path,'--size','256','--seed','20261022'],check=True,capture_output=True)
    pa,pb=Path(a),Path(b)
    fa={x.name:hashlib.sha256(x.read_bytes()).hexdigest() for x in pa.iterdir()}
    fb={x.name:hashlib.sha256(x.read_bytes()).hexdigest() for x in pb.iterdir()}
    assert fa==fb, 'Not deterministic'
    print('PASS deterministic:',len(fa),'identical file hashes')
    for material in ('ForestSoil','Granite','LeafGreen'):
        prefix='T_'+material+'_'
        for suffix in ('BaseColor','Normal','Roughness','Height'):
            im=Image.open(pa/(prefix+suffix+'.png'))
            assert im.size==(256,256)
            assert im.mode==('RGB' if suffix in ('BaseColor','Normal') else 'L')
            assert np.asarray(im).std()>2.0, (material,suffix,'flat')
        nm=np.asarray(Image.open(pa/(prefix+'Normal.png')),dtype=float)/255*2-1
        norms=np.linalg.norm(nm,axis=2)
        assert np.abs(norms-1).mean()<0.01,material
    print('PASS PBR sets: base color, normals, roughness, height, varied and normalized')
    for f in pa.glob('*.obj'):
        verts=0;uvs=0;faces=0
        for line in f.read_text().splitlines():
            if line.startswith('v '):verts+=1
            if line.startswith('vt '):uvs+=1
            if line.startswith('f '):
                faces+=1
                data=line.split()[1:]
                assert len(data)==3
                for face in data:
                    v,uv=map(int,face.split('/'))
                    assert 1<=v<=verts and 1<=uv<=uvs,(f.name,face,verts,uvs)
        assert verts>30 and faces>10,(f.name,verts,faces)
        print('PASS triangle mesh',f.name,'v',verts,'faces',faces)
print('SUCCESS original IRL mobile visual seed pack')
