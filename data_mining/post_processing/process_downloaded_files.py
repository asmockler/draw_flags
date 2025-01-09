#!/usr/bin/python
"""
Process all the files that we downloaded.
"""

import json
import logging
from pathlib import Path

# import coloredlogs
from tqdm import tqdm
from utils import check_options, look_at_commons_usage

# coloredlogs.install()

# TODO(bjafek) make a constants.py instead of re-defining here.
DATA_DIR = Path("/home/bjafek/personal/draw_flags/data_mining/wikimedia-downloader/output")
POST_DIR = Path(
    "/home/bjafek/personal/draw_flags/data_mining/wikimedia-downloader/commons_verified"
)
POST_DIR.mkdir(exist_ok=True)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(
            "/home/bjafek/personal/draw_flags/data_mining/post_processing/commons_verified.log"
        ),
    ],
)


data = sorted(DATA_DIR.rglob("*.json"))
n_files = len(data)

for idx, path in tqdm(enumerate(data), total=n_files):
    post_process_name = POST_DIR / path.relative_to(DATA_DIR)
    if post_process_name.is_file():
        continue

    # TODO(bjafek) at this point this deserves to be its own dataclass
    #  since it's starting to do a bunch of stuff
    with path.open() as f:
        single_row = json.load(f)

    single_row["verified_page"] = None
    single_row["verified_url"] = None

    single_row = look_at_commons_usage(single_row, idx)
    if single_row["verified_page"] is None:
        # Trust the commons usage first, but if that doesn't work
        #  do some guessing based on the name.
        single_row = check_options(single_row, idx)

    post_process_name.parent.mkdir(exist_ok=True, parents=True)
    with post_process_name.open("w") as f:
        json.dump(single_row, f, indent=1)
