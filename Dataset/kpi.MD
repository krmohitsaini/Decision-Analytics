# KPI Catalog for Synthetic Energy Customer Sites Data

This file describes KPIs that can be built from `synthetic_energy_customer_sites.csv`. The data is synthetic, but the KPI logic is designed for an energy retailer with business partners, sites, commodities, sales channels, renewals, churn, leakage, and digital adoption.

## Data Grain Reminder

Each row represents one site-level contract episode.

Use distinct counts carefully:

- Customer count: `COUNT(DISTINCT business_partner_id)`
- Site count: `COUNT(DISTINCT Site_id)`
- Contract episode count: `COUNT(*)`
- Active site count: `COUNT(DISTINCT Site_id WHERE drop_type = 'Active')`
- Active customer count: `COUNT(DISTINCT business_partner_id WHERE drop_type = 'Active')`

Business-partner-level fields are repeated across rows. For these fields, calculate KPIs at the distinct `business_partner_id` level to avoid double counting:

- `sign_up_date`
- `zipcode`
- `digital_status`
- `digital_start_date`
- `dob_status`

## Recommended Dashboard Placement

| Dashboard Area | Purpose | KPI Types |
| --- | --- | --- |
| Executive Summary | Fast health check for leadership | Customer base, active sites, churn, renewal, leakage, digital adoption, channel mix |
| Commercial Performance | Sales and renewal performance | Sales type, channel conversion proxy, renewal mix, agent/channel productivity |
| Retention and Churn Deep Dive | Contract outcomes and loss patterns | Churn rate, leakage rate, renewal outcomes, same-day drop, contract duration |
| Customer and Site Portfolio | Customer footprint and site distribution | Sites per customer, commodity mix, active/inactive portfolio, geographic distribution |
| Product and Plan Adoption | Plan enrollment and product behavior | AMB, evergreen, surge, commodity adoption |
| Digital Engagement | Website/app adoption | Digital penetration, digital start lag, digital behavior by channel and status |
| Agent and Channel Deep Dive | Field and sales operations | Agent productivity, channel mix, channel-specific churn, channel-specific renewals |
| Data Quality and Controls | Dataset quality and operational checks | Missing fields, invalid dates, inconsistent customer-level values |

## Executive Summary KPIs

These are the highest-value KPIs for a first dashboard page.

### Total Business Partners

Counts the total unique customers in the dataset.

Calculation:

```text
COUNT(DISTINCT business_partner_id)
```

Recommended view:

Single executive summary card.

### Total Sites

Counts total unique site IDs across all business partners.

Calculation:

```text
COUNT(DISTINCT Site_id)
```

Recommended view:

Single executive summary card.

### Total Contract Episodes

Counts all contract episodes. This will be higher than site count because a site can end and restart.

Calculation:

```text
COUNT(*)
```

Recommended view:

Executive summary card or supporting portfolio metric.

### Active Sites

Counts sites where the latest or current row is marked active.

Simple calculation:

```text
COUNT(DISTINCT Site_id WHERE drop_type = 'Active')
```

More robust calculation:

```text
For each Site_id, find the row with the latest site_contract_start_date.
Count distinct Site_id where that latest row has drop_type = 'Active'.
```

Recommended view:

Executive summary card.

### Active Business Partners

Counts business partners with at least one active site.

Calculation:

```text
COUNT(DISTINCT business_partner_id WHERE drop_type = 'Active')
```

Recommended view:

Executive summary card.

### Active Site Rate

Measures what share of unique sites are currently active.

Calculation:

```text
Active Sites / Total Sites
```

Recommended view:

Executive summary trend or KPI card.

### Churned Sites

Counts sites with a churn outcome.

Calculation:

```text
COUNT(DISTINCT Site_id WHERE drop_type = 'Churn')
```

Recommended view:

Executive summary card with trend.

### Churn Rate

Measures the share of closed contract episodes that ended in churn.

Calculation:

