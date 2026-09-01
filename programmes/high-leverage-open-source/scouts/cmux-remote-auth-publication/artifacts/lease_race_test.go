package fieldwork

import (
    "crypto/sha256"
    "crypto/subtle"
    "encoding/hex"
    "encoding/json"
    "errors"
    "fmt"
    "os"
    "path/filepath"
    "strings"
    "sync"
    "sync/atomic"
    "testing"
    "time"
)

// These types/functions are copied from daemon/remote/cmd/cmuxd-remote/ws_pty.go
// at 8ef183f1e5de765b183aec9d1799f17a0848ae84, with one explicit probe hook
// in consumeWebSocketLeaseHooked immediately before the production os.Remove.
type wsLease struct {
    Version       int    `json:"version"`
    TokenSHA256   string `json:"token_sha256"`
    ExpiresAtUnix int64  `json:"expires_at_unix"`
    SessionID     string `json:"session_id,omitempty"`
    SingleUse     bool   `json:"single_use"`
}

type wsAuthFrame struct {
    Type      string `json:"type"`
    Token     string `json:"token"`
    SessionID string `json:"session_id,omitempty"`
}

type wsRPCClientPayload struct {
    Token         string `json:"token"`
    SessionID     string `json:"sessionId"`
    ExpiresAtUnix int64  `json:"expiresAtUnix"`
}

var (
    errWSLeaseMissing   = errors.New("attach lease missing")
    errWSLeaseExpired   = errors.New("attach lease expired")
    errWSLeaseForbidden = errors.New("attach lease rejected")
    wsLeaseMu           sync.Mutex
)

func writeLeaseFile(path string, lease *wsLease) error {
    if strings.TrimSpace(path) == "" {
        return errors.New("lease path is empty")
    }
    return writeJSONFile(path, lease)
}

func writeJSONFile(path string, value any) error {
    dir := filepath.Dir(path)
    if err := os.MkdirAll(dir, 0o700); err != nil {
        return err
    }
    data, err := json.Marshal(value)
    if err != nil {
        return err
    }
    data = append(data, '\n')
    return os.WriteFile(path, data, 0o600)
}

func consumeWebSocketLeaseHooked(path string, auth wsAuthFrame, beforeRemove func()) error {
    wsLeaseMu.Lock()
    defer wsLeaseMu.Unlock()

    data, err := os.ReadFile(path)
    if err != nil {
        if errors.Is(err, os.ErrNotExist) {
            return errWSLeaseMissing
        }
        return err
    }
    var lease wsLease
    if err := json.Unmarshal(data, &lease); err != nil {
        return errWSLeaseForbidden
    }
    if lease.Version != 1 {
        return errWSLeaseForbidden
    }
    if lease.ExpiresAtUnix <= time.Now().Unix() {
        return errWSLeaseExpired
    }
    if lease.SessionID != "" && lease.SessionID != auth.SessionID {
        return errWSLeaseForbidden
    }

    expected, err := hex.DecodeString(strings.TrimSpace(lease.TokenSHA256))
    if err != nil || len(expected) != sha256.Size {
        return errWSLeaseForbidden
    }
    actualHash := sha256.Sum256([]byte(auth.Token))
    if subtle.ConstantTimeCompare(expected, actualHash[:]) != 1 {
        return errWSLeaseForbidden
    }

    if lease.SingleUse {
        if beforeRemove != nil {
            beforeRemove()
        }
        if err := os.Remove(path); err != nil && !errors.Is(err, os.ErrNotExist) {
            return err
        }
    }
    return nil
}

func lease(token, session string, single bool) *wsLease {
    sum := sha256.Sum256([]byte(token))
    return &wsLease{
        Version: 1, TokenSHA256: hex.EncodeToString(sum[:]),
        ExpiresAtUnix: time.Now().Add(time.Hour).Unix(),
        SessionID: session, SingleUse: single,
    }
}

func mustBytes(t *testing.T, path string) []byte {
    t.Helper()
    b, err := os.ReadFile(path)
    if err != nil { t.Fatalf("read %s: %v", path, err) }
    return b
}

