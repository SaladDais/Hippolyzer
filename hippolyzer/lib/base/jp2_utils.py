import os
import tempfile
from io import BytesIO
from typing import *

import defusedxml.ElementTree
from glymur import jp2box, Jp2k

# Replace glymur's ElementTree with a safe one
jp2box.ET = defusedxml.ElementTree


SL_DEFAULT_ENCODE = {
    "cratios": (1920.0, 480.0, 120.0, 30.0, 10.0),
    "irreversible": True,
}


class BufferedJp2k(Jp2k):
    """
    For manipulating JP2K from within a binary buffer.

    For many operations glymur expects to be able to re-read from a file
    based on filename, so this is the least brittle approach.
    """

    def __init__(self, contents: bytes, encode_kwargs: Optional[Dict] = None):
        if encode_kwargs is None:
            self.encode_kwargs = SL_DEFAULT_ENCODE.copy()
        else:
            self.encode_kwargs = encode_kwargs

        stream = BytesIO(contents)
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        stream.seek(0)
        self.temp_file.write(stream.read())
        # Windows NT can't handle two FHs open on a tempfile at once
        self.temp_file.close()

        super().__init__(self.temp_file.name)

    def __del__(self):
        if self.temp_file is not None:
            os.remove(self.temp_file.name)
        self.temp_file = None

    def _write(self, img_array, verbose=False, **kwargs):
        # Glymur normally only lets you control encode params when a write happens within
        # the constructor. Keep around the encode params from the constructor and pass
        # them to successive write calls.
        return super()._write(img_array, verbose=False, **self.encode_kwargs, **kwargs)

    def __bytes__(self):
        with open(self.temp_file.name, "rb") as f:
            return f.read()
