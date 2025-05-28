import os
import uuid
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.parse import urlparse

import pytest

from .cloud import HDFS

_hdfs_root = TemporaryDirectory()


@pytest.fixture(scope="session")
def docker_compose_file():
    return os.path.join(os.path.dirname(__file__), "docker-compose.yml")


def md5md5crc32c(path):
    # https://github.com/colinmarc/hdfs/blob/f2f512db170db82ad41590c4ba3b7718b13317d2/file_reader.go#L76
    import hashlib

    from crc32c import crc32c  # pylint: disable=no-name-in-module

    # dfs.bytes-per-checksum = 512, default on hadoop 2.7
    bytes_per_checksum = 512
    padded = 32
    total = 0

    md5md5 = hashlib.md5()

    with open(path, "rb") as fobj:
        while True:
            block = fobj.read(bytes_per_checksum)
            if not block:
                break

            crc_int = crc32c(block)

            # NOTE: hdfs is big-endian
            crc_bytes = crc_int.to_bytes((crc_int.bit_length() + 7) // 8, "big")

            md5 = hashlib.md5(crc_bytes).digest()

            total += len(md5)
            if padded < total:
                padded *= 2

            md5md5.update(md5)

    md5md5.update(b"\0" * (padded - total))
    return "000002000000000000000000" + md5md5.hexdigest()


def hadoop_fs_checksum(_, path):
    parsed = urlparse(path)

    return md5md5crc32c(Path(_hdfs_root.name) / parsed.path.lstrip("/"))


class FakeHadoopFileSystem:
    def __init__(self, *args, **kwargs):
        from pyarrow.fs import LocalFileSystem

        self._root = Path(_hdfs_root.name)
        self._fs = LocalFileSystem()

    def _path(self, path):
        from pyarrow.fs import FileSelector

        if isinstance(path, FileSelector):
            return FileSelector(
                os.fspath(self._root / path.base_dir.lstrip("/")),
                path.allow_not_found,
                path.recursive,
            )
        if isinstance(path, list):
            return [self._path(sub_path) for sub_path in path]

        return os.fspath(self._root / path.lstrip("/"))

    def create_dir(self, path, **kwargs):
        return self._fs.create_dir(self._path(path), **kwargs)

    def open_input_stream(self, path, **kwargs):
        return self._fs.open_input_stream(self._path(path), **kwargs)

    def open_input_file(self, path, **kwargs):
        return self._fs.open_input_file(self._path(path), **kwargs)

    def open_output_stream(self, path, **kwargs):
        import posixpath

        # NOTE: HadoopFileSystem.open_output_stream creates directories
        # automatically.
        self.create_dir(posixpath.dirname(path))
        return self._fs.open_output_stream(self._path(path), **kwargs)

    def get_file_info(self, path, **kwargs):
        from pyarrow.fs import FileInfo

        entries = self._fs.get_file_info(self._path(path), **kwargs)
        if isinstance(entries, FileInfo):
            ret = self._adjust_entry(entries)
        else:
            assert isinstance(entries, list)
            ret = list(map(self._adjust_entry, entries))

        #        import pdb; pdb.set_trace()

        return ret

    def _adjust_entry(self, entry):
        import posixpath

        from pyarrow.fs import FileInfo

        mocked_path = os.path.relpath(entry.path, self._root)
        mocked_parts = mocked_path.split(os.path.sep)
        return FileInfo(
            path=posixpath.join("/", *mocked_parts),
            type=entry.type,
            mtime=entry.mtime,
            size=entry.size,
        )

    def move(self, from_path, to_path):
        self._fs.move(self._path(from_path), self._path(to_path))

    def delete_file(self, path):
        self._fs.delete_file(self._path(path))


@pytest.fixture
def make_hdfs(mocker):
    # Windows might not have Visual C++ Redistributable for Visual Studio
    # 2015 installed, which will result in the following error:
    # "The pyarrow installation is not built with support for
    # 'HadoopFileSystem'"
    pytest.importorskip("pyarrow.fs")

    mocker.patch("pyarrow.fs._not_imported", [])
    mocker.patch("pyarrow.fs.HadoopFileSystem", FakeHadoopFileSystem, create=True)

    mocker.patch("dvc_hdfs.HDFSFileSystem._checksum", hadoop_fs_checksum)

    def _make_hdfs():
        url = f"hdfs://example.com:12345/{uuid.uuid4()}"
        return HDFS(url)

    return _make_hdfs


@pytest.fixture
def hdfs(make_hdfs):  # pylint: disable=redefined-outer-name
    return make_hdfs()
