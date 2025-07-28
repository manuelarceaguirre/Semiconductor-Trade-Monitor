# Product Requirements Document (PRD)

## Project Title

**HBM & Semiconductor Trade Monitor**

## Document Version

*Version 1.0 – 23 Jul 2025*

---

## 1. Executive Summary

The HBM & Semiconductor Trade Monitor is a web‑based analytics platform that provides investors, supply‑chain analysts, and semiconductor professionals with near‑real‑time visibility into global trade flows of high‑value semiconductor products (e.g., HBM memory, GPU/AI accelerators, and EUV lithography tools). It ingests publicly available customs data, harmonises HS‑codes, delivers interactive visualisations, anomaly alerts, and a programmatic API – filling the current market gap between generic trade‑data portals and expensive PDF‑bound research services.

---

## 2. Goals & Non‑Goals

### 2.1 Goals

1. **Actionable Insights** – Enable users to detect material shifts (≥ ±20 % MoM) in semiconductor supply chains within 48 hours of customs data release.
2. **Frictionless Exploration** – Provide charts, filters, and drill‑downs that require zero HS‑code knowledge.
3. **Developer‑Friendly** – Offer a REST/JSON API for quantitative analysts to automate models.
4. **Freemium Go‑To‑Market** – Deliver a usable free tier (limited HS‑codes & history) to drive awareness, while premium tiers unlock full data, alerts, and exports.

### 2.2 Non‑Goals

* Real‑time (< daily) shipment tracking at bill‑of‑lading level.
* Forecasting models (phase‑2 roadmap).
* Proprietary data sources that violate open‑data licences.

---

## 3. Problem Statement & Opportunity

*Investors and industry analysts cannot easily monitor vital semiconductor trade lanes without stitching together raw CSVs from multiple customs portals.* Existing solutions are either:

* **Generic trade dashboards** – Too broad, lacking semiconductor context.
* **Expensive research subscriptions** – Monthly spreadsheets, no API, limited interactivity.
  This product addresses the pain by packaging free customs data into a curated, always‑on monitor focused solely on semiconductor choke‑points.

---

## 4. Target Personas

| Persona                                | Primary Job‑To‑Be‑Done                      | Pain Points                          | Must‑Have Feature                  |
| -------------------------------------- | ------------------------------------------- | ------------------------------------ | ---------------------------------- |
| **Equity Analyst / Hedge Fund PM**     | Detect supply disruptions ahead of earnings | Slow, manual data pulls; no alerting | Email/SMS anomaly alerts           |
| **Fabless Ops / Supply‑Chain Manager** | Validate component lead‑time risks          | Data scattered across portals        | Country‑pair drill‑down charts     |
| **Government Policy Advisor**          | Monitor compliance with export controls     | Difficult to isolate dual‑use goods  | HS‑code bundles & sanction filters |
| **Data‑Science Quant**                 | Feed time‑series into models                | Manual scraping                      | REST API & CSV export              |

---

## 5. Competitive Landscape Snapshot

| Provider                         | Data Focus      | Interactivity | API                | Price    | Gap Our Product Fills             |
| -------------------------------- | --------------- | ------------- | ------------------ | -------- | --------------------------------- |
| SemiAnalysis (Import‑Export XLS) | Semi, monthly   | None          | No                 | \$\$\$   | No self‑serve; no alerts          |
| UN Comtrade Explorer             | All commodities | Basic GUI     | Yes (rate‑limited) | Free     | Not curated; no outlier detection |
| Panjiva (S\&P)                   | Bill‑of‑lading  | Dashboard     | Yes                | \$\$\$\$ | Generic; high cost                |

---

## 6. Detailed Requirements

### 6.1 Functional Requirements

| ID   | Requirement                                                                                                                           | Priority |
| ---- | ------------------------------------------------------------------------------------------------------------------------------------- | -------- |
| F‑01 | **Data Pipeline** – Automatically ingest monthly trade data from UN Comtrade, US DataWeb, Eurostat Comext, Taiwan MOF, Korea Customs. | P0       |
| F‑02 | **HS‑Code Curation** – Maintain a lookup table mapping semiconductor products to HS‑6 (and HS‑8/10 where available).                  | P0       |
| F‑03 | **Dashboard** – Interactive line/bar charts with selectors: commodity, origin, destination, value vs volume, date range.              | P0       |
| F‑04 | **Anomaly Engine** – Detect MoM and YoY deviations beyond configurable thresholds; surface in UI and via alerts.                      | P1       |
| F‑05 | **Email/Webhook Alerts** – Users set thresholds on commodity‑lane; system sends notifications.                                        | P1       |
| F‑06 | **REST API v1** – `/v1/series?commodity=HBM&origin=KOR&dest=TWN` returns JSON.                                                        | P1       |
| F‑07 | **Auth & Subscription** – Freemium model (OAuth, Stripe).                                                                             | P1       |
| F‑08 | **CSV/Excel Export** – Premium users download full dataset.                                                                           | P2       |
| F‑09 | **Admin UI** – Manage HS code catalogue, data integrity flags, user roles.                                                            | P2       |

