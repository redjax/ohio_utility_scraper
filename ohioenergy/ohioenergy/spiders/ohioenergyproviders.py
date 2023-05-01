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

from decimal import Decimal

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

        ## Select table rows
        tbody_provider_trs_select = table_body.xpath(".//tr")
        ## Get count of rows
        count_provider_trs = len(tbody_provider_trs_select.extract())

        ## Initialize empty list to store parsed providers
        providers = []
        ## Initialize loop counter. Start at 1 because table <td> tags index starts at 1
        provider_loop_count = 1

        log.debug(f"Number of Provider <tr>s: {count_provider_trs}")

        ## Loop over table rows, extract <td> values
        for provider_tr in tbody_provider_trs_select:
            # log.debug(
            #     f"Provider TR [{provider_loop_count}] ({type(provider_tr)}): {provider_tr}"
            # )

            ## Select <td> tags
            provider_tr_tds_select = provider_tr.xpath(".//td")
            ## Each provider has 10 <td> tags
            count_provider_tr_tds = len(provider_tr_tds_select)
            # log.debug(
            #     f"Detected {count_provider_tr_tds} <td> tags in current provider <tr>"
            # )

            ## Select <td> with Provider's name
            provider_name_select = provider_tr_tds_select.xpath(
                ".//span[@class='retail-title']/text()"
            )
            ## Extract provider name
            provider_name_content = " ".join(provider_name_select.extract())
            # log.debug(f"Provider name: {provider_name_content}")

            ## Select <span> with Provider's address, phone
            provider_contact_select = provider_tr_tds_select.xpath(
                ".//span[@class='retail-title']/p/text()"
            )
            # log.debug(f"Provider Contact Details: {provider_contact_select.extract()}")
            ## Extract contact info, split phone & address from list to get string values for each
            provider_address_content = " ".join(provider_contact_select.extract()[0:-1])
            provider_phone_content = provider_contact_select.extract()[-1]
            # log.debug(f"Provider address: {provider_address_content}")
            # log.debug(f"Provider phone: {provider_phone_content}")

            ## Select <td> with price
            provider_price_select = provider_tr.xpath(".//td[3]/text()")
            # log.debug(f"Provider price: {provider_price_select.extract()}")
            ## Extract price as a Decimal
            provider_price = (
                Decimal(
                    " ".join(provider_price_select.extract()).strip().replace(",", ".")
                )
                * 100
            )
            # log.debug(f"Provider price ({type(provider_price)}): {provider_price}")

            ## Select <td> with rate type (variable, fixed)
            rate_type_select = provider_tr.xpath(".//td[4]/text()")
            ## Extract rate
            rate_type_content = rate_type_select.extract()[1].strip()
            # log.debug(f"Rate type: {rate_type_content}")

            ## Select <td> with renewable energy percentage
            renewable_content_select = provider_tr.xpath(".//td[5]/text()").extract()
            ## Join list to str, extract renewable percentage
            renewable_content = " ".join(renewable_content_select).strip()
            # log.debug(f"Renewable content percentage: {renewable_content}")

            ## Select <td> with Provider's introductory discount
            intro_price_content_select = provider_tr.xpath(".//td[6]/p/text()")
            ## Join list to str, extract intro price value
            intro_price_content = " ".join(intro_price_content_select.extract()).strip()
            # log.debug(f"Introductory pricing: {intro_price_content}")

            ## Select <td> with Provider's term length
            term_length_select = provider_tr.xpath(".//td[7]/text()")
            ## Join list to str, extract term length value
            term_length_content = " ".join(term_length_select.extract()).strip()
            # log.debug(f"Term length: {term_length_content}")

            ## Select <td> with Provider's early termination fee
            early_term_fee_select = provider_tr.xpath(".//td[8]/text()")
            ## Join list to str, extract early term fee
            early_term_fee_content = " ".join(early_term_fee_select.extract()).strip()
            # log.debug(f"Early term fee: {early_term_fee_content}")

            ## Select <td> with Provider's monthly fee
            monthly_fee_select = provider_tr.xpath(".//td[9]/text()")
            ## Join list to str, extract monthly fee
            monthly_fee_content = " ".join(monthly_fee_select.extract()).strip()
            # log.debug(f"Monthly fee: {monthly_fee_content}")

            ## Select <td> with Provider's promo offers
            promo_offers_select = provider_tr.xpath(".//td[10]/p/text()")
            # log.debug(f"Promo offers select: {promo_offers_select.extract()}")
            ## Join list to str, extract promo offer
            promo_offers_content = " ".join(promo_offers_select.extract()).strip()
            # log.debug(f"Promo offers: {promo_offers_content}")

            _provider = {
                "table_id": {provider_loop_count},
                "name": provider_name_content,
                "contact": {
                    "address": provider_address_content,
                    "phone": provider_phone_content,
                },
                "price": provider_price,
                "rate_type": rate_type_content,
                "percent_renewable": renewable_content,
                "intro_price": intro_price_content,
                "term_length": term_length_content,
                "early_term_fee": early_term_fee_content,
                "monthly_fee": monthly_fee_content,
                "promo_offer": promo_offers_content,
            }

            log.debug(f"Provider:\n{_provider}")
            providers.append(_provider)
            # providers.append(_provider)
            provider_loop_count += 1

        # log.debug(f"Number of provider <td>s: {len(providers)}")
        # log.debug(f"Providers ({len(providers)}): {providers}")

        # test_provider = providers[0]["tds"]
        # log.debug(f"Test provider ({type(test_provider)}): {test_provider}")
