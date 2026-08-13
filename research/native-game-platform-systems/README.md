# Native game and platform systems — scouting surfaces

## In simple words

This is a durable pick-list of technically rich open-source systems to inspect when we want a new native, game-adjacent, graphics, realtime, emulation, platform, or performance research direction.

The names here are starting points, not prestige targets and not automatic upstream-contact permission. A future scout should select a bounded question, inspect exact current source and tests, record negative results, and promote only the seams that survive evidence.

## Graphics API translation, drivers, and GPU tooling

- `doitsujin/dxvk` — Direct3D 8/9/10/11 to Vulkan translation; synchronization, descriptors, shaders, resource lifetime, driver compatibility, performance.
- `HansKristian-Work/vkd3d-proton` — Direct3D 12 to Vulkan for Proton; command queues, barriers, descriptors, shaders, ray tracing, frame-generation interactions.
- `baldurk/renderdoc` — graphics capture/replay and debugging across Vulkan, Direct3D, OpenGL, and related APIs.
- `mesa3d/mesa` — OpenGL/Vulkan drivers, shader compilers, winsys code, GPU memory, synchronization, device-specific paths.
- `KhronosGroup/SPIRV-Tools` — SPIR-V validation, optimization, transformation, parsing, and binary tooling.
- `KhronosGroup/glslang` — GLSL/HLSL front-end and SPIR-V generation.
- `google/shaderc` — shader compilation tooling around glslang/SPIR-V.
- `GPUOpen-Drivers/AMDVLK` and adjacent GPUOpen projects — Vulkan driver and GPU-facing implementation work.
- `google/filament` — realtime physically based renderer; frame graph, materials, Vulkan/Metal/OpenGL backends, mobile/desktop performance.
- `bkaradzic/bgfx` — cross-platform rendering abstraction and backend behavior.
- `haasn/libplacebo` — GPU-accelerated image/video rendering, color management, Vulkan, shaders, timing.

## Linux gaming, compositors, display, and compatibility

- `ValveSoftware/gamescope` — SteamOS compositor; Vulkan, Wayland, DRM/KMS, HDR, frame pacing, display ownership.
- `ValveSoftware/Proton` — compatibility integration across Wine, DXVK, vkd3d-proton and game-specific runtime behavior.
- `wine-mirror/wine` — Windows API compatibility; loaders, processes, graphics, input, synchronization, filesystem and application compatibility.
- `FEX-Emu/FEX` — x86/x86-64 execution on ARM64 Linux; dynamic binary translation, JIT/code-cache lifetime, x86 memory ordering, signals, syscall/ABI translation, OpenGL/Vulkan forwarding, and Wine/Proton compatibility.
- `libsdl-org/SDL` — cross-platform input, windowing, controller, audio, GPU and platform backends.
- `swaywm/wlroots` — Wayland compositor primitives, DRM/KMS, input, rendering, output lifecycle.
- `GNOME/mutter` — compositor/window manager internals, Wayland/X11, input, frame scheduling and display behavior.
- `KDE/kwin` — compositor/window manager internals, Wayland, DRM, effects, color and presentation behavior.
- `emersion/libliftoff` — DRM/KMS plane allocation and display composition decisions.
- `libinput/libinput` — low-level Linux input behavior, device quirks, gestures, event ownership.
- `flightlessmango/MangoHud` — Vulkan/OpenGL performance overlay and telemetry paths.
- `DadSchoorse/vkBasalt` — Vulkan post-processing layer and shader/effect injection.

## Emulation and compatibility research

- `RPCS3/rpcs3` — PlayStation 3 emulator; Cell/PPU/SPU work, recompilation, RSX graphics, timing, synchronization, kernel behavior.
- `dolphin-emu/dolphin` — GameCube/Wii emulator; JITs, GPU backends, timing, audio, input, networking.
- `xenia-project/xenia` — Xbox 360 emulator; PowerPC translation, GPU command processing, shaders, kernel and memory behavior.
- `PCSX2/pcsx2` — PlayStation 2 emulator; CPU/VU recompilation, GS rendering, timing and compatibility.
- `PPSSPP/ppsspp` — PSP emulator; CPU emulation/JIT, graphics translation, timing and portable platform behavior.
- `libretro/RetroArch` and core ecosystem — frontend/runtime boundaries, timing, input, audio/video synchronization, platform integration.
- `scummvm/scummvm` — long-lived multi-engine compatibility, audio/video/input and platform code.
- `OpenMW/openmw` — open-source engine/runtime for Morrowind data; rendering, physics, scripting and compatibility.

## Game engines, engine internals, and realtime systems

