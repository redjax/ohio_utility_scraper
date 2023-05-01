from pathlib import Path

from typing import Union
from decimal import Decimal

import msgpack
from core.config import logging_settings
from core.logging.logger import get_logger

log = get_logger(__name__, level=logging_settings.LOG_LEVEL)


def loop_dir(
    _path: Path = None, packs_list: list = None
) -> list[dict[str, Union[str, float, Decimal, int, None]]]:
    # log.debug(f"Looping path: {_path}")

    for item in _path.iterdir():
        # log.debug(f"Item: {item}")

        if item.is_file():
            # log.debug(f"Item is a file.")
            packs_list.append(str(item))

        elif item.is_dir():
            # log.debug(f"Item is a dir.")
            loop_dir(_path=item, packs_list=packs_list)

    return packs_list


def get_packs(cache_dir: str = ".cache") -> list[str]:
    packs_list = []

    packs = loop_dir(_path=Path(cache_dir), packs_list=packs_list)

    return packs


def load_msgpackb(file: Path = None):
    log.info(f"Loading file: {file}")

    with open(file, "rb+") as f:
        contents = f.read()
        f.close()

    contents_load = msgpack.unpackb(contents)

    return contents_load


if __name__ == "__main__":
    packs = get_packs()
    # log.debug(f"Packs: {packs}")

    loaded = []

    for pack in packs:
        _load = load_msgpackb(file=pack)
        loaded.append(_load)

    for _load in loaded:
        log.debug(f"Loaded pack type: {type(_load)}")
        log.debug(f"Contents: {_load}")

    log.info(f"Loaded {len(loaded)} packs.")
