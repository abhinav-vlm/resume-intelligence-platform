from src.utils.intervals import merge_intervals


def test_single_interval():
    intervals = [
        ((2021, 1), (2021, 6))
    ]

    assert merge_intervals(intervals) == [
        ((2021, 1), (2021, 6))
    ]

def test_separate_intervals():
    intervals = [
        ((2021, 1), (2021, 6)),
        ((2021, 9), (2022, 3))
    ]

    assert merge_intervals(intervals) == [
        ((2021, 1), (2021, 6)),
        ((2021, 9), (2022, 3))
    ]

def test_adjacent_intervals():
    intervals = [
        ((2021, 1), (2021, 6)),
        ((2021, 7), (2021, 12))
    ]

    assert merge_intervals(intervals) == [
        ((2021, 1), (2021, 12))
    ]

def test_partially_overlapping_intervals():
    intervals = [
        ((2021, 1), (2022, 8)),
        ((2022, 1), (2023, 3))
    ]

    assert merge_intervals(intervals) == [
        ((2021, 1), (2023, 3))
    ]

def test_interval_inside_previous():
    intervals = [
        ((2021, 1), (2024, 12)),
        ((2022, 1), (2023, 6))
    ]

    assert merge_intervals(intervals) == [
        ((2021, 1), (2024, 12))
    ]


def test_interval_inside_previous():
    intervals = [
        ((2021, 1), (2024, 12)),
        ((2022, 1), (2023, 6))
    ]

    assert merge_intervals(intervals) == [
        ((2021, 1), (2024, 12))
    ]

def test_december_to_january():
    intervals = [
        ((2021, 12), (2022, 1)),
        ((2022, 2), (2022, 6))
    ]

    assert merge_intervals(intervals) == [
        ((2021, 12), (2022, 6))
    ]

def test_empty_intervals():
    assert merge_intervals([]) == []

def test_multiple_chained_overlaps():
    intervals = [
        ((2021, 1), (2021, 6)),
        ((2021, 5), (2022, 3)),
        ((2022, 2), (2023, 1)),
        ((2023, 1), (2023, 8))
    ]

    assert merge_intervals(intervals) == [
        ((2021, 1), (2023, 8))
    ]