### 6.2 Non‑Functional Requirements

| Category        | Target                                          |
| --------------- | ----------------------------------------------- |
| **Latency**     | Data available < 12 h after source publish.     |
| **Uptime**      | 99.5 % monthly.                                 |
| **Scalability** | Support 10 k API calls / day on MVP infra.      |
| **Security**    | HTTPS everywhere; OWASP top‑10 mitigations.     |
| **Compliance**  | Follow source‑data licences; GDPR & CCPA ready. |

---

## 7. Data Model & Sources

| Commodity           | HS‑6            | Extended Codes                                    | Primary Sources           |
| ------------------- | --------------- | ------------------------------------------------- | ------------------------- |
| HBM/DRAM/SRAM ICs   | 854232          | U.S. HTS 8542320010 (Static RAM); EU HS‑8 mapping | UN Comtrade, Taiwan MOF   |
| GPU/AI Accelerators | 854231 & 854239 | Split via partner country where possible          | UN Comtrade, U.S. DataWeb |
| Lithography Tools   | 848620          | 8486200010 (EUV) where available                  | UN Comtrade               |

**Schema (simplified)**

```sql
trade_flows (
  id            SERIAL PK,
  period        DATE,
  reporter_iso  CHAR(3),
  partner_iso   CHAR(3),
  hs6           CHAR(6),
  hs_extended   VARCHAR(12),
  value_usd     NUMERIC,
  quantity      NUMERIC,
  unit          VARCHAR(16),
  src_system    VARCHAR(16),
  load_time     TIMESTAMP
)
```

---

## 8. System Architecture (MVP)

1. **Ingestion Layer** – Python ETL scripts triggered by GitHub Actions nightly.
2. **Data Store** – PostgreSQL (Supabase) for structured data; S3 bucket for raw dumps.
3. **Backend API** – FastAPI (Python) container deployed on Fly.io.
4. **Dashboard** – Streamlit app served via Cloudflare tunnel.
5. **Alert Service** – Celery worker + PostgreSQL job queue; SendGrid for email.

---

## 9. User Journeys

### 9.1 Equity Analyst (Free Tier)

1. Lands on homepage → selects "HBM Memory" commodity → sees default chart Korea → Taiwan.
2. Toggles YoY view → notices spike → clicks “More details” → prompted to create free account for history back‑fill.

### 9.2 Premium Quant User

1. Auth via OAuth → navigates to API Docs → generates token.
2. Schedules `/v1/series` pull for GPU HS‑code across all reporters weekly.
3. Configures alert: “Notify when Korea exports of 848620 drop > 15 % MoM”.
4. Receives webhook → triggers trading model.

---

## 10. Success Metrics (MVP)

| Metric              | Target after 3 months                 |
| ------------------- | ------------------------------------- |
| Active free users   | ≥ 300                                 |
| Premium conversions | ≥ 10 paid seats                       |
| Alert engagement    | ≥ 50 % of premium users set ≥ 1 alert |
| Avg. query latency  | < 500 ms for cached request           |
| Data freshness SLA  | 90 % of loads < 12 h post‑publish     |

---

## 11. Milestones & Timeline

| Phase                                    | Duration | Deliverables                           |
| ---------------------------------------- | -------- | -------------------------------------- |
| **0**  – Planning & data validation      | 1 week   | HS‑code table, source API POCs         |
| **1**  – Core ETL + SQLite prototype     | 1 week   | Automated pull for 3 codes, CLI graphs |
| **2**  – Streamlit dashboard & hosted DB | 2 weeks  | Public beta with charts & filters      |
| **3**  – API & alerts                    | 2 weeks  | `/v1/series` endpoint, email alerts    |
| **4**  – Payments & paywall              | 1 week   | Stripe integration, tier gating        |
| **5**  – Hardening & launch              | 1 week   | Docs, monitoring, marketing site       |

*Total: 8 weeks part‑time (≈ 140 hrs).*

---

## 12. Risks & Mitigations

| Risk                         | Likelihood | Impact           | Mitigation                                                        |
| ---------------------------- | ---------- | ---------------- | ----------------------------------------------------------------- |
| Source API ratelimits change | Med        | Data gaps        | Cache raw dumps; implement back‑off; add mirror sources           |
| HS‑6 too coarse for HBM only | High       | Insight dilution | Note limitation; explore Panjiva HS‑10 upgrade as paid add‑on     |
| Revenue underperforms        | Med        | Sustainability   | Consulting add‑ons; sponsored research collaborations             |
| Legal licencing breach       | Low        | High             | Adhere to UN Comtrade Creative Commons licence; track provenance. |

---

---

## 14. Glossary

* **HBM** – High‑Bandwidth Memory.
* **HS code** – Harmonised Commodity Description and Coding System.
* **Reporter / Partner** – Country filing the trade data vs trading partner.
* **MoM / YoY** – Month‑over‑Month / Year‑over‑Year.

---