```text
COUNT(rows WHERE drop_type = 'Churn')
/ COUNT(rows WHERE drop_type <> 'Active')
```

Alternative site-level calculation:

```text
COUNT(DISTINCT Site_id WHERE latest non-active drop_type = 'Churn')
/ COUNT(DISTINCT Site_id WHERE latest row drop_type <> 'Active')
```

Recommended view:

Executive summary card. Use the episode-level version when analyzing contract outcomes and the site-level version when analyzing current portfolio loss.

### Renewal Rate

Measures how often closed contract episodes resulted in renewal-type outcomes.

Calculation:

```text
COUNT(rows WHERE drop_type IN ('Auto Renewal', 'Positive Renewal'))
/ COUNT(rows WHERE drop_type <> 'Active')
```

Recommended view:

Executive summary card.

### Positive Renewal Rate

Measures the share of closed contract episodes that ended in positive renewal.

Calculation:

```text
COUNT(rows WHERE drop_type = 'Positive Renewal')
/ COUNT(rows WHERE drop_type <> 'Active')
```

Recommended view:

Executive summary card or commercial performance page.

### Leakage Rate

Measures contracts that ended immediately or very shortly after starting.

Calculation:

```text
COUNT(rows WHERE drop_type = 'Leakage')
/ COUNT(*)
```

Alternative closed-episode calculation:

```text
COUNT(rows WHERE drop_type = 'Leakage')
/ COUNT(rows WHERE drop_type <> 'Active')
```

Recommended view:

Executive summary card and retention deep dive.

### Digital Adoption Rate

Measures the share of unique business partners using the website or app.

Calculation:

```text
COUNT(DISTINCT business_partner_id WHERE digital_status = 'true')
/ COUNT(DISTINCT business_partner_id)
```

Recommended view:

Executive summary card.

### Average Sites per Business Partner

Measures the average footprint per customer.

Calculation:

```text
COUNT(DISTINCT Site_id) / COUNT(DISTINCT business_partner_id)
```

Recommended view:

Executive summary supporting KPI.

## Commercial Performance KPIs

These KPIs help explain sales mix, renewal mix, and acquisition behavior.

### New Organic Sales

Counts contract episodes tagged as organic.

Calculation:

```text
COUNT(rows WHERE sales_type = 'Organic')
```

Recommended view:

Commercial performance dashboard.

### Organic Sales Share

Measures the share of contract episodes sourced organically.

Calculation:

```text
COUNT(rows WHERE sales_type = 'Organic') / COUNT(*)
```

Recommended view:

Commercial performance dashboard.

### Auto Renewal Sales

Counts episodes tagged as auto renewal sales.

Calculation:

```text
COUNT(rows WHERE sales_type = 'Auto Renewal')
```

Recommended view:

Commercial performance dashboard.

### Positive Renewal Sales

Counts episodes tagged as positive renewal sales.

Calculation:

```text
COUNT(rows WHERE sales_type = 'Positive Renewal')
```

Recommended view:

Commercial performance dashboard.

### TOS Sales

Counts episodes tagged as TOS sales.

Calculation:

```text
COUNT(rows WHERE sales_type = 'TOS')
```

Recommended view:

Commercial performance dashboard.

### Sales Mix by Type

Shows contract episode distribution across sales types.

Calculation:

```text
COUNT(rows by sales_type) / COUNT(*)
```

Recommended view:

Stacked bar chart or donut chart on commercial performance page.

### Channel Sales Volume

Counts contract episodes by sales channel.

Calculation:

```text
COUNT(rows by channel)
```

Recommended view:

Commercial performance and channel deep dive.

### Channel Mix

Shows each channel's share of all contract episodes.

Calculation:

```text
COUNT(rows by channel) / COUNT(*)
```

Recommended view:

Executive summary if limited to top channels. Full version belongs in channel deep dive.

### Digital Channel Share

Measures the share of sales made through the `Digital` channel.

Calculation:

