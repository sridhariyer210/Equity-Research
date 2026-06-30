# Adding a New Fund

This guide explains how to add a new mutual fund to the tracker.

## Steps

1. **Update funds.yaml**
   - Add a new entry under the `funds` section
   - Fill in: fund_id, fund_name, cap_category, amfi_code, amc_id, sheet_name (if multi-tab), is_active

2. **If New AMC**
   - Create a new parser in `src/parsing/amc/new_amc.py`
   - Inherit from `BaseAMCParser`
   - Implement `get_raw_dataframe()` and `normalize()` methods
   - Update `src/parsing/parser.py` to instantiate your new parser

3. **Run the Pipeline**
   - `python scripts/run_monthly.py --step all`

That's it! No code changes required if the AMC already exists.
