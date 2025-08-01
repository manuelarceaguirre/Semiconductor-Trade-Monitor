1.2. USITC DataWeb API – Rate Limiting Mitigation Strategy
Problem Statement: The USITC DataWeb API is intended to provide detailed U.S. import/export data (including 10-digit HTS codes), but our attempts result in HTTP 429 errors (“Too Many Requests”) immediately. This suggests we are hitting a rate limit or access restriction right away, preventing any data retrieval. We need to understand the API’s rate limiting and implement strategies to successfully pull data without triggering 429 errors. Official Rate Limiting Policy: The USITC DataWeb API documentation does not explicitly publish a numeric rate limit, but the 429 response itself indicates the server is rate limiting our requests
developer.mozilla.org
. In practice, users have noted that making even a single request without proper pacing or authentication can trigger a 429 if the API suspects a flood (possibly if not authenticated). Typically, APIs impose limits like X requests per second or per minute. The USITC API likely has a very low threshold for unauthenticated or improperly authenticated requests – possibly as low as a few requests per minute. The 429 on the first attempt could indicate that no requests are allowed without an API key/token, or that our usage must be serialized carefully. The DataWeb FAQ implies using the API requires login (and presumably an API token)
usitc.gov
. We should ensure we use a valid API token and then respect any suggested pacing. Since no exact numbers are published, a safe strategy is to assume we might be limited to perhaps ~1 request per second or a handful per minute initially. We will implement a conservative throttle (e.g. 1 request per 2 seconds to start, with backoff on 429). Many APIs include a Retry-After header in 429 responses indicating how long to wait
blog.hubspot.com
; we will check for that in the USITC response. In absence of guidance, we will design our code to exponentially back off and try again after a delay when a 429 is encountered (see Resilient Code below). The bottom line is we must slow down our request rate to what the API permits. Authentication & Access Tiers: Using the USITC DataWeb API requires an account and an API access token. The DataWeb FAQ states that to use the API, one must log in (via Login.gov) and obtain a token
usitc.gov
usitc.gov
. We have an example token (the string starting with eyJhbGci... in our notes), which is a JWT. We should ensure this token is valid (tokens may expire or need renewal after some time or each session). It appears that having a token (which we include as a Bearer token in the headers) is mandatory – otherwise the API might immediately reject requests (possibly causing the instant 429 if treated as “no token” scenario). There do not seem to be explicit “tiers” of access beyond the requirement that you register (for free) for DataWeb. All users likely face the same base limits. Using the token properly should grant us normal access, which might raise the threshold for rate limiting. The token is obtainable from the DataWeb web interface under the “API” tab when logged in
usitc.gov
usitc.gov
. The process is:
Register/Log in to DataWeb via login.gov (multifactor auth).
Navigate to the API section and copy the provided API token (it’s a long JWT string).
Include this token in requests: specifically, in the HTTP header as Authorization: Bearer <token>
usitc.gov
. Also set Content-Type: application/json for POST requests as required.
We have an example from the documentation illustrating how to set up the headers in Python
usitc.gov
. With a valid token, the API should allow a reasonable number of requests before rate limiting. It’s possible the token has an expiration (if so, one might re-auth or fetch a new token via the web interface periodically – the documentation doesn’t mention an auto-refresh, so likely the token remains valid until manually revoked). Bulk Data Alternatives: Given the rate limits, it’s worth noting alternative ways to obtain the U.S. trade data:
USITC DataWeb Bulk Download: The DataWeb interface itself allows downloading data (Excel/CSV) for large queries (up to 300,000 rows) via the web UI
usitc.gov
. This is not exactly an API, but if we need a one-off data dump (e.g. all 2022 semiconductor exports), using the UI might be an option (with manual steps or automation via a headless browser). However, 300k rows might not accommodate all detail (depending on query scope), but it’s quite large.
U.S. Census Bureau Trade API: The U.S. Census offers a free API for international trade data (part of their data platform). It provides monthly trade values by country and commodity (though often at HS chapter or HS4 level, not full 10-digit, except for certain datasets). However, Census has specific endpoints for HS-based trade. In fact, Census’s API includes the Monthly International Trade datasets, which have detailed HS data by country (up to HS6 or 10 for some categories)
census.gov
census.gov
. The Census API is free with up to 500 calls/day without a key (and higher with a free API key)
census.gov
. We can leverage this for U.S. trade as a backup. For example, we could query the Census API for “U.S. imports from Taiwan of HS854232 in 2023” directly. The drawback is that the Census API might only give data at the 6-digit level for commodity (the Census does have 10-digit data but typically in their USA Trade Online which is the DataWeb we are already using). Still, for many purposes HS6 data might suffice.
Bulk data portals: The UN Comtrade itself includes U.S. data (the UN receives U.S. trade stats at least at summary levels). For example, UN Comtrade has U.S. trade by HS (maybe not full 10-digit, but 6-digit). If 6-digit granularity is acceptable, Comtrade could serve the U.S. flows as well, avoiding USITC limitations. We have to be cautious: sometimes Comtrade values for US may be slightly different due to CIF/FOB differences or revisions, but it’s a viable alternative if USITC API proves too restrictive.
Direct download from data.gov or ITC: On data.gov, annual trade datasets (e.g. all U.S. exports by HS10 by country) might be available for bulk download. For instance, the Census publishes some historical data files. If such exist (e.g. as CSVs for each year), we could fetch those in lieu of many API calls. We should investigate data.gov or Census’s bulk download files.
In summary, while we prefer the API for automation, if it remains problematic, we can combine approaches: use the Census API or Comtrade for U.S. data at HS6 (for immediate needs), and in parallel resolve the USITC API for the full HTS10 detail in the longer run. USITC also sometimes provides a flat file or FTP for tariff data, but for trade data their main offering is DataWeb or the API. Verified HTS Codes (10-digit) for Semiconductors: The U.S. Harmonized Tariff Schedule (HTS) provides very granular 10-digit codes for semiconductor products. We need to identify the most relevant active HTS codes for modern semiconductors – including memory, processors, and manufacturing equipment – to query in DataWeb (or for mapping to HS codes). Based on the 2023 HTS and industry relevance, key codes include:
854232**.** (Memory chips) – In the U.S. HTS, 854232 is broken down into multiple 10-digit lines by memory type and capacity. For example, the HTS (2022 update) introduced lines for DRAMs by density: e.g. 8542320036 for DRAM >1 Gigabit, and other lines for <=512 Mbit, etc
trademo.com
. It also has lines for non-volatile memory: SRAM (e.g. 8542320041), EEPROM (8542320051), EPROM (8542320061), and “Other” memory (8542320071)
trademo.com
. For our purposes, all these fall under HS 854232, but if using the USITC API we might pull specific lines. The most “active” HTS codes here would be those for DRAM and NAND Flash (likely under “Other” if not explicitly listed). We will likely query the aggregate 854232 (which DataWeb can provide as a total) or specific sub-codes if needed. The rationale is to capture the bulk of memory trade (DRAM and flash are huge by value).
854231**.** (Processors/controllers) – The HTS splits this into many lines reflecting modern chip categories. As of 2023, U.S. export/import codes under 854231 include:
8542310015, 8542310020, 8542310025, 8542310030 – which distinguished microprocessor MCUs by bit length (8-bit, 16-bit, 32-bit, other) – though these might have been restructured in recent revisions.
8542310035 (Digital signal processors), 8542310040 (Graphics processing units, GPUs), 8542310045 (Central processing units, CPUs)
trademo.com
,
8542310055 (Complex programmable logic devices), 8542310060 (Field-programmable gate arrays, FPGAs)
trademo.com
,
8542310065, 8542310070, 8542310075 – which are additional “Other” categories in that sequence
trademo.com
.
Essentially, the U.S. has created separate codes for CPUs, GPUs, DSPs, FPGAs, etc under 854231. All are active (these were introduced in HTS 2022). For data collection, if we want fine detail, we could retrieve each, but summing them gives total “processors and controllers.” Initially, we might just query total 854231 (DataWeb allows summing by category). However, identifying these specific lines is useful: for instance, if we want to specifically track GPU exports vs CPU exports, we have the codes to do so. For completeness, the most relevant are CPUs (8542310045) and GPUs (8542310040) as they represent large value streams, as well as FPGAs (0060) which are strategically important. We will include all if possible.
854233 (Amplifier ICs) – U.S. HTS might not further split this (or might have generic lines). This is a smaller segment. We can include the total for completeness.
854239 (Other ICs) – The HTS likely has some lines for “other” ICs. This could include sensor ICs, mixed-signal, etc. It’s broad. We’ll capture the total here as well.
Semiconductor Manufacturing Equipment: The HS code for these is 8486. Specifically:
8486.20.00.00 – “Machines and apparatus for the manufacture of semiconductor devices or of electronic integrated circuits”
hts.usitc.gov
. This covers wafer fabrication equipment (lithography machines, etchers, deposition, etc.).
8486.30.00.00 – “Machines and apparatus for the manufacture of flat panel displays” (less relevant to chips, but adjacent).
8486.40.00.00 – “Machines and apparatus for the manufacture or repair of masks and reticles”
hts.usitc.gov
 (mask-making equipment for lithography).
