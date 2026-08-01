import os, signal, subprocess, sys, tempfile, time
from pathlib import Path
root = Path('/tmp/unit13-probe')

def live(pid):
    try: os.kill(pid, 0)
    except ProcessLookupError: return False
    try: return Path(f'/proc/{pid}/stat').read_text().split()[2] != 'Z'
    except OSError: return False

results=[]
with tempfile.TemporaryDirectory(prefix='unit13-run-') as td:
    base=Path(td)
    for variant in ('baseline','status','group'):
        case=base/variant; case.mkdir()
        p=subprocess.Popen([sys.executable, str(root/'driver.py'), variant, str(case)])
        deadline=time.time()+5
        while time.time()<deadline and not (case/'child-ready').exists(): time.sleep(.01)
        if not (case/'child-ready').exists():
            p.kill(); p.wait(); raise RuntimeError(f'{variant}: start timeout')
        wrapper_pid, child_pid = map(int,(case/'wrapper-ready').read_text().split())
        os.kill(p.pid, signal.SIGINT)
        rc=p.wait(timeout=5)
        time.sleep(1.0)
        later=(case/'later-work').exists(); alive=live(child_pid)
        results.append((variant,rc,later,alive))
        if live(child_pid): os.kill(child_pid, signal.SIGKILL)
        if live(wrapper_pid): os.kill(wrapper_pid, signal.SIGKILL)
for v,rc,later,alive in results:
    print(f'variant={v} rc={rc} later_work={str(later).lower()} child_live={str(alive).lower()}')
assert results[0][1:] == (0, True, False)
assert results[1][1:] == (130, True, False)
assert results[2][1:] == (130, False, False)
