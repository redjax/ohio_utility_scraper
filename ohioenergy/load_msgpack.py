from pathlib import Path

import msgpack
from core.config import logging_settings
from core.logging.logger import get_logger

log = get_logger(__name__, level=logging_settings.LOG_LEVEL)


def get_packs(cache_dir: str = ".cache") -> list[str]:
    packs = []

    for pack in Path(cache_dir).iterdir():
        if pack.is_file():
            packs.append(pack)
        elif pack.is_dir():
            for _pack in pack.iterdir():
                if _pack.is_file():
                    packs.append(_pack)
                elif _pack.is_dir():
                    raise NotImplemented(
                        f"Recursion below 2 subdirectories is not implemented yet."
                    )

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
    log.debug(f"Packs: {packs}")

    loaded = []

    for pack in packs:
        _load = load_msgpackb(file=pack)
        loaded.append(_load)

    log.debug(f"Loaded {len(loaded)} packs.")

    for _load in loaded:
        log.debug(f"Loaded pack type: {type(_load)}")
        # log.debug(f"Contents: {_load}")