func TestOldSingleUseConsumerDeletesReplacement(t *testing.T) {
    dir := t.TempDir()
    path := filepath.Join(dir, "lease.json")
    a := lease("token-A", "sess-A", true)
    b := lease("token-B", "sess-B", true)
    if err := writeLeaseFile(path, a); err != nil { t.Fatal(err) }

    reached := make(chan struct{})
    release := make(chan struct{})
    done := make(chan error, 1)
    go func() {
        done <- consumeWebSocketLeaseHooked(path, wsAuthFrame{Token:"token-A", SessionID:"sess-A"}, func() {
            close(reached)
            <-release
        })
    }()
    <-reached

    // Production admin installation reaches writeLeaseFile without wsLeaseMu.
    if err := writeLeaseFile(path, b); err != nil { t.Fatal(err) }
    installed := mustBytes(t, path)
    close(release)
    if err := <-done; err != nil { t.Fatalf("consume A: %v", err) }

    _, statErr := os.Stat(path)
    if !errors.Is(statErr, os.ErrNotExist) {
        t.Fatalf("replacement survived unexpectedly; stat=%v bytes-before-release=%q", statErr, installed)
    }
    t.Logf("B bytes immediately before releasing A: %q", installed)
    t.Log("surviving state after A removal: pathname absent")
}

func TestNegativeControlInstallAfterConsumeSettles(t *testing.T) {
    dir := t.TempDir()
    path := filepath.Join(dir, "lease.json")
    a := lease("token-A", "sess-A", true)
    b := lease("token-B", "sess-B", true)
    if err := writeLeaseFile(path, a); err != nil { t.Fatal(err) }
    if err := consumeWebSocketLeaseHooked(path, wsAuthFrame{Token:"token-A", SessionID:"sess-A"}, nil); err != nil { t.Fatal(err) }
    if err := writeLeaseFile(path, b); err != nil { t.Fatal(err) }
    got := mustBytes(t, path)
    want, _ := json.Marshal(b); want = append(want, '\n')
    if string(got) != string(want) { t.Fatalf("B mismatch: got=%q want=%q", got, want) }
    t.Logf("surviving B bytes: %q", got)
}

func TestReadRacingInPlaceWriteSeesInvalidJSON(t *testing.T) {
    dir := t.TempDir()
    path := filepath.Join(dir, "lease.json")
    a := lease(strings.Repeat("A", 512), "sess-A", true)
    b := lease(strings.Repeat("B", 512), "sess-B", true)
    if err := writeLeaseFile(path, a); err != nil { t.Fatal(err) }

    var invalid atomic.Int64
    var empty atomic.Int64
    var sampleMu sync.Mutex
    var sample []byte
    stop := make(chan struct{})
    readerDone := make(chan struct{})
    go func() {
        defer close(readerDone)
        for {
            select { case <-stop: return; default: }
            wsLeaseMu.Lock()
            data, err := os.ReadFile(path)
            wsLeaseMu.Unlock()
            if err != nil { continue }
            var l wsLease
            if err := json.Unmarshal(data, &l); err != nil {
                invalid.Add(1)
                if len(data) == 0 { empty.Add(1) }
                sampleMu.Lock()
                if sample == nil { sample = append([]byte(nil), data...) }
                sampleMu.Unlock()
            }
        }
    }()

    for i := 0; i < 100000; i++ {
        if i%2 == 0 { _ = writeLeaseFile(path, b) } else { _ = writeLeaseFile(path, a) }
        if invalid.Load() > 0 { break }
    }
    close(stop); <-readerDone
    if invalid.Load() == 0 {
        t.Fatalf("no invalid read observed in 100000 in-place replacements")
    }
    sampleMu.Lock(); s := append([]byte(nil), sample...); sampleMu.Unlock()
    t.Logf("invalid reads=%d empty=%d first-invalid-len=%d first-invalid=%q", invalid.Load(), empty.Load(), len(s), s)
}

type installSet struct { PTY *wsLease; RPC *wsLease; Client *wsRPCClientPayload }

// Same durable write order as handleWebSocketLeaseInstall after request/auth validation.
func installThree(ptyPath, rpcPath, clientPath string, s installSet) error {
    if s.PTY != nil { if err := writeLeaseFile(ptyPath, s.PTY); err != nil { return fmt.Errorf("pty: %w", err) } }
    if s.RPC != nil { if err := writeLeaseFile(rpcPath, s.RPC); err != nil { return fmt.Errorf("rpc: %w", err) } }
    if s.Client != nil { if err := writeJSONFile(clientPath, s.Client); err != nil { return fmt.Errorf("client: %w", err) } }
    return nil
}

