import glob

import setuptools  # noqa

import os
import shutil
from distutils.core import Command
from importlib.metadata import version
from pathlib import Path

from cx_Freeze import setup, Executable

# We don't need any of these and they make the archive huge.
TO_DELETE = [
    "lib/PySide6/Qt6DRender.pyd",
    "lib/PySide6/Qt63DRender.dll",
    "lib/PySide6/Qt6Charts.dll",
    "lib/PySide6/Qt6Location.dll",
    "lib/PySide6/Qt6Pdf.dll",
    "lib/PySide6/Qt6Quick.dll",
    "lib/PySide6/Qt6WebEngineCore.dll",
    "lib/PySide6/QtCharts.pyd",
    "lib/PySide6/QtMultimedia.pyd",
    "lib/PySide6/QtOpenGLFunctions.pyd",
    "lib/PySide6/QtOpenGLFunctions.pyi",
    "lib/PySide6/d3dcompiler_47.dll",
    "lib/PySide6/opengl32sw.dll",
    "lib/PySide6/lupdate.exe",
    "lib/PySide6/translations",
    "lib/aiohttp/_find_header.c",
    "lib/aiohttp/_frozenlist.c",
    "lib/aiohttp/_helpers.c",
    "lib/aiohttp/_http_parser.c",
    "lib/aiohttp/_http_writer.c",
    "lib/aiohttp/_websocket.c",
    # Improve this to work with different versions.
    "lib/aiohttp/python3*.dll",
    "lib/lazy_object_proxy/python3*.dll",
    "lib/lxml/python3*.dll",
    "lib/markupsafe/python3*.dll",
    "lib/multidict/python3*.dll",
    "lib/numpy/core/python3*.dll",
    "lib/numpy/fft/python3*.dll",
    "lib/numpy/linalg/python3*.dll",
    "lib/numpy/random/python3*.dll",
    "lib/python3*.dll",
    "lib/recordclass/python3*.dll",
    "lib/regex/python3*.dll",
    "lib/test",
    "lib/yarl/python3*.dll",
]

COPY_TO_ZIP = [
    "LICENSE.txt",
    "README.md",
    "NOTICE.md",
    # Must have been generated with pip-licenses before. Many dependencies
    # require their license to be distributed with their binaries.
    "lib_licenses.txt",
]


BASE_DIR = Path(__file__).parent.absolute()


class FinalizeCXFreezeCommand(Command):
    description = "Prepare cx_Freeze build dirs and create a zip"
    user_options = []

    def initialize_options(self) -> None:
        pass

    def finalize_options(self) -> None:
        pass

    def run(self):
        (BASE_DIR / "dist").mkdir(exist_ok=True)
        for path in (BASE_DIR / "build").iterdir():
            if path.name.startswith("exe.") and path.is_dir():
                for cleanse_suffix in TO_DELETE:
                    cleanse_path = path / cleanse_suffix
                    for globbed in glob.glob(str(cleanse_path)):
                        shutil.rmtree(globbed, ignore_errors=True)
                        try:
                            os.unlink(globbed)
                        except:
                            pass
                for to_copy in COPY_TO_ZIP:
                    shutil.copy(BASE_DIR / to_copy, path / to_copy)
                shutil.copytree(BASE_DIR / "addon_examples", path / "addon_examples")
                zip_path = BASE_DIR / "dist" / path.name
                shutil.make_archive(zip_path, "zip", path)


options = {
    "build_exe": {
        "packages": [
            "passlib",
            "_cffi_backend",
            "hippolyzer",
            "mitmproxy_windows",
        ],
        # exclude packages that are not really needed
        "excludes": [
            "tkinter",
        ],
        "include_msvcr": True,
    }
}

executables = [
    Executable(
        "hippolyzer/apps/proxy_gui.py",
        base=None,
        target_name="hippolyzer_gui"
    ),
]

setup(
    name="hippolyzer_gui",
    version=version("hippolyzer"),
    description="Hippolyzer GUI",
    options=options,
    executables=executables,
    cmdclass={
        "finalize_cxfreeze": FinalizeCXFreezeCommand,
    }
)
