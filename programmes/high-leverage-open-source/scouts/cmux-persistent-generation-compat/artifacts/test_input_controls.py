import os, json, time, subprocess, sqlite3, signal, pathlib, shutil, socket, threading
BIN='/mnt/data/cmux-eaa899c/cmux-tui-x86_64-unknown-linux-musl'


def wait_path(p, timeout=10):
    end=time.time()+timeout
    while time.time()<end:
        if p.exists(): return True
        time.sleep(.005)
    return False

def pid_alive(pid): return pathlib.Path(f'/proc/{pid}').exists()

def start(root, env=None):
    sock=root/'mux.sock'; state=root/'state'
    e=os.environ.copy(); e.update(env or {})
    p=subprocess.Popen([BIN,'--headless','--session','audit','--socket',str(sock),'--state',str(state)],
                       stdout=open(root/f'd{int(time.time()*1000)}.out','w'), stderr=open(root/f'd{int(time.time()*1000)}.err','w'), env=e)
    if not wait_path(sock): raise RuntimeError('socket timeout')
    return p,sock,state

def cli(sock,name,key,params,timeout=20):
    r=subprocess.run([BIN,'--socket',str(sock),'--json','raw','operation',name,'--mutation','--idempotency-key',key,'--params-json',json.dumps(params,separators=(',',':'))],capture_output=True,text=True,timeout=timeout)
    if r.returncode: raise RuntimeError((name,r.returncode,r.stdout,r.stderr))
    return json.loads(r.stdout)

def request(sock,req,timeout=10):
    s=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM); s.connect(str(sock)); s.settimeout(timeout)
    s.sendall(json.dumps(req,separators=(',',':')).encode()+b'\n'); b=b''
    try:
        while b'\n' not in b:
            q=s.recv(65536)
            if not q: break
            b+=q
    finally: s.close()
    return json.loads(b.split(b'\n',1)[0]) if b else None

def identify(sock):
    s=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM); s.connect(str(sock)); s.settimeout(5)
    s.sendall(b'{"id":999,"cmd":"identify"}\n'); b=b''
    while b'\n' not in b:
        q=s.recv(65536)
        if not q: break
        b+=q
    s.close(); return json.loads(b.split(b'\n',1)[0])['data']

def setup_terminal(root, short=False):
    d,sock,state=start(root)
    ws=cli(sock,'workspace.create','ws-key',{'machine':'current','session':'current','name':'Audit','initial_content':'empty','correlation_key':'ws-corr'})['value']['workspace_id']
    ready=root/'ready'; effect=root/'effect'; childpid=root/'child.pid'
    tail="" if short else "; time.sleep(600)"
    py=("import os,tty,time; tty.setraw(0); "
        f"open({str(childpid)!r},'w').write(str(os.getpid())); open({str(ready)!r},'w').close(); "
        "b=os.read(0,1); "
        f"open({str(effect)!r},'ab').write(b)"+tail)
    run=cli(sock,'workspace.run','run-key',{'machine':'current','session':'current','workspace':ws,'argv':['/usr/bin/python3','-c',py],'correlation_key':'run-corr'})['value']
    assert wait_path(ready)
    recs=[p for p in state.rglob('*.json') if p.name.endswith('.json')]
    assert len(recs)==1,recs
    rec=json.loads(recs[0].read_text())
    return d,sock,state,run['terminal_id'],recs[0],rec,int(childpid.read_text()),effect


