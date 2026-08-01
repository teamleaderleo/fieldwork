import os, subprocess, sys
from pathlib import Path
root = Path(sys.argv[1])
child = subprocess.Popen([sys.executable, str(Path(__file__).with_name('child.py')), str(root)])
(root / 'wrapper-ready').write_text(f'{os.getpid()} {child.pid}')
child.wait()
