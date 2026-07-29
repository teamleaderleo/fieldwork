# Targets

Targets are external ecosystems worth understanding. The registry is intentionally broader than the set of active campaigns.

## Lifecycle

- `inbox` — plausible target, not assessed.
- `mapped` — basic project, policy, ownership, and contribution map exists.
- `active` — one or more current campaigns depend on the target.
- `watch` — potentially relevant, but policy, congestion, or direction should be reassessed before work.
- `paused` — no current value or capacity.
- `retired` — intentionally removed from consideration.

## Activation rule

A registry entry does not authorize research or contribution work. Activate a target only when a concrete question intersects something we care about.

Before activation, record:

- canonical repository and governance owner;
- contribution and AI-assistance policy;
- issue and review process;
- release cadence and supported branches;
- relevant subsystems;
- known review bottlenecks;
- local projects that create a genuine reason to investigate it.

## Directory rule

Use `targets/<slug>/map.md` for a durable target map. Keep low-cost possibilities only in `registry.yml` until deeper mapping is justified.