func TestFailureAfterFirstArtifactLeavesMixedGeneration(t *testing.T) {
    dir := t.TempDir()
    ptyPath := filepath.Join(dir, "pty.json")
    rpcPath := filepath.Join(dir, "rpc.json")
    clientPath := filepath.Join(dir, "client.json")
    old := installSet{lease("pty-A","pty-A",true), lease("rpc-A","rpc-A",false), &wsRPCClientPayload{"rpc-A","rpc-A",time.Now().Add(time.Hour).Unix()}}
    if err := installThree(ptyPath,rpcPath,clientPath,old); err != nil { t.Fatal(err) }
    oldRPC := append([]byte(nil), mustBytes(t,rpcPath)...)
    oldClient := append([]byte(nil), mustBytes(t,clientPath)...)

    // Make the configured RPC pathname an existing directory so the second write fails.
    badRPC := filepath.Join(dir, "rpc-dir")
    if err := os.Mkdir(badRPC, 0o700); err != nil { t.Fatal(err) }
    fresh := installSet{lease("pty-B","pty-B",true), lease("rpc-B","rpc-B",false), &wsRPCClientPayload{"rpc-B","rpc-B",time.Now().Add(time.Hour).Unix()}}
    err := installThree(ptyPath,badRPC,clientPath,fresh)
    if err == nil { t.Fatal("expected second-artifact failure") }

    gotPTY := mustBytes(t, ptyPath)
    gotClient := mustBytes(t, clientPath)
    if string(gotClient) != string(oldClient) { t.Fatalf("client unexpectedly changed: %q", gotClient) }
    if string(mustBytes(t,rpcPath)) != string(oldRPC) { t.Fatalf("old rpc unexpectedly changed") }
    t.Logf("install error: %v", err)
    t.Logf("surviving PTY bytes (B): %q", gotPTY)
    t.Logf("surviving RPC bytes (A): %q", oldRPC)
    t.Logf("surviving client bytes (A): %q", gotClient)
}

func parseLeaseSession(t *testing.T, path string) string {
    t.Helper(); var l wsLease
    if err := json.Unmarshal(mustBytes(t,path), &l); err != nil { t.Fatalf("parse %s: %v",path,err) }
    return l.SessionID
}
func parseClientSession(t *testing.T, path string) string {
    t.Helper(); var c wsRPCClientPayload
    if err := json.Unmarshal(mustBytes(t,path), &c); err != nil { t.Fatalf("parse %s: %v",path,err) }
    return c.SessionID
}

func TestConcurrentUnmodifiedThreeFileInstallsCanMix(t *testing.T) {
    dir := t.TempDir(); p:=filepath.Join(dir,"p"); r:=filepath.Join(dir,"r"); c:=filepath.Join(dir,"c")
    rpcTokenX := strings.Repeat("X", 1<<15)
    rpcTokenY := strings.Repeat("Y", 1<<15)
    x := installSet{lease("pty-X","X",true), lease(rpcTokenX,"X",false), &wsRPCClientPayload{rpcTokenX,"X",time.Now().Add(time.Hour).Unix()}}
    y := installSet{lease("pty-Y","Y",true), lease(rpcTokenY,"Y",false), &wsRPCClientPayload{rpcTokenY,"Y",time.Now().Add(time.Hour).Unix()}}
    for i:=0; i<20000; i++ {
        var wg sync.WaitGroup; wg.Add(2)
        go func(){ defer wg.Done(); _=installThree(p,r,c,x) }()
        go func(){ defer wg.Done(); _=installThree(p,r,c,y) }()
        wg.Wait()
        ps, rs, cs := parseLeaseSession(t,p), parseLeaseSession(t,r), parseClientSession(t,c)
        if !(ps==rs && rs==cs) {
            t.Logf("mixed final set at iteration %d: pty=%s rpc=%s client=%s", i, ps, rs, cs)
            t.Logf("pty bytes=%q", mustBytes(t,p)); t.Logf("rpc bytes=%q", mustBytes(t,r));
            cb:=mustBytes(t,c); if len(cb)>200 { cb=cb[:200] }; t.Logf("client prefix=%q", cb)
            var meta wsRPCClientPayload
            if err := json.Unmarshal(mustBytes(t,c), &meta); err != nil { t.Fatal(err) }
            err := consumeWebSocketLeaseHooked(r, wsAuthFrame{Token:meta.Token, SessionID:meta.SessionID}, nil)
            if rs != cs && !errors.Is(err, errWSLeaseForbidden) {
                t.Fatalf("mixed client metadata unexpectedly authenticated against surviving RPC lease: %v", err)
            }
            if rs != cs { t.Logf("restart/reuse consequence: metadata session %s is rejected by surviving RPC lease session %s", cs, rs) }
            return
        }
    }
    t.Fatalf("no mixed set observed in 20000 concurrent install pairs")
}

