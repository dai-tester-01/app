"""Tests for the use-cases preset module."""

from model_comparator.use_cases import (
    CATEGORY_LABELS,
    USE_CASES,
    get_use_cases_by_category,
)


def test_all_use_cases_have_required_fields() -> None:
    for uc in USE_CASES:
        assert uc.id, f"UseCase missing id: {uc}"
        assert uc.category, f"UseCase missing category: {uc}"
        assert uc.title, f"UseCase missing title: {uc}"
        assert uc.prompt, f"UseCase missing prompt: {uc}"


def test_all_categories_are_known() -> None:
    for uc in USE_CASES:
        assert uc.category in CATEGORY_LABELS, f"Unknown category: {uc.category!r}"


def test_ids_are_unique() -> None:
    ids = [uc.id for uc in USE_CASES]
    assert len(ids) == len(set(ids)), "Duplicate use-case IDs found"


def test_three_categories_present() -> None:
    categories = {uc.category for uc in USE_CASES}
    assert "software_engineering" in categories
    assert "finance" in categories
    assert "math" in categories


def test_each_category_has_at_least_two_use_cases() -> None:
    grouped = get_use_cases_by_category()
    for cat, items in grouped.items():
        assert len(items) >= 2, f"Category {cat!r} has fewer than 2 use-cases"


def test_get_use_cases_by_category_covers_all() -> None:
    grouped = get_use_cases_by_category()
    total = sum(len(v) for v in grouped.values())
    assert total == len(USE_CASES)


def test_get_use_cases_by_category_keys_match_labels() -> None:
    grouped = get_use_cases_by_category()
    assert set(grouped.keys()) == set(CATEGORY_LABELS.keys())
