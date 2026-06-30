import pandas as pd
from pathlib import Path

from src.parsing.amc.base import BaseAMCParser


OUTPUT_COLUMNS = [
    "report_date",
    "fund_house",
    "fund_name",
    "company",
    "isin",
    "industry",
    "quantity",
    "market_value_lakhs",
    "aum_percent",
]

INDIAN_ISIN_PATTERN = r"^IN[A-Z0-9]{10}$"


class SBIParser(BaseAMCParser):
    """Parser for SBI Mutual Fund workbooks."""

    def get_raw_dataframe(self, file_path: str, fund_config: dict) -> pd.DataFrame:
        """Read and clean the SBI Small Cap Fund worksheet."""
        workbook_path = Path(file_path)
        sheet_name = fund_config.get("sheet_name", "SSCF")

        sheet_df = pd.read_excel(workbook_path, sheet_name=sheet_name, header=None)
        header_row = _find_header_row(sheet_df)
        report_date = _extract_report_date(sheet_df)

        raw_df = sheet_df.iloc[header_row + 1 :].copy()
        raw_df.columns = sheet_df.iloc[header_row].astype(str).str.strip()
        raw_df = _remove_empty_columns(raw_df)
        raw_df = raw_df.dropna(how="all")
        raw_df.attrs["report_date"] = report_date

        return raw_df

    def normalize(self, df: pd.DataFrame, fund_config: dict) -> pd.DataFrame:
        """Normalize SBI Small Cap Fund holdings to the current V1 schema."""
        holdings_df = df[
            df["ISIN"].astype(str).str.strip().str.match(INDIAN_ISIN_PATTERN, na=False)
        ].copy()

        normalized_df = pd.DataFrame(
            {
                "report_date": _format_report_date(df.attrs.get("report_date")),
                "fund_house": "SBI Mutual Fund",
                "fund_name": fund_config.get("name", "SBI Small Cap Fund"),
                "company": holdings_df["Name of the Instrument / Issuer"].astype(str).str.strip(),
                "isin": holdings_df["ISIN"].astype(str).str.strip(),
                "industry": holdings_df["Rating / Industry^"].astype(str).str.strip(),
                "quantity": pd.to_numeric(holdings_df["Quantity"], errors="coerce"),
                "market_value_lakhs": pd.to_numeric(
                    holdings_df["Market value\n(Rs. in Lakhs)"],
                    errors="coerce",
                ),
                "aum_percent": pd.to_numeric(holdings_df["% to AUM"], errors="coerce"),
            }
        )

        return normalized_df.loc[:, OUTPUT_COLUMNS].reset_index(drop=True)


def _find_header_row(sheet_df: pd.DataFrame) -> int:
    """Find the holdings header using column names, not row position."""
    for row_index, row in sheet_df.iterrows():
        row_values = {str(value).strip() for value in row.dropna()}
        if {"Name of the Instrument / Issuer", "ISIN"}.issubset(row_values):
            return row_index

    raise ValueError("Could not find SBI holdings header row")


def _extract_report_date(sheet_df: pd.DataFrame) -> pd.Timestamp | None:
    """Extract the portfolio statement date from sheet metadata."""
    for _, row in sheet_df.iterrows():
        values = [value for value in row.tolist() if pd.notna(value)]
        for index, value in enumerate(values):
            if str(value).strip().startswith("PORTFOLIO STATEMENT AS ON"):
                if index + 1 < len(values):
                    return pd.to_datetime(values[index + 1], errors="coerce")

    # TODO: Fall back to parsing the date from the filename if needed.
    return None


def _remove_empty_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Remove blank columns created by Excel layout spacing."""
    keep_column_positions = []
    for position, column in enumerate(df.columns):
        column_name = str(column).strip()
        has_header = not (
            column_name.startswith("Unnamed")
            or column_name.lower() in {"", "nan", "none"}
        )
        has_data = not df.iloc[:, position].isna().all()
        if has_header and has_data:
            keep_column_positions.append(position)

    return df.iloc[:, keep_column_positions]


def _format_report_date(report_date: pd.Timestamp | None) -> str | None:
    """Format report date as YYYY-MM-DD for CSV-friendly output."""
    if report_date is None or pd.isna(report_date):
        return None

    return pd.Timestamp(report_date).strftime("%Y-%m-%d")
