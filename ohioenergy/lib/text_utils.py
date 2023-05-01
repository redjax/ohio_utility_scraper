from core.config import logging_settings
from core.logging.logger import get_logger

log = get_logger(__name__, level=logging_settings.LOG_LEVEL)

from decimal import Decimal
from typing import Union

from scrapy.http.response.html import HtmlResponse
from scrapy.selector.unified import SelectorList

from lib.file_utils import ensure_dir

html_output_dir = "html_out"
ensure_dir(html_output_dir)


def clean_word_list(scrapy_text: SelectorList = None) -> str:
    """Clean a Scrapy SelectorList and join to string."""
    words = []
    for word in scrapy_text.extract():
        words.append(word.strip().capitalize())

    words_str = " ".join(words)

    return words_str


def extract_table_header_names(scrapy_thead_text: SelectorList = None) -> list[str]:
    """Extract table header column text.

    Returns a list of header column name strings.
    """
    ## Initialize list to fill with column headers
    table_header_cols = []

    ## Extract column names
    supplier_col_select = scrapy_thead_text.xpath(
        './/a[@id="ctl00_ContentPlaceHolder1_lstOffers_lnkRetailSupplier"]/text()'
    )
    ## Cleanup words in selector and join to list
    supplier_col_name = clean_word_list(scrapy_text=supplier_col_select)
    table_header_cols.append(supplier_col_name)

    price_per_kwh_col_select = scrapy_thead_text.xpath(
        './/a[@id="ctl00_ContentPlaceHolder1_lstOffers_lnkPrice"]/text()'
    )
    ## Cleanup words
    price_per_kwh_col_name = clean_word_list(scrapy_text=price_per_kwh_col_select)
    table_header_cols.append(price_per_kwh_col_name)

    ## Rate/type col is a list. Extract, clean, & join
    rate_type_col_select = scrapy_thead_text.xpath(".//th[4]/text()")
    rate_type_col_name = clean_word_list(rate_type_col_select)
    table_header_cols.append(rate_type_col_name)

    ## Renewable content col is a list. Extract, clean, & join
    renewable_content_col_select = scrapy_thead_text.xpath(
        ".//th[@category='electric']/text()"
    )
    renewable_content_col_name = clean_word_list(renewable_content_col_select)
    table_header_cols.append(renewable_content_col_name)

    ## Introductory price col is a list. Extract, clean, & join
    intro_price_col_select = scrapy_thead_text.xpath(
        ".//th/abbr[@title='Introductory Price']/text()"
    )
    intro_price_col_name = clean_word_list(intro_price_col_select)
    table_header_cols.append(intro_price_col_name)

    ## Term Length col is a list. Extract, clean, & join
    term_length_col_select = scrapy_thead_text.xpath(".//th[7]/text()")
    term_length_col_name = clean_word_list(term_length_col_select)
    table_header_cols.append(term_length_col_name)

    ## Early Termination Fee col is a list. Extract, clean, & join
    early_term_fee_col_select = scrapy_thead_text.xpath(".//th[8]/text()")
    early_term_fee_col_name = clean_word_list(early_term_fee_col_select)
    table_header_cols.append(early_term_fee_col_name)

    ## Monthly Fee col is a list. Extract, clean, & join
    monthly_fee_col_select = scrapy_thead_text.xpath(".//th[9]/text()")
    monthly_fee_col_name = clean_word_list(monthly_fee_col_select)
    table_header_cols.append(monthly_fee_col_name)

    ## Promotional Offers col is a list. Extract, clean, & join
    promo_offers_col_select = scrapy_thead_text.xpath(
        ".//th/abbr[@title='Promotional Offers']/text()"
    )
    promo_offers_col_name = clean_word_list(promo_offers_col_select)
    table_header_cols.append(promo_offers_col_name)

    return table_header_cols


