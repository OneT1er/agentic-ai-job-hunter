import pytest
from src.utils import (
    contains_banned_terms,
    is_campus_query,
    normalize_url,
    safe_json_array_from_text,
)


class TestSafeJsonArrayFromText:
    def test_plain_array(self):
        result = safe_json_array_from_text('["AI工程师", "算法工程师"]')
        assert result == ["AI工程师", "算法工程师"]

    def test_with_think_tags(self):
        text = "<think>reasoning</think>\n['AI工程师']"
        result = safe_json_array_from_text(text)
        assert "AI工程师" in result

    def test_empty_strings_filtered(self):
        result = safe_json_array_from_text('["AI", "", "ML"]')
        assert result == ["AI", "ML"]

    def test_invalid_text_raises(self):
        with pytest.raises(ValueError):
            safe_json_array_from_text("no array here")


class TestIsCampusQuery:
    def test_campus_keywords(self):
        assert is_campus_query("AI工程师 校招")
        assert is_campus_query("2026届 算法工程师")
        assert is_campus_query("应届毕业生 AI")

    def test_non_campus(self):
        assert not is_campus_query("AI工程师")
        assert not is_campus_query("算法专家")


class TestNormalizeUrl:
    def test_absolute_url(self):
        assert normalize_url("https://example.com/job", "nowcoder") == "https://example.com/job"

    def test_relative_url(self):
        assert normalize_url("/job/123", "nowcoder") == "https://www.nowcoder.com/job/123"

    def test_empty_url(self):
        assert normalize_url("", "nowcoder") == ""


class TestContainsBannedTerms:
    def test_banned(self):
        assert contains_banned_terms("数据分析 实习")
        assert contains_banned_terms("销售经理")

    def test_allowed(self):
        assert not contains_banned_terms("AI工程师 校招")
        assert not contains_banned_terms("算法工程师 2026届")
