package main

import (
  "fmt"
  "net"
  "os"
  "path/filepath"
  "time"
)

func main() {
  dir, err := os.MkdirTemp("", "cmux-socket-control-")
  if err != nil { panic(err) }
  defer os.RemoveAll(dir)
  path := filepath.Join(dir, "cmux-cloud-cli.sock")

  rawA, err := net.ListenUnix("unix", &net.UnixAddr{Name: path, Net: "unix"})
  if err != nil { panic(err) }
  rawA.SetUnlinkOnClose(false)
  aInfo, err := os.Lstat(path)
  if err != nil { panic(err) }

  aExited := make(chan struct{})
  go func() {
    defer close(aExited)
    for {
      c, err := rawA.Accept()
      if err != nil { return }
      c.Close()
    }
  }()

  _ = os.Remove(path)
  b, err := net.Listen("unix", path)
  if err != nil { panic(err) }
  defer b.Close()
  fmt.Println("CONTROL_B_READY", exists(path))

  _ = rawA.Close()
  select { case <-aExited: case <-time.After(2*time.Second): panic("A did not exit") }

  if cur, err := os.Lstat(path); err == nil && os.SameFile(aInfo, cur) {
    _ = os.Remove(path)
    fmt.Println("CONTROL_CLEANUP_REMOVED_CURRENT", true)
  } else {
    fmt.Println("CONTROL_CLEANUP_REMOVED_CURRENT", false)
  }

  fmt.Println("CONTROL_PATH_AFTER_A_CLEANUP", exists(path))
  c, err := net.DialTimeout("unix", path, 100*time.Millisecond)
  fmt.Println("CONTROL_NEW_DIAL_OK", err == nil)
  if c != nil { c.Close() }
}

func exists(path string) bool { _, err := os.Lstat(path); return err == nil }
