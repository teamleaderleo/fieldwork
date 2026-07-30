# What the hell are we doing here?

Fieldwork looks for places where software **says one thing happened, while the computer actually did something else**.

That sounds small. It is not always small.

A program may say:

- “the data loaded” when loading failed;
- “the process stopped” while part of it is still running;
- “this value is valid” and then corrupt its own bookkeeping;
- “nothing changed” while a background action already happened.

Those disagreements cause the worst kind of bugs: the application keeps going with a false understanding of reality.

Fieldwork tries to catch those bugs before proposing a repair.

## The basic method

1. Find a suspicious boundary in a real open-source project.
2. Read the exact source code that users are running.
3. Reproduce the behavior with the released package or a pinned commit.
4. Write a test that fails for the right reason.
5. Try the smallest reasonable repair in an owned fork.
6. Test the repair against nearby behavior so it does not fix one thing by breaking another.
7. Record exactly what ran, on which commit, and what is still unproven.

The receipts are not paperwork for its own sake. They stop us from turning a plausible story into a confident but false claim.

# The Zustand example, explained like you are five

## What is Zustand?

Zustand is a small JavaScript library that helps an application remember things while it is running.

Imagine an app has a little box labeled **current memory**. It may contain:

- whether you are logged in;
- what is in your shopping cart;
- which theme you selected;
- the draft you were editing;
- whether an onboarding screen is finished.

Zustand helps the app read and change what is inside that box.

## What does “persist” mean?

Normally, the box disappears when the app closes or the page reloads.

The `persist` feature copies important things from the box into longer-term storage, such as the browser's local storage. When the app starts again, Zustand reads that saved copy and puts it back into the memory box.

That loading-back step is called **rehydration**.

A simple picture is:

> app memory → save it → app closes → app starts → load it back

# Problem one: the app is told “done” when loading actually failed

Zustand gives callers several ways to ask whether rehydration finished:

- wait for `rehydrate()`;
- check `hasHydrated()`;
- listen for `onFinishHydration()`.

In the current failure path, these signals disagree.

Imagine asking someone to bring your lunch from the refrigerator.

They come back and say, “Done.”

But:

- they did not bring the lunch;
- the “lunch arrived” light is still off;
- the lunch-arrival bell never rang;
- only a special optional person standing nearby was quietly told that the refrigerator was broken.

That is roughly what happens today when storage reading, JSON parsing, migration, or state merging fails:

- waiting for `rehydrate()` finishes as though nothing went wrong;
- `hasHydrated()` remains false;
- finish listeners do not run;
- the old/default state remains in memory;
- the error is visible only through an optional callback.

## Why should anyone care?

An application may interpret the completed wait as success and continue using default or stale state.

Possible results include:

- a logged-in user being treated as logged out;
- a loading screen waiting forever because the finish signal never arrives;
- a shopping cart appearing empty;
- a saved draft not appearing;
- application startup continuing with the wrong settings;
- two parts of the same application disagreeing about whether loading is finished.

The proposed fork repair does not pretend failed hydration was successful. It makes an **explicit** `rehydrate()` call reject with the real error, while automatic startup loading keeps its existing contained-error behavior.

It also keeps `hasHydrated()` and the finish event as success signals.

# Problem two: a blank option can erase a working default

Zustand supplies safe default behavior for several persistence options.

JavaScript object spreading has a sharp edge: a property that is present with the value `undefined` is still copied. It can replace a useful default even though the caller did not provide a useful replacement.

Imagine a machine comes with these instructions:

- use this storage cupboard;
- prepare the whole state before saving it;
- use version zero;
- combine saved state with current state using this safe method.

Then somebody attaches blank sticky notes labeled:

- `storage: undefined`;
- `partialize: undefined`;
- `version: undefined`;
- `merge: undefined`.

The blank notes cover the real instructions.

The machine later tries to follow the missing instruction and breaks.

## What did that cause?

The released behavior allows several bad states:

- an undefined merge function makes later rehydration fail;
- an undefined partialize function lets in-memory state change and then throws before saving it;
- the public options can say no storage is configured while a private reference continues using the old storage;
- the default persistence version can silently disappear from saved JSON.

The proposed repair is deliberately selective.

It preserves required/defaulted values when they are replaced with `undefined`:

- name;
- storage;
- partialize;
- version;
- merge.

It does **not** ignore every undefined value. Optional callbacks can still be intentionally removed.

# Is this a security disaster?

No evidence currently says these Zustand findings are remote security vulnerabilities.

They are reliability and correctness defects.

That still matters. Libraries like Zustand sit beneath application login flows, saved work, preferences, carts, offline state, and startup logic. A small disagreement in a foundational library can become a confusing failure in thousands of applications.

The honest claim is:

- the released source behavior has been reproduced at the relevant control-flow boundaries;
- focused repairs and regression tests exist in owned forks;
- broader repository CI must still finish before calling those repairs fully validated;
- no public upstream project has been contacted without authorization.

# Why use forks and draft pull requests?

A fork is a safe copy of someone else's public project under our control.

It lets us:

- change code without touching the original project;
- write tests around a suspected defect;
- run continuous-integration checks;
- review the complete diff;
- throw away a bad idea without bothering upstream maintainers.

A draft pull request is a visible workbench, not a claim that the work is ready to merge.

# What success looks like

A good Fieldwork result is not “we found lots of scary things.”

It is one of these:

- the suspected bug was real, narrowly reproduced, and has a tested repair;
- the suspicious behavior was intentional and is now clearly documented;
- the first repair was wrong, and review caught why;
- the evidence was too weak, so the claim was dropped;
- a broader problem was reduced to one small, actionable question.

The point is to make software's reported state match reality—and to be precise about what we actually proved.