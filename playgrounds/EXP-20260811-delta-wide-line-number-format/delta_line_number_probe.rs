// Appended to exact dandavison/delta src/features/line_numbers.rs by Fieldwork CI.

#[cfg(test)]
mod fieldwork_wide_line_number_format_probe {
    use super::*;
    use crate::features::side_by_side::{available_line_width, ansifill::UseFullPanelWidth};
    use crate::minusplus::MinusPlus;
    use crate::tests::integration_test_utils::{make_config_from_args, DeltaTest};
    use unicode_width::UnicodeWidthStr;

    fn data<'a>(formats: &'a MinusPlus<String>) -> LineNumbersData<'a> {
        let mut data = LineNumbersData::from_format_strings(formats, UseFullPanelWidth(false));
        data.initialize_hunk(&[(1, 1), (1, 1)], "file.rs".to_string());
        data
    }

    #[test]
    fn fieldwork_delta_wide_line_number_prefix_is_underbudgeted() {
        let formats = MinusPlus::new("界{nm}".to_string(), "|{np}".to_string());
        let data = data(&formats);
        let widths = data.formatted_width();

        assert_eq!(widths[Left], 2, "current metadata counts one grapheme plus one digit");
        assert_eq!("界1".width(), 3, "actual terminal width is two-column prefix plus one digit");
    }

    #[test]
    fn fieldwork_delta_ascii_line_number_prefix_is_budgeted_correctly() {
        let formats = MinusPlus::new("|{nm}".to_string(), "|{np}".to_string());
        let data = data(&formats);
        let widths = data.formatted_width();

        assert_eq!(widths[Left], 2);
        assert_eq!("|1".width(), 2);
    }

    #[test]
    fn fieldwork_delta_wide_prefix_gives_content_one_extra_panel_column() {
        let config = make_config_from_args(&[
            "--side-by-side",
            "--width",
            "20",
            "--line-fill-method=spaces",
            "--line-numbers-left-format",
            "界{nm}",
            "--line-numbers-right-format",
            "|{np}",
        ]);
        let mut data = LineNumbersData::from_format_strings(
            &config.line_numbers_format,
            UseFullPanelWidth::new(&config),
        );
        data.initialize_hunk(&[(1, 1), (1, 1)], "file.rs".to_string());

        let metadata_width = data.formatted_width()[Left];
        let planned_content_width = available_line_width(&config, &data)[Left];
        let actual_prefix_width = "界1".width();
        let actual_content_width = config.side_by_side_data[Left]
            .width
            .saturating_sub(actual_prefix_width);

        assert_eq!(config.side_by_side_data[Left].width, 10);
        assert_eq!(metadata_width, 2);
        assert_eq!(actual_prefix_width, 3);
        assert_eq!(planned_content_width, 8);
        assert_eq!(actual_content_width, 7);
        assert_eq!(planned_content_width, actual_content_width + 1);
    }

    const FIELDWORK_BOUNDARY_DIFF: &str = "\
diff --git a/a.txt b/a.txt
--- a/a.txt
+++ b/a.txt
@@ -1 +1 @@
-abcdefgh
+zzzzzzzz
";

    fn rendered_output(left_format: &'static str) -> String {
        DeltaTest::with_args(&[
            "--side-by-side",
            "--width",
            "20",
            "--line-fill-method=spaces",
            "--wrap-max-lines",
            "2",
            "--line-numbers-left-format",
            left_format,
            "--line-numbers-right-format",
            "|{np}",
        ])
        .set_config(|cfg| cfg.truncation_symbol = ">".into())
        .with_input(FIELDWORK_BOUNDARY_DIFF)
        .output
    }

    #[test]
    fn fieldwork_delta_wide_prefix_changes_rendered_boundary_output() {
        let ascii = rendered_output("|{nm}");
        let wide = rendered_output("界{nm}");

        assert!(
            ascii.contains("abcdefgh"),
            "the one-column prefix control should preserve the eight-column boundary text: {ascii:?}"
        );
        assert!(
            !wide.contains("abcdefgh"),
            "the wide prefix should expose the one-column over-budget in final output: {wide:?}"
        );
        assert!(
            wide.contains('界'),
            "the configured wide prefix must reach rendered output: {wide:?}"
        );
    }
}