func atomicWriteJSONFile(path string, value any) error {
    dir := filepath.Dir(path)
    if err := os.MkdirAll(dir, 0o700); err != nil { return err }
    data, err := json.Marshal(value); if err != nil { return err }
    data = append(data, '\n')
    f, err := os.CreateTemp(dir, ".lease-tmp-"); if err != nil { return err }
    tmp := f.Name()
    defer os.Remove(tmp)
    if err := f.Chmod(0o600); err != nil { f.Close(); return err }
    if _, err := f.Write(data); err != nil { f.Close(); return err }
    if err := f.Close(); err != nil { return err }
    return os.Rename(tmp, path)
}

func TestAtomicRenameAloneStillAllowsOldConsumerToDeleteReplacement(t *testing.T) {
    dir := t.TempDir(); path := filepath.Join(dir, "lease.json")
    a := lease("token-A", "sess-A", true); b := lease("token-B", "sess-B", true)
    if err := writeLeaseFile(path, a); err != nil { t.Fatal(err) }
    reached:=make(chan struct{}); release:=make(chan struct{}); done:=make(chan error,1)
    go func(){ done <- consumeWebSocketLeaseHooked(path, wsAuthFrame{Token:"token-A",SessionID:"sess-A"}, func(){close(reached); <-release}) }()
    <-reached
    if err := atomicWriteJSONFile(path,b); err != nil { t.Fatal(err) }
    before := mustBytes(t,path)
    close(release); if err:=<-done; err!=nil { t.Fatal(err) }
    _, err := os.Stat(path)
    if !errors.Is(err, os.ErrNotExist) { t.Fatalf("atomic replacement unexpectedly survived: %v", err) }
    t.Logf("atomic B bytes before old A removal: %q", before)
    t.Log("atomic rename fixes torn reads, yet stale pathname removal still deletes B")
}

func TestAtomicRenamePreventsTornReadControl(t *testing.T) {
    dir:=t.TempDir(); path:=filepath.Join(dir,"lease.json")
    a:=lease(strings.Repeat("A",512),"A",true); b:=lease(strings.Repeat("B",512),"B",true)
    if err:=atomicWriteJSONFile(path,a); err!=nil {t.Fatal(err)}
    var invalid atomic.Int64
    stop:=make(chan struct{}); done:=make(chan struct{})
    go func(){ defer close(done); for { select { case <-stop:return; default: }
        data,err:=os.ReadFile(path); if err!=nil {continue}; var l wsLease; if json.Unmarshal(data,&l)!=nil {invalid.Add(1)}
    }}()
    for i:=0;i<20000;i++ { if i%2==0 {_=atomicWriteJSONFile(path,b)} else {_=atomicWriteJSONFile(path,a)} }
    close(stop); <-done
    if invalid.Load()!=0 { t.Fatalf("atomic rename control observed %d invalid reads", invalid.Load()) }
    t.Log("atomic rename control: 0 invalid JSON reads during 20000 replacements")
}

func writeLeaseFileWithSharedLock(path string, l *wsLease) error {
    wsLeaseMu.Lock(); defer wsLeaseMu.Unlock(); return writeLeaseFile(path,l)
}

func TestSharedLockSerializesOldConsumeBeforeReplacement(t *testing.T) {
    dir:=t.TempDir(); path:=filepath.Join(dir,"lease.json")
    a:=lease("token-A","sess-A",true); b:=lease("token-B","sess-B",true)
    if err:=writeLeaseFile(path,a); err!=nil {t.Fatal(err)}
    reached:=make(chan struct{}); release:=make(chan struct{}); consumed:=make(chan error,1)
    go func(){ consumed <- consumeWebSocketLeaseHooked(path,wsAuthFrame{Token:"token-A",SessionID:"sess-A"},func(){close(reached);<-release}) }()
    <-reached
    writeDone:=make(chan error,1)
    go func(){ writeDone <- writeLeaseFileWithSharedLock(path,b) }()
    select { case err:=<-writeDone: t.Fatalf("writer passed lock before A settled: %v",err); case <-time.After(2*time.Millisecond): }
    close(release); if err:=<-consumed; err!=nil {t.Fatal(err)}; if err:=<-writeDone; err!=nil {t.Fatal(err)}
    got:=mustBytes(t,path); var l wsLease; if err:=json.Unmarshal(got,&l);err!=nil{t.Fatal(err)}
    if l.SessionID!="sess-B" {t.Fatalf("want B, got %s",l.SessionID)}
    t.Logf("shared-lock control surviving bytes: %q",got)
}

