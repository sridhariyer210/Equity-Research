# Data Dictionary

This document describes the schema and fields in the MF Holdings Tracker.

## Holdings Table

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| date | Date | First day of month (YYYY-MM-01) |
| fund_id | String | Reference to fund |
| isin | String | ISIN code of security |
| stock_name | String | Name of holding |
| sector | String | Sector classification |
| instrument_type | String | equity, debt, etf, reit, etc. |
| market_value_cr | Float | Market value in crores |
| pct_of_nav | Float | Percentage of net asset value |
| rank_in_fund | Integer | Rank of holding in fund (1=largest) |
| created_at | DateTime | Record creation timestamp |

## Funds Table

| Column | Type | Description |
|--------|------|-------------|
| fund_id | String | Primary key |
| fund_name | String | Fund name |
| cap_category | String | small_cap, mid_cap, large_cap, flexi_cap |
| amc_id | String | Reference to AMC |
| amfi_code | String | AMFI classification code |
| sheet_name | String | For multi-tab AMCs |
| is_active | Boolean | Whether fund is actively tracked |
| created_at | DateTime | Record creation timestamp |

## AMCs Table

| Column | Type | Description |
|--------|------|-------------|
| amc_id | String | Primary key |
| amc_name | String | Full name of AMC |
| file_pattern | String | single_file or multi_tab |
| url_template | String | URL pattern for downloads |
| created_at | DateTime | Record creation timestamp |
