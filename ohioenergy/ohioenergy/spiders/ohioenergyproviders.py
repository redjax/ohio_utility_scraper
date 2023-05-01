import json
from decimal import Decimal
from pathlib import Path

from typing import Union

import msgpack
import scrapy
from core.config import logging_settings
from core.logging.logger import get_logger
from lib.file_utils import ensure_dir, write_scrapy_text_to_file
from lib.msgpack_utils import serialize
from lib.text_utils import (
    clean_word_list,
    extract_table_header_names,
    parse_providers_table,
    parse_table_body,
)
from lib.time_utils import get_ts, get_date
from scrapy.http.response.html import HtmlResponse

from ohioenergy.items import OhioenergyItem

log = get_logger(__name__, level=logging_settings.LOG_LEVEL)


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


class OhioenergyprovidersSpider(scrapy.Spider):
    name = "ohioenergyproviders"
    allowed_domains = ["energychoice.ohio.gov"]
    start_urls = [
        "https://energychoice.ohio.gov/ApplesToApplesComparision.aspx?Category=Electric&TerritoryId=6&RateCode=1",
    ]

    def parse(self, response: HtmlResponse):
        log.info(f"Begin parsing")

        parsed_table = parse_providers_table(scrapy_response=response)

        for item in parsed_table["table_body"]:
            ## Create OhioenergyItem to pass into pipelines
            item["utility_type"] = "electric"
            provider_item = OhioenergyItem(**item)

            ## Yield items, pipelines kick in next. If no pipelines,
            #  item will just be returned
            yield provider_item
