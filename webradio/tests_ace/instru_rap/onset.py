import subprocess,sys,numpy as np
from numpy.fft import rfft,rfftfreq
f=sys.argv[1]; sr=22050
x=np.frombuffer(subprocess.run(['ffmpeg','-loglevel','error','-i',f,'-ac','1','-ar','22050','-f','f32le','-'],capture_output=True).stdout,dtype=np.float32)
low=[]
for i in range(int(len(x)/sr)):
    s=x[i*sr:(i+1)*sr]; S=np.abs(rfft(s*np.hanning(len(s)))); fr=rfftfreq(len(s),1/sr); low.append(S[fr<120].sum())
low=np.array(low); ref=np.median(low[:8])
print(' '.join(f"{i}:{v:.0f}" for i,v in enumerate(low[:40])))
