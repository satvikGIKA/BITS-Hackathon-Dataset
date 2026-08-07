"""Tests for grade extraction."""

from bidintel.parse_common import extract_grade


def test_graded_satisfactory_long_form():
    text = "The overall quality of the completed work is graded Satisfactory. Workmanship was acceptable."
    assert extract_grade(text) == "Satisfactory"


def test_short_cc_satisfactory_completion_is_grade():
    text = (
        "The agency attended to all observations raised during execution and the work was taken over on "
        "satisfactory completion of the final inspection."
    )
    assert extract_grade(text) == "Satisfactory"


def test_found_satisfactory_during_is_not_grade():
    text = (
        "contract conditions. The quality of work has been found satisfactory during the final inspection "
        "carried out by the undersigned."
    )
    assert extract_grade(text) is None


def test_assessed_excellent():
    text = "the client's representative assessed the completed work as Excellent. We, National Infrastructure Corp."
    assert extract_grade(text) == "Excellent"
