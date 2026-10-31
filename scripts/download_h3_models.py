"""Download the six public H3 files; no model weights are bundled here."""
import argparse,hashlib,json,time,urllib.request
from pathlib import Path

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--models-dir',type=Path,default=Path('models'));p.add_argument('--accept-license',action='store_true',help='Confirm you have the applicable model rights before downloading');p.add_argument('--verify-only',action='store_true');p.add_argument('--hash-check',action='store_true',help='Also hash existing files; reads about44GB');p.add_argument('--plan',action='store_true');a=p.parse_args()
 manifest=json.loads((Path(__file__).resolve().parents[1]/'docs/h3/models.json').read_text());failed=[]
 if a.plan:
  print(json.dumps(manifest,indent=2));return
 if not a.verify_only and not a.accept_license:p.error('Read the model licence and obtain any required authorization, then pass --accept-license. This flag grants no rights.')
 for item in manifest['files']:
  dest=a.models_dir/item['path'];expected=item['size'];digest=item['sha256']
  if dest.exists():
   if dest.stat().st_size!=expected:raise RuntimeError(f'Existing file has wrong size; preserved: {dest}')
   if a.hash_check:
    with dest.open('rb') as f:actual=hashlib.file_digest(f,'sha256').hexdigest()
    if actual!=digest:raise RuntimeError(f'Checksum mismatch; preserved: {dest}')
   print('VERIFIED' if a.hash_check else 'SIZE_OK',item['path'],flush=True);continue
  if a.verify_only:failed.append(item['path']);continue
  dest.parent.mkdir(parents=True,exist_ok=True);part=dest.with_name(dest.name+'.part')
  for attempt in range(5):
   try:
    offset=part.stat().st_size if part.exists() else 0
    if offset>expected:raise RuntimeError(f'Partial file too large; preserved: {part}')
    if offset<expected:
     req=urllib.request.Request(f'https://huggingface.co/{manifest["repository"]}/resolve/main/{item["path"]}',headers={'Range':f'bytes={offset}-'} if offset else {})
     with urllib.request.urlopen(req,timeout=90) as response:
      if offset and response.status!=206:raise RuntimeError('Server did not honor resume; partial file preserved')
      with part.open('ab' if offset else 'wb') as f:
       while chunk:=response.read(1024*1024):f.write(chunk)
    if part.stat().st_size!=expected:raise RuntimeError('Incomplete download')
    with part.open('rb') as f:actual=hashlib.file_digest(f,'sha256').hexdigest()
    if actual!=digest:raise RuntimeError('Downloaded checksum mismatch')
    part.replace(dest);print('DOWNLOADED_AND_VERIFIED',item['path'],flush=True);break
   except Exception:
    if attempt==4:raise
    time.sleep(3)
 if failed:raise SystemExit('Missing files: '+', '.join(failed))
if __name__=='__main__':main()
