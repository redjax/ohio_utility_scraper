# Ohio Energy Provider Comparison

[![pdm-managed](https://img.shields.io/badge/pdm-managed-blueviolet)](https://pdm.fming.dev)

Scrapes [Energy Choice Ohio](https://energychoice.ohio.gov/ApplesToApplesComparision.aspx)'s provider comparison tables.

- [ELECTRIC](https://energychoice.ohio.gov/ApplesToApplesComparision.aspx?Category=Electric&TerritoryId=6&RateCode=1)
- [GAS](https://energychoice.ohio.gov/ApplesToApplesComparision.aspx?Category=NaturalGas&TerritoryId=8&RateCode=1)

## Usage

### With PDM

- Setup environment
  - `$ pdm install`
- Run start script
  - `$ pdm start`

### Without PDM

- Create `venv`
  - `$ virtualenv .venv`
- Activate `venv`
  - Linux: `$ . .venv/bin/activate`
- Install requirements
  - `$ pip install -r requirements.txt`
- `cd` to app directory
  - `$ cd ohioenergy`
- Run crawler(s)
  - `$ python main.py`


## Notes

### Run Scrapy spiders from a Python script

#### Scrapy's CrawlerRunner, for running multiple crawlers

Utilized `twisted` for async crawls.

Example single crawler, using the `ohioenergy.spiders.ohioenergyproviders.OhioenergyprovidersSpider` spider:

```
from twisted.internet import reactor
from scrapy.crawler import CrawlerRunner

from ohioenergy.spiders.ohioenergyproviders import OhioenergyprovidersSpider

if __name__ == "__main__":
    
    configure_logging({"LOG_FORMAT": default_fmt})
    settings = get_project_settings()
    
    runner = CrawlerRunner(settings=settings)
    
    electric_providers = runner.crawl(OhioenergyprovidersSpider)
    
    ## Add runners and a twisted reactor.stop() to runner
    electric_providers.addBoth(lambda _: reactor.stop())
    
    ## Run crawlers
    reactor.run()

```

Example multiple crawlers, using hypothetical `Crawler1` and `Crawler2`:

```
from twisted.internet import reactor
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_projectsettings


class Spider1(scrapy.Spider):
    ...

class Spider2(scrapy.Spider):
    ...

if __name__ == "__main__":
    settings = get_project_settings()
    runner = CrawlerRunner(settings)

    ## Add spiders to runner
    runner.crawl(Spider1)
    runner.crawl(Spider2)

    ## Join crawlers
    crawl = runner.join()

    ## Set Twisted's reactor.stop()
    crawl.addBoth(lambda _: reactor.stop())

    ## Run crawler
    reactor.run()

```

#### Scrapy's CrawlerProcess

Use `scrapy.crawler.CrawlerProcess` to run spiders. Make sure to import spiders into the script.

Example using the `ohioenergy.spiders.ohioenergyproviders.OhioenergyprovidersSpider` spider:

```
## main.py

import scrapy
## Import CrawlerProcess
from scrapy.crawler import CrawlerProcess
## Import scrapy project's settings
from scrapy.utils.project import get_project_settings

## Import OhioenergyprovidersSpider
from ohioenergy.spiders.ohioenergyproviders import OhioenergyprovidersSpider

if __name__ == "__main__":
    
    ## Create CrawlerProcess object. Initialize with Scrapy project's settings
    process = CrawlerProcess(get_project_settings())
    
    ## Prepare crawl
    process.crawl(OhioenergyprovidersSpider)
    ## Start crawl
    process.start()

```