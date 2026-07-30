use std::panic::{catch_unwind, AssertUnwindSafe};

use bevy_ecs::{
    error::{BevyError, ErrorContext, FallbackErrorHandler, Severity},
    prelude::*,
    schedule::{MultiThreadedExecutor, Schedule, SingleThreadedExecutor},
};

#[derive(Resource, Default, Debug)]
struct Applied(Vec<&'static str>);

#[derive(Clone, Copy, Debug)]
enum ExecutorKind {
    Single,
    Multi,
}

#[derive(Clone, Copy, Debug)]
enum Case {
    Success,
    IgnoredError,
    PanicSeverityError,
    HandledPanic,
    DefaultPanic,
}

#[derive(Debug, PartialEq, Eq)]
struct Receipt {
    panicked: bool,
    applied: Vec<&'static str>,
}

fn ignore_error(_: BevyError, _: ErrorContext) {}

fn queue_marker(commands: &mut Commands, marker: &'static str) {
    commands.queue(move |world: &mut World| {
        world.resource_mut::<Applied>().0.push(marker);
    });
}

fn success(mut commands: Commands) {
    queue_marker(&mut commands, "success");
}

fn ignored_error(mut commands: Commands) -> Result<(), BevyError> {
    queue_marker(&mut commands, "ignored_error");
    Err(BevyError::ignore("ignored system error"))
}

fn panic_severity_error(mut commands: Commands) -> Result<(), BevyError> {
    queue_marker(&mut commands, "panic_severity_error");
    Err(BevyError::new(
        Severity::Panic,
        "panic-severity system error",
    ))
}

fn panic_after_queue(mut commands: Commands) {
    queue_marker(&mut commands, "panic_after_queue");
    panic!("system panic after queuing a command");
}

fn run_case(executor: ExecutorKind, case: Case) -> Receipt {
    let mut world = World::new();
    world.init_resource::<Applied>();

    match case {
        Case::HandledPanic => {
            world.insert_resource(FallbackErrorHandler(ignore_error));
        }
        _ => {
            world.init_resource::<FallbackErrorHandler>();
        }
    }

    let mut schedule = Schedule::default();
    match executor {
        ExecutorKind::Single => {
            schedule.set_executor(SingleThreadedExecutor::new());
        }
        ExecutorKind::Multi => {
            schedule.set_executor(MultiThreadedExecutor::new());
        }
    }

    match case {
        Case::Success => {
            schedule.add_systems(success);
        }
        Case::IgnoredError => {
            schedule.add_systems(ignored_error);
        }
        Case::PanicSeverityError => {
            schedule.add_systems(panic_severity_error);
        }
        Case::HandledPanic | Case::DefaultPanic => {
            schedule.add_systems(panic_after_queue);
        }
    }

    let panicked = catch_unwind(AssertUnwindSafe(|| schedule.run(&mut world))).is_err();
    let applied = world.resource::<Applied>().0.clone();
    Receipt { panicked, applied }
}

fn assert_development_source_prediction() {
    for executor in [ExecutorKind::Single, ExecutorKind::Multi] {
        assert_eq!(
            run_case(executor, Case::Success),
            Receipt {
                panicked: false,
                applied: vec!["success"],
            }
        );
        assert_eq!(
            run_case(executor, Case::IgnoredError),
            Receipt {
                panicked: false,
                applied: vec!["ignored_error"],
            }
        );
        assert_eq!(
            run_case(executor, Case::HandledPanic),
            Receipt {
                panicked: false,
                applied: vec!["panic_after_queue"],
            }
        );
    }

    assert_eq!(
        run_case(ExecutorKind::Single, Case::PanicSeverityError),
        Receipt {
            panicked: true,
            applied: vec![],
        }
    );
    assert_eq!(
        run_case(ExecutorKind::Multi, Case::PanicSeverityError),
        Receipt {
            panicked: true,
            applied: vec!["panic_severity_error"],
        }
    );
    assert_eq!(
        run_case(ExecutorKind::Single, Case::DefaultPanic),
        Receipt {
            panicked: true,
            applied: vec![],
        }
    );
    assert_eq!(
        run_case(ExecutorKind::Multi, Case::DefaultPanic),
        Receipt {
            panicked: true,
            applied: vec!["panic_after_queue"],
        }
    );
}

fn main() {
    for executor in [ExecutorKind::Single, ExecutorKind::Multi] {
        for case in [
            Case::Success,
            Case::IgnoredError,
            Case::PanicSeverityError,
            Case::HandledPanic,
            Case::DefaultPanic,
        ] {
            println!("{executor:?} {case:?}: {:?}", run_case(executor, case));
        }
    }

    assert_development_source_prediction();
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn deferred_visibility_matches_the_source_predicted_matrix() {
        assert_development_source_prediction();
    }
}
