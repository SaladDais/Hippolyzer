import itertools
from pathlib import Path
import shutil
import sys


class InvalidConfigDir(Exception):
    pass


def setup_ca(config_path, mitmproxy_master):
    p = Path(config_path)
    if not p.exists():
        raise InvalidConfigDir("Config path does not exist!")
    settings_path = p / "user_settings"
    if not (settings_path / "settings.xml").exists():
        raise InvalidConfigDir("Path is not a second life config dir!")

    mitmproxy_conf_dir = Path(mitmproxy_master.options.confdir)
    mitmproxy_ca_path = (mitmproxy_conf_dir.expanduser() / "mitmproxy-ca-cert.pem")

    shutil.copy(mitmproxy_ca_path, settings_path / "CA.pem")


def setup_ca_everywhere(mitmproxy_master):
    valid_paths = set()
    paths = _viewer_config_dir_iter()
    for path in paths:
        try:
            setup_ca(path, mitmproxy_master)
            valid_paths.add(path)
        except InvalidConfigDir:
            pass
        except PermissionError:
            pass

    return valid_paths


def _viewer_config_dir_iter():
    if sys.platform.startswith("linux"):
        paths = (x for x in Path.home().iterdir() if x.name.startswith("."))
    elif sys.platform == "darwin":
        paths = (Path.home() / "Library" / "Application Support").iterdir()
    elif sys.platform in ("win32", "msys", "cygwin"):
        app_data = Path.home() / "AppData"
        paths = itertools.chain((app_data / "Local").iterdir(), (app_data / "Roaming").iterdir())
    else:
        raise Exception("Unknown OS, can't locate viewer config dirs!")

    return (path for path in paths if path.is_dir())
