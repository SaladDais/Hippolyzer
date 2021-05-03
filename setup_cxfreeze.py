import setuptools  # noqa

import os
import shutil
from distutils.core import Command
from pathlib import Path

from cx_Freeze import setup, Executable

# We don't need any of these and they make the archive huge.
TO_DELETE = [
    "lib/PySide2/Qt3DRender.pyd",
    "lib/PySide2/Qt53DRender.dll",
    "lib/PySide2/Qt5Charts.dll",
    "lib/PySide2/Qt5Location.dll",
    "lib/PySide2/Qt5Pdf.dll",
    "lib/PySide2/Qt5Quick.dll",
    "lib/PySide2/Qt5WebEngineCore.dll",
    "lib/PySide2/QtCharts.pyd",
    "lib/PySide2/QtMultimedia.pyd",
    "lib/PySide2/QtOpenGLFunctions.pyd",
    "lib/PySide2/QtOpenGLFunctions.pyi",
    "lib/PySide2/d3dcompiler_47.dll",
    "lib/PySide2/opengl32sw.dll",
    "lib/PySide2/translations",
    "lib/aiohttp/_find_header.c",
    "lib/aiohttp/_frozenlist.c",
    "lib/aiohttp/_helpers.c",
    "lib/aiohttp/_http_parser.c",
    "lib/aiohttp/_http_writer.c",
    "lib/aiohttp/_websocket.c",
    # Improve this to work with different versions.
    "lib/aiohttp/python39.dll",
    "lib/lazy_object_proxy/python39.dll",
    "lib/lxml/python39.dll",
    "lib/markupsafe/python39.dll",
    "lib/multidict/python39.dll",
    "lib/numpy/core/python39.dll",
    "lib/numpy/fft/python39.dll",
    "lib/numpy/linalg/python39.dll",
    "lib/numpy/random/python39.dll",
    "lib/python39.dll",
    "lib/recordclass/python39.dll",
    "lib/regex/python39.dll",
    "lib/test",
    "lib/yarl/python39.dll",
]


BASE_DIR = Path(__file__).parent.absolute()


class FinalizeCXFreezeCommand(Command):
    description = "Prepare cx_Freeze build dirs for zipping"
    user_options = []

    def initialize_options(self) -> None:
        pass

    def finalize_options(self) -> None:
        pass

    def run(self):
        for path in (BASE_DIR / "build").iterdir():
            if path.name.startswith("exe.") and path.is_dir():
                for cleanse_suffix in TO_DELETE:
                    cleanse_path = path / cleanse_suffix
                    shutil.rmtree(cleanse_path, ignore_errors=True)
                    try:
                        os.unlink(cleanse_path)
                    except:
                        pass
                # Must have been generated with pip-licenses before. Many dependencies
                # require their license to be distributed with their binaries.
                shutil.copy(BASE_DIR / "lib_licenses.txt", path / "lib_licenses.txt")


class BuildZipArchiveCommand(Command):
    description = "Make a distributable zip from an EXE build"
    user_options = []

    def initialize_options(self) -> None:
        pass

    def finalize_options(self) -> None:
        pass

    def run(self):
        (BASE_DIR / "dist").mkdir(exist_ok=True)
        for path in (BASE_DIR / "build").iterdir():
            if path.name.startswith("exe.") and path.is_dir():
                zip_path = BASE_DIR / "dist" / (path.name + ".zip")
                shutil.make_archive(zip_path, "zip", path)


options = {
    "build_exe": {
        "packages": [
            "passlib",
            "_cffi_backend",
            "hippolyzer",
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
    version="0.1",
    description="Hippolyzer GUI",
    options=options,
    executables=executables,
    cmdclass={
        "finalize_cxfreeze": FinalizeCXFreezeCommand,
        "build_zip": BuildZipArchiveCommand,
    }
)
