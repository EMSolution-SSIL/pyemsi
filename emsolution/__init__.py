import os

ICONS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "icons")


def icon(name):
    return os.path.join(ICONS, name + ".svg")
