"""
Navigation controller for pagination.
Handles all pagination logic in a single, testable class.
"""

from typing import List, Tuple, Optional, Any
from dataclasses import dataclass

from .view_context import ViewContext
from .search import SearchResult


@dataclass
class PaginationResult:
    """Result of a pagination operation."""
    items: List[Any]
    start_idx: int
    end_idx: int
    current_page: int
    total_pages: int
    total_items: int


class NavigationController:
    """
    Manages pagination for different view types.
    Follows Single Responsibility Principle by only handling navigation logic.
    """

    def __init__(self, items_per_page: int = 10):
        self.items_per_page = items_per_page
        self._first_view_of_messages: bool = True

    def set_items_per_page(self, count: int) -> None:
        """Set the number of items per page."""
        self.items_per_page = max(1, count)

    def paginate_messages(
        self,
        messages: List[Any],
        current_page: int,
        auto_jump_to_last: bool = False
    ) -> PaginationResult:
        """
        Paginate a list of messages.

        Args:
            messages: List of messages (oldest first)
            current_page: Current page number (1-indexed)
            auto_jump_to_last: Whether to jump to last page on first view

        Returns:
            PaginationResult with paginated data
        """
        total_items = len(messages)
        if total_items == 0:
            return PaginationResult(
                items=[],
                start_idx=0,
                end_idx=0,
                current_page=1,
                total_pages=0,
                total_items=0
            )

        total_pages = self._calculate_total_pages(total_items)

        # Auto-jump to last page (newest messages) on first view
        if auto_jump_to_last and current_page == 1:
            current_page = total_pages

        # Ensure page is in valid range
        current_page = max(1, min(current_page, total_pages))

        # Calculate indices
        start_idx = (current_page - 1) * self.items_per_page
        end_idx = min(start_idx + self.items_per_page, total_items)

        # Get items for current page
        page_items = messages[start_idx:end_idx]

        return PaginationResult(
            items=page_items,
            start_idx=start_idx,
            end_idx=end_idx,
            current_page=current_page,
            total_pages=total_pages,
            total_items=total_items
        )

    def paginate_search_results(
        self,
        results: List[SearchResult],
        current_page: int
    ) -> PaginationResult:
        """
        Paginate search results.

        Args:
            results: List of search results
            current_page: Current page number (1-indexed)

        Returns:
            PaginationResult with paginated data
        """
        total_items = len(results)
        if total_items == 0:
            return PaginationResult(
                items=[],
                start_idx=0,
                end_idx=0,
                current_page=1,
                total_pages=0,
                total_items=0
            )

        total_pages = self._calculate_total_pages(total_items)
        current_page = max(1, min(current_page, total_pages))

        start_idx = (current_page - 1) * self.items_per_page
        end_idx = min(start_idx + self.items_per_page, total_items)

        page_items = results[start_idx:end_idx]

        return PaginationResult(
            items=page_items,
            start_idx=start_idx,
            end_idx=end_idx,
            current_page=current_page,
            total_pages=total_pages,
            total_items=total_items
        )

    def next_page(self, context: ViewContext) -> Tuple[int, str]:
        """
        Navigate to next page.

        Args:
            context: Current view context

        Returns:
            Tuple of (new_page_number, message_or_empty_string)
        """
        if context.is_viewing_search():
            total_pages = self._calculate_total_pages(len(context.search_results))
            if context.current_page < total_pages:
                return context.current_page + 1, ""
            else:
                return context.current_page, "Already on the last page."

        elif context.is_viewing_messages():
            messages = context.get_current_messages()
            total_pages = self._calculate_total_pages(len(messages))
            if context.current_page < total_pages:
                return context.current_page + 1, ""
            else:
                return context.current_page, "Already on the last page."

        return context.current_page, "No search results to paginate."

    def prev_page(self, context: ViewContext) -> Tuple[int, str]:
        """
        Navigate to previous page.

        Args:
            context: Current view context

        Returns:
            Tuple of (new_page_number, message_or_empty_string)
        """
        if context.is_viewing_search():
            if context.current_page > 1:
                return context.current_page - 1, ""
            else:
                return context.current_page, "Already on the first page."

        elif context.is_viewing_messages():
            if context.current_page > 1:
                return context.current_page - 1, ""
            else:
                return context.current_page, "Already on the first page.\nUse 'fetch <limit>' to load more messages from the server."

        return context.current_page, "No search results to paginate."

    def goto_page(self, context: ViewContext, page_num: int) -> Tuple[int, str]:
        """
        Navigate to a specific page.

        Args:
            context: Current view context
            page_num: Target page number

        Returns:
            Tuple of (new_page_number, message_or_empty_string)
        """
        if context.is_viewing_search():
            total_pages = self._calculate_total_pages(len(context.search_results))
            if 1 <= page_num <= total_pages:
                return page_num, ""
            else:
                return context.current_page, f"Invalid page number. Must be between 1 and {total_pages}"

        elif context.is_viewing_messages():
            messages = context.get_current_messages()
            total_pages = self._calculate_total_pages(len(messages))
            if 1 <= page_num <= total_pages:
                return page_num, ""
            else:
                return context.current_page, f"Invalid page number. Must be between 1 and {total_pages}"

        return context.current_page, "No search results to paginate."

    def _calculate_total_pages(self, total_items: int) -> int:
        """Calculate total number of pages."""
        if total_items == 0:
            return 0
        return (total_items + self.items_per_page - 1) // self.items_per_page
