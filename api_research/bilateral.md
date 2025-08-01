Optimal Query Parameters: The UN Comtrade API requires specifying several parameters to filter data properly. Key parameters include:
reporter (r): The reporting country’s code (numeric or ISO). Must be a specific country code for bilateral flows; using r=all is not allowed in combination with p=all
statalist.org
. For example, r=156 for China (156 is China’s numeric UN code
stevekwong.com
). We will use numeric country codes (UN M49 codes) for reporter and partner.
partner (p): The partner country’s code. Should be a specific country or 0/World for aggregate world data. For bilateral flows, we set a specific partner code (e.g. p=842 for USA) and avoid using all for both reporter and partner simultaneously
statalist.org
.
tradeflow (rg): The trade flow direction code. In Comtrade, rg=1 represents imports (Reporter’s imports), and rg=2 represents exports
stevekwong.com
. Using rg=all (both flows) in one query is possible, but splitting into separate import/export queries is often necessary for bilateral detail (to stay within result limits).
commodity code (cc): The product code or aggregate code. For specific semiconductor products, we use detailed HS codes (6-digit). For example, cc=854232 to query “electronic integrated circuits – memory” category. Comtrade also supports special codes like TOTAL or aggregates (AG6 for all HS6)
stevekwong.com
, but to get specific product flows we will use the actual HS codes.
Other parameters:
type=C for commodity trade (goods)
stevekwong.com
,
freq=A or freq=M for annual or monthly data (we can use annual for aggregate 2023 values or monthly for time series),
px=HS for HS classification (Comtrade defaults to the latest HS revision; we can specify HS to let Comtrade handle the appropriate revision for each year),
ps=2023 (period, e.g. 2023 for annual, or 202301 for monthly Jan 2023, etc. We can retrieve one year or a range of years). We will query recent years 2023 and 2024.
fmt=json or csv for output format (JSON for programmatic processing).
Each parameter’s role: specifying a single reporter and single partner is crucial to get bilateral data. For example, to get Taiwan’s exports to the USA for HS 854232 in 2022, we would set r=490 (Taiwan’s code, see below), p=842 (USA), rg=2 (export), cc=854232, ps=2022, etc. This ensures we get a bilateral flow instead of a world total. (Comtrade will reject overly broad queries where both reporter and partner are “all”
statalist.org
.) Validated HS Codes for Semiconductors: We will focus on key 6-digit HS codes in Chapter 85 that represent semiconductors. The primary codes of interest (HS 2017/2022 nomenclature) are in the 8542 family (Electronic integrated circuits):
854231 – Electronic integrated circuits: Processors and controllers, whether or not combined with other circuits
trademo.com
. This covers microprocessors, CPUs, microcontrollers, etc. Many countries report data at this level. If data for sub-codes is sparse, we may aggregate at 854231 (or even 8542) to capture total “logic” ICs. Notably, the U.S. HTS splits this into several 10-digit codes (e.g. separate lines for CPUs, GPUs, DSPs, FPGAs, etc.
trademo.com
trademo.com
), but at the 6-digit level 854231 includes all these. We expect decent coverage since “processors and controllers” is a broad category.
854232 – Electronic integrated circuits: Memory (e.g. DRAM, flash memory). This code covers semiconductor memory devices. Many countries report it (it’s a major trade category for Korea, Taiwan, etc.). Some nations further split it (e.g. by memory type or capacity). For instance, the U.S. distinguishes by DRAM capacity and memory type in 10-digit codes
trademo.com
. At 6 digits (854232) we capture total memory ICs, which should be well-reported. If granular sub-codes are missing for some reporters, we can use this aggregate. (HS Note: 854232 includes goods specified in Note 12(b) to Chapter 85, e.g. various memory chips. The UK HTS example lists sub-codes like 8542321030 for DRAMs
eximguru.com
, confirming this category covers DRAM.)
854233 – Electronic integrated circuits: Amplifiers. This is a smaller category (amplifier ICs). Data might be sparse for some countries. If so, we might combine it with “other” below.
854239 – Electronic integrated circuits: Other (those not elsewhere specified in 854231–854233). This catches all remaining ICs (analog ICs, mixed-signal, etc.). It’s quite significant in trade if countries don’t classify a chip as a processor, memory, or amplifier. We will include 854239 to ensure we capture all integrated circuits trade. Some countries might report most IC exports under this “other” category, so it has high data availability by design.
Rationale: These 8542.x codes cover integrated circuits which form the bulk of semiconductor trade value. If we find that any specific sub-category (e.g. 854233) has patchy data for certain reporters, we will fall back to a higher-level code. For example, if a country only reports total IC exports (8542 aggregate) without distinguishing subtypes, we would use the aggregate to get that country’s flows
stevekwong.com
. Using broader codes ensures we don’t miss data just because of reporting differences. Our priority, however, is to use the specific 6-digit codes (854231/32/33/39) for granularity, since these are standard across countries. Additionally, we acknowledge there are other semiconductor-related codes:
854121, 854129, 8541 etc. (discrete semiconductors like transistors, diodes). These are also part of semiconductors. While our focus is on integrated circuits, we might include these if needed (they are usually smaller in value but still relevant). For instance, 854129 covers transistor devices other than bipolar, etc. However, to limit scope, we may initially concentrate on the integrated circuits (8542 series) which constitute the majority of trade value.
8486 (Machines and apparatus for the manufacture of semiconductors) – see below for equipment codes.
Verified Country Codes: UN Comtrade uses numeric country codes (UN M49 codes) for reporters and partners in the API. We will use the following numeric codes for key trading nations in our queries (and map them to country names/ISO3 in our output):
United States of America – code 842 (USA as reporter in recent data)
rpubs.com
. (Note: The US code appears as 842 in Comtrade for current data, corresponding to ISO numeric 840; historically 841/842 have been used for US including territories
comtradeapi.un.org
. We will use 842.)
China – code 156
stevekwong.com
.
Taiwan (Chinese Taipei) – code 490. Taiwan is not listed by name in Comtrade; it is reported under “Other Asia, nes”. The artificial code 490 represents Taiwan’s trade in Comtrade data
groups.google.com
cepii.fr
. We will use reporter=490 (or partner=490) to capture Taiwan’s trade via this “Other Asia, nes” designation.
South Korea (Republic of Korea) – code 410.
Japan – code 392.
Netherlands – code 528.
Germany – code 276.
Singapore – code 702.
Malaysia – code 458.
These numeric codes can be confirmed via Comtrade’s reference data or sources like the World Bank WITS country list. For example, WITS shows “Country Code: 490” for “Other Asia, nes” (Taiwan)
wits.worldbank.org
. We have verified each key country’s code matches the UN M49 standard or Comtrade’s internal list. (If needed, Comtrade’s API provides JSON lists of reporter and partner codes
docs.ropensci.org
.) Executable Code Example: Below is a Python requests example that queries the UN Comtrade API for a bilateral semiconductor flow – specifically, Taiwan’s exports to the USA of memory chips (HS 854232) in 2022:
python
Copy
import requests

