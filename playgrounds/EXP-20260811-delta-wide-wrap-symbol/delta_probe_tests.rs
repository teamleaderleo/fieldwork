// Appended to exact dandavison/delta src/wrapping.rs by the Fieldwork workflow.

#[cfg(test)]
mod fieldwork_wide_wrap_symbol_probe {
    use super::*;
    use crate::style::Style;
    use crate::tests::integration_test_utils::make_config_from_args;
    use unicode_width::UnicodeWidthStr;

    fn config(left: &'static str) -> Config {
        make_config_from_args(&[
            "--wrap-left-symbol",
            left,
            "--wrap-right-symbol",
            "<",
            "--wrap-right-prefix-symbol",
            ">",
            "--wrap-max-lines",
            "unlimited",
            "--wrap-right-percent",
            "37.0%",
        ])
    }

    #[test]
    fn fieldwork_delta_wide_marker_is_accepted_as_width_one_option() {
        let cfg = config("界");
        assert_eq!(cfg.wrap_config.left_symbol.graphemes(true).count(), 1);
        assert_eq!(cfg.wrap_config.left_symbol.width(), 2);
    }

    #[test]
    fn fieldwork_delta_one_column_marker_unlimited_wrap_terminates() {
        let cfg = config("+");
        let style = Style::default();
        let lines = wrap_line(&cfg, vec![(style, "abc")], 2, &style, &None);
        let plain: Vec<String> = lines
            .iter()
            .map(|sections| sections.iter().map(|(_, text)| *text).collect::<String>())
            .collect();
        assert_eq!(plain, vec!["a+".to_string(), "bc".to_string()]);
    }

    #[test]
    fn fieldwork_delta_two_column_marker_unlimited_wrap_must_make_progress() {
        let cfg = config("界");
        let style = Style::default();
        // Current source is expected to make zero text progress here: line width 2 minus
        // a 2-column marker leaves no room for the first grapheme, while unlimited mode
        // has no line-count stop. The CI watchdog classifies non-termination.
        let _ = wrap_line(&cfg, vec![(style, "abc")], 2, &style, &None);
    }
}
