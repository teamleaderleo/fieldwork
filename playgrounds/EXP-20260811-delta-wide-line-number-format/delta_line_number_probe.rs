// Appended to exact dandavison/delta src/features/line_numbers.rs by Fieldwork CI.

#[cfg(test)]
mod fieldwork_wide_line_number_format_probe {
    use super::*;
    use crate::features::side_by_side::{available_line_width, ansifill::UseFullPanelWidth};
    use crate::minusplus::MinusPlus;
    use crate::tests::integration_test_utils::make_config_from_args;
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
}
