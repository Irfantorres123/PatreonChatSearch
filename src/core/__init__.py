"""Core functionality module."""

from .search import MessageSearcher, SearchResult, search_channels_interactive
from .pagination import ChannelPaginator, MultiChannelPaginator, PaginationState
from .interactive_cli import InteractiveCLI, start_interactive_cli
from .renderers import DisplayConfig
from .view_context import ViewContext, ViewMode
from .navigation import NavigationController
from .command_parser import CommandParser
from .logger import get_logger

__all__ = [
    'MessageSearcher',
    'SearchResult',
    'search_channels_interactive',
    'ChannelPaginator',
    'MultiChannelPaginator',
    'PaginationState',
    'InteractiveCLI',
    'start_interactive_cli',
    'DisplayConfig',
    'ViewContext',
    'ViewMode',
    'NavigationController',
    'CommandParser',
    'get_logger'
]
