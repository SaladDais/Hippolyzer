import itertools
import sys
from pathlib import Path

from hippolyzer.lib.base import llsd


def iter_viewer_data_dirs():
    if sys.platform.startswith("linux"):
        paths = (x for x in Path.home().iterdir() if x.name.startswith("."))
    elif sys.platform == "darwin":
        paths = (Path.home() / "Library" / "Application Support").iterdir()
    elif sys.platform in ("win32", "msys", "cygwin"):
        app_data = Path.home() / "AppData"
        # On Windows the cache directory is in Local, the settings are in Roaming. I think.
        paths = itertools.chain((app_data / "Local").iterdir(), (app_data / "Roaming").iterdir())
    else:
        raise Exception("Unknown OS, can't locate viewer config dirs!")

    for path in paths:
        if not path.is_dir():
            continue
        if not has_settings_file(path) and not has_cache_file(path):
            continue
        yield path


def has_cache_file(path: Path):
    try:
        return (path / "avatar_name_cache.xml").exists()
    except PermissionError:
        return False


def has_settings_file(path: Path):
    try:
        return (path / "user_settings" / "settings.xml").exists()
    except PermissionError:
        return False


def iter_viewer_config_dirs():
    for viewer_dir in iter_viewer_data_dirs():
        if has_settings_file(viewer_dir):
            yield viewer_dir


def iter_viewer_cache_dirs():
    for viewer_dir in iter_viewer_data_dirs():
        # Is this a settings dir
        if has_settings_file(viewer_dir):
            # Users can choose custom locations for the cache directory, we need to parse
            # their settings to see if they've done so.
            with open(viewer_dir / "user_settings" / "settings.xml", "rb") as fh:
                config: dict = llsd.parse_xml(fh.read())
            # TODO: is this the case on all platforms?
            cache_location = None
            cache_elem = config.get("CacheLocation")
            if cache_elem:
                cache_location = cache_elem.get("Value")
            if cache_location:
                cache_location = Path(cache_location)
                if has_cache_file(cache_location):
                    yield cache_location
        # Cache may be in the base dir on Windows
        if has_cache_file(viewer_dir):
            yield viewer_dir
        # but it might also be in a subfolder
        if has_cache_file(viewer_dir / "cache"):
            yield viewer_dir / "cache"
