from pathlib import Path

import pandas as pd

from src.parsing.amc.sbi import SBIParser


def test_sbi_parser_normalizes_only_valid_holding_rows(monkeypatch):
    sheet_df = pd.DataFrame(
        [
            [None, None, "SBI Mutual Fund", None, None, None, None],
            [None, None, "SCHEME NAME :", "SBI Smallcap Fund", None, None, None],
            [
                None,
                None,
                "PORTFOLIO STATEMENT AS ON :",
                pd.Timestamp("2026-05-31"),
                None,
                None,
                None,
            ],
            [None, None, None, None, None, None, None],
            [
                None,
                None,
                "Name of the Instrument / Issuer",
                "ISIN",
                "Rating / Industry^",
                "Quantity",
                "Market value\n(Rs. in Lakhs)",
                "% to AUM",
            ],
            [None, None, "Equity Shares", None, None, None, None, None],
            [
                None,
                102597,
                "Ather Energy Ltd.",
                "INE0LEZ01016",
                "Automobiles",
                20096960,
                193754.79,
                5.18,
            ],
            [
                None,
                100332,
                "Navin Fluorine International Ltd.",
                "INE048G01026",
                "Chemicals & Petrochemicals",
                1631795,
                116330.67,
                3.11,
            ],
            [None, None, "Grand Total", None, None, None, 310085.46, 8.29],
        ]
    )

    def fake_read_excel(file_path, sheet_name, header):
        assert Path(file_path) == Path("sbi.xlsx")
        assert sheet_name == "SSCF"
        assert header is None
        return sheet_df

    monkeypatch.setattr(pd, "read_excel", fake_read_excel)

    parser = SBIParser()
    raw_df = parser.get_raw_dataframe("sbi.xlsx", {"sheet_name": "SSCF"})
    normalized_df = parser.normalize(raw_df, {"name": "SBI Small Cap Fund"})

    assert list(normalized_df.columns) == [
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
    assert normalized_df.shape == (2, 9)
    assert normalized_df["report_date"].tolist() == ["2026-05-31", "2026-05-31"]
    assert normalized_df["isin"].tolist() == ["INE0LEZ01016", "INE048G01026"]
    assert "Grand Total" not in normalized_df["company"].tolist()