- `godotengine/godot` — renderer, physics, animation, resource management, threading, platform backends and editor/runtime boundaries.
- `bevyengine/bevy` — Rust game engine; ECS, renderer, scheduling, asset lifetime, platform integration.
- `o3de/o3de` — large open-source engine; renderer, tools, asset pipeline, multiplayer and platform layers.
- `urho3d/Urho3D` and active descendants — engine/runtime code, rendering, scene systems and tooling.
- `cocos/cocos-engine` — engine/runtime and platform integration, rendering and scripting boundaries.

## Physics, geometry, animation, and simulation

- `jrouwe/JoltPhysics` — modern C++ physics engine; collision detection, constraints, broadphase, SIMD, determinism and threading.
- `bulletphysics/bullet3` — mature collision/physics code and simulation tooling.
- `erincatto/box2d` — compact high-quality physics code; contacts, constraints, broadphase and numerical behavior.
- `NVIDIAGameWorks/PhysX` / current NVIDIA PhysX repository — production physics, collision, scene queries and solver behavior.
- `isl-org/Open3D` — geometry, visualization and GPU/CPU processing useful for adjacent realtime research.

## Networking, multiplayer, and streaming

- `ValveSoftware/GameNetworkingSockets` — realtime game transport, reliable/unreliable messaging, congestion behavior, P2P, NAT traversal and encryption.
- `lsalzman/enet` — compact reliable-UDP networking library with approachable protocol internals.
- `paullouisageneau/libdatachannel` — WebRTC/data-channel stack; ICE, SCTP, DTLS, media/data transport.
- `moonlight-stream/moonlight-qt` — game-streaming client; decoding, input, latency and platform integration.
- `LizardByte/Sunshine` — game-streaming host; capture, encoding, input and network latency paths.
- `obsproject/obs-studio` — realtime capture, GPU composition, encoding, audio/video synchronization, plugin and platform behavior.

## Audio, media, and frame pipelines

- `FFmpeg/FFmpeg` — codecs, demuxing, filters, hardware acceleration, synchronization and high-performance media pipelines.
- `PipeWire/pipewire` — Linux realtime audio/video graph, scheduling, buffers, device/session behavior.
- `OpenALSoft/openal-soft` — spatial audio, mixers, device backends and realtime audio behavior.
- `mackron/miniaudio` — compact audio engine/library with device, decoding, mixing and cross-platform code.
- `libsndfile/libsndfile` — mature audio file parsing and codec boundary behavior.

## Performance, profiling, debugging, and developer tooling

- `wolfpld/tracy` — low-overhead CPU/GPU profiler; event collection, sampling, unwinding, networking and viewer performance.
- `ocornut/imgui` — immediate-mode UI used heavily in game tooling; layout, docking, input, renderer backends and performance.
- `google/orbit` — native profiler and performance tooling.
- `google/sanitizers` and LLVM sanitizer code — runtime correctness, memory, race and undefined-behavior tooling.
- `llvm/llvm-project` — compiler, optimizer, debugger, sanitizers, JIT and code-generation work adjacent to engines and emulators.

## Platform, runtime, and systems code worth crossing into

- `systemd/systemd` — service/process/device/session lifecycle that gaming and desktop stacks depend on.
- `torvalds/linux` — DRM, input, scheduler, futex, io_uring, memory and device behavior when a user-space question reaches the kernel boundary.
- `util-linux/util-linux` — devices, namespaces, mounts, process and terminal utilities.
- `flatpak/flatpak` and `containers/bubblewrap` — sandboxing and desktop application runtime boundaries relevant to game launchers and distribution.
- `ostreedev/ostree` — immutable/update-oriented system deployment relevant to appliance-like gaming systems.

## How to use this list

A scout can pick one repository or one cross-project theme and answer:

1. What subsystem is technically rich and currently active?
2. Which code and tests own the behavior?
3. What failure, ambiguity, performance boundary, compatibility edge, or missing invariant is worth testing?
4. Can the question be reproduced locally or through existing native tests?
5. What evidence would make the candidate lose?
6. Does the result deserve a target hub, experiment, investigation, campaign, or only a retained research note?

Useful cross-project themes include:

- synchronization and resource lifetime;
- frame pacing and presentation;
- GPU memory and descriptor lifetime;
- shader translation and compiler correctness;
- JIT/recompiler correctness and performance;
- deterministic timing and emulation accuracy;
- input ownership and device hotplug;
- realtime audio/video synchronization;
- cancellation, shutdown and cleanup;
- network congestion, retransmission and latency;
- sandboxing, compatibility and filesystem behavior;
- driver/backend equivalence;
- observability overhead and profiler correctness.

This list should grow when a repository repeatedly appears in useful research. A name alone creates no obligation to investigate or contact upstream.