```text
COUNT(rows WHERE channel = 'Digital') / COUNT(*)
```

Recommended view:

Executive summary or digital engagement dashboard.

### Renewal Outcome Mix

Shows how closed episodes are distributed across renewal and non-renewal outcomes.

Calculation:

```text
COUNT(rows by drop_type WHERE drop_type <> 'Active')
/ COUNT(rows WHERE drop_type <> 'Active')
```

Recommended view:

Commercial performance and retention deep dive.

## Retention and Churn Deep Dive KPIs

These KPIs help understand contract outcomes, early losses, and site restarts.

### Closed Episodes

Counts all contract episodes that are no longer active.

Calculation:

```text
COUNT(rows WHERE drop_type <> 'Active')
```

Recommended view:

Retention deep dive.

### Drop Type Mix

Shows the distribution of outcomes across all rows or closed rows.

Calculation:

```text
COUNT(rows by drop_type) / COUNT(*)
```

Closed-only version:

```text
COUNT(rows by drop_type WHERE drop_type <> 'Active')
/ COUNT(rows WHERE drop_type <> 'Active')
```

Recommended view:

Executive summary for high-level view. Detailed breakdown belongs in retention deep dive.

### Same-Day Drop Count

Counts contract episodes where start and end date are the same.

Calculation:

```text
COUNT(rows WHERE site_contract_start_date = site_contract_end_date)
```

Recommended view:

Retention deep dive.

### Same-Day Drop Rate

Measures the share of contract episodes that ended on the start date.

Calculation:

```text
COUNT(rows WHERE site_contract_start_date = site_contract_end_date)
/ COUNT(*)
```

Recommended view:

Retention deep dive.

### Leakage Within Five Days

Counts leakage rows based on the date rule, regardless of tagging.

Calculation:

```text
COUNT(rows WHERE DATEDIFF(site_contract_end_date, site_contract_start_date) BETWEEN 0 AND 5)
```

Recommended view:

Retention deep dive and data quality control.

### Tagged Leakage Rate

Measures rows explicitly tagged as leakage.

Calculation:

```text
COUNT(rows WHERE drop_type = 'Leakage') / COUNT(*)
```

Recommended view:

Executive summary and retention deep dive.

### Average Contract Duration

Measures average days between contract start and end.

Calculation:

```text
AVG(DATEDIFF(site_contract_end_date, site_contract_start_date))
```

Recommended view:

Retention deep dive.

### Average Closed Contract Duration

Measures average completed contract length, excluding active rows.

Calculation:

```text
AVG(DATEDIFF(site_contract_end_date, site_contract_start_date)
    WHERE drop_type <> 'Active')
```

Recommended view:

Retention deep dive.

### Median Closed Contract Duration

Measures the median completed contract length.

Calculation:

```text
MEDIAN(DATEDIFF(site_contract_end_date, site_contract_start_date)
       WHERE drop_type <> 'Active')
```

Recommended view:

Retention deep dive.

### Restarted Sites

Counts sites with more than one contract episode.

Calculation:

```text
COUNT(DISTINCT Site_id WHERE COUNT(rows per Site_id) > 1)
```

Recommended view:

Retention deep dive and customer/site portfolio.

### Site Restart Rate

Measures the share of sites that restarted after a previous contract episode.

Calculation:

```text
Restarted Sites / Total Sites
```

Recommended view:

Retention deep dive.

### Average Episodes per Site

Measures how many contract episodes each site has on average.

Calculation:

```text
COUNT(*) / COUNT(DISTINCT Site_id)
```

Recommended view:

Retention deep dive.

### Churn by Commodity

Measures churn rate for each commodity type.

Calculation:

```text
COUNT(rows WHERE drop_type = 'Churn' GROUP BY commodity_type)
/ COUNT(rows WHERE drop_type <> 'Active' GROUP BY commodity_type)
```

Recommended view:

Retention deep dive.

### Churn by Channel

Measures churn rate for each sales channel.

Calculation:

