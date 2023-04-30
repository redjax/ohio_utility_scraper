import json
from pathlib import Path

import msgpack
import scrapy
from core.config import logging_settings
from core.logging.logger import get_logger
from lib.time_utils import get_ts
from scrapy.http.response.html import HtmlResponse

log = get_logger(__name__, level=logging_settings.LOG_LEVEL)

output_dir = "tmp"
default_cache_dir = ".cache"

if not Path(default_cache_dir).exists():
    Path(default_cache_dir).mkdir(exist_ok=True, parents=True)

# if not Path(output_dir).exists():
#     Path(output_dir).mkdir(exist_ok=True, parents=True)


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


class OhioenergyprovidersSpider(scrapy.Spider):
    name = "ohioenergyproviders"
    allowed_domains = ["energychoice.ohio.gov"]
    start_urls = [
        # "http://energychoice.ohio.gov/",
        "https://energychoice.ohio.gov/ApplesToApplesComparision.aspx?Category=Electric&TerritoryId=6&RateCode=1",
    ]

    def parse(self, response: HtmlResponse):
        log.info("Parsing response")

        ## Get HTML table section
        table_content = response.css(
            "#ctl00_ContentPlaceHolder1_upOffers > div.tab-right"
        )
        # log.debug(f"Table content: {table_content.extract()}")

        ## Extract table body
        table_body = table_content.css("table > tbody")
        # log.debug(f"Table body: {table_body.extract()}")

        ## Extract rows from body
        table_rows = table_body.xpath("//tr")
        # log.debug(f"Table rows: {table_rows.extract()}")

        ## Initialize lists for looping over table rows
        providers_tmp = []
        seen_providers = []
        unique_providers = []

        ## Loop table rows
        for row in table_rows:
            ## Get provider details span content
            provider_span = row.css("span.retail-title")
            ## Get name, address paragraphs
            provider_name_address = provider_span.css("::text").extract()
            # log.debug(f"Provider:\n{provider_name_address}")

            ## Initialize empty list to store provider contact values
            values = []

            ## Ensure provider name/address span text was found
            if provider_name_address:
                # list_len = len(provider_name_address)
                # log.debug(f"Provider name/address length: {list_len}")

                ## Loop over values in provider_name_addresses list
                for val in provider_name_address:
                    if val:
                        # log.debug(f"Provider name/address value: {val}")
                        ## Extract value
                        values.append(val)

                # log.debug(f"Current values: {values}")

                ## Extract provider's URL
                provider_url = row.css("p a::attr(href)").extract_first()

                ## Build a dict of provider data
                _provider = {
                    "name": values[0],
                    "details": {
                        "address": " ".join(values[1:-1]),
                        "phone": values[-1],
                        "url": provider_url,
                    },
                }
                # log.debug(f"Provider: {_provider}")

                ## Append to temporary providers list
                providers_tmp.append(_provider)

                # log.debug(f"Current providers: {providers}")

            # log.debug(f"Providers: {providers}")

        ## Loop over found providers and cleanup list, reduce duplicates
        for provider in providers_tmp:
            ## Ensure provider has not been seen
            if provider["name"] not in seen_providers:
                # log.debug(f"Unique provider detected: {provider['name']}")
                ## Add unseen providers to seen_providers list
                seen_providers.append(provider["name"])
                ## Add to unique providers
                unique_providers.append(provider)

        log.debug(
            f"Original list len: {len(providers_tmp)}, cleanup len: {len(unique_providers)}"
        )

        ## Set providers list to unique/deduplicated list
        providers = unique_providers

        log.debug(f"Providers length: {len(providers)}")
