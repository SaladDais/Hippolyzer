import sys

from cx_Freeze import setup, Executable

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
        ]
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
)
