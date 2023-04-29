from datetime import timedelta
from typing import Any, Optional, Tuple, Union

import requests_cache

default_req_cache_dir = ".cache"


def get_req_session(
    cache_dir: str = default_req_cache_dir,
    session_name: str = "default_req_cache",
    expire_after: Union[int, timedelta] = timedelta(minutes=15),
    allowable_codes: list[int] = [200, 400],
) -> requests_cache.CachedSession:
    """Create & return a requests-cache CachedSession.

    CachedSession is an object for caching requests.
    """
    if cache_dir:
        _cache = f"{cache_dir}/{session_name}"
    else:
        _cache = session_name

    print(f"[DEBUG] Creating cache: {_cache}")
    # log.debug(f"Creating cache: {_cache}")

    ## Create cached request session
    session = requests_cache.CachedSession(
        cache_name=_cache,
        expire_after=expire_after,
        cache_control=True,
        allowable_codes=allowable_codes,
        stale_if_error=True,
    )

    return session
