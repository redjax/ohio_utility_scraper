from scrapy.selector.unified import SelectorList


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
