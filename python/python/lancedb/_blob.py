# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright The LanceDB Authors

"""Fetch-path helpers for blob v2 columns."""

from __future__ import annotations

from typing import Optional, Union

import pyarrow as pa


class BlobFile:
    """Lazy handle from :meth:`lancedb.table.Table.fetch_blob_files`.

    Call ``read`` from sync code, ``aread`` from async code.
    """

    def __init__(self, inner):
        self._inner = inner

    async def aread(self) -> bytes:
        return await self._inner.read()

    def read(self) -> bytes:
        return self._inner.read_bytes()


def _normalize_blob_row_ids(row_ids: Union[list[int], pa.Table]) -> list[int]:
    if isinstance(row_ids, pa.Table):
        if "_rowid" not in row_ids.column_names:
            raise ValueError(
                "query result has no '_rowid'; "
                "call .with_row_id(True) before .to_arrow()"
            )
        return row_ids["_rowid"].to_pylist()
    if isinstance(row_ids, (pa.Array, pa.ChunkedArray)):
        raise ValueError(
            "pass a query table with _rowid, not a column array "
            "(use fetch_blobs('image', hits), not fetch_blobs('image', hits['image']))"
        )
    return list(row_ids)


def _wrap_blob_files(handles) -> list[Optional[BlobFile]]:
    return [BlobFile(handle) if handle is not None else None for handle in handles]
