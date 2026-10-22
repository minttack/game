#!/usr/bin/env python3
"""IRL evidence-led Android scene comparison: measurements only, no invented results."""
import argparse,csv,json,math,statistics
from pathlib import Path

def read_capture(path):
    with Path(path).open(newline='',encoding='utf-8') as file:
        rows=list(csv.DictReader(file))
    if len(rows)<120: raise ValueError('Need >=120 measured frame rows for each capture')
    out={}
    for name in ('frame_ms','gpu_ms','temperature_c','memory_mb'):
        values=[]
        for row in rows:
            raw=row.get(name,'').strip()
            if not raw:
                if name=='frame_ms':raise ValueError('Missing frame_ms')
                continue
            try: value=float(raw)
            except ValueError: raise ValueError('Invalid '+name)
            if not math.isfinite(value) or (name in ('frame_ms','gpu_ms') and value<=0) or (name=='memory_mb' and value<0):
                raise ValueError('Invalid '+name)
            values.append(value)
        if values: out[name]=values
    return out

def percentile(values,p):
    values=sorted(values)
    k=(len(values)-1)*p
    a,b=math.floor(k),math.ceil(k)
    return values[a]+(values[b]-values[a])*(k-a)

def measure(data):
    frames=data['frame_ms']
    summary={'frames':len(frames), 'mean_fps':round(1000/statistics.mean(frames),3),
       'median_ms':round(statistics.median(frames),3),
       'p95_ms':round(percentile(frames,.95),3),
       'p99_ms':round(percentile(frames,.99),3),
       'one_percent_low_fps':round(1000/percentile(frames,.99),3)}
    if 'gpu_ms' in data:summary['p95_gpu_ms']=round(percentile(data['gpu_ms'],.95),3)
    if 'temperature_c' in data:summary['peak_temp_c']=round(max(data['temperature_c']),3)
    if 'memory_mb' in data:summary['peak_memory_mb']=round(max(data['memory_mb']),3)
    return summary

def compare(base,candidate,metadata):
    a,b=measure(read_capture(base)),measure(read_capture(candidate))
    exact=('device_model','graphics_api','resolution','map','camera_path','test_seconds')
    missing=[key for key in exact if not metadata.get(key)]
    if missing:raise ValueError('Required comparable capture metadata missing: '+','.join(missing))
    limitations=[]
    for name in ('peak_temp_c','peak_memory_mb','p95_gpu_ms'):
        if name not in a or name not in b:limitations.append(name+' missing in one/both captures')
    score={'baseline':a,'candidate':b,'context':{key:metadata[key] for key in exact},'limitations':limitations}
    p95_pass=b['p95_ms']<=33.333 and b['p95_ms']<=a['p95_ms']*1.05
    p99_pass=b['p99_ms']<=a['p99_ms']*1.10
    mem_pass='peak_memory_mb' in a and 'peak_memory_mb' in b and b['peak_memory_mb']<=a['peak_memory_mb']*1.05
    therm_pass='peak_temp_c' in a and 'peak_temp_c' in b and b['peak_temp_c']<=a['peak_temp_c']+2.0
    gpu_pass='p95_gpu_ms' in a and 'p95_gpu_ms' in b and b['p95_gpu_ms']<=a['p95_gpu_ms']*1.10
    score['gate_checks']={'p95_frame':p95_pass,'p99_frame':p99_pass,'peak_memory':mem_pass,'peak_temperature':therm_pass,'p95_gpu':gpu_pass}
    score['disposition']='REVIEW_ELIGIBLE' if all(score['gate_checks'].values()) else 'NOT_ESTABLISHED'
    score['note']='REVIEW_ELIGIBLE is NOT approval: independently compare screenshots and 3+ repeated runs per state, and verify source/device capture provenance.'
    return score

def main():
    p=argparse.ArgumentParser()
    p.add_argument('baseline_csv');p.add_argument('candidate_csv');p.add_argument('context_json');p.add_argument('--output')
    args=p.parse_args()
    result=compare(args.baseline_csv,args.candidate_csv,json.loads(Path(args.context_json).read_text(encoding='utf8')))
    text=json.dumps(result,indent=2)
    if args.output:Path(args.output).write_text(text,encoding='utf8')
    print(text)

if __name__=='__main__':main()
