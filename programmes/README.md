# Programmes

This directory is the durable coordinator surface for long-lived research directions.

## Layout

```text
programmes/
├── registry.yml
├── <programme>/
│   ├── STATUS.md          # coordinator-owned
│   ├── scouts/
│   │   └── <scout>/
│   │       ├── report.md  # scout-owned
│   │       └── artifacts/
│   └── synthesis.md       # coordinator-owned when needed
```

Programme hubs and scout issues are the live coordination surface. The registry provides stable discovery. Scout reports and artifacts hold durable evidence.

Workers must not edit `registry.yml`, programme `STATUS.md`, or programme synthesis unless they are explicitly acting as the programme coordinator.
