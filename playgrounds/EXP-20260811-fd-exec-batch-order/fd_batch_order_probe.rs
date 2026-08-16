// Appended to exact sharkdp/fd src/exec/mod.rs by Fieldwork CI.

#[cfg(all(test, unix))]
mod fieldwork_exec_batch_order_probe {
    use super::{CommandBuilder, CommandTemplate, ExecutionMode};
    use std::fs;
    use std::iter;
    use std::path::{Path, PathBuf};
    use tempfile::tempdir;

    fn command_builder(marker: &str, log: &Path) -> CommandBuilder {
        let script = format!("printf '{marker}\\n' >> '{}'", log.display());
        let template = CommandTemplate::new(
            vec![
                "/bin/sh".to_string(),
                "-c".to_string(),
                script,
                "_".to_string(),
                "{}".to_string(),
            ],
            ExecutionMode::Batch,
        )
        .expect("batch template");
        CommandBuilder::new(&template, 0).expect("command builder")
    }

    fn log_lines(log: &Path) -> Vec<String> {
        match fs::read_to_string(log) {
            Ok(text) => text.lines().map(str::to_owned).collect(),
            Err(err) if err.kind() == std::io::ErrorKind::NotFound => Vec::new(),
            Err(err) => panic!("read log: {err}"),
        }
    }

    #[test]
    fn fieldwork_fd_equal_capacity_batch_builders_finish_in_declaration_order() {
        let temp = tempdir().expect("tempdir");
        let log = temp.path().join("order.log");
        let mut first = command_builder("1", &log);
        let mut second = command_builder("2", &log);

        let path1 = PathBuf::from("first-path");
        let path2 = PathBuf::from("second-path");

        first.push(&path1, None).expect("first path into command 1");
        second.push(&path1, None).expect("first path into command 2");
        first.push(&path2, None).expect("second path into command 1");
        second.push(&path2, None).expect("second path into command 2");

        assert_eq!(log_lines(&log), Vec::<String>::new(), "neither builder should flush yet");

        first.finish().expect("finish command 1");
        second.finish().expect("finish command 2");

        assert_eq!(log_lines(&log), vec!["1", "2"]);
    }

    #[test]
    fn fieldwork_fd_later_builder_can_flush_before_earlier_builder_on_argv_pressure() {
        let temp = tempdir().expect("tempdir");
        let log = temp.path().join("order.log");
        let mut first = command_builder("1", &log);
        let mut second = command_builder("2", &log);

        let path1 = PathBuf::from("first-path");
        let path2 = PathBuf::from("p".repeat(8192));

        first.push(&path1, None).expect("first path into command 1");
        second.push(&path1, None).expect("first path into command 2");

        let second_target_arg = second.path_arg.generate(&path2, None);
        let filler = "x".repeat(4096);
        let mut fillers_added = 0usize;

        // Reduce only command 2's remaining argv capacity. Every filler is checked
        // with argmax before insertion, so this adapts to the runner's actual limit.
        while second.cmd.args_would_fit(iter::once(&second_target_arg)) {
            assert!(
                second.cmd.args_would_fit(iter::once(&filler)),
                "ran out of argv room before creating a useful discriminator"
            );
            second.cmd.try_arg(filler.clone()).expect("append harmless filler");
            fillers_added += 1;
            assert!(fillers_added < 4096, "unexpectedly large argv capacity loop");
        }

        assert!(fillers_added > 0);
        assert!(
            first
                .cmd
                .args_would_fit(iter::once(first.path_arg.generate(&path2, None))),
            "command 1 should still accept the second path"
        );
        assert!(
            !second.cmd.args_would_fit(iter::once(&second_target_arg)),
            "command 2 must be the pressured builder"
        );

        // Declaration-order push into command 1 does not execute it.
        first.push(&path2, None).expect("second path into command 1");
        assert_eq!(log_lines(&log), Vec::<String>::new());

        // The later command now flushes its first batch immediately before accepting path 2.
        second.push(&path2, None).expect("pressured second builder push");
        assert_eq!(
            log_lines(&log),
            vec!["2"],
            "later declared command executed while command 1 remained buffered"
        );

        first.finish().expect("finish command 1");
        second.finish().expect("finish command 2 remainder");

        assert_eq!(
            log_lines(&log),
            vec!["2", "1", "2"],
            "early independent flush permanently crosses declaration order"
        );
    }
}
