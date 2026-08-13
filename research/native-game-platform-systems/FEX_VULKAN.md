# FEX and Vulkan ecosystem scouting surfaces

These projects extend the native game/platform scouting inventory with two especially useful clusters.

## Cross-architecture execution and game compatibility

- `FEX-Emu/FEX` — x86/x86-64 execution on ARM64 Linux. High-value seams include dynamic binary translation, JIT/code-cache lifetime, x86 memory-ordering emulation, signals, syscall and ABI translation, host-library forwarding, OpenGL/Vulkan thunking, and Wine/Proton game compatibility.
- `FEX-Emu/RootFS` — supporting x86 root filesystem/runtime surface for FEX; useful when a compatibility question crosses guest userspace, loader, library, packaging, or runtime boundaries.

Useful scout questions include cross-architecture syscall ABI differences, TSO/memory-model compatibility, code invalidation, signal delivery, thunk equivalence, game-specific performance regressions, and host/guest resource ownership.

## Khronos Vulkan ecosystem

- `KhronosGroup/Vulkan-Tools` — VulkanInfo, vkcube/vkcube++, Mock ICD, and SDK-facing utilities. Interesting seams include device/property enumeration, WSI, extension plumbing, platform behavior, and mock-driver correctness.
- `KhronosGroup/Vulkan-ValidationLayers` — synchronization validation, GPU-assisted validation, object/state tracking, VUID coverage, extension semantics, and instrumentation.
- `KhronosGroup/Vulkan-Loader` — ICD/layer discovery, dispatch, loader configuration, multi-driver behavior, environment handling, and platform integration.
- `KhronosGroup/Vulkan-Headers` — generated/public Vulkan API declarations and registry-derived interface surfaces; useful when specification evolution meets consumers.
- `KhronosGroup/Vulkan-Docs` — Vulkan specification and registry sources; useful for tracing API contracts, extension semantics, and implementation/test mismatches.
- `KhronosGroup/SPIRV-Tools` — SPIR-V validation, optimization, transformation, parsing, and binary tooling.
- `KhronosGroup/glslang` — GLSL/HLSL front-end and SPIR-V generation.

Useful cross-project questions include specification/loader/validation/tool equivalence, extension rollout mismatches, WSI differences, state-validation gaps, shader contract drift, mock-ICD fidelity, and platform-specific loader behavior.

Treat these as scouting surfaces. Promote a project only after exact-source reading and a bounded reproducible question identify a concrete owner and consequence.