def committed_control():
    root=pathlib.Path('/mnt/data/cmux-audit-input-committed-control'); shutil.rmtree(root,ignore_errors=True); root.mkdir()
    d,sock,state,term,recpath,rec,cpid,effect=setup_terminal(root,False)
    gen1=identify(sock)['generation']; hpid=rec['host_pid']; inc=rec['terminal_incarnation'] if 'terminal_incarnation' in rec else rec.get('incarnation')
    req={'protocol':'cmux.protocol/2','type':'request','id':'input-request','operation':'terminal.input.write','idempotency_key':'input-key','params':{'machine':'current','session':'current','terminal':term,'text':'X'}}
    first=request(sock,req)
    assert wait_path(effect,3), 'effect not observed'
    db=next(state.rglob('workspace-registry.sqlite3')); con=sqlite3.connect(db)
    er=con.execute("select state,outcome_json,committed_revision from resource_effect_receipts where idempotency_key='input-key'").fetchone()
    comp=con.execute("select count(*) from resource_input_receipt_completions where idempotency_key='input-key'").fetchone()[0]
    jr=con.execute("select sequence,kind,correlation_id,payload_json from session_journal where correlation_id='input-key' order by sequence").fetchall(); con.close()
    print('COMMITTED FIRST',first,'effect',effect.read_bytes(),'receipt',er,'completion_rows',comp,'journal',jr,'gen',gen1,'host',hpid,'inc',inc)
    os.kill(d.pid,signal.SIGKILL); d.wait(timeout=5); time.sleep(.2)
    print('COMMITTED POST_KILL host_alive',pid_alive(hpid),'child_alive',pid_alive(cpid),'effect',effect.read_bytes())
    try:sock.unlink()
    except FileNotFoundError:pass
    d2,sock2,_=start(root); gen2=identify(sock2)['generation']; time.sleep(.3)
    # exact replay
    replay=request(sock2,req)
    time.sleep(.2)
    recs=[p for p in state.rglob('*.json') if p.name.endswith('.json')]
    live=[]
    for p in recs:
        try:
            rr=json.loads(p.read_text()); live.append((str(p),rr.get('host_pid'),rr.get('terminal_id'),rr.get('terminal_incarnation') or rr.get('incarnation')))
        except:pass
    con=sqlite3.connect(db)
    er2=con.execute("select state,outcome_json,committed_revision from resource_effect_receipts where idempotency_key='input-key'").fetchone()
    comp2=con.execute("select count(*) from resource_input_receipt_completions where idempotency_key='input-key'").fetchone()[0]
    jr2=con.execute("select sequence,kind,correlation_id,payload_json from session_journal where correlation_id='input-key' order by sequence").fetchall(); con.close()
    print('COMMITTED REPLAY',replay,'effect',effect.read_bytes(),'receipt',er2,'completion_rows',comp2,'journal',jr2,'gen2',gen2,'host_records',live)
    assert effect.read_bytes()==b'X'
    assert er2[0]=='committed' and comp2==1
    assert replay['ok'] is True and replay['result'].get('replayed') is True
    cli(sock2,'terminal.close','close-key',{'machine':'current','session':'current','terminal':term}); time.sleep(.3)
    d2.terminate(); d2.wait(timeout=5)
    (root/'summary.json').write_text(json.dumps({'generation_before':gen1,'generation_after':gen2,'host_pid':hpid,'child_pid':cpid,'first':first,'replay':replay,'effect':effect.read_bytes().decode(),'receipt_before':er,'receipt_after':er2,'completion_rows_before':comp,'completion_rows_after':comp2,'journal_before':jr,'journal_after':jr2,'host_records_after_restart':live},default=str,indent=2))


