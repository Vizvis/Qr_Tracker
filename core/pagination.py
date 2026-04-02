"""Shared pagination helpers and limits."""

DEFAULT_PAGE_SIZE = 10
MAX_PAGE_SIZE = 10


def normalize_page_size(page_size: int) -> int:
    """Clamp page size to the allowed maximum."""
    if page_size < 1:
        return 1
    return min(page_size, MAX_PAGE_SIZE)


def build_pagination(page: int, page_size: int, total: int) -> dict:
    """Build a standard pagination payload."""
    normalized_page_size = normalize_page_size(page_size)
    total_pages = (total + normalized_page_size - 1) // normalized_page_size if total else 0
    return {
        "page": page,
        "page_size": normalized_page_size,
        "total": total,
        "total_pages": total_pages,
    }