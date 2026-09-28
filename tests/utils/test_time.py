"""Tests for the ISO-8601 time helpers."""

from datetime import UTC, datetime

from shift_scheduling.utils.time import format_time, parse_time


class TestParseTime:
    def test_parses_z_suffix_as_utc(self):
        assert parse_time("2026-09-15T22:00:00Z") == datetime(
            2026, 9, 15, 22, tzinfo=UTC
        )

    def test_converts_offset_to_utc(self):
        parsed = parse_time("2026-09-15T18:00:00-04:00")
        assert parsed == datetime(2026, 9, 15, 22, tzinfo=UTC)
        assert parsed.tzinfo == UTC

    def test_treats_naive_timestamp_as_utc(self):
        assert parse_time("2026-09-15T22:00:00") == datetime(
            2026, 9, 15, 22, tzinfo=UTC
        )


class TestFormatTime:
    def test_formats_with_z_suffix(self):
        assert (
            format_time(datetime(2026, 9, 15, 22, tzinfo=UTC)) == "2026-09-15T22:00:00Z"
        )

    def test_round_trips_with_parse_time(self):
        value = "2026-09-16T06:00:00Z"
        assert format_time(parse_time(value)) == value
