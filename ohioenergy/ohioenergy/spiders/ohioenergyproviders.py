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
        def serialize_providers(
            providers: list[
                dict[str, Union[str, float, Decimal, int, bool, None]]
            ] = None
        ) -> None:
            ## Serialize providers
            for provider in providers:
                # log.debug(f"Provider type: {type(provider)}")

                # for k in provider.keys():
                #     log.debug(f"Provider item ({type(provider[k])}): {provider[k]}")

                _serialize_prep = json.dumps(provider, indent=2).encode("utf-8")
                # log.debug(f"Serialize string type: {type(_serialize_prep)}")

                provider_serialize = serialize(
                    input=_serialize_prep,
                    output_dir=f"providers/{get_date()}",
                    filename=f"{get_ts()}_{provider['name']}.msgpack",
                )

        log.info(f"Begin parsing")

        parsed_table = parse_providers_table(scrapy_response=response)

        table_headers = parsed_table["table_headers"]
        providers: list[
            dict[str, Union[str, float, Decimal, int, bool, None]]
        ] = parsed_table["table_body"]

        log.debug(f"Number of providers: {len(providers)}")
        log.debug(f"Table headers: {table_headers}")

        serialize_providers(providers=providers)
