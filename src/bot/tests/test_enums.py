from bot.enums import Mode, Type


def test_mode() -> None:
    modes = {item.value for item in Mode}
    assert modes == {"100644", "100755", "040000", "160000", "120000"}


def test_type() -> None:
    for item in Type:
        assert item.name.lower() == item.value
        assert item.name == item.value.upper()
