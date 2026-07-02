# Weichai Power — config for model-viz/build.py
#
# To adapt to another company: copy this file, point 'file' at the new Excel
# models, adjust years/estFrom, and fix the row labels that differ (rows are
# found by label text, so most survive as-is when the bank reuses its template).
# 'rows' entries are either a label string or (label, occurrence) when the same
# label appears more than once in the sheet. SOTP sheets are free-form, so those
# use explicit cell references; basis strings may embed {CELL:pyformat} refs.

MS_FILE = "/Users/kq/Downloads/潍柴 MS 2026.5.5.XLSM"
UBS_FILE = "/Users/kq/Downloads/潍柴 UBS 2026.4.9.xlsx"

CONFIG = {
    "company": "Weichai Power",
    "tickers": "000338.SZ / 2338.HK",
    "currency": "RMB",
    "output": "weichai-model-viz.html",

    "sources": {
        "MS": {
            "file": MS_FILE,
            "name": "Morgan Stanley",
            "asOf": "5 May 2026",
            "years": (2007, 2028),
            "estFrom": 2026,
            "metricSheet": "Financial Summary",
            "labelCol": 1,   # labels in column A
            "valueCol": 2,   # first year value in column B
        },
        "UBS": {
            "file": UBS_FILE,
            "name": "UBS",
            "asOf": "9 Apr 2026",
            "years": (2007, 2030),
            "estFrom": 2026,
            "metricSheet": "main",
            "labelCol": 2,   # English labels in column B
            "valueCol": 3,   # first year value in column C
        },
    },

    # unit: rmbmn | pct | x | rmb (per share) | days
    "metrics": [
        # Income statement
        dict(id="revenue", label="Total revenue", unit="rmbmn", category="Income Statement",
             rows={"MS": "Turnover", "UBS": "Total Revenue"}),
        dict(id="gross_profit", label="Gross profit", unit="rmbmn", category="Income Statement",
             rows={"MS": "Gross profit", "UBS": "Gross profit"}),
        dict(id="selling_exp", label="Selling expenses", unit="rmbmn", category="Income Statement",
             rows={"MS": "Selling expenses", "UBS": "Selling Expenses"}),
        dict(id="admin_exp", label="Admin expenses", unit="rmbmn", category="Income Statement",
             rows={"MS": "Admin expenses", "UBS": "Admin Expenses"}),
        dict(id="op_profit", label="Operating profit", unit="rmbmn", category="Income Statement",
             rows={"MS": "Operating profit", "UBS": "Operating profit"}),
        dict(id="pbt", label="Profit before tax", unit="rmbmn", category="Income Statement",
             rows={"MS": "Profit before taxation", "UBS": "Profit before tax"}),
        dict(id="net_profit", label="Net profit (to parent)", unit="rmbmn", category="Income Statement",
             rows={"MS": ("Net profit", 1), "UBS": "Net Profit Attributable to Parent Company"}),
        # Growth & margins
        dict(id="rev_growth", label="Revenue growth", unit="pct", category="Growth & Margins",
             rows={"MS": ("Turnover", 2), "UBS": "Revenue YoY"}),
        dict(id="np_growth", label="Net profit growth", unit="pct", category="Growth & Margins",
             rows={"MS": ("Net profit", 2), "UBS": ("yoy %", 1)}),
        dict(id="gross_margin", label="Gross margin", unit="pct", category="Growth & Margins",
             rows={"MS": "Gross margin", "UBS": "GPM"}),
        dict(id="op_margin", label="Operating margin", unit="pct", category="Growth & Margins",
             rows={"MS": "EBIT margin", "UBS": "Operating profit margin"}),
        dict(id="net_margin", label="Net margin", unit="pct", category="Growth & Margins",
             rows={"MS": "Net margin", "UBS": "Net margin excluding minority %"}),
        # Per share
        dict(id="eps", label="EPS (basic)", unit="rmb", category="Per Share",
             rows={"MS": "Basic EPS (in RMB)", "UBS": "EPS basic"}),
        dict(id="bps", label="Book value per share", unit="rmb", category="Per Share",
             rows={"MS": "BPS (in RMB)", "UBS": None}),
        dict(id="dps", label="Dividend per share", unit="rmb", category="Per Share",
             rows={"MS": "DPS (in RMB)", "UBS": "DPS (Full year)"}),
        dict(id="payout", label="Dividend payout ratio", unit="pct", category="Per Share",
             rows={"MS": None, "UBS": "Payout ratio"}),
        # Balance sheet
        dict(id="cash", label="Cash & equivalents", unit="rmbmn", category="Balance Sheet",
             rows={"MS": "Cash and cash equivalents", "UBS": "Cash & Cash Eqv"}),
        dict(id="inventories", label="Inventories", unit="rmbmn", category="Balance Sheet",
             rows={"MS": "Inventories", "UBS": "Inventory"}),
        dict(id="receivables", label="Accounts receivable", unit="rmbmn", category="Balance Sheet",
             rows={"MS": "Accounts receivable", "UBS": "Account Receivable"}),
        dict(id="payables", label="Accounts payable", unit="rmbmn", category="Balance Sheet",
             rows={"MS": "Accounts payable", "UBS": "Account Payable"}),
        dict(id="total_equity", label="Total equity", unit="rmbmn", category="Balance Sheet",
             rows={"MS": "Shareholders' equity", "UBS": "Total Equity"}),
        dict(id="total_assets", label="Total assets", unit="rmbmn", category="Balance Sheet",
             rows={"MS": None, "UBS": "Total Asset"}),
        dict(id="total_liab", label="Total liabilities", unit="rmbmn", category="Balance Sheet",
             rows={"MS": None, "UBS": "Total Liabilities"}),
        # Cash flow
        dict(id="ocf", label="Operating cash flow", unit="rmbmn", category="Cash Flow",
             rows={"MS": "Net cash fr. operation", "UBS": "Net cash generated from operations"}),
        dict(id="icf", label="Investing cash flow", unit="rmbmn", category="Cash Flow",
             rows={"MS": "Net cash fr. investment", "UBS": "Cash Flow from Investment Actitivities"}),
        dict(id="fcf_fin", label="Financing cash flow", unit="rmbmn", category="Cash Flow",
             rows={"MS": "Net cash fr. financing", "UBS": ("Cash Flow from Financing Activities", 1)}),
        # Returns / gearing / efficiency (MS only)
        dict(id="roe", label="ROE", unit="pct", category="Returns & Gearing",
             rows={"MS": "ROE", "UBS": None}),
        dict(id="roaa", label="ROAA", unit="pct", category="Returns & Gearing",
             rows={"MS": "ROAA", "UBS": None}),
        dict(id="net_gearing", label="Net debt / equity", unit="pct", category="Returns & Gearing",
             rows={"MS": "Net debt/equity", "UBS": None}),
        dict(id="liab_equity", label="Total liabilities / equity", unit="pct", category="Returns & Gearing",
             rows={"MS": ("Total liabilities/equity", 1), "UBS": None}),
        dict(id="inv_days", label="Inventory days", unit="days", category="Efficiency",
             rows={"MS": "Inventory days", "UBS": None}),
        dict(id="recv_days", label="Receivable days", unit="days", category="Efficiency",
             rows={"MS": "Receivables days", "UBS": None}),
        dict(id="pay_days", label="Payable days", unit="days", category="Efficiency",
             rows={"MS": "Payable days", "UBS": None}),
        dict(id="asset_turn", label="Asset turnover", unit="x", category="Efficiency",
             rows={"MS": "Asset turnover (x)", "UBS": None}),
        # Valuation (MS only)
        dict(id="pe_h", label="P/E (H-share)", unit="x", category="Valuation",
             rows={"MS": ("P/E", 1), "UBS": None}),
        dict(id="pb_h", label="P/BV (H-share)", unit="x", category="Valuation",
             rows={"MS": ("P/BV", 1), "UBS": None}),
        dict(id="yield_h", label="Dividend yield (H)", unit="pct", category="Valuation",
             rows={"MS": ("Dividend Yield (%)", 1), "UBS": None}),
        dict(id="pe_a", label="P/E (A-share)", unit="x", category="Valuation",
             rows={"MS": ("P/E", 2), "UBS": None}),
        dict(id="pb_a", label="P/BV (A-share)", unit="x", category="Valuation",
             rows={"MS": ("P/BV", 2), "UBS": None}),
        dict(id="ev_ebitda", label="EV/EBITDA (A)", unit="x", category="Valuation",
             rows={"MS": "EV/EBITDA", "UBS": None}),
    ],

    "segments": {
        "MS": {
            "sheet": "Segments",
            "labelCol": 2,
            "valueCol": 3,
            "mixOf": "revenue",  # metric id used as denominator for the mix view
            "groups": {
                "revenue": {
                    "anchors": [(1, "Turnover (RMB '000)")],
                    "scale": 1e-3,  # sheet is in RMB '000
                    "series": [
                        ("Engine", "Engine"),
                        ("Heavy Truck", "Shaanxi Heavy Truck"),
                        ("Fast Gear", "Shaanxi Fast Gear"),
                        ("Linde Hydraulics", "Linde Hydraulic"),
                        ("KION", "KION"),
                        ("Others", "Others"),
                    ],
                    "note": "Excludes inter-segment eliminations.",
                },
                "grossMargin": {
                    "anchors": [(1, "Gross Profit (RMB '000)"), (2, "Gross margin")],
                    "series": [
                        ("Engine", "Engine"),
                        ("Heavy Truck", "Shaanxi Heavy Truck"),
                        ("Fast Gear", "Shaanxi Fast Gear"),
                        ("Linde Hydraulics", "Linde Hydraulic"),
                        ("KION", "KION"),
                        ("Total", "Total"),
                    ],
                },
            },
        },
        "UBS": {
            "sheet": "topline",
            "labelCol": 3,
            "valueCol": 4,
            "mixOf": "revenue",
            "groups": {
                "revenue": {
                    "anchors": [(3, "Total Revenue")],
                    "series": [
                        ("Engine", "Engine"),
                        ("Gearbox", "Gearbox"),
                        ("Truck", "Truck"),
                        ("Agri machinery", "Agricultural machinary"),
                        ("KION", "Kion"),
                        ("Others", "other"),
                    ],
                    "note": "'Others' is net of inter-segment eliminations.",
                },
            },
        },
    },

    "sotp": {
        # canonical buckets so the same part wears the same color across banks
        "groups": [
            {"id": "trad", "label": "Traditional business"},
            {"id": "kion", "label": "KION stake"},
            {"id": "newpower", "label": "AIDC / power generation"},
            {"id": "other", "label": "Other stakes"},
        ],
        "sources": {
            "MS": {
                "sheet": "SOTP",
                "parts": [
                    {"name": "Traditional business", "group": "trad", "value": "E9",
                     "basis": "2026E NP RMB{E6:,.0f}mn × {E8:.1f}x target P/E"},
                    {"name": "KION stake", "group": "kion", "value": "E14",
                     "basis": "{E13:.1%} of KION market cap RMB{E12:,.0f}mn"},
                    {"name": "AIDC business", "group": "newpower", "value": "E24",
                     "basis": "2026E NP RMB{E17:,.0f}mn × {E23:.0f}x target P/E"},
                    {"name": "PSI stake", "group": "other", "value": "E29",
                     "basis": "{E28:.0%} of PSI market cap RMB{E27:,.0f}mn"},
                ],
                "total": "E31",
                "stats": [
                    {"label": "Equity value", "cell": "E31", "fmt": "RMB {v:,.0f}mn"},
                    {"label": "Per share", "cell": "E36", "fmt": "RMB {v:.1f}"},
                    {"label": "H-share price target", "cell": "E37", "fmt": "HK${v:.0f}"},
                    {"label": "A-share price target", "cell": "E41", "fmt": "RMB {v:.1f}"},
                    {"label": "Last close (A)", "cell": "E43", "fmt": "RMB {v:.2f}"},
                    {"label": "Upside", "cell": "E44", "fmt": "{v:+.1%}"},
                    {"label": "Implied 2026E P/E", "cell": "E38", "fmt": "{v:.1f}x"},
                ],
            },
            "UBS": {
                "sheet": "SOTP",
                "parts": [
                    {"name": "Traditional business", "group": "trad", "value": "C6", "old": "D6",
                     "basis": "2026E NP RMB{C4:,.0f}mn × {C5:.0f}x P/E"},
                    {"name": "KION stake", "group": "kion", "value": "C12", "old": "D12",
                     "basis": "{C11:.1%} stake at €{C8:.0f}/sh target, EUR/CNY {C10:.1f}"},
                    {"name": "Power generation", "group": "newpower", "value": "C18", "old": "D18",
                     "basis": "2030E NP RMB{C14:,.0f}mn × {C15:.0f}x, discounted at {C17:.0%}"},
                ],
                "total": "C20",
                "oldTotal": "D20",
                "stats": [
                    {"label": "Equity value", "cell": "C20", "fmt": "RMB {v:,.0f}mn"},
                    {"label": "Per share", "cell": "C21", "fmt": "RMB {v:.1f}"},
                    {"label": "A-share price target", "cell": "C22", "fmt": "RMB {v:.1f}"},
                    {"label": "H-share price target", "cell": "C24", "fmt": "HK${v:.1f}"},
                    {"label": "Current price (A)", "cell": "C31", "fmt": "RMB {v:.2f}"},
                    {"label": "Implied 2026E P/E", "cell": "C27", "fmt": "{v:.1f}x"},
                ],
            },
        },
    },
}
