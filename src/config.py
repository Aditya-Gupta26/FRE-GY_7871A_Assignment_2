"""Shared paths and constants for the FOMC communications project."""
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_RAW = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
DATA_RAW.mkdir(parents=True, exist_ok=True)
DATA_PROCESSED.mkdir(parents=True, exist_ok=True)

FED_BASE = "https://www.federalreserve.gov"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (NYU FRE-GY 7871 coursework research script; contact: ag11023@nyu.edu)"
}
REQUEST_DELAY_SECONDS = 0.5  # politeness delay between requests

# Regular scheduled FOMC meeting end-dates (YYYYMMDD), verified directly against
# federalreserve.gov/monetarypolicy/fomchistorical{2018,2019,2020}.htm and
# federalreserve.gov/monetarypolicy/fomccalendars.htm (2021-2026) on 2026-09-12.
FOMC_MEETING_DATES = [
    # 2018 (Powell's first meeting as Chair: 2018-02-05; first FOMC meeting under him: Mar 2018)
    "20180131", "20180321", "20180502", "20180613",
    "20180801", "20180926", "20181108", "20181219",
    # 2019
    "20190130", "20190320", "20190501", "20190619",
    "20190731", "20190918", "20191030", "20191211",
    # 2020 (regular scheduled meetings)
    "20200129", "20200315", "20200429", "20200610",
    "20200729", "20200916", "20201105", "20201216",
    # 2021
    "20210127", "20210317", "20210428", "20210616",
    "20210728", "20210922", "20211103", "20211215",
    # 2022
    "20220126", "20220316", "20220504", "20220615",
    "20220727", "20220921", "20221102", "20221214",
    # 2023
    "20230201", "20230322", "20230503", "20230614",
    "20230726", "20230920", "20231101", "20231213",
    # 2024
    "20240131", "20240320", "20240501", "20240612",
    "20240731", "20240918", "20241107", "20241218",
    # 2025
    "20250129", "20250319", "20250507", "20250618",
    "20250730", "20250917", "20251029", "20251210",
    # 2026 (through the last completed meeting before the Sept 15-16 meeting we forecast)
    "20260128", "20260318", "20260429", "20260617", "20260729",
]

# 2020 unscheduled/special monetary-policy statements not tied to a regular 8x/year
# meeting (emergency COVID actions + the Aug 2020 framework announcement). These have
# statements but not all have minutes/press conferences - verified individually.
FOMC_SPECIAL_STATEMENT_DATES = ["20200303", "20200323", "20200331", "20200827"]

# Chair tenure boundaries (public record). Powell was sworn in as Chair 2018-02-05.
# His confirmed term ended 2026-05-15 (he then served briefly as "chair pro tempore").
# Warsh was sworn in as Chair 2026-05-22. Speeches/testimony are attributed to
# whoever was actually Chair on that date - e.g. a Powell speech after 2026-05-15 is
# NOT a Chair speech (he's back to being a plain Governor) and must be excluded.
POWELL_SWORN_IN_DATE = "20180205"
POWELL_LAST_DAY_AS_CHAIR = "20260515"
WARSH_SWORN_IN_DATE = "20260522"

FORECAST_MEETING_DATE = "20260915"  # the meeting we are forecasting (Sept 15-16, 2026)