```text
COUNT(rows WHERE drop_type = 'Churn' GROUP BY channel)
/ COUNT(rows WHERE drop_type <> 'Active' GROUP BY channel)
```

Recommended view:

Retention deep dive and channel deep dive.

## Customer and Site Portfolio KPIs

These KPIs describe the size and composition of the customer/site base.

### Customers by Site Count

Segments business partners by the number of sites they have.

Calculation:

```text
For each business_partner_id:
  site_count = COUNT(DISTINCT Site_id)

Then group customers by site_count.
```

Recommended view:

Customer and site portfolio dashboard.

### Single-Site Customers

Counts customers with exactly one site.

Calculation:

```text
COUNT(business_partner_id WHERE COUNT(DISTINCT Site_id) = 1)
```

Recommended view:

Customer and site portfolio dashboard.

### Multi-Site Customers

Counts customers with more than one site.

Calculation:

```text
COUNT(business_partner_id WHERE COUNT(DISTINCT Site_id) > 1)
```

Recommended view:

Customer and site portfolio dashboard.

### Multi-Site Customer Rate

Measures the share of business partners with more than one site.

Calculation:

```text
Multi-Site Customers / Total Business Partners
```

Recommended view:

Executive summary supporting KPI or portfolio dashboard.

### Active Sites per Active Business Partner

Measures the active footprint per active customer.

Calculation:

```text
COUNT(DISTINCT Site_id WHERE drop_type = 'Active')
/ COUNT(DISTINCT business_partner_id WHERE drop_type = 'Active')
```

Recommended view:

Customer and site portfolio dashboard.

### Commodity Mix

Shows the distribution of contract episodes by commodity.

Calculation:

```text
COUNT(rows by commodity_type) / COUNT(*)
```

Recommended view:

Executive summary if shown compactly. Full breakdown belongs in portfolio dashboard.

### Active Commodity Mix

Shows the commodity distribution among active sites.

Calculation:

```text
COUNT(DISTINCT Site_id WHERE drop_type = 'Active' GROUP BY commodity_type)
/ COUNT(DISTINCT Site_id WHERE drop_type = 'Active')
```

Recommended view:

Customer and site portfolio dashboard.

### Customers by Alberta Postal FSA

Groups customers by the first three characters of `zipcode`.

Calculation:

```text
FSA = LEFT(zipcode, 3)
COUNT(DISTINCT business_partner_id GROUP BY FSA)
```

Recommended view:

Customer and site portfolio dashboard or geography deep dive.

### Active Site Count by FSA

Counts active sites by Alberta forward sortation area.

Calculation:

```text
FSA = LEFT(zipcode, 3)
COUNT(DISTINCT Site_id WHERE drop_type = 'Active' GROUP BY FSA)
```

Recommended view:

Geography deep dive.

## Product and Plan Adoption KPIs

These KPIs describe customer choices around billing and plan options.

### AMB Enrollment Rate

Measures average monthly billing adoption across contract episodes.

Calculation:

```text
COUNT(rows WHERE AMB_status = 'true') / COUNT(*)
```

Recommended view:

Product and plan adoption dashboard.

### Active AMB Enrollment Rate

Measures AMB adoption among active site contracts.

Calculation:

```text
COUNT(rows WHERE AMB_status = 'true' AND drop_type = 'Active')
/ COUNT(rows WHERE drop_type = 'Active')
```

Recommended view:

Executive summary supporting KPI or product dashboard.

### Evergreen Plan Adoption Rate

Measures adoption of evergreen plans.

Calculation:

```text
COUNT(rows WHERE evergreen_status = 'true') / COUNT(*)
```

Recommended view:

Product and plan adoption dashboard.

### Active Evergreen Plan Adoption Rate

Measures evergreen plan adoption among active rows.

Calculation:

```text
COUNT(rows WHERE evergreen_status = 'true' AND drop_type = 'Active')
/ COUNT(rows WHERE drop_type = 'Active')
```

