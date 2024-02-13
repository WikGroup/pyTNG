"""
Subprocess functions for use in scripting.
"""
import threading

import pandas as pd
import requests

from pyTNG.utility.utils import devLogger


def write_subhalos_to_sql(engine, table, url, mass_threshold, apikey, pbar):
    """

    Parameters
    ----------
    engine
    url
    mass_threshold

    Returns
    -------

    """
    devLogger.debug(f"Calling {url} [Thread={threading.current_thread().name}].")
    r = requests.get(url, headers={"api-key": apikey})
    r.raise_for_status()

    response_df = pd.DataFrame(r.json()["results"])
    n = len(response_df)
    if mass_threshold is not None:
        response_df = response_df.loc[:, response_df["mass_log_msun"] > mass_threshold]

    with threading.Lock():
        # lock out the thread to force readwrite to work correctly.
        response_df.to_sql(table, con=engine, if_exists="append", index=False)
        pbar.update(n=n)

    devLogger.debug(f"Wrote {len(response_df)} from {threading.current_thread().name}.")

    return len(response_df)
