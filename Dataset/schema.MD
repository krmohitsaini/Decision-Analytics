# Synthetic Energy Customer Sites Schema

This CSV contains synthetic customer, site, contract, channel, and plan data for an Alberta-based energy retailer. Each row represents one site-level contract episode for a business partner. A single business partner can have multiple sites, and the same site can appear across multiple rows when it ended and later restarted.

## File

`synthetic_energy_customer_sites.csv`

## Grain

One row per `business_partner_id` + `Site_id` + contract episode.

## Columns

| Column | Level | Type | Description |
| --- | --- | --- | --- |
| `business_partner_id` | Business partner | Text identifier | Unique customer/business partner ID. One business partner can have 1 to 10 sites. |
| `Site_id` | Site | Text identifier | Site/account location ID. A business partner can have multiple site IDs. The same site ID can appear more than once if the site contract ended and then restarted. |
| `commodity_type` | Site contract episode | Categorical text | Commodity served at the site. Values are `ELE`, `GAS`, or `BOTH`. |
| `site_contract_start_date` | Site contract episode | Date, `YYYY-MM-DD` | Start date of the site contract episode. Always after the business partner's `sign_up_date`. |
| `site_contract_end_date` | Site contract episode | Date, `YYYY-MM-DD` | End date of the site contract episode. Always greater than or equal to `site_contract_start_date`. If it equals the start date, the site churned or dropped on the same day. |
| `sign_up_date` | Business partner | Date, `YYYY-MM-DD` | Customer signup date. This is fixed for each business partner and is always on or after `2023-01-01`. |
| `zipcode` | Business partner | Text | Synthetic Canadian postal code restricted to Alberta forward sortation areas. Kept as text because postal codes are identifiers. |
| `AMB_status` | Site contract episode | Boolean text | Whether the site contract episode is enrolled in average monthly billing. Values are `true` or `false`. |
| `drop_type` | Site contract episode | Categorical text | Outcome/status of the contract episode. Values are `Churn`, `Auto Renewal`, `Positive Renewal`, `TOS`, `Leakage`, or `Active`. `Active` means the site is still active as of the dataset generation date. |
| `sales_type` | Site contract episode | Categorical text | Sales tagging for the contract episode. Values are `Organic`, `Auto Renewal`, `Positive Renewal`, or `TOS`. If the previous episode for the same site ended with `Auto Renewal`, `Positive Renewal`, or `TOS`, the next episode uses that value as its `sales_type`; otherwise it is `Organic`. |
| `evergreen_status` | Site contract episode | Boolean text | Whether the customer opted into an evergreen plan for this site contract episode. Values are `true` or `false`. |
| `surge_status` | Site contract episode | Boolean text | Whether the customer opted into a surge plan for this site contract episode. Values are `true` or `false`. |
| `channel` | Site contract episode | Categorical text | Channel through which the sale was made. Example values include `IBTS`, `Direct Sale`, `Digital`, `Telesales`, `Broker`, `Door-to-Door`, `Retail Kiosk`, `Field Sales`, `Referral`, and `Partner`. |
| `digital_status` | Business partner | Boolean text | Whether the business partner uses the website or app. This is fixed for each business partner. About 30% of business partners have `digital_status = true`. |
| `digital_start_date` | Business partner | Date, `YYYY-MM-DD`, nullable | Date when the business partner started using the digital portal. Present only when `digital_status = true`. It is always after `sign_up_date`. Blank when `digital_status = false`. |
| `dob_status` | Business partner | Boolean text | Whether the customer's date of birth was captured during signup. This is fixed for each business partner. Values are `true` or `false`. |
| `agent_name` | Site contract episode | Text, nullable | Agent who made the sale. Populated for non-digital sales channels and blank for `Digital` channel rows. The synthetic dataset uses about 100 agent names. |

## Important Rules

- `business_partner_id`, `sign_up_date`, `zipcode`, `digital_status`, `digital_start_date`, and `dob_status` are customer-level fields and stay constant across all rows for the same business partner.
- `Site_id`, `commodity_type`, contract dates, billing/plan flags, `drop_type`, `sales_type`, `channel`, and `agent_name` are site-contract-level fields.
- `site_contract_start_date <= site_contract_end_date` for every row.
- `sign_up_date < site_contract_start_date` for every row.
- `drop_type = Active` means the contract is active as of `2026-09-09`.
- `drop_type = Leakage` means the contract ended on the same day or within 5 days of the start date. The generated dataset targets roughly 2% leakage rows.
- If `channel = Digital`, `agent_name` is blank.
- If `channel` is not `Digital`, `agent_name` is populated.
- Boolean fields are stored as lowercase text values: `true` and `false`.

## Generated Dataset Summary

- Business partners: 100,000
- Unique sites: 626,767
- Data rows: 992,631
- Digital business partners: approximately 30%
- Leakage rows: approximately 2%
