# Target Map: Gemini CLI

Repository: https://github.com/google-gemini/gemini-cli

## Why it is here

A prominent open AI coding tool exposes real problems in agent loops, terminal interaction, tool execution, configuration, sandboxing, extensions, and model-facing developer experience.

## Areas worth understanding

- tool invocation and approval boundaries;
- terminal and shell portability;
- session persistence and recovery;
- extension and MCP integration;
- structured error reporting;
- repository context collection;
- automated testing of interactive flows.

## Evidence we can produce

- isolated repositories and command transcripts;
- cross-shell and cross-platform matrices;
- deterministic tool fixtures;
- recovery and cancellation tests;
- malformed-output and partial-failure cases;
- accessibility and terminal-state reproductions.

## Entry standard

Confirm current roadmap and contribution guidance before implementation. Separate model behaviour, service behaviour, CLI orchestration, and terminal presentation.

## Stop conditions

- the result depends on non-reproducible model variance alone;
- the relevant behaviour is controlled entirely by a closed service;
- maintainers have declared the area in transition;
- the lead is merely an opportunity to work on a famous repository.
