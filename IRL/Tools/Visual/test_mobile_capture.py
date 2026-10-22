import csv,json,tempfile
from pathlib import Path
from score_mobile_capture import compare

METADATA={'device_model':'Moto G test profile','graphics_api':'Vulkan','resolution':'1280x720','map':'IRL_Biome','camera_path':'matched_path_001','test_seconds':120}

def make(path, ms,mem,temp,gpu):
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=('frame_ms','gpu_ms','temperature_c','memory_mb'))
        w.writeheader();[w.writerow(dict(frame_ms=ms,gpu_ms=gpu,temperature_c=temp,memory_mb=mem)) for _ in range(240)]

with tempfile.TemporaryDirectory() as tmp:
    a,b=Path(tmp)/'a.csv',Path(tmp)/'b.csv'
    make(a,31.0,450,38,24)
    make(b,30.0,448,37,23)
    result=compare(a,b,METADATA)
    assert result['disposition']=='REVIEW_ELIGIBLE'
    assert result['candidate']['frames']==240
    make(b,38.0,550,43,33)
    assert compare(a,b,METADATA)['disposition']=='NOT_ESTABLISHED'
    try:compare(a,b,{})
    except ValueError:pass
    else:raise AssertionError('Missing context was accepted')
    with a.open('w',newline='') as f:
        f.write('frame_ms\n');f.write('nan\n'*240)
    try:compare(a,b,METADATA)
    except ValueError:pass
    else:raise AssertionError('Nonfinite values accepted')
print('PASS: fair comparison, failure case, missing context, invalid measurements')
