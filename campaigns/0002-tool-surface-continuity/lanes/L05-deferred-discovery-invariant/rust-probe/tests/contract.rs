use deferred_discovery_contract::{
    evaluate, normalize_unloadable_deferred, repair_actions, Exposure, RepairAction, Runtime,
    Surface, TransportDelivery,
};

fn deferred_mcp() -> Runtime {
    Runtime::new("mcp__sample__health_check", Exposure::Deferred, true)
}

#[test]
fn direct_mode_tool_search_keeps_deferred_mcp_reachable() {
    let surface = Surface::direct_mode(TransportDelivery::Direct);
    let result = evaluate(&[deferred_mcp()], &surface);

    assert!(result.accepted, "unexpected errors: {:?}", result.errors);
    assert!(result.warnings.is_empty());
}

#[test]
fn code_mode_all_tools_is_valid_without_nested_tool_search() {
    let surface = Surface::code_mode(TransportDelivery::Direct);
    let result = evaluate(&[deferred_mcp()], &surface);

    assert!(result.accepted, "unexpected errors: {:?}", result.errors);
}

#[test]
fn code_mode_missing_all_tools_rejects_deferred_runtime() {
    let mut surface = Surface::code_mode(TransportDelivery::Direct);
    surface.code_mode_all_tools_available = false;

    let result = evaluate(&[deferred_mcp()], &surface);

    assert!(!result.accepted);
    assert!(result.errors.iter().any(|error| error.contains("ALL_TOOLS")));
    assert_eq!(
        repair_actions(&[deferred_mcp()], &surface),
        vec![RepairAction::PromoteToDirect("mcp__sample__health_check")]
    );
}

#[test]
fn responses_lite_additional_tools_counts_as_direct_delivery() {
    let surface = Surface::direct_mode(TransportDelivery::Direct);
    let result = evaluate(&[deferred_mcp()], &surface);

    assert!(result.accepted, "unexpected errors: {:?}", result.errors);
}

#[test]
fn websocket_incremental_reuse_requires_matching_manifest_receipt() {
    let mut surface = Surface::direct_mode(TransportDelivery::OmittedUnverified);
    let runtimes = [deferred_mcp()];

    let omitted = evaluate(&runtimes, &surface);
    assert!(!omitted.accepted);
    assert!(repair_actions(&runtimes, &surface).contains(&RepairAction::SendFullManifest));

    surface.delivery = TransportDelivery::InheritedVerified;
    let mismatched = evaluate(&runtimes, &surface);
    assert!(!mismatched.accepted);

    surface.inherited_manifest_matches = true;
    let verified = evaluate(&runtimes, &surface);
    assert!(verified.accepted, "unexpected errors: {:?}", verified.errors);
}

#[test]
fn deferred_runtime_without_search_metadata_is_promoted_only_as_needed() {
    let surface = Surface::direct_mode(TransportDelivery::Direct);
    let runtimes = [
        Runtime::new("extension__opaque", Exposure::Deferred, false),
        deferred_mcp(),
    ];

    let normalized = normalize_unloadable_deferred(&runtimes, &surface);

    assert_eq!(normalized[0].exposure, Exposure::Direct);
    assert_eq!(normalized[1].exposure, Exposure::Deferred);
    assert!(evaluate(&normalized, &surface).accepted);
}

#[test]
fn search_disabled_promotes_deferred_runtime_without_disabling_direct_tools() {
    let mut surface = Surface::direct_mode(TransportDelivery::Direct);
    surface.search_enabled = false;
    surface.top_level_tool_search_advertised = false;
    surface.top_level_tool_search_registered = false;

    let runtimes = [
        deferred_mcp(),
        Runtime::new("exec_command", Exposure::Direct, false),
    ];
    let normalized = normalize_unloadable_deferred(&runtimes, &surface);

    assert_eq!(normalized[0].exposure, Exposure::Direct);
    assert_eq!(normalized[1].exposure, Exposure::Direct);
    assert!(evaluate(&normalized, &surface).accepted);
}

#[test]
fn stale_catalogue_is_separate_from_route_existence() {
    let mut surface = Surface::direct_mode(TransportDelivery::Direct);
    surface.catalogue_current = false;

    let result = evaluate(&[deferred_mcp()], &surface);

    assert!(result.accepted);
    assert_eq!(result.warnings.len(), 1);
    assert_eq!(
        repair_actions(&[deferred_mcp()], &surface),
        vec![RepairAction::RebuildCatalogue]
    );
}