Recommended view:

Product and plan adoption dashboard.

### Surge Plan Adoption Rate

Measures adoption of surge plans.

Calculation:

```text
COUNT(rows WHERE surge_status = 'true') / COUNT(*)
```

Recommended view:

Product and plan adoption dashboard.

### Active Surge Plan Adoption Rate

Measures surge adoption among active rows.

Calculation:

```text
COUNT(rows WHERE surge_status = 'true' AND drop_type = 'Active')
/ COUNT(rows WHERE drop_type = 'Active')
```

Recommended view:

Product and plan adoption dashboard.

### Churn Rate by AMB Status

Compares churn for AMB-enrolled and non-AMB rows.

Calculation:

```text
COUNT(rows WHERE drop_type = 'Churn' GROUP BY AMB_status)
/ COUNT(rows WHERE drop_type <> 'Active' GROUP BY AMB_status)
```

Recommended view:

Product and retention deep dive.

### Churn Rate by Evergreen Status

Compares churn for evergreen and non-evergreen rows.

Calculation:

```text
COUNT(rows WHERE drop_type = 'Churn' GROUP BY evergreen_status)
/ COUNT(rows WHERE drop_type <> 'Active' GROUP BY evergreen_status)
```

Recommended view:

Product and retention deep dive.

### Churn Rate by Surge Status

Compares churn for surge and non-surge rows.

Calculation:

```text
COUNT(rows WHERE drop_type = 'Churn' GROUP BY surge_status)
/ COUNT(rows WHERE drop_type <> 'Active' GROUP BY surge_status)
```

Recommended view:

Product and retention deep dive.

## Digital Engagement KPIs

These KPIs should be calculated at the business partner level unless stated otherwise.

### Digital Customers

Counts unique business partners using the digital portal.

Calculation:

```text
COUNT(DISTINCT business_partner_id WHERE digital_status = 'true')
```

Recommended view:

Executive summary and digital engagement dashboard.

### Non-Digital Customers

Counts unique business partners not using the digital portal.

Calculation:

```text
COUNT(DISTINCT business_partner_id WHERE digital_status = 'false')
```

Recommended view:

Digital engagement dashboard.

### Digital Adoption Rate

Measures the share of customers using the website or app.

Calculation:

```text
Digital Customers / Total Business Partners
```

Recommended view:

Executive summary.

### Average Digital Activation Lag

Measures the average time between signup and first digital portal use.

Calculation:

```text
AVG(DATEDIFF(digital_start_date, sign_up_date)
    WHERE digital_status = 'true')
```

Recommended view:

Digital engagement dashboard.

### Median Digital Activation Lag

Measures the median time between signup and first digital portal use.

Calculation:

```text
MEDIAN(DATEDIFF(digital_start_date, sign_up_date)
       WHERE digital_status = 'true')
```

Recommended view:

Digital engagement dashboard.

### Digital Adoption by Signup Cohort

Shows digital adoption by customer signup month.

Calculation:

```text
signup_month = MONTH(sign_up_date)
COUNT(DISTINCT business_partner_id WHERE digital_status = 'true' GROUP BY signup_month)
/ COUNT(DISTINCT business_partner_id GROUP BY signup_month)
```

Recommended view:

Digital engagement dashboard.

### Active Customer Digital Adoption Rate

Measures digital adoption among customers with at least one active site.

Calculation:

```text
COUNT(DISTINCT business_partner_id
      WHERE digital_status = 'true' AND business_partner_id has at least one Active site)
/ COUNT(DISTINCT business_partner_id
        WHERE business_partner_id has at least one Active site)
```

Recommended view:

Executive summary supporting KPI or digital engagement dashboard.

### Churn Rate by Digital Status

Compares closed-episode churn between digital and non-digital customers.

Calculation:

```text
COUNT(rows WHERE drop_type = 'Churn' GROUP BY digital_status)
/ COUNT(rows WHERE drop_type <> 'Active' GROUP BY digital_status)
```

