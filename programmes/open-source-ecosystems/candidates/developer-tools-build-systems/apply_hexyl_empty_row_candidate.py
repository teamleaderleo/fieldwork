#!/usr/bin/env python3
from pathlib import Path

source = Path("src/lib.rs")
text = source.read_text(encoding="utf-8")

before = '''        if is_empty {
            self.base_digits = 2;
            self.print_header()?;
            if self.show_position_panel {
                write!(self.writer, "{0:9}", "│")?;
            }
            write!(
                self.writer,
                "{0:2}{1:2$}{0}{0:>3$}",
                "│",
                "No content",
                self.panel_sz() - 1,
                self.panel_sz() + 1,
            )?;
            if self.show_char_panel {
                write!(self.writer, "{0:>9}{0:>9}", "│")?;
            }
            writeln!(self.writer)?;
'''

after = '''        if is_empty {
            self.base_digits = 2;
            self.print_header()?;

            let outer_sep = self.border_style.outer_sep();
            let inner_sep = self.border_style.inner_sep();
            write!(self.writer, "{outer_sep}")?;

            if self.show_position_panel {
                write!(self.writer, "{:8}{outer_sep}", "")?;
            }

            for panel in 0..self.panels {
                let content = if panel == 0 { "No content" } else { "" };
                write!(
                    self.writer,
                    " {content:<width$}",
                    width = self.panel_sz() - 1,
                )?;
                let separator = if panel + 1 == self.panels {
                    outer_sep
                } else {
                    inner_sep
                };
                write!(self.writer, "{separator}")?;
            }

            if self.show_char_panel {
                for panel in 0..self.panels {
                    let separator = if panel + 1 == self.panels {
                        outer_sep
                    } else {
                        inner_sep
                    };
                    write!(self.writer, "{:8}{separator}", "")?;
                }
            }
            writeln!(self.writer)?;
'''

count = text.count(before)
if count != 1:
    raise SystemExit(f"expected one exact empty-row source block, found {count}")

source.write_text(text.replace(before, after, 1), encoding="utf-8")
print("FIELDWORK_RESULT hexyl-empty-row-transform=applied")
