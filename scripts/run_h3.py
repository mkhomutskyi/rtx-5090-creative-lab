"""Animate a local image through native ComfyUI H3 nodes using Python3.11+."""
import argparse,json,time,urllib.request,urllib.parse,uuid
from pathlib import Path

def request(url,path,body=None):
 req=urllib.request.Request(url+path,data=json.dumps(body).encode() if body is not None else None,headers={'Content-Type':'application/json'})
 with urllib.request.urlopen(req,timeout=45) as r:
  data=r.read();return json.loads(data) if data else {}

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--url',default='http://127.0.0.1:8193');p.add_argument('--image',type=Path,required=True);group=p.add_mutually_exclusive_group(required=True);group.add_argument('--prompt');group.add_argument('--prompt-file',type=Path);p.add_argument('--profile',choices=['draft','preview','quality'],default='draft');p.add_argument('--width',type=int);p.add_argument('--height',type=int);p.add_argument('--seed',type=int,default=42);p.add_argument('--output',type=Path,default=Path('outputs/h3-example.mp4'));p.add_argument('--timeout',type=int,default=900);p.add_argument('--dry-run',action='store_true');a=p.parse_args()
 if urllib.parse.urlparse(a.url).hostname not in ['127.0.0.1','localhost','::1']:p.error('This helper is intended for a local ComfyUI endpoint.')
 if not a.image.is_file():p.error('Input image does not exist')
 if a.output.exists():p.error('Output exists; choose another filename')
 g=json.loads((Path(__file__).resolve().parents[1]/f'workflows/h3/{a.profile}.json').read_text());text=a.prompt_file.read_text(encoding='utf-8-sig') if a.prompt_file else a.prompt
 g['5']['inputs']['prompt']=text;g['7']['inputs']['noise_seed']=a.seed
 for key,value in [('width',a.width),('height',a.height)]:
  if value is not None:
   if value<=0 or value%32:p.error('Dimensions must be positive multiples of32')
   g['5']['inputs'][key]=value
 if a.dry_run:print(json.dumps(g,indent=2));return
 q=request(a.url,'/queue')
 if q.get('queue_running') or q.get('queue_pending'):raise RuntimeError('ComfyUI queue busy; nothing submitted')
 token=uuid.uuid4().hex;filename='h3-'+token+a.image.suffix.lower();boundary='h3-'+token
 body=(f'--{boundary}\r\nContent-Disposition: form-data; name="image"; filename="{filename}"\r\nContent-Type: application/octet-stream\r\n\r\n'.encode()+a.image.read_bytes()+f'\r\n--{boundary}--\r\n'.encode())
 req=urllib.request.Request(a.url+'/upload/image',data=body,headers={'Content-Type':f'multipart/form-data; boundary={boundary}'})
 with urllib.request.urlopen(req,timeout=60) as r:upload=json.load(r)
 g['16']['inputs']['image']='/'.join(x for x in [upload.get('subfolder',''),upload['name']] if x);g['14']['inputs']['filename_prefix']='h3-guide/'+token
 a.output.parent.mkdir(parents=True,exist_ok=True);record=a.output.with_suffix('.run.json');started=time.monotonic();receipt={'profile':a.profile,'seed':a.seed,'graph':g};record.write_text(json.dumps(receipt,indent=2))
 receipt.update(request(a.url,'/prompt',{'prompt':g,'client_id':'h3-guide-'+token}));record.write_text(json.dumps(receipt,indent=2));ident=receipt['prompt_id'];print('Submitted',ident,flush=True)
 while time.monotonic()-started<a.timeout:
  h=request(a.url,'/history/'+ident)
  if ident in h:
   row=h[ident];receipt.update(seconds=round(time.monotonic()-started,3),history=row);record.write_text(json.dumps(receipt,indent=2))
   if row.get('status',{}).get('status_str')!='success':raise RuntimeError('Generation failed; see run record')
   outputs=row.get('outputs',{}).get('14',{});files=[v for key in ['images','videos','gifs'] for v in outputs.get(key,[]) if v.get('filename','').endswith('.mp4')]
   if len(files)!=1:raise RuntimeError('Expected one MP4 output; inspect history')
   url=a.url+'/view?'+urllib.parse.urlencode(files[0]);part=a.output.with_suffix('.mp4.part')
   with urllib.request.urlopen(url,timeout=120) as src,part.open('wb') as dst:
    while chunk:=src.read(1024*1024):dst.write(chunk)
   if part.stat().st_size==0:raise RuntimeError('Empty video download')
   part.replace(a.output);print('Saved',a.output,'in',receipt['seconds'],'seconds');return
  time.sleep(2)
 q=request(a.url,'/queue')
 if any(len(job)>1 and job[1]==ident for job in q.get('queue_running',[])):request(a.url,'/interrupt',{})
 raise TimeoutError('Job exceeded timeout; inspect queue and run record before retrying')
if __name__=='__main__':main()
