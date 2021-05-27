from pathlib import Path
import shutil

from hippolyzer.lib.proxy.viewer_settings import iter_viewer_config_dirs, has_settings_file


class InvalidConfigDir(Exception):
    pass


def setup_ca(config_path, mitmproxy_master):
    p = Path(config_path)
    if not p.exists():
        raise InvalidConfigDir("Config path does not exist!")
    if not has_settings_file(p):
        raise InvalidConfigDir("Path is not a second life config dir!")

    mitmproxy_conf_dir = Path(mitmproxy_master.options.confdir)
    mitmproxy_ca_path = (mitmproxy_conf_dir.expanduser() / "mitmproxy-ca-cert.pem")

    shutil.copy(mitmproxy_ca_path, p / "user_settings" / "CA.pem")


def setup_ca_everywhere(mitmproxy_master):
    valid_paths = set()
    paths = iter_viewer_config_dirs()
    for path in paths:
        try:
            setup_ca(path, mitmproxy_master)
            valid_paths.add(path)
        except InvalidConfigDir:
            pass
    return valid_paths
