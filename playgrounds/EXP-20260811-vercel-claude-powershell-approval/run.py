#!/usr/bin/env python3

"""Model the Claude bridge permission-kind split at Vercel AI SDK cfc587bd.

The host catalog classifies PowerShell as bash. The bridge permission table does
not contain PowerShell and falls back unknown native tools to edit. In
allow-edits mode, bash requires approval while edit is allowed.
"""

import json

HOST_TOOL_KINDS = {
    "Bash": "bash",
    "PowerShell": "bash",
}

BRIDGE_NATIVE_TOOL_KINDS = {
    "Bash": "bash",
    "Monitor": "bash",
    # PowerShell absent at the reviewed revision.
}


def bridge_kind(native_name: str) -> str:
    return BRIDGE_NATIVE_TOOL_KINDS.get(native_name, "edit")


def requires_approval(native_name: str, permission_mode: str) -> bool:
    if permission_mode == "allow-all":
        return False
    kind = bridge_kind(native_name)
    if permission_mode == "allow-edits":
        return kind == "bash"
    return kind in {"edit", "bash"}


def main() -> None:
    result = {
        "bash_host_kind": HOST_TOOL_KINDS["Bash"],
        "bash_bridge_kind": bridge_kind("Bash"),
        "bash_requires_approval_in_allow_edits": requires_approval(
            "Bash", "allow-edits"
        ),
        "powershell_host_kind": HOST_TOOL_KINDS["PowerShell"],
        "powershell_bridge_kind": bridge_kind("PowerShell"),
        "powershell_requires_approval_in_allow_edits": requires_approval(
            "PowerShell", "allow-edits"
        ),
        "classification_disagrees": (
            HOST_TOOL_KINDS["PowerShell"] != bridge_kind("PowerShell")
        ),
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
