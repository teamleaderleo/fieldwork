#!/usr/bin/env python3

"""Model Pi loader diagnostics crossing the Vercel harness boundary."""

import json


def load_factories(factories):
    extensions = []
    errors = []
    for index, factory in enumerate(factories):
        try:
            extensions.append(factory())
        except Exception as exc:
            errors.append({"path": f"<inline:{index}>", "error": str(exc)})
    return {"extensions": extensions, "errors": errors, "runtime": {}}


def pi_create_agent_session(extensions_result):
    # Pi builds from the successful subset and returns the diagnostic carrier.
    return {"session": {"extension_count": len(extensions_result["extensions"])}, "extensionsResult": extensions_result}


def current_vercel_handoff(agent_session_result):
    # Current harness destructures only { session }.
    return {"session": agent_session_result["session"]}


def main():
    success = load_factories([lambda: "loaded-extension"])
    failed = load_factories([lambda: (_ for _ in ()).throw(RuntimeError("inline extension failed"))])
    handed_off = current_vercel_handoff(pi_create_agent_session(failed))

    result = {
        "negative_control_success_has_no_errors": success["errors"] == [],
        "factory_error_recorded_by_loader": failed["errors"] == [
            {"path": "<inline:0>", "error": "inline extension failed"}
        ],
        "pi_can_build_from_successful_subset": pi_create_agent_session(failed)["session"]["extension_count"] == 0,
        "current_harness_handoff_contains_error": "extensionsResult" in handed_off,
        "current_harness_can_return_session_without_extension": handed_off["session"]["extension_count"] == 0,
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
