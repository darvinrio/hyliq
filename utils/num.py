def format_number(value):
    """Format numbers into human-readable format with K, M, B abbreviations."""
    if abs(value) >= 1e9:
        return f"{value / 1e9:.1f}B"
    elif abs(value) >= 1e6:
        return f"{value / 1e6:.1f}M"
    elif abs(value) >= 1e3:
        return f"{value / 1e3:.1f}K"
    else:
        return f"{value:.0f}"
