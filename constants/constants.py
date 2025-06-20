import configparser
from typing import Any, Optional


def read_ini_config(
        section: str,
        key: str,
        default: Optional[Any] = None,
        config_type: Optional[type] = str
) -> Any:
    config = configparser.ConfigParser()
    config.read(INI_FILE)

    try:
        value = config[section][key]
        if config_type is bool:
            return config.getboolean(section, key)
        elif config_type is int:
            return int(value)
        elif config_type is float:
            return float(value)
        return value

    except (configparser.NoSectionError, configparser.NoOptionError, KeyError):
        return default
    except (ValueError, TypeError):
        return default


INI_FILE = "datexlite.ini"
DATABASE_NAME = "datex_lite.db"
PATH_FOR_BACKUP = read_ini_config("MAIN", "path_for_backup", ".")
