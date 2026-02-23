from decimal import Decimal


def format_number_for_pdf(value: Decimal, decimals: int = 2) -> str:
    """
    Format a number with spaces as thousands separator for better readability in PDFs.

    Args:
        value: The number to format (Decimal or float)
        decimals: Number of decimal places (default: 2)

    Returns:
        Formatted string with spaces as thousands separators
        Example: 1234567.89 -> "1 234 567,89"
    """
    if value is None:
        return "0,00" if decimals == 2 else "0"

    num = float(value)
    formatted = f"{num:,.{decimals}f}"
    # Use space for thousands separator, comma for decimal separator (French style)
    formatted = formatted.replace(",", " ")
    formatted = formatted.replace(".", ",")

    return formatted
