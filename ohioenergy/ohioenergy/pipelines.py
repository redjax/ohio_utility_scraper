# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import json
from pathlib import Path

import msgpack
from core.config import logging_settings
from core.logging.logger import get_logger
from itemadapter import ItemAdapter
from lib.time_utils import get_ts
from scrapy.http.response.html import HtmlResponse

log = get_logger(__name__, level=logging_settings.LOG_LEVEL)

default_cache_dir = ".cache"

if not Path(default_cache_dir).exists():
    Path(default_cache_dir).mkdir(exist_ok=True, parents=True)


def serialize(
    input: str | bytes = None,
    cache_dir: str = default_cache_dir,
    output_dir: str = None,
    filename: str = f"{get_ts()}_illuminatingco_htmlbody_util.msgpack",
):
    if not Path(cache_dir).exists():
        Path(cache_dir).mkdir(parents=True, exist_ok=True)

    if output_dir:
        if not Path(f"{cache_dir}/{output_dir}").exists():
            log.info(f"Creating dir: {f'{cache_dir}/{output_dir}'}")
            Path(f"{cache_dir}/{output_dir}").mkdir(parents=True, exist_ok=True)

    if not output_dir:
        output_file = f"{cache_dir}/{filename}"
    else:
        output_file = f"{cache_dir}/{output_dir}/{filename}"

    log.info(f"Serializing HTML body to {output_file}")
    # print(f"Input type: {type(input)}")
    with open(output_file, "wb") as f:
        if isinstance(input, bytes):
            input = input.decode()
        packed = msgpack.packb(input)
        f.write(packed)


def prepare_res_obj(response: HtmlResponse = None) -> dict:
    if not response:
        raise ValueError("Missing HtmlResponse object.")

    res_body: bytes | None = response.body.decode()
    res_attributes: tuple | None = list(response.attributes)
    res_encoding: str | None = response.encoding
    res_flags: list | None = response.flags
    res_url: str | None = response.url

    return_obj = {
        "attributes": res_attributes,
        "encoding": res_encoding,
        "flags": res_flags,
        "url": res_url,
        "body": res_body,
    }

    return return_obj


class OhioenergyPipeline:
    def process_item(self, item, spider):
        log.info("Starting OhioenergyPipeline.process_item()")
        log.debug(f"Item: {item}")
        log.info("Finish processing item.")

        return item


class SerializePipeline:
    def process_item(self, item, spider):
        item_bytes = json.dumps(item).encode("utf-8")

        log.info(f"Serializing results.")
        serialize(input=item_bytes)
