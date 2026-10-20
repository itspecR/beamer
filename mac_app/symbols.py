import AppKit

SYMBOL_FACTORY = "imageWithSystemSymbolName_accessibilityDescription_"


def available():
    return hasattr(AppKit.NSImage, SYMBOL_FACTORY)


def image(name, description=None):
    if not available():
        return None
    return getattr(AppKit.NSImage, SYMBOL_FACTORY)(name, description)


def configuration(point_size, weight):
    if not available():
        return None
    return AppKit.NSImageSymbolConfiguration.configurationWithPointSize_weight_(point_size, weight)