8486.90.00.00 – Parts and accessories for the above machines
tariffnumber.com
.
For our project’s scope of “all equipment,” 8486200000 is the main code capturing semiconductor fabrication equipment. For example, lithography systems exported by the Netherlands fall here. The U.S. also uses this code for any export of fab tools. We will track 848620 (and possibly 848640 for mask equipment, if needed). 8486900000 (parts) is also significant (spare parts and subassemblies can be a large trade volume). We should include 848690 as it’s often reported when tools are shipped in pieces or for parts supply chains. Additionally, certain testing and measuring equipment for semiconductors might appear under other chapters (e.g., HS 9030/9031 for semiconductor testing instruments). For example, 9030.82 covers semiconductor wafer testers. If we aim for completeness in “equipment,” we may consider:
HS 903082 – “Instruments for measuring or checking semiconductor wafers or devices” (this is an HS code that covers semiconductor test equipment).
HS 903141/903149 – optical instruments for inspecting masks/wafers, etc.
However, these might be too detailed; a lot of such equipment trade may already fall under 8486 or be relatively smaller. As a starting point, 8486 series will cover the core manufacturing tools.
Other relevant HTS: We should also note machines for semiconductor assembly (bonders, etc.) might be classified in 8486 as well (or possibly 8479 if not specified, but since 8486 is broad “for semiconductor devices”, it likely covers them). The HTS codes we’ve identified should cover “all equipment” as requested.
To summarize, our priority HTS10 codes to query from DataWeb will be:
854231 series (especially .0040 GPUs, .0045 CPUs, .0060 FPGAs, etc. – or total 854231 if summation possible),
854232 series (especially DRAM and Flash related lines – or total 854232),
854239 (others),
8486200000 (fab machines), 8486900000 (parts),
possibly 9030820000 (test equipment) if needed.
We will use the USITC’s HTS Search tool to double-check these codes’ descriptions and ensure they are active in 2023 (they are, as they appear in the current HTS and were used in recent trade filings
trademo.com
hts.usitc.gov
). The codes listed align with what the USITC DataWeb’s interface provides for semiconductor-related queries. Resilient Code Strategy (Rate-Limit Handling): To safely navigate the USITC API’s rate limits, we will implement exponential backoff and error handling. Using a Python library like tenacity or backoff simplifies this. For example, using tenacity:
python
Copy
from tenacity import retry, wait_exponential, stop_after_attempt
import requests, time

