# Target Map: Supabase

Repository: https://redirect.github.com/supabase/supabase

## In simple words

A developer platform around Postgres, authentication, storage, realtime, functions, and client SDKs. Interesting failures often cross generated types, authorization, retries, network state, and several services.

## Areas worth understanding

- client initialization and session lifecycle;
- authentication refresh and recovery;
- realtime reconnection and ordering;
- generated types versus runtime behavior;
- edge-function invocation and retries;
- storage upload and partial failure;
- database migrations and compatibility;
- local versus hosted behavior.

## Evidence we can produce

- local synthetic projects;
- auth and reconnect state machines;
- type/runtime comparison cases;
- retry and partial-failure experiments;
- integration trials in Fin Agent or Stensibly;
- local/hosted behavior matrices where safe.

## Entry standard

Identify which repository or package owns the behavior. Record service, client, CLI, and schema versions. Avoid claims based on one hosted deployment when local or client behavior can be isolated.

## Stop conditions

- the experiment requires real user data or production credentials;
- the behavior belongs solely to application authorization policy;
- the result is only dashboard presentation or documentation cleanup;
- several services are involved but the owning boundary cannot be isolated.
