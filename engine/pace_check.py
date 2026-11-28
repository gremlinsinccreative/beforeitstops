"""Creative Direction pace check (27 Nov 2026). Usage: python3 pace_check.py video.mp4 [payoff_s]
Visual event = a frame where >0.3% of pixels (108x192 grey copy) change by >20 levels vs the previous frame
(a new word, a number tick, a cut, a move), or slow motion that adds up to that. Audio event = onset (RMS +4 dB in 50 ms).
Dead beat = longest gap with neither a visual nor an audio event. Gate: dead beat <= 2.0 s; event every <= 2 s."""
import sys, subprocess, numpy as np
VT = 0.3   # 0.3% of the frame changes by >20 levels (a word, a number, a cut, a move)
def frames(p):
    pr = subprocess.run(["ffmpeg","-v","error","-i",p,"-vf","scale=108:192,format=gray","-f","rawvideo","-"],capture_output=True)
    a = np.frombuffer(pr.stdout,np.uint8).reshape(-1,192,108).astype(np.float32); return a
def fps(p):
    o = subprocess.run(["ffprobe","-v","error","-select_streams","v","-show_entries","stream=r_frame_rate","-of","csv=p=0",p],capture_output=True,text=True).stdout.strip()
    n,d = o.split("/"); return float(n)/float(d)
def audio(p, sr=8000):
    pr = subprocess.run(["ffmpeg","-v","error","-i",p,"-ac","1","-ar",str(sr),"-f","s16le","-"],capture_output=True)
    return np.frombuffer(pr.stdout,np.int16).astype(np.float32)/32768, sr
p = sys.argv[1]; payoff = float(sys.argv[2]) if len(sys.argv)>2 else None
f = frames(p); r = fps(p); d = (np.abs(np.diff(f,axis=0))>20).mean(axis=(1,2))*100  # % of pixels that visibly change
win = max(1,int(r*0.5)); vis=[]; acc=0; last=-99
for i,x in enumerate(d):
    t=(i+1)/r; acc = acc*0.9 + x
    if x>VT or acc>VT*3:
        if t-last>0.25: vis.append(round(t,2)); last=t
        acc=0
a,sr = audio(p); w=int(sr*0.05); aud=[]
if len(a)>w*2:
    rms = np.sqrt(np.convolve(a*a,np.ones(w)/w,'valid')[::w]+1e-9); db=20*np.log10(rms)
    for k in range(1,len(db)):
        if db[k]-db[k-1]>4 and db[k]>-45:
            t=k*0.05
            if not aud or t-aud[-1]>0.25: aud.append(round(t,2))
dur=len(f)/r; ev=sorted(set([0.0]+vis+aud+[dur])); gaps=np.diff(ev)
k=int(np.argmax(gaps))
print(f"file {p}\nduration {dur:.2f} s, fps {r:.0f}")
print(f"visual events {len(vis)}: {vis[:40]}")
print(f"audio onsets {len(aud)}: {aud[:40]}")
print(f"events per 10 s: {10*(len(ev)-2)/dur:.1f}; longest dead beat {gaps[k]:.2f} s ({ev[k]:.2f}-{ev[k+1]:.2f}) -> {'PASS' if gaps[k]<=2.0 else 'FAIL'} (gate 2.0 s)")
fv = vis[0] if vis else None
print(f"first visual change at {fv} s -> {'PASS' if fv is not None and fv<=0.5 else 'CHECK'} (moving in second 0)")
if payoff is not None: print(f"payoff at {payoff:.2f} s = {100*payoff/dur:.0f}% of length")
