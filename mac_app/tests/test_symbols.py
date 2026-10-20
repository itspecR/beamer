"""SF Symbols arrived in macOS 11; on macOS 10.15 the sidebar goes without its icons."""

import importlib
import sys
import types
import unittest
from unittest.mock import Mock, patch


def _symbols_with(image_class, configuration_class=None):
    appkit = types.SimpleNamespace(NSImage=image_class, NSImageSymbolConfiguration=configuration_class)
    with patch.dict(sys.modules, {"AppKit": appkit}):
        sys.modules.pop("symbols", None)
        module = importlib.import_module("symbols")
    sys.modules.pop("symbols", None)
    return module


class WithoutSymbolsTests(unittest.TestCase):
    def setUp(self):
        self.symbols = _symbols_with(types.SimpleNamespace())

    def test_symbols_are_unavailable(self):
        self.assertFalse(self.symbols.available())

    def test_image_is_none(self):
        self.assertIsNone(self.symbols.image("keyboard", "Keyboard"))

    def test_configuration_is_none(self):
        self.assertIsNone(self.symbols.configuration(13, 0.0))


class WithSymbolsTests(unittest.TestCase):
    def setUp(self):
        self.image_class = Mock()
        self.configuration_class = Mock()
        self.symbols = _symbols_with(self.image_class, self.configuration_class)

    def test_symbols_are_available(self):
        self.assertTrue(self.symbols.available())

    def test_image_asks_appkit_for_the_named_symbol(self):
        result = self.symbols.image("keyboard", "Keyboard")
        self.image_class.imageWithSystemSymbolName_accessibilityDescription_.assert_called_once_with("keyboard", "Keyboard")
        self.assertIs(result, self.image_class.imageWithSystemSymbolName_accessibilityDescription_.return_value)

    def test_image_description_defaults_to_none(self):
        self.symbols.image("network")
        self.image_class.imageWithSystemSymbolName_accessibilityDescription_.assert_called_once_with("network", None)

    def test_configuration_uses_the_point_size_and_weight(self):
        self.symbols.configuration(13, 0.0)
        self.configuration_class.configurationWithPointSize_weight_.assert_called_once_with(13, 0.0)


if __name__ == "__main__":
    unittest.main()
