import os, json, time, subprocess, sqlite3, signal, pathlib, shutil, socket, threading
BIN='/mnt/data/cmux-eaa899c/cmux-tui-x86_64-unknown-linux-musl'

def run_case(case, resume_before_kill):
 ROOT=pathlib.Path('/mnt/data')/f'cmux-audit-input-{case}'
 shutil.rmtree(ROOT,ignore_errors=True); ROOT.mkdir()
 SOCK=ROOT/'mux.sock'; STATE=ROOT/'state';
 def wait_socket(t=10):
  end=time.time()+t
  while time.time()<end:
   if SOCK.exists(): return
   time.sleep(.005)
  raise RuntimeError('socket timeout')
 def cliop(name,key,params,timeout=20):
  return subprocess.run([BIN,'--socket',str(SOCK),'--json','raw','operation',name,'--mutation','--idempotency-key',key,'--params-json',json.dumps(params,separators=(',',':'))],capture_output=True,text=True,timeout=timeout)
 d1=subprocess.Popen([BIN,'--headless','--session','audit','--socket',str(SOCK),'--state',str(STATE)],stdout=open(ROOT/'d1.out','w'),stderr=open(ROOT/'d1.err','w'))
 wait_socket()
 c=cliop('workspace.create','ws-key',{'machine':'current','session':'current','name':'Audit','initial_content':'empty','correlation_key':'ws-corr'}); assert c.returncode==0,c.stderr
 ws=json.loads(c.stdout)['value']['workspace_id']
 ready=ROOT/'ready'; effect=ROOT/'effect'; childpid=ROOT/'child.pid'
 py=("import os,tty,time; tty.setraw(0); "
     f"open({str(childpid)!r},'w').write(str(os.getpid())); open({str(ready)!r},'w').close(); "
     "b=os.read(0,1); "
     f"open({str(effect)!r},'wb').write(b); time.sleep(600)")
 r=cliop('workspace.run','run-key',{'machine':'current','session':'current','workspace':ws,'argv':['/usr/bin/python3','-c',py],'correlation_key':'run-corr'},timeout=20); assert r.returncode==0,(r.stdout,r.stderr)
 runval=json.loads(r.stdout)['value']; term=runval['terminal_id']
 end=time.time()+5
 while time.time()<end and not ready.exists(): time.sleep(.005)
 assert ready.exists()
 recs=list(STATE.rglob('*.json')); assert len(recs)==1,recs
 rec_path=recs[0]; rec=json.loads(rec_path.read_text()); hpid=rec['host_pid']; cpid=int(childpid.read_text())
 # Stop owner before submitting input, so daemon blocks in large host write after durable prepare.
 os.kill(hpid,signal.SIGSTOP); time.sleep(.05)
 db=next(STATE.rglob('workspace-registry.sqlite3'))
 payload='X'*(2*1024*1024)
 req={'protocol':'cmux.protocol/2','type':'request','id':'input-request','operation':'terminal.input.write','idempotency_key':'input-key','params':{'machine':'current','session':'current','terminal':term,'text':payload}}
 response={}
 def request_thread():
  s=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM); s.connect(str(SOCK)); s.settimeout(30)
  try:
   s.sendall(json.dumps(req,separators=(',',':')).encode()+b'\n')
   buf=b''
   while b'\n' not in buf:
    x=s.recv(65536)
    if not x: break
    buf+=x
   response['raw']=buf.split(b'\n',1)[0].decode(errors='replace')
  except Exception as e: response['error']=repr(e)
  finally: s.close()
 t=threading.Thread(target=request_thread,daemon=True); t.start()
 # Wait for durable prepare executing, proving the request crossed registry prepare.
 end=time.time()+10; eff=None
 while time.time()<end:
  try:
   con=sqlite3.connect(db,timeout=.1)
   eff=con.execute("select state,outcome_json,committed_revision from resource_effect_receipts where idempotency_key='input-key'").fetchone()
   con.close()
  except sqlite3.OperationalError: eff=None
  if eff and eff[0]=='executing': break
  time.sleep(.005)
 assert eff and eff[0]=='executing',eff
 # Ensure no completion event exists yet.
 con=sqlite3.connect(db); j0=con.execute("select count(*) from session_journal where correlation_id='input-key'").fetchone()[0]; con.close(); assert j0==0,j0
 print(case,'PREPARED','daemon',d1.pid,'host',hpid,'child',cpid,'effect_receipt',eff,'journal_count',j0,'effect_file',effect.exists())
 lock=None
 if resume_before_kill:
  # Fence completion: with host stopped, daemon is still inside external write. Hold SQLite writer before allowing it to finish.
  lock=sqlite3.connect(db,timeout=1,isolation_level=None); lock.execute('BEGIN IMMEDIATE')
  print(case,'DB_WRITE_LOCK_HELD')
  os.kill(hpid,signal.SIGCONT)
  end=time.time()+5
  while time.time()<end and not effect.exists(): time.sleep(.002)
  assert effect.exists(),'external PTY consumer never observed input'
  print(case,'EXTERNAL_EFFECT_OBSERVED',effect.read_bytes()[:8])
  # freeze daemon once owner has definitely consumed input, then inspect durable state from WAL reader.
  os.kill(d1.pid,signal.SIGSTOP); time.sleep(.03)
  con=sqlite3.connect(db,timeout=.2)
  eff2=con.execute("select state,outcome_json,committed_revision from resource_effect_receipts where idempotency_key='input-key'").fetchone()
  j1=con.execute("select count(*) from session_journal where correlation_id='input-key'").fetchone()[0]
  con.close(); print(case,'BEFORE_KILL','effect_receipt',eff2,'journal_count',j1); assert eff2[0]=='executing' and j1==0
 else:
  # Kill while owner remains stopped and the large host frame is incomplete.
  print(case,'KILL_WITH_HOST_STOPPED')
 # daemon SIGKILL at the targeted boundary
 os.kill(d1.pid,signal.SIGKILL); d1.wait(timeout=5)
 if lock is not None:
  lock.rollback(); lock.close()
 # host independently survives; allow it to drain/discard any old connection bytes.
 try: os.kill(hpid,signal.SIGCONT)
 except ProcessLookupError: pass
 time.sleep(.3)
 print(case,'POST_KILL','host_alive',pathlib.Path(f'/proc/{hpid}').exists(),'child_alive',pathlib.Path(f'/proc/{cpid}').exists(),'effect_file',effect.exists(),'request_response',response)
 # restart same state and wait for recovery
 try: SOCK.unlink()
 except FileNotFoundError: pass
 d2=subprocess.Popen([BIN,'--headless','--session','audit','--socket',str(SOCK),'--state',str(STATE)],stdout=open(ROOT/'d2.out','w'),stderr=open(ROOT/'d2.err','w'))
 wait_socket(); time.sleep(.4)
 # exact replay: same operation/key/payload; use socket to avoid argv size limits
 replay={}
 s=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM); s.connect(str(SOCK)); s.settimeout(5); s.sendall(json.dumps(req,separators=(',',':')).encode()+b'\n'); buf=b''
 try:
  while b'\n' not in buf:
   x=s.recv(65536)
   if not x: break
   buf+=x
 except Exception as e: replay['recv_error']=repr(e)
 s.close(); replay['raw']=buf.split(b'\n',1)[0].decode(errors='replace')
 con=sqlite3.connect(db)
 er=con.execute("select state,outcome_json,committed_revision from resource_effect_receipts where idempotency_key='input-key'").fetchone()
 jr=con.execute("select sequence,kind,correlation_id,payload_json from session_journal where correlation_id='input-key' order by sequence").fetchall()
 con.close()
 print(case,'REPLAY',replay); print(case,'RECOVERED_EFFECT',er); print(case,'JOURNAL',json.dumps(jr)); print(case,'EFFECT_FILE_AFTER_REPLAY',effect.exists(),effect.read_bytes()[:1] if effect.exists() else None)
 (ROOT/'summary.json').write_text(json.dumps({'case':case,'resume_before_kill':resume_before_kill,'pre':eff,'post_effect_file':effect.exists(),'replay':replay,'recovered_effect':er,'journal':jr,'host_pid':hpid,'child_pid':cpid},default=str,indent=2))
 # cleanup terminal, which also kills hosted child
 close=cliop('terminal.close','close-key',{'machine':'current','session':'current','terminal':term},timeout=10); print(case,'CLOSE',close.returncode,close.stdout.strip(),close.stderr.strip())
 time.sleep(.3); d2.terminate();
 try:d2.wait(timeout=3)
 except: d2.kill();d2.wait()
 return {'effect':effect.exists(),'replay':replay,'receipt':er,'journal':jr}

print('=== AFTER EFFECT CASE ===')
a=run_case('after-effect',True)
print('=== BEFORE EFFECT CASE ===')
b=run_case('before-effect',False)
print('FINAL',a,b)
