# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import json
from decimal import Decimal
from pathlib import Path
from typing import Union

import msgpack
from core.config import logging_settings
from core.database import SessionLocal, generate_uuid, generate_uuid_str
from core.logging.logger import get_logger
from itemadapter import ItemAdapter
from lib.time_utils import get_date, get_hour, get_ts
from models import provider_models
from scrapy.http.response.html import HtmlResponse
from sqlalchemy.exc import IntegrityError

from ohioenergy.items import OhioenergyItem

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


def serialize_providers(
    providers: list[dict[str, Union[str, float, Decimal, int, bool, None]]] = None
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
    def process_item(self, item: OhioenergyItem, spider):
        pass


class OhioenergySerializePipeline:
    def process_item(self, item: OhioenergyItem, spider):
        item_dict = item.__dict__["_values"]
        # log.debug(f"Item dict ({type(item_dict)}): {item_dict}")

        providers_bytes = json.dumps(item_dict).encode("utf-8")
        # log.debug(f"Provider bytes ({type(providers_bytes)}): {providers_bytes}")

        # log.info(f"Serializing results.")
        serialize(
            input=providers_bytes,
            output_dir=f"providers/{get_date()}/{get_hour()}",
            filename=f"{get_ts()}_{item['name']}.msgpack",
        )


class OhioenergySavePipeline:
    """Save OhioenergyItem to database."""

    def process_item(self, item: OhioenergyItem, spider):
        """Process item, save to database."""
        if not item:
            raise ValueError("Missing item data")

        # log.debug(f"Item ({type(item)}: {item})")
        item_dict = item.__dict__["_values"]
        # log.debug(f"Item dict: {item_dict}")
        session = SessionLocal
        # log.debug(f"Session ({type(session)}): {session}")

        item_dict["id"] = generate_uuid_str()

        provider = provider_models.OhioenergyProvider(**item_dict)
        log.debug(f"Provider: {provider}")

        for _item in provider.__dict__:
            log.debug(f"Provider item ({type(_item)}): {_item}")

        with session as sess:
            try:
                result = sess.add(provider)
                log.debug(f"Provider add result: {result}")
            except IntegrityError as integrity_exc:
                raise IntegrityError(
                    f"Integrity error adding provider to session. Exception details: {integrity_exc}"
                )
            except Exception as exc:
                raise Exception(
                    f"Unhandled exception adding provider to session. Exception defailt: {exc}"
                )

            session.commit()
