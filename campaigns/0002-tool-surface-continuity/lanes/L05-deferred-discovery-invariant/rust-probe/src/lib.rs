//! Executable contract model for deferred Codex tool discovery.
//!
//! This crate does not copy Codex internals. It models the cross-layer
//! invariant that a deferred runtime must remain reachable through the
//! effective model-visible surface after transport serialization.

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ToolMode {
    Direct,
    CodeMode,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Exposure {
    Direct,
    DirectModelOnly,
    Deferred,
    Hidden,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum TransportDelivery {
    /// The complete effective surface is present in the generated request.
    Direct,
    /// The generated request omits the surface, but a receipt proves that the
    /// referenced response contains the identical manifest.
    InheritedVerified,
    /// The request relies on a previous response without a matching receipt.
    OmittedUnverified,
    /// No manifest is delivered or inherited.
    Absent,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Runtime {
    pub name: &'static str,
    pub exposure: Exposure,
    pub searchable_metadata: bool,
}

impl Runtime {
    pub const fn new(
        name: &'static str,
        exposure: Exposure,
        searchable_metadata: bool,
    ) -> Self {
        Self {
            name,
            exposure,
            searchable_metadata,
        }
    }
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Surface {
    pub mode: ToolMode,
    pub search_enabled: bool,
    pub top_level_tool_search_advertised: bool,
    pub top_level_tool_search_registered: bool,
    pub code_mode_exec_advertised: bool,
    pub code_mode_all_tools_available: bool,
    pub delivery: TransportDelivery,
    pub inherited_manifest_matches: bool,
    pub catalogue_current: bool,
}

impl Surface {
    pub const fn direct_mode(delivery: TransportDelivery) -> Self {
        Self {
            mode: ToolMode::Direct,
            search_enabled: true,
            top_level_tool_search_advertised: true,
            top_level_tool_search_registered: true,
            code_mode_exec_advertised: false,
            code_mode_all_tools_available: false,
            delivery,
            inherited_manifest_matches: false,
            catalogue_current: true,
        }
    }

    pub const fn code_mode(delivery: TransportDelivery) -> Self {
        Self {
            mode: ToolMode::CodeMode,
            search_enabled: true,
            top_level_tool_search_advertised: false,
            top_level_tool_search_registered: false,
            code_mode_exec_advertised: true,
            code_mode_all_tools_available: true,
            delivery,
            inherited_manifest_matches: false,
            catalogue_current: true,
        }
    }
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Evaluation {
    pub accepted: bool,
    pub errors: Vec<String>,
    pub warnings: Vec<String>,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum RepairAction {
    PromoteToDirect(&'static str),
    SendFullManifest,
    RebuildCatalogue,
}

pub fn evaluate(runtimes: &[Runtime], surface: &Surface) -> Evaluation {
    let mut errors = Vec::new();
    let mut warnings = Vec::new();

    let has_model_visible_runtime = runtimes
        .iter()
        .any(|runtime| runtime.exposure != Exposure::Hidden);

    if has_model_visible_runtime && !delivery_is_verified(surface) {
        errors.push("effective tool manifest is not directly delivered or verifiably inherited".into());
    }

    for runtime in runtimes {
        if runtime.exposure != Exposure::Deferred {
            continue;
        }

        if !runtime.searchable_metadata {
            errors.push(format!(
                "deferred runtime `{}` has no searchable metadata",
                runtime.name
            ));
            continue;
        }

        if !logical_discovery_route_available(surface) {
            let route = match surface.mode {
                ToolMode::Direct => "top-level client-executed tool_search",
                ToolMode::CodeMode => "code-mode exec plus ALL_TOOLS/global tools runtime",
            };
            errors.push(format!(
                "deferred runtime `{}` has no usable {route}",
                runtime.name
            ));
        }
    }

    if !surface.catalogue_current {
        warnings.push("discovery catalogue or binding generation is stale".into());
    }

    Evaluation {
        accepted: errors.is_empty(),
        errors,
        warnings,
    }
}

pub fn normalize_unloadable_deferred(
    runtimes: &[Runtime],
    surface: &Surface,
) -> Vec<Runtime> {
    let logical_route_available = logical_discovery_route_available(surface);
    runtimes
        .iter()
        .cloned()
        .map(|mut runtime| {
            if runtime.exposure == Exposure::Deferred
                && (!runtime.searchable_metadata || !logical_route_available)
            {
                runtime.exposure = Exposure::Direct;
            }
            runtime
        })
        .collect()
}

pub fn repair_actions(runtimes: &[Runtime], surface: &Surface) -> Vec<RepairAction> {
    let mut actions = Vec::new();
    let logical_route_available = logical_discovery_route_available(surface);

    for runtime in runtimes {
        if runtime.exposure == Exposure::Deferred
            && (!runtime.searchable_metadata || !logical_route_available)
        {
            actions.push(RepairAction::PromoteToDirect(runtime.name));
        }
    }

    if runtimes
        .iter()
        .any(|runtime| runtime.exposure != Exposure::Hidden)
        && !delivery_is_verified(surface)
    {
        actions.push(RepairAction::SendFullManifest);
    }

    if !surface.catalogue_current {
        actions.push(RepairAction::RebuildCatalogue);
    }

    actions
}

fn logical_discovery_route_available(surface: &Surface) -> bool {
    if !surface.search_enabled {
        return false;
    }

    match surface.mode {
        ToolMode::Direct => {
            surface.top_level_tool_search_advertised
                && surface.top_level_tool_search_registered
        }
        ToolMode::CodeMode => {
            surface.code_mode_exec_advertised && surface.code_mode_all_tools_available
        }
    }
}

fn delivery_is_verified(surface: &Surface) -> bool {
    match surface.delivery {
        TransportDelivery::Direct => true,
        TransportDelivery::InheritedVerified => surface.inherited_manifest_matches,
        TransportDelivery::OmittedUnverified | TransportDelivery::Absent => false,
    }
}