@retry(wait=wait_exponential(multiplier=1, min=1, max=60), stop=stop_after_attempt(5))
def get_with_backoff(url, headers, payload):
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 429:
        # Trigger retry with exponential wait
        raise Exception("Rate limit hit, retrying...")
    return response

# Usage:
headers = {"Authorization": "Bearer <TOKEN>", "Content-Type": "application/json"}
data_request = { ... }  # JSON payload for the query
try:
    resp = get_with_backoff("https://datawebws.usitc.gov/api/v2/report2/runReport", headers, data_request)
except Exception as e:
    print("Failed after retries:", e)
In this snippet, the retry decorator catches the 429, waits (1s, 2s, 4s, etc.) and retries up to 5 attempts
blog.hubspot.com
. Alternatively, without external libraries, we could implement manually:
python
Copy
max_retries = 5
delay = 1  # start with 1 second
for attempt in range(max_retries):
    res = requests.post(url, headers=headers, json=requestData)
    if res.status_code == 429:
        print("Rate limit hit. Waiting", delay, "seconds")
        time.sleep(delay)
        delay *= 2  # exponential backoff
        continue
    else:
        break
This ensures we respect the API’s pacing. Additionally, we will incorporate logic to detect the Retry-After header if provided and wait accordingly. By serializing requests and using backoff, we can avoid hammering the server. We will also use the ratelimit library to enforce a delay between calls globally – for instance, setting a decorator to allow only e.g. 1 request per 2 seconds. In practice, once we get the first successful response, we’ll have a sense of allowed throughput. If the API still responds with 429 even with delays, we might reduce frequency further (or contact USITC support if an official limit is documented). The code strategies above provide a robust way to automatically slow down when needed and are critical for long-running ETL jobs aggregating a lot of data.
