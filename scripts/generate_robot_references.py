"""Reference-guided robot illustrations with installed FLUX.2 Klein 9B KV."""
import argparse
import json
from pathlib import Path
import time
from generate_robot_study import request


def graph(item):
    g={
    '1':{'class_type':'UNETLoader','inputs':{'unet_name':'flux-2-klein-9b-kv-fp8.safetensors','weight_dtype':'default'}},
    '2':{'class_type':'CLIPLoader','inputs':{'clip_name':'qwen_3_8b_fp8mixed.safetensors','type':'flux2'}},
    '3':{'class_type':'VAELoader','inputs':{'vae_name':'flux2-vae.safetensors'}},
    '4':{'class_type':'CLIPTextEncode','inputs':{'text':item['prompt'],'clip':['2',0]}},
    '5':{'class_type':'ConditioningZeroOut','inputs':{'conditioning':['4',0]}},
    '6':{'class_type':'LoadImage','inputs':{'image':item['reference']}},
    '7':{'class_type':'ImageScaleToTotalPixels','inputs':{'image':['6',0],'upscale_method':'lanczos','megapixels':0.75,'resolution_steps':16}},
    '8':{'class_type':'VAEEncode','inputs':{'pixels':['7',0],'vae':['3',0]}},
    '9':{'class_type':'ReferenceLatent','inputs':{'conditioning':['4',0],'latent':['8',0]}},
    '10':{'class_type':'ReferenceLatent','inputs':{'conditioning':['5',0],'latent':['8',0]}},
    '11':{'class_type':'FluxKVCache','inputs':{'model':['1',0]}},
    '12':{'class_type':'CFGGuider','inputs':{'model':['11',0],'positive':['9',0],'negative':['10',0],'cfg':1.0}},
    '13':{'class_type':'RandomNoise','inputs':{'noise_seed':item['seed']}},
    '14':{'class_type':'KSamplerSelect','inputs':{'sampler_name':'euler'}},
    '15':{'class_type':'Flux2Scheduler','inputs':{'steps':4,'width':1280,'height':768}},
    '16':{'class_type':'EmptyFlux2LatentImage','inputs':{'width':1280,'height':768,'batch_size':1}},
    '17':{'class_type':'SamplerCustomAdvanced','inputs':{'noise':['13',0],'guider':['12',0],'sampler':['14',0],'sigmas':['15',0],'latent_image':['16',0]}},
    '18':{'class_type':'VAEDecode','inputs':{'samples':['17',0],'vae':['3',0]}},
    '19':{'class_type':'SaveImage','inputs':{'images':['18',0],'filename_prefix':item['name']}}
    }
    if item.get('crop'):
        g['20']={'class_type':'ImageCrop','inputs':{'image':['6',0],**item['crop']}}
        g['7']['inputs']['image']=['20',0]
    return g


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--url',required=True)
    p.add_argument('--prompts',type=Path,required=True)
    p.add_argument('--record-dir',type=Path,required=True)
    a=p.parse_args()
    a.record_dir.mkdir(parents=True,exist_ok=True)
    queue=request(a.url,'/queue')
    if queue.get('queue_running') or queue.get('queue_pending'):
        raise RuntimeError('Queue busy')
    request(a.url,'/free',{'unload_models':True,'free_memory':True})
    for index,item in enumerate(json.loads(a.prompts.read_text(encoding='utf-8-sig'))['jobs']):
        g=graph(item)
        (a.record_dir/(item['name']+'-api.json')).write_text(json.dumps(g,indent=2),encoding='utf-8')
        start=time.monotonic()
        prompt_id=request(a.url,'/prompt',{'prompt':g,'client_id':'rtx5090-reference-study'})['prompt_id']
        print('Submitted',item['name'],prompt_id,flush=True)
        for attempt in range(360):
            entry=request(a.url,'/history/'+prompt_id).get(prompt_id)
            if entry:
                if entry.get('status',{}).get('status_str')=='error':
                    raise RuntimeError(json.dumps(entry['status'],indent=2))
                outputs=entry.get('outputs',{}).get('19',{}).get('images',[])
                if outputs:
                    receipt={'name':item['name'],'model':'flux-2-klein-9b-kv-fp8.safetensors',
                        'prompt_id':prompt_id,'reference':item['reference'],'image_conditioning':True,
                        'first_flux_job_includes_model_loading':index==0,
                        'elapsed_wall_seconds':round(time.monotonic()-start,2),'outputs':outputs,'history':entry}
                    (a.record_dir/(item['name']+'-receipt.json')).write_text(json.dumps(receipt,indent=2),encoding='utf-8')
                    print('Finished',item['name'],receipt['elapsed_wall_seconds'],'seconds',outputs,flush=True)
                    break
            time.sleep(5)
        else:
            raise TimeoutError('Inspect queue before retrying')


if __name__=='__main__':
    main()