Recommended view:

Retention deep dive and digital engagement dashboard.

### Digital Channel Penetration Among Digital Customers

Measures how many digital customers also purchased through the digital channel.

Calculation:

```text
COUNT(DISTINCT business_partner_id
      WHERE digital_status = 'true' AND channel = 'Digital')
/ COUNT(DISTINCT business_partner_id WHERE digital_status = 'true')
```

Recommended view:

Digital engagement dashboard.

## Agent and Channel Deep Dive KPIs

These KPIs support sales management. Exclude `Digital` rows from agent-level KPIs because `agent_name` is blank for digital-channel rows.

### Agent Sales Volume

Counts non-digital contract episodes handled by each agent.

Calculation:

```text
COUNT(rows WHERE agent_name IS NOT BLANK GROUP BY agent_name)
```

Recommended view:

Agent and channel deep dive.

### Active Sites by Agent

Counts active site rows handled by each agent.

Calculation:

```text
COUNT(DISTINCT Site_id
      WHERE drop_type = 'Active' AND agent_name IS NOT BLANK
      GROUP BY agent_name)
```

Recommended view:

Agent and channel deep dive.

### Agent Churn Rate

Measures churn among closed episodes handled by each agent.

Calculation:

```text
COUNT(rows WHERE drop_type = 'Churn' GROUP BY agent_name)
/ COUNT(rows WHERE drop_type <> 'Active' GROUP BY agent_name)
```

Use only rows where `agent_name` is not blank.

Recommended view:

Agent and channel deep dive.

### Agent Renewal Rate

Measures renewal outcomes among closed episodes handled by each agent.

Calculation:

```text
COUNT(rows WHERE drop_type IN ('Auto Renewal', 'Positive Renewal') GROUP BY agent_name)
/ COUNT(rows WHERE drop_type <> 'Active' GROUP BY agent_name)
```

Use only rows where `agent_name` is not blank.

Recommended view:

Agent and channel deep dive.

### Channel Churn Rate

Measures churn by sales channel.

Calculation:

```text
COUNT(rows WHERE drop_type = 'Churn' GROUP BY channel)
/ COUNT(rows WHERE drop_type <> 'Active' GROUP BY channel)
```

Recommended view:

Channel deep dive.

### Channel Renewal Rate

Measures renewal outcomes by sales channel.

Calculation:

```text
COUNT(rows WHERE drop_type IN ('Auto Renewal', 'Positive Renewal') GROUP BY channel)
/ COUNT(rows WHERE drop_type <> 'Active' GROUP BY channel)
```

Recommended view:

Channel deep dive.

### Channel Leakage Rate

Measures leakage by sales channel.

Calculation:

```text
COUNT(rows WHERE drop_type = 'Leakage' GROUP BY channel)
/ COUNT(rows GROUP BY channel)
```

Recommended view:

Channel deep dive and retention deep dive.

### Channel Active Rate

Measures active contract share by channel.

Calculation:

```text
COUNT(rows WHERE drop_type = 'Active' GROUP BY channel)
/ COUNT(rows GROUP BY channel)
```

Recommended view:

Channel deep dive.

## Signup, Cohort, and Time-Based KPIs

These KPIs help analyze acquisition and lifecycle timing.

### New Customers by Signup Month

Counts new business partners by signup month.

Calculation:

```text
signup_month = DATE_TRUNC('month', sign_up_date)
COUNT(DISTINCT business_partner_id GROUP BY signup_month)
```

Recommended view:

Executive summary trend or cohort deep dive.

### New Sites by Contract Start Month

Counts site contract episodes started each month.

Calculation:

```text
start_month = DATE_TRUNC('month', site_contract_start_date)
COUNT(rows GROUP BY start_month)
```

Recommended view:

Commercial performance dashboard.

### Closed Sites by Contract End Month

Counts closed contract episodes by end month.

Calculation:

