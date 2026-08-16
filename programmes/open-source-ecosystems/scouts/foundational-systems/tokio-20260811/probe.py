#!/usr/bin/env python3
"""Small model for Tokio LengthDelimitedCodec field-width limits.

This models the max-frame arithmetic read from tokio-rs/tokio at
625954f365727668cb02d04172b34f1149637728. It is deliberately a model,
not target-native execution.
"""


def max_length_field_value(field_len: int) -> int:
    bits = 8 * field_len
    if bits >= 64:
        return (1 << 64) - 1
    return (1 << bits) - 1


def max_allowed_frame_len(field_len: int, adjustment: int, usize_bits: int = 64) -> int:
    max_u64 = (1 << 64) - 1
    max_usize = (1 << usize_bits) - 1
    value = max_length_field_value(field_len) + adjustment
    value = max(0, min(value, max_u64))
    return min(value, max_usize)


def main() -> None:
    cases = [(-1, 254), (0, 255), (1, 256)]
    for adjustment, expected in cases:
        observed = max_allowed_frame_len(1, adjustment)
        print(f"1-byte field, adjustment={adjustment:+d}: max payload={observed}")
        assert observed == expected

    # A two-byte field can encode at most 65535 before adjustment.
    assert max_allowed_frame_len(2, 0) == 65535
    assert max_allowed_frame_len(2, 5) == 65540

    print("model agrees with the source/test boundary")


if __name__ == "__main__":
    main()
