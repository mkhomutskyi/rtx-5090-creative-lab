"""Run only this lab's ComfyUI and release its models after 15 idle minutes."""
import json,signal,subprocess,sys,time,urllib.request,os
child=subprocess.Popen([sys.executable,'main.py',*sys.argv[1:]])
stop=False
last_work=time.monotonic();freed=False;last_history=None
idle_seconds=max(10,int(os.getenv('H3_IDLE_SECONDS','900')))
def shutdown(*_):
 global stop
 stop=True
 child.terminate()
signal.signal(signal.SIGTERM,shutdown);signal.signal(signal.SIGINT,shutdown)
def request(path,body=None):
 req=urllib.request.Request('http://127.0.0.1:8188'+path,None if body is None else json.dumps(body).encode(),{'Content-Type':'application/json'})
 with urllib.request.urlopen(req,timeout=5) as r:
  data=r.read();return json.loads(data) if data else {}
try:
 while not stop and child.poll() is None:
  try:
   q=request('/queue');history=list(request('/history?max_items=1'))
   if q.get('queue_running') or q.get('queue_pending') or history!=last_history:last_work=time.monotonic();freed=False
   last_history=history
   if not freed and time.monotonic()-last_work>=idle_seconds:
    request('/free',{'unload_models':True,'free_memory':True});freed=True;print(f'H3 lab: released models after {idle_seconds} idle seconds.',flush=True)
  except Exception:pass
  time.sleep(5)
finally:
 if child.poll() is None:
  child.terminate()
  try:child.wait(timeout=30)
  except subprocess.TimeoutExpired:child.kill();child.wait()
sys.exit(child.returncode or 0)
