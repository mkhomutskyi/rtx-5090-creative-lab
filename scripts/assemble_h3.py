"""Join H3 clips with crossfades and one continuous licensed music excerpt. Requires ffmpeg/ffprobe."""
import argparse,json,subprocess
from pathlib import Path

def probe(path):return json.loads(subprocess.check_output(['ffprobe','-v','quiet','-show_streams','-show_format','-of','json',str(path)],text=True))
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--clips',nargs='+',type=Path,required=True);p.add_argument('--music',type=Path,required=True);p.add_argument('--music-start',type=float,default=22);p.add_argument('--output',type=Path,required=True);p.add_argument('--fade',type=float,default=.5);a=p.parse_args()
 if a.output.exists():p.error('Output exists; choose a new filename')
 if not all(x.is_file() for x in [*a.clips,a.music]):p.error('Missing input file')
 data=[probe(x) for x in a.clips];videos=[next(s for s in d['streams'] if s['codec_type']=='video') for d in data];dims={(v['width'],v['height'],v['r_frame_rate']) for v in videos}
 if len(dims)!=1:p.error('Clips must have matching dimensions and frame rate')
 durations=[float(v.get('duration',d['format']['duration'])) for v,d in zip(videos,data)]
 if a.fade<=0 or a.fade>=min(durations):p.error('Fade must be shorter than every clip')
 total=sum(durations)-a.fade*(len(a.clips)-1)
 if float(probe(a.music)['format']['duration'])<a.music_start+total:p.error('Music is too short for the requested excerpt')
 args=['ffmpeg','-v','error','-n']
 for path in a.clips:args+=['-i',str(path)]
 args+=['-ss',str(a.music_start),'-i',str(a.music)]
 f=[f'[{i}:v]settb=AVTB,setpts=PTS-STARTPTS[v{i}]' for i in range(len(a.clips))];prev='v0';offset=0
 for i in range(1,len(a.clips)):
  offset+=durations[i-1]-a.fade;f.append(f'[{prev}][v{i}]xfade=transition=fade:duration={a.fade}:offset={offset:.8f}[x{i}]');prev=f'x{i}'
 f += [f'[{prev}]format=yuv420p[vout]',f'[{len(a.clips)}:a]atrim=duration={total:.8f},asetpts=PTS-STARTPTS,volume=0.75,afade=t=in:d=0.4,afade=t=out:st={max(0,total-1.5):.8f}:d=1.5[aout]']
 a.output.parent.mkdir(parents=True,exist_ok=True);args+=['-filter_complex',';'.join(f),'-map','[vout]','-map','[aout]','-t',str(total),'-c:v','libx264','-preset','fast','-crf','18','-c:a','aac','-b:a','192k','-movflags','+faststart',str(a.output)];subprocess.run(args,check=True)
 result=probe(a.output);v=next(s for s in result['streams'] if s['codec_type']=='video');s=next(s for s in result['streams'] if s['codec_type']=='audio')
 if abs(float(v['duration'])-float(s['duration']))>.1:raise RuntimeError('Audio/video duration mismatch')
 subprocess.run(['ffmpeg','-v','error','-i',str(a.output),'-f','null','-'],check=True);a.output.with_suffix('.media.json').write_text(json.dumps(result,indent=2));print('Saved',a.output,'duration',v['duration'])
if __name__=='__main__':main()