# Define query parameters for Comtrade API
params = {
    "max": 50000,             # max records to return (set high to ensure full data)
    "type": "C",              # trade type: Commodities (goods)
    "freq": "A",              # frequency: Annual data
    "px": "HS",               # classification: HS codes
    "ps": "2022",             # period: year 2022
    "r": "490",               # reporter: 490 = Other Asia, nes (Taiwan)
    "p": "842",               # partner: 842 = United States
    "rg": "2",                # trade flow: 2 = exports (reporter -> partner)
    "cc": "854232",           # commodity code: HS 854232 (memory circuits)
    "fmt": "json"             # output format: JSON
}

url = "https://comtrade.un.org/api/get"
response = requests.get(url, params=params)
data = response.json()
print(data["dataset"][0]["TradeValue"])
# This would print the trade value (in USD) of Taiwan's exports of HS854232 to USA in 2022
This query uses the correct parameters for a bilateral flow. It should return a JSON with Taiwan’s export value to the US for HS 854232 in 2022 (along with any metadata). In general, to build the full dataset, we would iterate over combinations of reporter, partner, year, and commodity code as needed. (Note: Taiwan is handled via “Other Asia, nes” in Comtrade
groups.google.com
. In this example, r=490 effectively gives Taiwan’s data. If we needed Taiwan as a partner in other countries’ reports, we would use p=490.)