```text
end_month = DATE_TRUNC('month', site_contract_end_date)
COUNT(rows WHERE drop_type <> 'Active' GROUP BY end_month)
```

Recommended view:

Retention deep dive.

### Monthly Churn Rate

Measures churn as a share of closed episodes for each month.

Calculation:

```text
end_month = DATE_TRUNC('month', site_contract_end_date)
COUNT(rows WHERE drop_type = 'Churn' GROUP BY end_month)
/ COUNT(rows WHERE drop_type <> 'Active' GROUP BY end_month)
```

Recommended view:

Executive summary trend and retention deep dive.

### Monthly Renewal Rate

Measures renewal outcomes as a share of closed episodes for each month.

Calculation:

```text
end_month = DATE_TRUNC('month', site_contract_end_date)
COUNT(rows WHERE drop_type IN ('Auto Renewal', 'Positive Renewal') GROUP BY end_month)
/ COUNT(rows WHERE drop_type <> 'Active' GROUP BY end_month)
```

Recommended view:

Executive summary trend and commercial performance dashboard.

### Time from Signup to First Site Start

Measures how long it takes customers to start their first site contract.

Calculation:

```text
For each business_partner_id:
  first_site_start_date = MIN(site_contract_start_date)
  lag_days = DATEDIFF(first_site_start_date, sign_up_date)

Then calculate AVG(lag_days), MEDIAN(lag_days), or distribution buckets.
```

Recommended view:

Customer lifecycle deep dive.

### Contract Start to End Duration Buckets

Groups contract episodes by duration.

Calculation:

```text
duration_days = DATEDIFF(site_contract_end_date, site_contract_start_date)

Bucket examples:
  0 days
  1-5 days
  6-30 days
  31-180 days
  181-365 days
  366+ days
```

Recommended view:

Retention deep dive.

## Data Quality and Control KPIs

These are useful for validating pipelines, dashboards, and business logic.

### Missing Digital Start Date for Digital Customers

Counts rows where `digital_status` is true but `digital_start_date` is blank.

Calculation:

```text
COUNT(rows WHERE digital_status = 'true' AND digital_start_date IS BLANK)
```

Recommended view:

Data quality page.

### Digital Start Date Present for Non-Digital Customers

Counts rows where `digital_status` is false but `digital_start_date` is populated.

Calculation:

```text
COUNT(rows WHERE digital_status = 'false' AND digital_start_date IS NOT BLANK)
```

Recommended view:

Data quality page.

### Invalid Contract Date Rows

Counts rows where contract start is after contract end.

Calculation:

```text
COUNT(rows WHERE site_contract_start_date > site_contract_end_date)
```

Recommended view:

Data quality page.

### Signup After Contract Start Rows

Counts rows where signup date is not before contract start date.

Calculation:

```text
COUNT(rows WHERE sign_up_date >= site_contract_start_date)
```

Recommended view:

Data quality page.

### Digital Channel Rows with Agent

Counts rows where digital channel has an agent populated.

Calculation:

```text
COUNT(rows WHERE channel = 'Digital' AND agent_name IS NOT BLANK)
```

Recommended view:

Data quality page.

### Non-Digital Channel Rows Missing Agent

Counts rows where a non-digital channel has no agent populated.

Calculation:

```text
COUNT(rows WHERE channel <> 'Digital' AND agent_name IS BLANK)
```

Recommended view:

Data quality page.

### Inconsistent Business Partner Signup Date

Counts business partners with more than one signup date.

Calculation:

```text
COUNT(business_partner_id
      WHERE COUNT(DISTINCT sign_up_date) > 1)
```

Recommended view:

Data quality page.

### Inconsistent Business Partner Digital Status

Counts business partners with more than one digital status.

Calculation:

```text
COUNT(business_partner_id
      WHERE COUNT(DISTINCT digital_status) > 1)
```

Recommended view:

Data quality page.

### Inconsistent Business Partner Postal Code

Counts business partners with more than one postal code.

