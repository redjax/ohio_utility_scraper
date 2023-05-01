import msgpack
from core.config import logging_settings
from core.logging.logger import get_logger

from lib.file_utils import ensure_dir
from lib.time_utils import get_ts

log = get_logger(__name__, level=logging_settings.LOG_LEVEL)

default_cache_dir = ".cache"


def serialize(
    input: str | bytes = None,
    cache_dir: str = default_cache_dir,
    output_dir: str = None,
    filename: str = f"{get_ts()}_unnamed_serialize.msgpack",
):
    ensure_dir(dir_path=f"{cache_dir}/{output_dir}")

    if not output_dir:
        output_file = f"{cache_dir}/{filename}"
    else:
        output_file = f"{cache_dir}/{output_dir}/{filename}"

    # log.info(f"Serializing input to {output_file}")
    # print(f"Input type: {type(input)}")
    with open(output_file, "wb") as f:
        if isinstance(input, bytes):
            input = input.decode()
        packed = msgpack.packb(input)
        f.write(packed)
