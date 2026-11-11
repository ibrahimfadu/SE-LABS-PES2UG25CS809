import pytest
from hypothesis import given, strategies as st

from processor import (
    clean_dish_name,
    parse_item_prices,
    split_amount
)


# ==========================================
# TEST 1: clean_dish_name()
# ==========================================

@given(
    st.text(min_size=1).filter(
        lambda s: bool(
            s.strip()
            .replace('*', '')
            .replace('#', '')
            .replace('~', '')
            .strip()
        )
    )
)
def test_clean_dish_name_removes_special_characters(name):
    result = clean_dish_name(name)

    expected = name.strip()

    for ch in ['*', '#', '~']:
        expected = expected.replace(ch, '')

    assert result == expected.title()


@given(st.one_of(
    st.none(),
    st.integers(),
    st.floats(),
    st.lists(st.integers())
))
def test_clean_dish_name_rejects_invalid_types(name):
    with pytest.raises(TypeError):
        clean_dish_name(name)


@given(st.sampled_from(["", " ", "*", "#", "~", "*#~"]))
def test_clean_dish_name_rejects_empty_names(name):
    with pytest.raises(ValueError):
        clean_dish_name(name)


# ==========================================
# TEST 2: parse_item_prices()
# ==========================================

@given(st.lists(
    st.integers(min_value=0, max_value=100000),
    min_size=1,
    max_size=20
))
def test_parse_item_prices_valid_inputs(prices):
    text = ",".join(map(str, prices))

    result = parse_item_prices(text)

    assert result == prices


@given(st.lists(
    st.integers(min_value=0, max_value=100000),
    min_size=1,
    max_size=10
))
def test_parse_item_prices_handles_whitespace(prices):
    text = ", ".join(map(str, prices))

    result = parse_item_prices(text)

    assert result == prices


@given(st.text().filter(lambda s: not s.strip().isdigit()))
def test_parse_item_prices_rejects_invalid_values(value):
    with pytest.raises(ValueError):
        parse_item_prices("100," + value)


@given(st.integers(max_value=-1))
def test_parse_item_prices_rejects_negative_prices(price):
    with pytest.raises(ValueError):
        parse_item_prices(str(price))


def test_parse_item_prices_rejects_empty_input():
    with pytest.raises(ValueError):
        parse_item_prices("")


def test_parse_item_prices_rejects_empty_elements():
    with pytest.raises(ValueError):
        parse_item_prices("100,,200")


def test_parse_item_prices_rejects_invalid_types():
    with pytest.raises(TypeError):
        parse_item_prices(None)


# ==========================================
# TEST 3: split_amount()
# ==========================================

@given(
    st.integers(min_value=0, max_value=1000000),
    st.integers(min_value=1, max_value=10000)
)
def test_split_amount_valid_inputs(total, people):
    text = f"{total}/{people}"

    result = split_amount(text)

    assert result == total // people


@given(st.integers(max_value=-1))
def test_split_amount_rejects_negative_total(total):
    with pytest.raises(ValueError):
        split_amount(f"{total}/4")


@given(st.integers(max_value=0))
def test_split_amount_rejects_zero_or_negative_people(people):
    with pytest.raises(ValueError):
        split_amount(f"1200/{people}")


@given(st.sampled_from([
    "",
    "1200",
    "/4",
    "1200/",
    "1200/4/2",
    "abc/4",
    "1200/abc"
]))
def test_split_amount_rejects_invalid_formats(text):
    with pytest.raises(ValueError):
        split_amount(text)


def test_split_amount_rejects_invalid_types():
    with pytest.raises(TypeError):
        split_amount(None)