Calculation:

```text
COUNT(business_partner_id
      WHERE COUNT(DISTINCT zipcode) > 1)
```

Recommended view:

Data quality page.

### Non-Alberta Postal Code Rows

Counts rows where the postal code does not start with Alberta's `T` prefix.

Calculation:

```text
COUNT(rows WHERE LEFT(zipcode, 1) <> 'T')
```

Recommended view:

Data quality page.

## Suggested Executive Summary Layout

Recommended top-level KPIs:

1. Total Business Partners
2. Total Sites
3. Active Sites
4. Active Business Partners
5. Churn Rate
6. Renewal Rate
7. Leakage Rate
8. Digital Adoption Rate
9. Average Sites per Business Partner
10. Channel Mix

Recommended supporting visuals:

- Monthly churn rate trend
- Monthly renewal rate trend
- Active commodity mix
- Top channels by contract episode volume
- Digital adoption by signup cohort

## Suggested Deep Dive Pages

### Retention Deep Dive

Use:

- Churn Rate
- Drop Type Mix
- Same-Day Drop Rate
- Tagged Leakage Rate
- Average Closed Contract Duration
- Restarted Sites
- Site Restart Rate
- Churn by Commodity
- Churn by Channel

### Commercial Performance Deep Dive

Use:

- Sales Mix by Type
- Channel Sales Volume
- Channel Mix
- Renewal Outcome Mix
- New Sites by Contract Start Month
- Monthly Renewal Rate
- Agent Sales Volume

### Customer and Site Portfolio Deep Dive

Use:

- Customers by Site Count
- Single-Site Customers
- Multi-Site Customers
- Multi-Site Customer Rate
- Active Sites per Active Business Partner
- Commodity Mix
- Active Commodity Mix
- Customers by Alberta Postal FSA
- Active Site Count by FSA

### Product and Plan Deep Dive

Use:

- AMB Enrollment Rate
- Active AMB Enrollment Rate
- Evergreen Plan Adoption Rate
- Active Evergreen Plan Adoption Rate
- Surge Plan Adoption Rate
- Active Surge Plan Adoption Rate
- Churn Rate by AMB Status
- Churn Rate by Evergreen Status
- Churn Rate by Surge Status

### Digital Engagement Deep Dive

Use:

- Digital Customers
- Non-Digital Customers
- Digital Adoption Rate
- Average Digital Activation Lag
- Median Digital Activation Lag
- Digital Adoption by Signup Cohort
- Active Customer Digital Adoption Rate
- Churn Rate by Digital Status
- Digital Channel Penetration Among Digital Customers

### Agent and Channel Deep Dive

Use:

- Agent Sales Volume
- Active Sites by Agent
- Agent Churn Rate
- Agent Renewal Rate
- Channel Churn Rate
- Channel Renewal Rate
- Channel Leakage Rate
- Channel Active Rate

### Data Quality Page

Use:

- Missing Digital Start Date for Digital Customers
- Digital Start Date Present for Non-Digital Customers
- Invalid Contract Date Rows
- Signup After Contract Start Rows
- Digital Channel Rows with Agent
- Non-Digital Channel Rows Missing Agent
- Inconsistent Business Partner Signup Date
- Inconsistent Business Partner Digital Status
- Inconsistent Business Partner Postal Code
- Non-Alberta Postal Code Rows

## Notes for BI Implementation

- Treat `zipcode` as text, not a number.
- Convert date columns to date type when loading into BI tools.
- Use customer-level deduplication for `digital_status`, `dob_status`, `zipcode`, and `sign_up_date`.
- Decide whether a KPI should be episode-level or site-level before building it. Episode-level measures answer contract-event questions. Site-level measures answer portfolio-state questions.
- For current-state reporting, use the latest row per `Site_id` or rows with `drop_type = 'Active'`, depending on the business question.
- For renewal analysis, exclude `drop_type = 'Active'` from denominators unless the KPI is explicitly about active rows.
