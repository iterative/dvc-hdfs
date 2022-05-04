import pytest
from dvc.testing.test_api import TestAPI  # noqa, pylint: disable=unused-import
from dvc.testing.test_remote import (  # noqa, pylint: disable=unused-import
    TestRemote,
)
from dvc.testing.test_workspace import (  # noqa, pylint: disable=unused-import
    TestAdd,
    TestImport,
)


@pytest.fixture
def cloud_name():
    return "hdfs"


@pytest.fixture
def remote(make_remote, cloud_name):
    yield make_remote(name="upstream", typ=cloud_name)


@pytest.fixture
def workspace(make_workspace, cloud_name):
    yield make_workspace(name="workspace", typ=cloud_name)


class TestImportHDFS(TestImport):
    @pytest.fixture
    def stage_md5(self):
        return "ec0943f83357f702033c98e70b853c8c"

    @pytest.fixture
    def dir_md5(self):
        return "e6dcd267966dc628d732874f94ef4280.dir"

    @pytest.fixture
    def is_object_storage(self):
        return False


class TestAddHDFS(TestAdd):
    @pytest.fixture
    def hash_name(self):
        return "checksum"

    @pytest.fixture
    def hash_value(self):
        return "000002000000000000000000a86fe4d846edc1bf4c355cb6112f141e"

    @pytest.fixture
    def dir_hash_value(self):
        pytest.skip("external outputs are broken for hdfs dirs")
