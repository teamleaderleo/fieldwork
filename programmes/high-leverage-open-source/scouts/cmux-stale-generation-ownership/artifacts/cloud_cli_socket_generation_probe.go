package main

import (
  "fmt"
  "net"
  "os"
  "path/filepath"
  "time"
)

func main() {
  dir, err := os.MkdirTemp("", "cmux-socket-gen-")
  if err != nil { panic(err) }
  defer os.RemoveAll(dir)
  path := filepath.Join(dir, "cmux-cloud-cli.sock")

  a, err := net.Listen("unix", path)
  if err != nil { panic(err) }
  aExited := make(chan struct{})
  go func() {
    defer close(aExited)
    defer os.Remove(path)
    for {
      c, err := a.Accept()
      if err != nil { return }
      c.Close()
    }
  }()
  fmt.Println("A_READY", exists(path))

  _ = os.Remove(path)
  b, err := net.Listen("unix", path)
  if err != nil { panic(err) }
  defer b.Close()
  fmt.Println("B_READY", exists(path))

  pre, err := net.Dial("unix", path)
  if err != nil { panic(err) }
  fmt.Println("B_DIAL_BEFORE_A_CLEANUP", err == nil)

  _ = a.Close()
  select {
  case <-aExited:
  case <-time.After(2*time.Second): panic("A accept loop did not exit")
  }
  fmt.Println("PATH_AFTER_A_CLEANUP", exists(path))

  _ = pre.SetDeadline(time.Now().Add(100*time.Millisecond))
  fmt.Println("B_PREEXISTING_CONN_FD_OPEN", pre != nil)
  pre.Close()

  _, err = net.DialTimeout("unix", path, 100*time.Millisecond)
  fmt.Printf("NEW_DIAL_AFTER_A_CLEANUP_OK %v ERR %v\n", err == nil, err)
}

func exists(path string) bool {
  _, err := os.Lstat(path)
  return err == nil
}