def short_after_effect():
    root=pathlib.Path('/mnt/data/cmux-audit-input-short-after-effect'); shutil.rmtree(root,ignore_errors=True); root.mkdir()
    d,sock,state,term,recpath,rec,cpid,effect=setup_terminal(root,True)
    gen1=identify(sock)['generation']; hpid=rec['host_pid']; inc=rec.get('terminal_incarnation') or rec.get('incarnation')
    os.kill(hpid,signal.SIGSTOP); time.sleep(.05)
    db=next(state.rglob('workspace-registry.sqlite3'))
    payload='X'*(2*1024*1024)
    req={'protocol':'cmux.protocol/2','type':'request','id':'input-request','operation':'terminal.input.write','idempotency_key':'input-key','params':{'machine':'current','session':'current','terminal':term,'text':payload}}
    response={}
    def worker():
        try: response['value']=request(sock,req,30)
        except Exception as e: response['error']=repr(e)
    t=threading.Thread(target=worker,daemon=True); t.start()
    end=time.time()+10; er=None
    while time.time()<end:
        try:
            c=sqlite3.connect(db,timeout=.1); er=c.execute("select state,outcome_json,committed_revision from resource_effect_receipts where idempotency_key='input-key'").fetchone(); c.close()
        except sqlite3.OperationalError: er=None
        if er and er[0]=='executing':break
        time.sleep(.005)
    assert er and er[0]=='executing',er
    lock=sqlite3.connect(db,timeout=1,isolation_level=None); lock.execute('BEGIN IMMEDIATE')
    os.kill(hpid,signal.SIGCONT)
    assert wait_path(effect,5),'short child never consumed input'
    # allow short child to exit and host to publish owner-side exit record; daemon DB commits remain fenced
    end=time.time()+3
    exit_paths=[]
    while time.time()<end:
        exit_paths=list(state.rglob('*.exit'))
        if exit_paths or not pid_alive(cpid): break
        time.sleep(.005)
    time.sleep(.05)
    os.kill(d.pid,signal.SIGSTOP); time.sleep(.02)
    # reader still sees pre-lock state
    c=sqlite3.connect(db,timeout=.2)
    er2=c.execute("select state,outcome_json,committed_revision from resource_effect_receipts where idempotency_key='input-key'").fetchone()
    j0=c.execute("select count(*) from session_journal where correlation_id='input-key'").fetchone()[0]
    th=c.execute("select terminal_id,incarnation,lifecycle,exit_json,updated_revision from terminal_hosts where terminal_id=(select terminal_id from resource_terminals where public_id=?)",(term,)).fetchone(); c.close()
    print('SHORT BEFORE_KILL effect',effect.read_bytes(),'receipt',er2,'journal_count',j0,'child_alive',pid_alive(cpid),'host_alive',pid_alive(hpid),'exit_files',[str(x) for x in exit_paths],'terminal_row',th,'gen',gen1,'inc',inc)
    os.kill(d.pid,signal.SIGKILL); d.wait(timeout=5); lock.rollback(); lock.close(); time.sleep(.3)
    print('SHORT POST_KILL effect',effect.read_bytes(),'child_alive',pid_alive(cpid),'host_alive',pid_alive(hpid),'records',[str(x) for x in state.rglob('*.json')],'exits',[str(x) for x in state.rglob('*.exit')], 'response',response)
    try:sock.unlink()
    except FileNotFoundError:pass
    d2,sock2,_=start(root); gen2=identify(sock2)['generation']; time.sleep(.5)
    replay=request(sock2,req,10)
    c=sqlite3.connect(db)
    er3=c.execute("select state,outcome_json,committed_revision from resource_effect_receipts where idempotency_key='input-key'").fetchone()
    jr=c.execute("select sequence,kind,correlation_id,payload_json from session_journal where correlation_id='input-key' order by sequence").fetchall()
    termrow=c.execute("select h.lifecycle,h.exit_json,h.incarnation,h.updated_revision from terminal_hosts h join resource_terminals t on t.terminal_id=h.terminal_id where t.public_id=?",(term,)).fetchone()
    exitsnap=c.execute("select terminal_id,generation,covered_through from terminal_exit_snapshots where terminal_id=(select terminal_id from resource_terminals where public_id=?)",(term,)).fetchall(); c.close()
    print('SHORT REPLAY',replay,'receipt',er3,'journal',jr,'effect',effect.read_bytes(),'termrow',termrow,'exit_snapshots',exitsnap,'gen2',gen2)
    assert replay['ok'] is False and replay['error']['code']=='mutation.indeterminate'
    assert er3[0]=='indeterminate' and effect.read_bytes()==b'X'
    # cleanup may already be detached/exited; terminate daemon
    d2.terminate();
    try:d2.wait(timeout=5)
    except: d2.kill(); d2.wait()
    (root/'summary.json').write_text(json.dumps({'generation_before':gen1,'generation_after':gen2,'host_pid':hpid,'child_pid':cpid,'incarnation':inc,'pre_receipt':er,'before_kill_receipt':er2,'replay':replay,'after_receipt':er3,'journal':jr,'terminal_after':termrow,'exit_snapshots':exitsnap,'effect':effect.read_bytes().decode()},default=str,indent=2))

print('=== COMMITTED CONTROL ==='); committed_control()
print('=== SHORT AFTER-EFFECT ==='); short_after_effect()
