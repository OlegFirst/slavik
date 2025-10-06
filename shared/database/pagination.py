"""
Pagination Helpers for SQLAlchemy Async Queries

This module provides cursor-based and keyset pagination utilities
to efficiently paginate large datasets without the performance issues
of OFFSET-based pagination.

Cursor-based pagination benefits:
- Constant time complexity O(1) instead of O(n) for OFFSET
- Works correctly with real-time data changes
- Scales to millions of records

Usage:
    from shared.database.pagination import (
        paginate_cursor,
        paginate_keyset,
        CursorPage,
        KeysetPage
    )

    # Cursor-based pagination
    page = await paginate_cursor(
        session,
        select(User),
        cursor=request.cursor,
        limit=100
    )

    # Keyset pagination (multi-column ordering)
    page = await paginate_keyset(
        session,
        select(Plan).order_by(Plan.priority.desc(), Plan.created_at.desc()),
        keys={'priority': last_priority, 'created_at': last_created_at},
        limit=50
    )
"""

import logging
from typing import Generic, TypeVar, Optional, List, Dict, Any, Tuple
from dataclasses import dataclass
from sqlalchemy import select, Select, Column, asc, desc, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import ColumnElement
import base64
import json

logger = logging.getLogger(__name__)

T = TypeVar('T')


@dataclass
class CursorPage(Generic[T]):
    """
    Result of cursor-based pagination.

    Attributes:
        items: List of results for current page
        next_cursor: Cursor for next page (None if no more results)
        has_next: Whether there are more results
        count: Number of items in current page
    """
    items: List[T]
    next_cursor: Optional[str]
    has_next: bool
    count: int

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            "items": [item if isinstance(item, dict) else item for item in self.items],
            "next_cursor": self.next_cursor,
            "has_next": self.has_next,
            "count": self.count
        }


@dataclass
class KeysetPage(Generic[T]):
    """
    Result of keyset pagination.

    Attributes:
        items: List of results for current page
        next_keys: Key values for next page (None if no more results)
        has_next: Whether there are more results
        count: Number of items in current page
    """
    items: List[T]
    next_keys: Optional[Dict[str, Any]]
    has_next: bool
    count: int

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            "items": [item if isinstance(item, dict) else item for item in self.items],
            "next_keys": self.next_keys,
            "has_next": self.has_next,
            "count": self.count
        }


class CursorEncoder:
    """Encode/decode cursor values for pagination"""

    @staticmethod
    def encode(value: Any) -> str:
        """
        Encode a value into a cursor string.

        Args:
            value: Value to encode (usually an ID)

        Returns:
            Base64-encoded cursor string
        """
        if value is None:
            return ""

        # Convert to JSON string then base64
        json_str = json.dumps({"v": value})
        encoded = base64.urlsafe_b64encode(json_str.encode()).decode()
        return encoded

    @staticmethod
    def decode(cursor: str) -> Any:
        """
        Decode a cursor string to a value.

        Args:
            cursor: Base64-encoded cursor string

        Returns:
            Decoded value

        Raises:
            ValueError: If cursor is invalid
        """
        if not cursor:
            return None

        try:
            decoded = base64.urlsafe_b64decode(cursor.encode()).decode()
            data = json.loads(decoded)
            return data["v"]
        except Exception as e:
            raise ValueError(f"Invalid cursor: {e}")


async def paginate_cursor(
    session: AsyncSession,
    query: Select,
    cursor: Optional[str] = None,
    limit: int = 100,
    cursor_column: Optional[Column] = None,
    order_desc: bool = False
) -> CursorPage:
    """
    Paginate query using cursor-based pagination.

    Optimization: Uses WHERE id > cursor instead of OFFSET
    - OFFSET 10000: scans 10000 rows
    - WHERE id > cursor: uses index, constant time

    Args:
        session: SQLAlchemy async session
        query: Base query to paginate
        cursor: Cursor from previous page (None for first page)
        limit: Number of results per page
        cursor_column: Column to use for cursor (defaults to first primary key)
        order_desc: Whether to order descending

    Returns:
        CursorPage with results and next cursor

    Example:
        # First page
        page = await paginate_cursor(session, select(User), limit=50)

        # Next page
        page = await paginate_cursor(session, select(User), cursor=page.next_cursor, limit=50)
    """
    # Decode cursor to get last value
    cursor_value = None
    if cursor:
        try:
            cursor_value = CursorEncoder.decode(cursor)
        except ValueError as e:
            logger.warning(f"Invalid cursor: {e}")
            cursor_value = None

    # Add cursor filter if provided
    if cursor_value is not None and cursor_column is not None:
        if order_desc:
            query = query.where(cursor_column < cursor_value)
        else:
            query = query.where(cursor_column > cursor_value)

    # Add ordering if cursor column provided
    if cursor_column is not None:
        if order_desc:
            query = query.order_by(desc(cursor_column))
        else:
            query = query.order_by(asc(cursor_column))

    # Fetch limit + 1 to check if there are more results
    query = query.limit(limit + 1)

    # Execute query
    result = await session.execute(query)
    items = list(result.scalars().all())

    # Check if there are more results
    has_next = len(items) > limit
    if has_next:
        items = items[:limit]

    # Generate next cursor
    next_cursor = None
    if has_next and items and cursor_column is not None:
        last_item = items[-1]
        last_value = getattr(last_item, cursor_column.name, None)
        if last_value is not None:
            next_cursor = CursorEncoder.encode(last_value)

    return CursorPage(
        items=items,
        next_cursor=next_cursor,
        has_next=has_next,
        count=len(items)
    )


