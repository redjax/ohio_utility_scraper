"""Spider controller.

The main script imports spiders and runs them with CrawlerProcess.
"""
import stackprinter

stackprinter.set_excepthook(style="darkbg2")

import scrapy
from core.config import logging_settings
from core.database import Base, SessionLocal, engine, get_db
from core.logging.logger import default_fmt, get_logger
from models import provider_models
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings
from sqlalchemy import select
from twisted.internet import reactor

log = get_logger(__name__, level=logging_settings.LOG_LEVEL)

## Import spiders
from ohioenergy.spiders.ohioenergyproviders import OhioenergyprovidersSpider

if __name__ == "__main__":
    log_settings = configure_logging({"LOG_FORMAT": default_fmt})
    settings = get_project_settings()

    ## Create runner for crawlers
    runner = CrawlerRunner(settings)
    runner.crawl(OhioenergyprovidersSpider)

    ## Join spiders
    deferred = runner.join()

    ## Add runners and a twisted reactor.stop() to runner
    deferred.addBoth(lambda _: reactor.stop())

    ## Run crawlers
    reactor.run()
