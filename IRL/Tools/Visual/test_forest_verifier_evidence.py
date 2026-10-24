"""Host regression tests for fail-closed Unreal forest validation evidence."""
import importlib.util
import sys
import types
import unittest
from pathlib import Path

# The verifier's evidence helper is host-testable without pretending to run Unreal.
sys.modules.setdefault("unreal", types.SimpleNamespace())
SCRIPT = Path(__file__).with_name("verify_irl_forest_visual_level.py")
SPEC = importlib.util.spec_from_file_location("irl_forest_verifier", SCRIPT)
VERIFIER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFIER)


class Actor:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    def last_generated_instance_count(self):
        if self.error:
            raise self.error
        return self.value


class ForestVerifierEvidenceTests(unittest.TestCase):
    def test_positive_integer_count_is_accepted(self):
        errors = []
        self.assertEqual(VERIFIER._validated_instance_count(Actor(12), "biome", errors), 12)
        self.assertEqual(errors, [])

    def test_zero_count_fails(self):
        errors = []
        VERIFIER._validated_instance_count(Actor(0), "biome", errors)
        self.assertTrue(any("no decorative instances" in item for item in errors))

    def test_none_count_fails_closed(self):
        errors = []
        VERIFIER._validated_instance_count(Actor(None), "biome", errors)
        self.assertTrue(any("invalid generated instance count" in item for item in errors))

    def test_boolean_is_not_accepted_as_integer(self):
        errors = []
        VERIFIER._validated_instance_count(Actor(True), "biome", errors)
        self.assertTrue(any("invalid generated instance count" in item for item in errors))

    def test_unknown_count_type_is_serializable_and_rejected(self):
        errors = []
        result = VERIFIER._validated_instance_count(Actor(object()), "biome", errors)
        self.assertIsInstance(result, str)
        self.assertTrue(any("invalid generated instance count" in item for item in errors))

    def test_editor_api_exception_fails_closed(self):
        errors = []
        VERIFIER._validated_instance_count(
            Actor(error=RuntimeError("reflection unavailable")), "biome", errors
        )
        self.assertTrue(any("could not read generated instance count" in item for item in errors))


if __name__ == "__main__":
    unittest.main(verbosity=2)
