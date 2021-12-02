from contextlib import contextmanager

from dvc.testing.cloud import Cloud
from dvc.testing.path_info import URLInfo


class HDFS(Cloud, URLInfo):  # pylint: disable=abstract-method
    @contextmanager
    def _hdfs(self):
        import pyarrow.fs

        conn = pyarrow.fs.HadoopFileSystem(self.host, self.port)
        yield conn

    @property
    def config(self):
        return {"url": self.url}

    def is_file(self):
        with self._hdfs() as _hdfs:
            import pyarrow.fs

            file_info = _hdfs.get_file_info(self.path)
            return file_info.type == pyarrow.fs.FileType.File

    def is_dir(self):
        with self._hdfs() as _hdfs:
            import pyarrow.fs

            file_info = _hdfs.get_file_info(self.path)
            return file_info.type == pyarrow.fs.FileType.Directory

    def exists(self):
        with self._hdfs() as _hdfs:
            import pyarrow.fs

            file_info = _hdfs.get_file_info(self.path)
            return file_info.type != pyarrow.fs.FileType.NotFound

    def mkdir(self, mode=0o777, parents=False, exist_ok=False):
        assert mode == 0o777
        assert parents

        with self._hdfs() as _hdfs:
            # NOTE: fs.create_dir creates parents by default
            _hdfs.create_dir(self.path)

    def write_bytes(self, contents):
        with self._hdfs() as _hdfs:
            with _hdfs.open_output_stream(self.path) as fobj:
                fobj.write(contents)

    def read_bytes(self):
        with self._hdfs() as _hdfs:
            with _hdfs.open_input_stream(self.path) as fobj:
                return fobj.read()

    @property
    def fs_path(self):
        return self.path.lstrip("/")
