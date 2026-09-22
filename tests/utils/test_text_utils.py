from src.utils.text_utils import is_duration

  
def test_is_duration_month_year_range():
    assert is_duration("Jan 2023 - Dec 2024")