async def paginate_keyset(
    session: AsyncSession,
    query: Select,
    keys: Optional[Dict[str, Any]] = None,
    limit: int = 100,
    order_columns: Optional[List[Tuple[Column, bool]]] = None
) -> KeysetPage:
    """
    Paginate query using keyset pagination (multiple sort columns).

    Keyset pagination is more complex than cursor-based but supports
    multi-column ordering (e.g., ORDER BY priority DESC, created_at DESC).

    Args:
        session: SQLAlchemy async session
        query: Base query to paginate (should include ORDER BY)
        keys: Key values from last item of previous page
        limit: Number of results per page
        order_columns: List of (column, is_desc) tuples for ordering

    Returns:
        KeysetPage with results and next keys

    Example:
        # First page
        page = await paginate_keyset(
            session,
            select(Plan).order_by(Plan.priority.desc(), Plan.created_at.desc()),
            order_columns=[(Plan.priority, True), (Plan.created_at, True)],
            limit=50
        )

        # Next page
        page = await paginate_keyset(
            session,
            select(Plan).order_by(Plan.priority.desc(), Plan.created_at.desc()),
            keys=page.next_keys,
            order_columns=[(Plan.priority, True), (Plan.created_at, True)],
            limit=50
        )
    """
    # Add keyset filter if keys provided
    if keys and order_columns:
        keyset_filters = []

        for i, (column, is_desc) in enumerate(order_columns):
            col_name = column.name
            if col_name not in keys:
                continue

            # Build keyset condition
            # For DESC: (col1 < val1) OR (col1 = val1 AND col2 < val2) OR ...
            # For ASC: (col1 > val1) OR (col1 = val1 AND col2 > val2) OR ...

            conditions = []

            # Add exact matches for previous columns
            for j in range(i):
                prev_col, _ = order_columns[j]
                prev_name = prev_col.name
                if prev_name in keys:
                    conditions.append(prev_col == keys[prev_name])

            # Add comparison for current column
            if is_desc:
                conditions.append(column < keys[col_name])
            else:
                conditions.append(column > keys[col_name])

            if conditions:
                keyset_filters.append(and_(*conditions))

        if keyset_filters:
            query = query.where(or_(*keyset_filters))

    # Fetch limit + 1 to check if there are more results
    query = query.limit(limit + 1)

    # Execute query
    result = await session.execute(query)
    items = list(result.scalars().all())

    # Check if there are more results
    has_next = len(items) > limit
    if has_next:
        items = items[:limit]

    # Generate next keys
    next_keys = None
    if has_next and items and order_columns:
        last_item = items[-1]
        next_keys = {}
        for column, _ in order_columns:
            col_name = column.name
            value = getattr(last_item, col_name, None)
            if value is not None:
                # Convert datetime/date to ISO string for JSON serialization
                if hasattr(value, 'isoformat'):
                    value = value.isoformat()
                next_keys[col_name] = value

    return KeysetPage(
        items=items,
        next_keys=next_keys,
        has_next=has_next,
        count=len(items)
    )


async def paginate_offset(
    session: AsyncSession,
    query: Select,
    page: int = 1,
    per_page: int = 100
) -> Dict[str, Any]:
    """
    Traditional offset-based pagination.

    WARNING: Not recommended for large datasets or real-time data.
    Use cursor-based or keyset pagination instead.

    Performance degrades linearly with page number:
    - Page 1: Fast
    - Page 100: Slow (scans first 10000 rows)
    - Page 1000: Very slow (scans first 100000 rows)

    Args:
        session: SQLAlchemy async session
        query: Base query to paginate
        page: Page number (1-indexed)
        per_page: Number of results per page

    Returns:
        Dictionary with items, total, page, per_page, total_pages
    """
    # Count total results
    from sqlalchemy import func, select as sql_select

    count_query = sql_select(func.count()).select_from(query.subquery())
    total_result = await session.execute(count_query)
    total = total_result.scalar() or 0

    # Calculate pagination
    offset = (page - 1) * per_page
    total_pages = (total + per_page - 1) // per_page

    # Fetch page
    query = query.offset(offset).limit(per_page)
    result = await session.execute(query)
    items = list(result.scalars().all())

    return {
        "items": items,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1
    }
