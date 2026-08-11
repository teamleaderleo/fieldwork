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
    fn fieldwork_delta_valid_marker_wide_first_grapheme_finite_wrap_terminates() {
        let mut cfg = config("+");
        // Internal max_lines is the bounded-loop owner. A finite value should cut off
        // the zero-progress retry even though the first wide grapheme still cannot fit.
        cfg.wrap_config.max_lines = 2;
        let style = Style::default();
        let lines = wrap_line(&cfg, vec![(style, "界a")], 2, &style, &None);
        let plain: Vec<String> = lines
            .iter()
            .map(|sections| sections.iter().map(|(_, text)| *text).collect::<String>())
            .collect();
        assert_eq!(plain, vec!["+".to_string(), "界a".to_string()]);
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

    #[test]
    fn fieldwork_delta_valid_marker_wide_first_grapheme_unlimited_wrap_must_make_progress() {
        let cfg = config("+");
        let style = Style::default();
        // This keeps the documented one-column marker. With line width 2, only one
        // source column remains before the marker. The first source grapheme is width 2,
        // so the split loop can consume zero bytes and requeue the same text forever.
        let _ = wrap_line(&cfg, vec![(style, "界a")], 2, &style, &None);
    }
}
