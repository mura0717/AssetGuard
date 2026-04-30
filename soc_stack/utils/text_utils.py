"""General-purpose text utility functions."""

import re

def normalize_for_comparison(text: str) -> str:
    """Normalizes text for case-insensitive comparison by lowercasing and removing special chars."""
    if not isinstance(text, str):
        return ""
    text = text.lower().replace('"', ' inch')
    normalized = re.sub(r'[()/*-.]', ' ', text)
    normalized = re.sub(r'\s+', ' ', normalized).strip()
    return normalized

def normalize_for_display(name: str) -> str:
    """Normalizes a name for display or creation, preserving case but handling special chars."""
    if not isinstance(name, str):
        return ""
    name = name.replace('"', '-inch').replace('\"', 'inch')
    name = re.sub(r'[()"\/]', ' ', name)
    name = re.sub(r'\s+', ' ', name)
    return name.strip()

