import os, signal, subprocess, sys
from pathlib import Path
variant, root = sys.argv[1], Path(sys.argv[2])
wrapper = str(Path(__file__).with_name('wrapper.py'))
kwargs = {'start_new_session': True} if variant == 'group' else {}
proc = subprocess.Popen([sys.executable, wrapper, str(root)], **kwargs)
(root / 'driver-ready').write_text(str(proc.pid))
try:
    proc.wait()
except KeyboardInterrupt:
    if variant == 'group':
        try:
            os.killpg(proc.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
    else:
        proc.terminate()
    proc.wait()
    raise SystemExit(0 if variant == 'baseline' else 130)
