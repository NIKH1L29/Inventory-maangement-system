"""
Parses plain-English inventory commands into structured actions.

This is regex-based, not AI - predictable and easy to demo in interviews.
Supports the exact format from the assignment brief plus a few extras.
"""

import re
from typing import Optional
from dataclasses import dataclass


@dataclass
class ParsedCommand:
    action: str
    item_name: Optional[str] = None
    quantity: Optional[int] = None
    location: Optional[str] = None
    from_location: Optional[str] = None
    to_location: Optional[str] = None


def _extract_item_name(text: str) -> Optional[str]:
    """
    Pull item name from quoted strings first, then fall back to 'of X to/from' patterns.
    """
    quoted = re.search(r'["\']([^"\']+)["\']', text)
    if quoted:
        return quoted.group(1).strip()

    # "50 units of Dell Laptop to warehouse A"
    of_match = re.search(r'\bof\s+(.+?)\s+(?:to|from|in)\s+warehouse', text, re.IGNORECASE)
    if of_match:
        return of_match.group(1).strip()

    return None


def _extract_quantity(text: str) -> Optional[int]:
    """First number in the string is treated as quantity."""
    match = re.search(r'\b(\d+)\b', text)
    return int(match.group(1)) if match else None


def _extract_warehouse(text: str, keyword: str = "to") -> Optional[str]:
    """
    Grabs warehouse name after 'to warehouse X' or 'from warehouse X'.
    """
    pattern = rf'{keyword}\s+warehouse\s+([a-zA-Z0-9\s\-]+?)(?:\.|$|\s+from|\s+to)'
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return match.group(1).strip()

    # Shorthand: "to warehouse A" at end of string
    end_pattern = rf'{keyword}\s+warehouse\s+([a-zA-Z0-9\s\-]+)\.?$'
    end_match = re.search(end_pattern, text, re.IGNORECASE)
    if end_match:
        return end_match.group(1).strip()

    return None


def parse_command(command: str) -> ParsedCommand:
    """
    Main entry point. Returns ParsedCommand or raises ValueError with a helpful hint.
    """
    text = command.strip()
    lower = text.lower()

    if not text:
        raise ValueError("Command cannot be empty.")

    # --- List / show inventory ---
    if re.search(r'\b(list|show|display|view)\b.*\binventory\b', lower):
        loc = _extract_warehouse(text, "in") or _extract_warehouse(text, "at")
        return ParsedCommand(action="list_inventory", location=loc)

    if re.search(r'\b(list|show)\b.*\bwarehouse', lower):
        return ParsedCommand(action="list_warehouses")

    # --- Transfer between warehouses ---
    if "transfer" in lower and "from warehouse" in lower and "to warehouse" in lower:
        qty = _extract_quantity(text)
        item = _extract_item_name(text)
        from_loc = _extract_warehouse(text, "from")
        to_loc = _extract_warehouse(text, "to")
        if not all([qty, item, from_loc, to_loc]):
            raise ValueError("Transfer needs: quantity, item name, from warehouse, to warehouse.")
        return ParsedCommand(
            action="transfer_item",
            item_name=item,
            quantity=qty,
            from_location=from_loc,
            to_location=to_loc,
        )

    # --- Remove / deduct stock ---
    if re.search(r'\b(remove|deduct|subtract|take out|pull)\b', lower):
        qty = _extract_quantity(text)
        item = _extract_item_name(text)
        loc = _extract_warehouse(text, "from") or _extract_warehouse(text, "in")
        if not qty or not item or not loc:
            raise ValueError('Try: Remove 10 units of "Item Name" from warehouse A.')
        return ParsedCommand(action="remove_item", item_name=item, quantity=qty, location=loc)

    # --- Add stock (default action) ---
    if re.search(r'\b(add|stock|insert|put)\b', lower):
        qty = _extract_quantity(text)
        item = _extract_item_name(text)
        loc = _extract_warehouse(text, "to") or _extract_warehouse(text, "in")
        if not qty or not item or not loc:
            raise ValueError('Try: Add 50 units of "Dell Laptop" to warehouse A.')
        return ParsedCommand(action="add_item", item_name=item, quantity=qty, location=loc)

    raise ValueError(
        "Could not understand command. Examples:\n"
        '- Add 50 units of "Dell Laptop" to warehouse A.\n'
        '- Remove 5 units of "Dell Laptop" from warehouse A.\n'
        '- List inventory in warehouse A.\n'
        '- Transfer 10 units of "Dell Laptop" from warehouse A to warehouse B.'
    )
