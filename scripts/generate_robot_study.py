"""Run a small local Z-Image Base robot study with the ComfyUI HTTP API."""
import argparse
import json
from pathlib import Path
import time
from urllib.request import Request, urlopen


def request(base, path, payload=None):
    body = None if payload is None else json.dumps(payload).encode('utf-8')
    req = Request(base.rstrip('/') + path, data=body,
                  headers={'Content-Type': 'application/json'})
    with urlopen(req, timeout=60) as response:
        data = response.read()
        return json.loads(data) if data else {}


def workflow(prompt, seed, prefix, negative):
    return {
        '1': {'class_type':'UNETLoader','inputs':{'unet_name':'z_image_bf16.safetensors','weight_dtype':'default'}},
        '2': {'class_type':'CLIPLoader','inputs':{'clip_name':'qwen_3_4b.safetensors','type':'lumina2'}},
        '3': {'class_type':'VAELoader','inputs':{'vae_name':'ae.safetensors'}},
        '4': {'class_type':'CLIPTextEncode','inputs':{'text':prompt,'clip':['2',0]}},
        '5': {'class_type':'CLIPTextEncode','inputs':{'text':negative,'clip':['2',0]}},
        '6': {'class_type':'EmptySD3LatentImage','inputs':{'width':1280,'height':768,'batch_size':1}},
        '7': {'class_type':'ModelSamplingAuraFlow','inputs':{'model':['1',0],'shift':3.0}},
        '8': {'class_type':'KSampler','inputs':{'model':['7',0],'positive':['4',0],'negative':['5',0],
             'latent_image':['6',0],'seed':seed,'steps':30,'cfg':4.0,'sampler_name':'res_multistep','scheduler':'simple','denoise':1.0}},
        '9': {'class_type':'VAEDecode','inputs':{'samples':['8',0],'vae':['3',0]}},
        '10': {'class_type':'SaveImage','inputs':{'images':['9',0],'filename_prefix':prefix}}
    }


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url',required=True)
    parser.add_argument('--prompts',type=Path,required=True)
    parser.add_argument('--record-dir',type=Path,required=True)
    args=parser.parse_args()
    args.record_dir.mkdir(parents=True,exist_ok=True)
    queue=request(args.url,'/queue')
    if queue.get('queue_running') or queue.get('queue_pending'):
        raise RuntimeError('Queue is not empty; refusing to add work to a busy instance.')
    stats=request(args.url,'/system_stats')
    (args.record_dir/'system-stats.json').write_text(json.dumps(stats,indent=2),encoding='utf-8')
    config=json.loads(args.prompts.read_text(encoding='utf-8-sig'))
    results=[]
    for item in config['jobs']:
        receipt=args.record_dir/(item['name']+'-receipt.json')
        if receipt.exists():
            print('Skipping recorded job:',item['name'],flush=True)
            continue
        graph=workflow(item['prompt'],item['seed'],item['name'],config['negative'])
        (args.record_dir/(item['name']+'-api.json')).write_text(json.dumps(graph,indent=2),encoding='utf-8')
        start=time.monotonic()
        submitted=request(args.url,'/prompt',{'prompt':graph,'client_id':'rtx5090-robot-study'})
        prompt_id=submitted['prompt_id']
        print('Submitted',item['name'],prompt_id,flush=True)
        for attempt in range(360):
            history=request(args.url,'/history/'+prompt_id)
            if prompt_id in history:
                entry=history[prompt_id]
                if entry.get('status',{}).get('status_str') == 'error':
                    raise RuntimeError(json.dumps(entry.get('status'),indent=2))
                outputs=entry.get('outputs',{}).get('10',{}).get('images',[])
                if outputs:
                    result={'name':item['name'],'seed':item['seed'],'prompt_id':prompt_id,
                        'elapsed_wall_seconds':round(time.monotonic()-start,2),
                        'first_job_includes_cold_model_loading':len(results)==0,
                        'image_conditioning':False,'outputs':outputs,'history':entry}
                    receipt.write_text(json.dumps(result,indent=2),encoding='utf-8')
                    results.append(result)
                    print('Finished',item['name'],result['elapsed_wall_seconds'],'seconds',outputs,flush=True)
                    break
            time.sleep(5)
        else:
            raise TimeoutError('Job still unresolved after 30 minutes. Inspect queue before retrying.')
    (args.record_dir/'batch-results.json').write_text(json.dumps(results,indent=2),encoding='utf-8')


if __name__=='__main__':
    main()