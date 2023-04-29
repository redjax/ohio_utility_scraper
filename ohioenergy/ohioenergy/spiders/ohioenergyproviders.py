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

    #     print(
    #         f"""
    # Response types:
    # body: {type(res_body)}
    # attributes: {type(res_attributes)}
    # encoding: {type(res_encoding)}
    # flags: {type(res_flags)}
    # url: {type(res_url)}
    #           """
    #     )

    return_obj = {
        "attributes": res_attributes,
        "encoding": res_encoding,
        "flags": res_flags,
        "url": res_url,
        "body": res_body,
    }

    # return_obj_json = json.dumps(return_obj)

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

        # print(f"Response dict keys: {vars(response).keys()}")
        res_body = response.body.decode()

        serialize(input=response.body, output_dir="illuminating_co")

        res_prepared = prepare_res_obj(response)

        res_json = res_prepared

        # with open(f"{output_dir}/{get_ts()}res.json", "w") as f:
        #     try:
        #         json.dump(res_json, f, indent=4)
        #     except Exception as exc:
        #         raise Exception(
        #             f"Unhandled exception dumping response JSON. Details:\n{exc}"
        #         )

        # f.close()

        # with open(f"{output_dir}/{get_ts()}_output", "w") as f:
        #     f.write(res_body)

        # f.close()
        pass
