import json
from pathlib import Path

import msgpack
import scrapy
from core.config import logging_settings
from core.logging.logger import get_logger
from lib.time_utils import get_ts
from lib.file_utils import ensure_dir, write_scrapy_text_to_file
from lib.text_utils import clean_word_list, extract_table_header_names
from scrapy.http.response.html import HtmlResponse

log = get_logger(__name__, level=logging_settings.LOG_LEVEL)

output_dir = "tmp"
html_output_dir = "html_out"
default_cache_dir = ".cache"

ensure_dir(default_cache_dir)
ensure_dir(html_output_dir)


def serialize(
    input: str | bytes = None,
    cache_dir: str = default_cache_dir,
    output_dir: str = None,
    filename: str = f"{get_ts()}_illuminatingco_htmlbody_util.msgpack",
):
    ensure_dir(dir_path=f"{cache_dir}/{output_dir}")

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
        log.info(f"Begin parsing")

        #########################
        # Pre-defined Selectors #
        #########################

        ## Class selector for main table
        SELECT_table_classes = "table-container persist-area"
        ## Class selector for thead with table column names
        SELECT_thead_col_names_select_classes = "persist-header"

        #####################
        # Main table scrape #
        #####################

        ## Select main table tag
        table = response.xpath(f"//table[@class='{SELECT_table_classes}']")
        # log.debug(f"Table ({type(table)})")

        ## Write table HTML to file
        table_html_path = f"{html_output_dir}/table.html"
        write_scrapy_text_to_file(scrapy_text=table, output_file=table_html_path)

        #############################
        # Table Head <thead> scrape #
        #############################

        ## Select thead tag
        table_headers = table.xpath(".//thead")
        # log.debug(f"Table header ({type(table_headers)})")

        ## Write table header HTML to file
        table_headers_html_path = f"{html_output_dir}/table_head.html"
        write_scrapy_text_to_file(
            scrapy_text=table_headers, output_file=table_headers_html_path
        )

        ## Select header with table column names
        thead_col_names_select = table_headers.xpath(
            f".//tr[@class='{SELECT_thead_col_names_select_classes}']"
        )

        ## Write thead column names to file
        thead_col_names_select_html_path = (
            f"{html_output_dir}/thead_col_names_select.html"
        )
        write_scrapy_text_to_file(
            scrapy_text=thead_col_names_select,
            output_file=thead_col_names_select_html_path,
        )

        thead_headers = extract_table_header_names(
            scrapy_thead_text=thead_col_names_select
        )
        log.debug(f"Table Header Column Names: {thead_headers}")

        #############################
        # Table Body <tbody> scrape #
        #############################

        ## Select tbody tag
        table_body = table.xpath(".//tbody")
        # log.debug(f"Table body ({type(table_body)})")

        ## Write table body HTML to file
        table_body_html_path = f"{html_output_dir}/table_body.html"
        write_scrapy_text_to_file(
            scrapy_text=table_body, output_file=table_body_html_path
        )

        tbody_provider_trs_select = table_body.xpath(".//tr")

        providers = []

        provider_loop_count = 1

        for provider_tr in tbody_provider_trs_select:
            # log.debug(
            #     f"Provider TR [{provider_loop_count}] ({type(provider_tr)}): {provider_tr}"
            # )

            provider_tds = []
            provider_td_loop_count = 1

            provider_tr_tds_select = provider_tr.xpath(".//td")

            for provider_tr_td in provider_tr_tds_select.extract():
                # log.debug(
                #     f"Provider <tr> <td> [{provider_td_loop_count}] ({type(provider_tr_td)}): {provider_tr_td}"
                # )

                provider_tds.append(provider_tr_td)

                provider_td_loop_count += 1

            _provider = {f"{provider_loop_count}": {"tds": provider_tds}}
            providers.append(_provider)
            provider_loop_count += 1

        log.debug(f"Provider TRs looped: {provider_loop_count}")
        log.debug(f"Providers ({len(providers)}): {providers}")
