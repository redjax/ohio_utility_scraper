from pathlib import Path

from core.config import logging_settings
from core.logging.logger import get_logger

log = get_logger(__name__, level=logging_settings.LOG_LEVEL)

from scrapy.selector.unified import SelectorList


def ensure_dir(dir_path: str = None):
    """Ensure existence of directory path.

    Checks if path exists, creates if not.
    """
    # log.debug(f"Ensuring path exists ({type(dir_path)}): {dir_path}")

    if not dir_path:
        raise ValueError("Missing directory path")

    try:
        if not Path(dir_path).exists():
            Path(dir_path).mkdir(exist_ok=True, parents=True)
    except PermissionError as perm_exc:
        raise PermissionError(
            f"Permission error creating path [{dir_path}]. Exception detail: {perm_exc}"
        )
    except Exception as exc:
        raise Exception(
            f"Unhandled exception creating directory [{dir_path}]. Exception detail: {exc}"
        )


def write_scrapy_text_to_file(
    scrapy_text: SelectorList = None, output_file: str = None
):
    """Write a scraped object to file.

    scrapy_text should be a Scrapy object, i.e. response.xpath(...).
    output_file should be a filepath, i.e. html_output/file_name.html.
    """
    try:
        if not Path(output_file).exists():
            with open(output_file, "w") as f:
                f.write(" ".join(scrapy_text.extract()))

            f.close()
    except PermissionError as perm_exc:
        raise PermissionError(
            f"Permission error creating path [{output_file}]. Exception detail: {perm_exc}"
        )
    except Exception as exc:
        raise Exception(
            f"Unhandled exception creating file [{output_file}]. Exception detail: {exc}"
        )