func installThreeAtomic(ptyPath,rpcPath,clientPath string,s installSet) error {
    if s.PTY!=nil { if err:=atomicWriteJSONFile(ptyPath,s.PTY);err!=nil{return err} }
    if s.RPC!=nil { if err:=atomicWriteJSONFile(rpcPath,s.RPC);err!=nil{return err} }
    if s.Client!=nil { if err:=atomicWriteJSONFile(clientPath,s.Client);err!=nil{return err} }
    return nil
}

func TestPerArtifactAtomicRenameStillAllowsMixedBundle(t *testing.T) {
    dir:=t.TempDir(); p:=filepath.Join(dir,"p"); r:=filepath.Join(dir,"r"); c:=filepath.Join(dir,"c")
    tx:=strings.Repeat("X",1<<15); ty:=strings.Repeat("Y",1<<15)
    x:=installSet{lease("pty-X","X",true),lease(tx,"X",false),&wsRPCClientPayload{tx,"X",time.Now().Add(time.Hour).Unix()}}
    y:=installSet{lease("pty-Y","Y",true),lease(ty,"Y",false),&wsRPCClientPayload{ty,"Y",time.Now().Add(time.Hour).Unix()}}
    for i:=0;i<20000;i++ {
        var wg sync.WaitGroup; wg.Add(2)
        go func(){defer wg.Done();_=installThreeAtomic(p,r,c,x)}()
        go func(){defer wg.Done();_=installThreeAtomic(p,r,c,y)}()
        wg.Wait()
        ps,rs,cs:=parseLeaseSession(t,p),parseLeaseSession(t,r),parseClientSession(t,c)
        if !(ps==rs && rs==cs) { t.Logf("per-file atomic mixed final set at iteration %d: pty=%s rpc=%s client=%s",i,ps,rs,cs); return }
    }
    t.Fatalf("no mixed set observed in 20000 per-artifact atomic install pairs")
}

func TestFailureAfterSecondArtifactLeavesRPCClientMismatch(t *testing.T) {
    dir:=t.TempDir(); p:=filepath.Join(dir,"p"); r:=filepath.Join(dir,"r"); c:=filepath.Join(dir,"c")
    old:=installSet{lease("pty-A","pty-A",true),lease("rpc-A","rpc-A",false),&wsRPCClientPayload{"rpc-A","rpc-A",time.Now().Add(time.Hour).Unix()}}
    if err:=installThree(p,r,c,old);err!=nil{t.Fatal(err)}
    badClient:=filepath.Join(dir,"client-dir"); if err:=os.Mkdir(badClient,0o700);err!=nil{t.Fatal(err)}
    fresh:=installSet{lease("pty-B","pty-B",true),lease("rpc-B","rpc-B",false),&wsRPCClientPayload{"rpc-B","rpc-B",time.Now().Add(time.Hour).Unix()}}
    err:=installThree(p,r,badClient,fresh); if err==nil{t.Fatal("expected client write failure")}
    var meta wsRPCClientPayload; if err:=json.Unmarshal(mustBytes(t,c),&meta);err!=nil{t.Fatal(err)}
    rs:=parseLeaseSession(t,r)
    authErr:=consumeWebSocketLeaseHooked(r,wsAuthFrame{Token:meta.Token,SessionID:meta.SessionID},nil)
    if !errors.Is(authErr,errWSLeaseForbidden){t.Fatalf("stale client metadata unexpectedly authenticated: %v",authErr)}
    t.Logf("install error: %v",err)
    t.Logf("surviving sessions after interruption/restart: pty=%s rpc=%s client=%s",parseLeaseSession(t,p),rs,meta.SessionID)
    t.Logf("reuse consequence: client metadata %s rejected by surviving RPC lease %s",meta.SessionID,rs)
}