def parse_table_body(scrapy_tbody_text: SelectorList):
    """Parse table body.

    Providers are organized into an HTML table. Columns are extracted
    separately, by the extract_table_header_names() function.

    Creates a list of providers & returns to script that called this func.
    """
    ## Select table rows
    tbody_provider_trs_select = scrapy_tbody_text.xpath(".//tr")
    ## Get count of rows
    count_provider_trs = len(tbody_provider_trs_select.extract())

    ## Initialize empty list to store parsed providers
    providers = []
    ## Initialize loop counter. Start at 1 because table <td> tags index starts at 1
    provider_loop_count = 1

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

        ## Select provider URL

        provider_url_select = provider_tr_tds_select.xpath(".//p[1]/a/@href")
        # log.debug(f"Provider URL select: {provider_url_select}")
        ## Join list to str, extract provider URL
        provider_url_content = " ".join(provider_url_select.extract()).strip()

        ## Select <td> with price
        provider_price_select = provider_tr.xpath(".//td[3]/text()")
        # log.debug(f"Provider price: {provider_price_select.extract()}")
        ## Extract price as a Decimal
        provider_price = float(
            Decimal(" ".join(provider_price_select.extract()).strip().replace(",", "."))
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
            # "table_id": provider_loop_count,
            "name": provider_name_content,
            "address": provider_address_content,
            "phone": provider_phone_content,
            "url": provider_url_content,
            "price": provider_price,
            "rate_type": rate_type_content,
            "percent_renewable": renewable_content,
            "intro_price": intro_price_content,
            "term_length": term_length_content,
            "early_term_fee": early_term_fee_content,
            "monthly_fee": monthly_fee_content,
            "promo_offer": promo_offers_content,
        }

        # log.debug(f"Provider:\n{_provider}")
        providers.append(_provider)
        # providers.append(_provider)
        provider_loop_count += 1

    return providers


def parse_providers_table(
    scrapy_response: HtmlResponse,
) -> dict[str, Union[str, Decimal, float, None]]:
    """Parse response into table content.

    Accepts a Scrapy HtmlResponse object, the raw HTML from the scrape.

    Extracts the HTML table from the page, and parses content out by passing
    pieces of extracted HTML to different functions.

    Returns a list of Provider dict objects.
    """
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
    table = scrapy_response.xpath(f"//table[@class='{SELECT_table_classes}']")
    # log.debug(f"Table ({type(table)})")

    ## Write table HTML to file
    # table_html_path = f"{html_output_dir}/table.html"
    # write_scrapy_text_to_file(scrapy_text=table, output_file=table_html_path)

    #############################
    # Table Head <thead> scrape #
    #############################

    ## Select thead tag
    table_headers_select = table.xpath(".//thead")
    # log.debug(f"Table header ({type(table_headers)})")

    ## Write table header HTML to file
    # table_headers_html_path = f"{html_output_dir}/table_head.html"
    # write_scrapy_text_to_file(
    #     scrapy_text=table_headers, output_file=table_headers_html_path
    # )

    ## Select header with table column names
    thead_col_names_select = table_headers_select.xpath(
        f".//tr[@class='{SELECT_thead_col_names_select_classes}']"
    )

    ## Write thead column names to file
    # thead_col_names_select_html_path = (
    #     f"{html_output_dir}/thead_col_names_select.html"
    # )
    # write_scrapy_text_to_file(
    #     scrapy_text=thead_col_names_select,
    #     output_file=thead_col_names_select_html_path,
    # )

    table_headers_content = extract_table_header_names(
        scrapy_thead_text=thead_col_names_select
    )
    # log.debug(f"Table Header Column Names: {table_headers}")

    #############################
    # Table Body <tbody> scrape #
    #############################

    ## Select tbody tag
    table_body_select = table.xpath(".//tbody")
    # log.debug(f"Table body ({type(table_body)})")

    ## Write table body HTML to file
    # table_body_html_path = f"{html_output_dir}/table_body.html"
    # write_scrapy_text_to_file(
    #     scrapy_text=table_body, output_file=table_body_html_path
    # )

    table_body_content = parse_table_body(scrapy_tbody_text=table_body_select)

    return_obj = {
        "table_headers": table_headers_content,
        "table_body": table_body_content,
    }
    return return_obj
