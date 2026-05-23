import pytest


def parametrize(testdata: list[dict]):
    """Shorthand for data-driven parametrize with indirect ``data`` fixture."""
    return pytest.mark.parametrize(
        "data",
        testdata,
        ids=lambda d: d.get("description"),
        indirect=True,
    )
