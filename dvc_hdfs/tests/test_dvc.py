import pytest
from dvc.testing.test_api import TestAPI  # noqa, pylint: disable=unused-import
from dvc.testing.test_remote import (  # noqa, pylint: disable=unused-import
    TestRemote,
)
from dvc.testing.test_workspace import TestAdd as _TestAdd
from dvc.testing.test_workspace import TestImport as _TestImport


@pytest.fixture
def remote(make_remote):
    yield make_remote(name="upstream", typ="hdfs")


@pytest.fixture
def workspace(make_workspace):
    yield make_workspace(name="workspace", typ="hdfs")


class TestImport(_TestImport):
    @pytest.fixture
    def stage_md5(self):
        return "ec0943f83357f702033c98e70b853c8c"

    @pytest.fixture
    def dir_md5(self):
        pytest.skip("https://github.com/iterative/dvc-hdfs/issues/2")

    @pytest.fixture
    def is_object_storage(self):
        return False


class TestAdd(_TestAdd):
    @pytest.fixture
    def hash_name(self):
        return "checksum"

    @pytest.fixture
    def hash_value(self):
        return "000002000000000000000000a86fe4d846edc1bf4c355cb6112f141e"

    @pytest.fixture
    def dir_hash_value(self):
        pytest.skip("external outputs are broken for hdfs dirs")
