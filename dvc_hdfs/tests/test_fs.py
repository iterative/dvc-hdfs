import pytest

from dvc_hdfs import HDFSFileSystem


@pytest.mark.parametrize(
    "urlpath, stripped",
    [
        ("hdfs://example.com", ""),
        ("hdfs://example.com:8020", ""),
    ],
)
@pytest.mark.parametrize("path", ["", "/path"])
def test_strip_prptocol(urlpath, stripped, path):
    # pylint: disable=protected-access
    assert HDFSFileSystem._strip_protocol(urlpath + path) == stripped + path


@pytest.mark.parametrize(
    "fs_args, expected_url",
    [
        ({"host": "example.com"}, "hdfs://example.com"),
        ({"host": "example.com", "port": None}, "hdfs://example.com"),
        ({"host": "example.com", "port": 8020}, "hdfs://example.com:8020"),
    ],
)
def test_unstrip_protocol(fs_args, expected_url):
    fs = HDFSFileSystem(**fs_args)
    assert fs.unstrip_protocol("/path") == expected_url + "/path"
