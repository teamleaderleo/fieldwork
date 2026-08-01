import os, sys, time
from pathlib import Path
root = Path(sys.argv[1])
(root / 'child-ready').write_text(str(os.getpid()))
time.sleep(0.8)
(root / 'later-work').write_text('ran')
