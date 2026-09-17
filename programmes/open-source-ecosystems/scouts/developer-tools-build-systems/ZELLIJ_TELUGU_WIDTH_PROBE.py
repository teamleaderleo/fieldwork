#!/usr/bin/env python3
"""Model the exact Telugu fixture against two width policies.

This probe is intentionally dependency-free. It transcribes only the
unicode-width 0.2.2 rules needed by the code points in the reporter's fixture
and the width loop in Zellij draft PR #4800 head
d5c04daccfac765814e55ef2b89543bbe711629d.

It is a mechanism probe, not a terminal emulator.
"""

FIXTURE = "వసంత ఋతువు గురించి ఒక కంద పద్యం వ్రాయి"
RESIDUAL = "ఒక పద్యం వ్రాయి"

# UAX #29 EGC segmentation for the exact issue fixture.
FIXTURE_CLUSTERS = (
    "వ", "సం", "త", " ", "ఋ", "తు", "వు", " ",
    "గు", "రిం", "చి", " ", "ఒ", "క", " ", "కం", "ద", " ",
    "ప", "ద్యం", " ", "వ్రా", "యి",
)
RESIDUAL_CLUSTERS = ("ఒ", "క", " ", "ప", "ద్యం", " ", "వ్రా", "యి")

# In unicode-width 0.2.2 these exact Telugu scalars have Grapheme_Extend
# and therefore char width 0. The other code points present in the fixture
# fall through to width 1.
GRAPHEME_EXTEND_IN_FIXTURE = {
    "\u0c3e",  # TELUGU VOWEL SIGN AA
    "\u0c3f",  # TELUGU VOWEL SIGN I
    "\u0c4d",  # TELUGU SIGN VIRAMA
}


def unicode_width_0_2_2_char(c: str) -> int:
    assert len(c) == 1
    return 0 if c in GRAPHEME_EXTEND_IN_FIXTURE else 1


def unicode_width_0_2_2_string(s: str) -> int:
    # No special unicode-width 0.2.2 ligature rule applies to this Telugu fixture,
    # so string width is the sum of char widths.
    return sum(unicode_width_0_2_2_char(c) for c in s)


def zellij_draft_grapheme_width(g: str) -> int:
    # Transcription of zellij-utils/src/grapheme_width.rs at the inspected draft.
    if not g:
        return 0

    base = g[0]
    width = unicode_width_0_2_2_char(base)
    prefix = base

    for c in g[1:]:
        prefix += c
        # The draft recomputes only for scalars whose char width is != 1.
        # Width-1 non-RI scalars are intentionally skipped.
        if unicode_width_0_2_2_char(c) != 1:
            width = unicode_width_0_2_2_string(prefix)

    return width


def run_case(name: str, text: str, clusters: tuple[str, ...]) -> tuple[int, int]:
    assert "".join(clusters) == text
    unicode_total = 0
    draft_total = 0

    print(name)
    print("cluster\tunicode-width-0.2.2\tdraft")
    for cluster in clusters:
        unicode_w = unicode_width_0_2_2_string(cluster)
        draft_w = zellij_draft_grapheme_width(cluster)
        unicode_total += unicode_w
        draft_total += draft_w
        if unicode_w != draft_w or len(cluster) > 1:
            cps = " ".join(f"U+{ord(c):04X}" for c in cluster)
            print(f"{cluster!r}\t{unicode_w}\t{draft_w}\t{cps}")

    print(f"TOTAL\t{unicode_total}\t{draft_total}")
    print(f"DELTA\t{unicode_total - draft_total}")
    print()
    return unicode_total, draft_total


def main() -> None:
    residual = run_case("residual", RESIDUAL, RESIDUAL_CLUSTERS)
    full = run_case("full-issue-fixture", FIXTURE, FIXTURE_CLUSTERS)

    assert residual == (11, 9), residual
    assert full == (32, 24), full
    assert unicode_width_0_2_2_string("ద్యం") == 3
    assert zellij_draft_grapheme_width("ద్యం") == 1
    assert unicode_width_0_2_2_string("వ్రా") == 2
    assert zellij_draft_grapheme_width("వ్రా") == 2

    print("RESULT residual=11/9 full=32/24 critical-cluster=ద్యం:3/1 control=వ్రా:2/2")


if __name__ == "__main__":
    main()
