"""Validate references against the exact paper IDs in the input evidence."""
import re

ID = re.compile(r"[a-zA-Z0-9_.:/-]+")


def validate(text, known, *, require_inline=True):
    references = set(re.findall(r"(?<!!)\[([^\[\]\n]+)\](?!\()", text))
    unknown = {value for value in references - known if ID.fullmatch(value)}
    if unknown:
        raise ValueError("Unverified citation IDs: " + ", ".join(sorted(unknown)))
    found = references & known
    if require_inline and not found:
        raise ValueError("Report requires at least one exact [paper_id] citation")
    return sorted(found)
