import pytest

from dvc.testing.workspace_tests import TestImport as _TestImport


@pytest.fixture
def remote(make_remote):
    return make_remote(name="upstream", typ="hdfs")


@pytest.fixture
def workspace(make_workspace):
    return make_workspace(name="workspace", typ="hdfs")


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
