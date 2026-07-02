# Weichai Power — config for model-viz/build.py
#
# To adapt to another company: copy this file, point 'file' at the new Excel
# models, adjust years/estFrom, and fix the row labels that differ (rows are
# found by label text, so most survive as-is when the bank reuses its template).
# 'rows' entries are either a label string or (label, occurrence) when the same
# label appears more than once in the sheet. SOTP sheets are free-form, so those
# use explicit cell references; basis strings may embed {CELL:pyformat} refs.
# All *Zh fields are optional — omit them and the app simply stays in English.

MS_FILE = "/Users/kq/Downloads/潍柴 MS 2026.5.5.XLSM"
UBS_FILE = "/Users/kq/Downloads/潍柴 UBS 2026.4.9.xlsx"

CONFIG = {
    "company": "Weichai Power",
    "companyZh": "潍柴动力",
    "tickers": "000338.SZ / 2338.HK",
    "currency": "RMB",
    "output": "weichai-model-viz.html",

    "sources": {
        "MS": {
            "file": MS_FILE,
            "name": "Morgan Stanley",
            "nameZh": "摩根士丹利",
            "asOf": "5 May 2026",
            "asOfZh": "2026年5月5日",
            "years": (2007, 2028),
            "estFrom": 2026,
            "metricSheet": "Financial Summary",
            "labelCol": 1,   # labels in column A
            "valueCol": 2,   # first year value in column B
        },
        "UBS": {
            "file": UBS_FILE,
            "name": "UBS",
            "nameZh": "瑞银",
            "asOf": "9 Apr 2026",
            "asOfZh": "2026年4月9日",
            "years": (2007, 2030),
            "estFrom": 2026,
            "metricSheet": "main",
            "labelCol": 2,   # English labels in column B
            "valueCol": 3,   # first year value in column C
        },
    },

    "categories": {
        "Income Statement": "利润表",
        "Growth & Margins": "增长与利润率",
        "Per Share": "每股指标",
        "Balance Sheet": "资产负债表",
        "Cash Flow": "现金流量表",
        "Returns & Gearing": "回报与杠杆",
        "Efficiency": "营运效率",
        "Valuation": "估值",
    },

    # unit: rmbmn | pct | x | rmb (per share) | days
    "metrics": [
        # Income statement
        dict(id="revenue", label="Total revenue", labelZh="营业总收入", unit="rmbmn", category="Income Statement",
             rows={"MS": "Turnover", "UBS": "Total Revenue"}),
        dict(id="gross_profit", label="Gross profit", labelZh="毛利润", unit="rmbmn", category="Income Statement",
             rows={"MS": "Gross profit", "UBS": "Gross profit"}),
        dict(id="selling_exp", label="Selling expenses", labelZh="销售费用", unit="rmbmn", category="Income Statement",
             rows={"MS": "Selling expenses", "UBS": "Selling Expenses"}),
        dict(id="admin_exp", label="Admin expenses", labelZh="管理费用", unit="rmbmn", category="Income Statement",
             rows={"MS": "Admin expenses", "UBS": "Admin Expenses"}),
        dict(id="op_profit", label="Operating profit", labelZh="营业利润", unit="rmbmn", category="Income Statement",
             rows={"MS": "Operating profit", "UBS": "Operating profit"}),
        dict(id="pbt", label="Profit before tax", labelZh="税前利润", unit="rmbmn", category="Income Statement",
             rows={"MS": "Profit before taxation", "UBS": "Profit before tax"}),
        dict(id="net_profit", label="Net profit (to parent)", labelZh="归母净利润", unit="rmbmn", category="Income Statement",
             rows={"MS": ("Net profit", 1), "UBS": "Net Profit Attributable to Parent Company"}),
        # Growth & margins
        dict(id="rev_growth", label="Revenue growth", labelZh="收入增速", unit="pct", category="Growth & Margins",
             rows={"MS": ("Turnover", 2), "UBS": "Revenue YoY"}),
        dict(id="np_growth", label="Net profit growth", labelZh="净利润增速", unit="pct", category="Growth & Margins",
             rows={"MS": ("Net profit", 2), "UBS": ("yoy %", 1)}),
        dict(id="gross_margin", label="Gross margin", labelZh="毛利率", unit="pct", category="Growth & Margins",
             rows={"MS": "Gross margin", "UBS": "GPM"}),
        dict(id="op_margin", label="Operating margin", labelZh="营业利润率", unit="pct", category="Growth & Margins",
             rows={"MS": "EBIT margin", "UBS": "Operating profit margin"}),
        dict(id="net_margin", label="Net margin", labelZh="净利率", unit="pct", category="Growth & Margins",
             rows={"MS": "Net margin", "UBS": "Net margin excluding minority %"}),
        # Per share
        dict(id="eps", label="EPS (basic)", labelZh="基本每股收益", unit="rmb", category="Per Share",
             rows={"MS": "Basic EPS (in RMB)", "UBS": "EPS basic"}),
        dict(id="bps", label="Book value per share", labelZh="每股净资产", unit="rmb", category="Per Share",
             rows={"MS": "BPS (in RMB)", "UBS": None}),
        dict(id="dps", label="Dividend per share", labelZh="每股股利", unit="rmb", category="Per Share",
             rows={"MS": "DPS (in RMB)", "UBS": "DPS (Full year)"}),
        dict(id="payout", label="Dividend payout ratio", labelZh="股利支付率", unit="pct", category="Per Share",
             rows={"MS": None, "UBS": "Payout ratio"}),
        # Balance sheet
        dict(id="cash", label="Cash & equivalents", labelZh="货币资金", unit="rmbmn", category="Balance Sheet",
             rows={"MS": "Cash and cash equivalents", "UBS": "Cash & Cash Eqv"}),
        dict(id="inventories", label="Inventories", labelZh="存货", unit="rmbmn", category="Balance Sheet",
             rows={"MS": "Inventories", "UBS": "Inventory"}),
        dict(id="receivables", label="Accounts receivable", labelZh="应收账款", unit="rmbmn", category="Balance Sheet",
             rows={"MS": "Accounts receivable", "UBS": "Account Receivable"}),
        dict(id="payables", label="Accounts payable", labelZh="应付账款", unit="rmbmn", category="Balance Sheet",
             rows={"MS": "Accounts payable", "UBS": "Account Payable"}),
        dict(id="total_equity", label="Total equity", labelZh="所有者权益合计", unit="rmbmn", category="Balance Sheet",
             rows={"MS": "Shareholders' equity", "UBS": "Total Equity"}),
        dict(id="total_assets", label="Total assets", labelZh="资产总计", unit="rmbmn", category="Balance Sheet",
             rows={"MS": None, "UBS": "Total Asset"}),
        dict(id="total_liab", label="Total liabilities", labelZh="负债合计", unit="rmbmn", category="Balance Sheet",
             rows={"MS": None, "UBS": "Total Liabilities"}),
        # Cash flow
        dict(id="ocf", label="Operating cash flow", labelZh="经营活动现金流", unit="rmbmn", category="Cash Flow",
             rows={"MS": "Net cash fr. operation", "UBS": "Net cash generated from operations"}),
        dict(id="icf", label="Investing cash flow", labelZh="投资活动现金流", unit="rmbmn", category="Cash Flow",
             rows={"MS": "Net cash fr. investment", "UBS": "Cash Flow from Investment Actitivities"}),
        dict(id="fcf_fin", label="Financing cash flow", labelZh="筹资活动现金流", unit="rmbmn", category="Cash Flow",
             rows={"MS": "Net cash fr. financing", "UBS": ("Cash Flow from Financing Activities", 1)}),
        # Returns / gearing / efficiency (MS only)
        dict(id="roe", label="ROE", labelZh="净资产收益率 (ROE)", unit="pct", category="Returns & Gearing",
             rows={"MS": "ROE", "UBS": None}),
        dict(id="roaa", label="ROAA", labelZh="平均总资产收益率 (ROAA)", unit="pct", category="Returns & Gearing",
             rows={"MS": "ROAA", "UBS": None}),
        dict(id="net_gearing", label="Net debt / equity", labelZh="净负债/权益", unit="pct", category="Returns & Gearing",
             rows={"MS": "Net debt/equity", "UBS": None}),
        dict(id="liab_equity", label="Total liabilities / equity", labelZh="总负债/权益", unit="pct", category="Returns & Gearing",
             rows={"MS": ("Total liabilities/equity", 1), "UBS": None}),
        dict(id="inv_days", label="Inventory days", labelZh="存货周转天数", unit="days", category="Efficiency",
             rows={"MS": "Inventory days", "UBS": None}),
        dict(id="recv_days", label="Receivable days", labelZh="应收账款天数", unit="days", category="Efficiency",
             rows={"MS": "Receivables days", "UBS": None}),
        dict(id="pay_days", label="Payable days", labelZh="应付账款天数", unit="days", category="Efficiency",
             rows={"MS": "Payable days", "UBS": None}),
        dict(id="asset_turn", label="Asset turnover", labelZh="总资产周转率", unit="x", category="Efficiency",
             rows={"MS": "Asset turnover (x)", "UBS": None}),
        # Valuation (MS only)
        dict(id="pe_h", label="P/E (H-share)", labelZh="市盈率（H股）", unit="x", category="Valuation",
             rows={"MS": ("P/E", 1), "UBS": None}),
        dict(id="pb_h", label="P/BV (H-share)", labelZh="市净率（H股）", unit="x", category="Valuation",
             rows={"MS": ("P/BV", 1), "UBS": None}),
        dict(id="yield_h", label="Dividend yield (H)", labelZh="股息率（H股）", unit="pct", category="Valuation",
             rows={"MS": ("Dividend Yield (%)", 1), "UBS": None}),
        dict(id="pe_a", label="P/E (A-share)", labelZh="市盈率（A股）", unit="x", category="Valuation",
             rows={"MS": ("P/E", 2), "UBS": None}),
        dict(id="pb_a", label="P/BV (A-share)", labelZh="市净率（A股）", unit="x", category="Valuation",
             rows={"MS": ("P/BV", 2), "UBS": None}),
        dict(id="ev_ebitda", label="EV/EBITDA (A)", labelZh="EV/EBITDA（A股）", unit="x", category="Valuation",
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
                        ("Engine", "发动机", "Engine"),
                        ("Heavy Truck", "重卡（陕重汽）", "Shaanxi Heavy Truck"),
                        ("Fast Gear", "法士特变速箱", "Shaanxi Fast Gear"),
                        ("Linde Hydraulics", "林德液压", "Linde Hydraulic"),
                        ("KION", "凯傲", "KION"),
                        ("Others", "其他", "Others"),
                    ],
                    "note": "Excludes inter-segment eliminations.",
                    "noteZh": "不含分部间抵消。",
                },
                "grossMargin": {
                    "anchors": [(1, "Gross Profit (RMB '000)"), (2, "Gross margin")],
                    "series": [
                        ("Engine", "发动机", "Engine"),
                        ("Heavy Truck", "重卡（陕重汽）", "Shaanxi Heavy Truck"),
                        ("Fast Gear", "法士特变速箱", "Shaanxi Fast Gear"),
                        ("Linde Hydraulics", "林德液压", "Linde Hydraulic"),
                        ("KION", "凯傲", "KION"),
                        ("Total", "合计", "Total"),
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
                        ("Engine", "发动机", "Engine"),
                        ("Gearbox", "变速箱", "Gearbox"),
                        ("Truck", "重卡", "Truck"),
                        ("Agri machinery", "农业机械（雷沃）", "Agricultural machinary"),
                        ("KION", "凯傲", "Kion"),
                        ("Others", "其他", "other"),
                    ],
                    "note": "'Others' is net of inter-segment eliminations.",
                    "noteZh": "“其他”已扣除分部间抵消。",
                },
            },
        },
    },

    "sotp": {
        # canonical buckets so the same part wears the same color across banks
        "groups": [
            {"id": "trad", "label": "Traditional business", "labelZh": "传统业务"},
            {"id": "kion", "label": "KION stake", "labelZh": "凯傲股权"},
            {"id": "newpower", "label": "AIDC / power generation", "labelZh": "AIDC/发电业务"},
            {"id": "other", "label": "Other stakes", "labelZh": "其他股权"},
        ],
        "sources": {
            "MS": {
                "sheet": "SOTP",
                "parts": [
                    {"name": "Traditional business", "nameZh": "传统业务", "group": "trad", "value": "E9",
                     "basis": "2026E NP RMB{E6:,.0f}mn × {E8:.1f}x target P/E",
                     "basisZh": "2026E净利润 人民币{E6:,.0f}百万 × {E8:.1f}倍目标市盈率"},
                    {"name": "KION stake", "nameZh": "凯傲股权", "group": "kion", "value": "E14",
                     "basis": "{E13:.1%} of KION market cap RMB{E12:,.0f}mn",
                     "basisZh": "凯傲市值 人民币{E12:,.0f}百万 × {E13:.1%}持股"},
                    {"name": "AIDC business", "nameZh": "AIDC业务", "group": "newpower", "value": "E24",
                     "basis": "2026E NP RMB{E17:,.0f}mn × {E23:.0f}x target P/E",
                     "basisZh": "2026E净利润 人民币{E17:,.0f}百万 × {E23:.0f}倍目标市盈率"},
                    {"name": "PSI stake", "nameZh": "PSI股权", "group": "other", "value": "E29",
                     "basis": "{E28:.0%} of PSI market cap RMB{E27:,.0f}mn",
                     "basisZh": "PSI市值 人民币{E27:,.0f}百万 × {E28:.0%}持股"},
                ],
                "total": "E31",
                "stats": [
                    {"label": "Equity value", "labelZh": "股权价值", "cell": "E31", "fmt": "RMB {v:,.0f}mn"},
                    {"label": "Per share", "labelZh": "每股价值", "cell": "E36", "fmt": "RMB {v:.1f}"},
                    {"label": "H-share price target", "labelZh": "H股目标价", "cell": "E37", "fmt": "HK${v:.0f}"},
                    {"label": "A-share price target", "labelZh": "A股目标价", "cell": "E41", "fmt": "RMB {v:.1f}"},
                    {"label": "Last close (A)", "labelZh": "最新收盘价（A股）", "cell": "E43", "fmt": "RMB {v:.2f}"},
                    {"label": "Upside", "labelZh": "上行空间", "cell": "E44", "fmt": "{v:+.1%}"},
                    {"label": "Implied 2026E P/E", "labelZh": "隐含2026E市盈率", "cell": "E38", "fmt": "{v:.1f}x"},
                ],
            },
            "UBS": {
                "sheet": "SOTP",
                "parts": [
                    {"name": "Traditional business", "nameZh": "传统业务", "group": "trad", "value": "C6", "old": "D6",
                     "basis": "2026E NP RMB{C4:,.0f}mn × {C5:.0f}x P/E",
                     "basisZh": "2026E净利润 人民币{C4:,.0f}百万 × {C5:.0f}倍市盈率"},
                    {"name": "KION stake", "nameZh": "凯傲股权", "group": "kion", "value": "C12", "old": "D12",
                     "basis": "{C11:.1%} stake at €{C8:.0f}/sh target, EUR/CNY {C10:.1f}",
                     "basisZh": "按凯傲目标价€{C8:.0f}/股 × {C11:.1%}持股（欧元/人民币 {C10:.1f}）"},
                    {"name": "Power generation", "nameZh": "发电业务", "group": "newpower", "value": "C18", "old": "D18",
                     "basis": "2030E NP RMB{C14:,.0f}mn × {C15:.0f}x, discounted at {C17:.0%}",
                     "basisZh": "2030E净利润 人民币{C14:,.0f}百万 × {C15:.0f}倍，按{C17:.0%}折现"},
                ],
                "total": "C20",
                "oldTotal": "D20",
                "stats": [
                    {"label": "Equity value", "labelZh": "股权价值", "cell": "C20", "fmt": "RMB {v:,.0f}mn"},
                    {"label": "Per share", "labelZh": "每股价值", "cell": "C21", "fmt": "RMB {v:.1f}"},
                    {"label": "A-share price target", "labelZh": "A股目标价", "cell": "C22", "fmt": "RMB {v:.1f}"},
                    {"label": "H-share price target", "labelZh": "H股目标价", "cell": "C24", "fmt": "HK${v:.1f}"},
                    {"label": "Current price (A)", "labelZh": "当前股价（A股）", "cell": "C31", "fmt": "RMB {v:.2f}"},
                    {"label": "Implied 2026E P/E", "labelZh": "隐含2026E市盈率", "cell": "C27", "fmt": "{v:.1f}x"},
                ],
            },
        },
    },

    # Deep dives: driver-sheet detail pages. These sheets are free-form, so
    # series use explicit row numbers (like SOTP cells). Chart indicator chips
    # (actuals depth, cross-bank gap) are COMPUTED by build.py; claim chips are
    # editorial and authored here. 'compare' names the two series indices to
    # measure agreement between.
    "deepDives": [
        {
            "id": "aidc",
            "title": "AIDC / data-center power",
            "titleZh": "AIDC / 数据中心电力",
            "summaryKey": "aidc",
            "claims": [
                {
                    "src": "MS",
                    "text": "AIDC (data-center & primary power) reaches RMB31.0bn revenue / RMB7.7bn net profit by 2028E — 26.5% of engine-segment revenue and 38% of group profit — built from 6,500 DC diesel gensets (ASP ~RMB2.3mn), gas engines ramping to RMB12bn and SOFC to RMB3.8bn. This earnings ramp is what the 90x SOTP multiple is applied to.",
                    "textZh": "AIDC（数据中心及主电源）到2028E达到收入310亿元/净利润77亿元——占发动机分部收入26.5%、集团利润38%——由6,500台数据中心柴油机组（单价约230万元）、放量至120亿元的燃气发动机和38亿元的SOFC构成。90倍SOTP估值正是乘在这条盈利曲线上。",
                    "chips": [
                        {"k": "Actuals", "kZh": "实际数据", "v": "3y (2023–25)", "vZh": "3年 (2023–25)", "tone": "warn"},
                        {"k": "Rev CAGR 25A→28E", "kZh": "收入CAGR 25A→28E", "v": "+132%", "tone": "warn"},
                        {"k": "Net margin", "kZh": "净利率", "v": "25–27%, ~flat", "vZh": "25–27%，基本持平", "tone": "neutral"},
                        {"k": "SOTP weight", "kZh": "SOTP权重", "v": "59% of equity value", "vZh": "占股权价值59%", "tone": "warn"},
                    ],
                },
                {
                    "src": "UBS",
                    "text": "Baudouin data-center gensets reach RMB20.1bn revenue / RMB4.8bn net profit by 2030E on 6,621 units, with Weichai's DC market share peaking near 31% and net margin fading from 30% to 24%. UBS models diesel gensets only (no gas engines, no SOFC) and values the result at 15x 2030E, discounted back at 9%.",
                    "textZh": "博杜安数据中心机组到2030E达到收入201亿元/净利润48亿元（6,621台），潍柴数据中心市场份额见顶于约31%，净利率从30%递减至24%。瑞银只对柴油机组建模（不含燃气发动机和SOFC），并对2030E结果按15倍估值、以9%折现。",
                    "chips": [
                        {"k": "Actuals", "kZh": "实际数据", "v": "3y (2023–25)", "vZh": "3年 (2023–25)", "tone": "warn"},
                        {"k": "Rev CAGR 25A→30E", "kZh": "收入CAGR 25A→30E", "v": "+48%", "tone": "neutral"},
                        {"k": "Margin path", "kZh": "利润率路径", "v": "fading 30%→24%", "vZh": "30%→24%递减", "tone": "neutral"},
                        {"k": "Scope", "kZh": "口径", "v": "diesel gensets only", "vZh": "仅柴油机组", "tone": "warn"},
                    ],
                },
            ],
            "charts": [
                {
                    "title": "Data-center diesel genset volumes",
                    "titleZh": "数据中心柴油机组销量",
                    "unit": "units",
                    "compare": [0, 1],
                    "series": [
                        {"src": "MS", "name": "Morgan Stanley", "nameZh": "摩根士丹利",
                         "sheet": "Engine", "row": 130, "col0": 3, "n": 22, "y0": 2007, "slot": 1},
                        {"src": "UBS", "name": "UBS", "nameZh": "瑞银",
                         "sheet": "Power", "row": 10, "col0": 3, "n": 18, "y0": 2013, "slot": 2},
                    ],
                    "note": "Identical 2026E unit assumptions; they diverge from 2027E.",
                    "noteZh": "两家2026E台数假设完全一致；自2027E起分化。",
                },
                {
                    "title": "AIDC revenue — scope matters",
                    "titleZh": "AIDC收入——口径决定差异",
                    "unit": "rmbmn",
                    "compare": [1, 2],   # like-for-like: MS diesel-only vs UBS
                    "series": [
                        {"src": "MS", "name": "MS — all AIDC (incl. gas + SOFC)", "nameZh": "大摩——AIDC合计（含燃气+SOFC）",
                         "sheet": "Engine", "row": 85, "col0": 3, "n": 22, "y0": 2007, "scale": 1e-3, "slot": 3},
                        {"src": "MS", "name": "MS — DC diesel only", "nameZh": "大摩——仅数据中心柴油机",
                         "sheet": "Engine", "row": 78, "col0": 3, "n": 22, "y0": 2007, "scale": 1e-3, "slot": 1},
                        {"src": "UBS", "name": "UBS — DC gensets (diesel)", "nameZh": "瑞银——数据中心机组（柴油）",
                         "sheet": "Power", "row": 15, "col0": 3, "n": 18, "y0": 2013, "scale": 100, "slot": 2},
                    ],
                    "note": "On matching scope (diesel) the banks land within ~1% by 2028E; MS's extra RMB15.8bn is gas engines + SOFC that UBS does not model.",
                    "noteZh": "口径一致（柴油）时两家2028E收入相差约1%；大摩多出的约158亿元来自瑞银未建模的燃气发动机与SOFC。",
                },
                {
                    "title": "AIDC net profit — the SOTP earnings base",
                    "titleZh": "AIDC净利润——SOTP估值的盈利基础",
                    "unit": "rmbmn",
                    "compare": [0, 1],
                    "series": [
                        {"src": "MS", "name": "Morgan Stanley", "nameZh": "摩根士丹利",
                         "sheet": "Engine", "sumRows": [212, 214, 215], "col0": 3, "n": 22, "y0": 2007, "scale": 1e-3, "slot": 1},
                        {"src": "UBS", "name": "UBS", "nameZh": "瑞银",
                         "sheet": "Power", "row": 18, "col0": 3, "n": 18, "y0": 2013, "scale": 100, "slot": 2},
                    ],
                    "note": "MS applies 90x to its 2026E figure; UBS applies 15x to its 2030E figure discounted back at 9%.",
                    "noteZh": "大摩对其2026E数字给90倍；瑞银对其2030E数字给15倍并按9%折现。",
                },
            ],
            "drivers": [
                {
                    "src": "MS", "sheet": "Engine", "col0": 3, "n": 22, "y0": 2007,
                    "rows": [
                        {"name": "DC diesel genset volume", "nameZh": "数据中心柴油机组销量", "row": 130, "unit": "units", "unitZh": "台"},
                        {"name": "DC diesel ASP", "nameZh": "数据中心柴油机组单价", "row": 190, "scale": 1e-3, "unit": "RMB mn / unit", "unitZh": "百万元/台"},
                        {"name": "Gas engine volume (primary power)", "nameZh": "燃气发动机销量（主电源）", "row": 134, "unit": "units", "unitZh": "台"},
                        {"name": "Gas engine ASP", "nameZh": "燃气发动机单价", "row": 192, "scale": 1e-3, "unit": "RMB mn / unit", "unitZh": "百万元/台"},
                        {"name": "SOFC shipments", "nameZh": "SOFC出货量", "row": 137, "unit": "MW", "unitZh": "兆瓦"},
                        {"name": "AIDC diesel net margin", "nameZh": "AIDC柴油机净利率", "row": 220, "pct": True, "unit": "%", "unitZh": "%"},
                    ],
                },
                {
                    "src": "UBS", "sheet": "Power", "col0": 3, "n": 18, "y0": 2013,
                    "rows": [
                        {"name": "AIDC genset volume", "nameZh": "AIDC机组销量", "row": 10, "unit": "units", "unitZh": "台"},
                        {"name": "AIDC ASP", "nameZh": "AIDC机组单价", "row": 11, "scale": 0.01, "unit": "RMB mn / unit", "unitZh": "百万元/台"},
                        {"name": "DC genset market demand", "nameZh": "数据中心机组市场规模", "row": 27, "unit": "units", "unitZh": "台"},
                        {"name": "Weichai DC market share", "nameZh": "潍柴数据中心份额", "row": 28, "pct": True, "unit": "%", "unitZh": "%"},
                        {"name": "AIDC net margin", "nameZh": "AIDC净利率", "row": 19, "pct": True, "unit": "%", "unitZh": "%"},
                    ],
                },
            ],
        },
    ],

    # Section explainers — shown above the charts for the active section.
    # Keys: category names (as in metrics), plus 'segments' and 'sotp'.
    "summaries": {
        "Income Statement": {
            "en": "Headline P&L lines from both models. History is identical — both banks transcribe reported financials — so any gap from 2026E onwards is pure assumption. MS runs above UBS on revenue and net profit mainly because it models a much faster ramp in AIDC (data-center power) engines inside the engine business; by 2028E the models are ~RMB27bn apart on revenue and ~RMB3bn on net profit.",
            "zh": "两家模型的损益表主线。历史数据完全一致（均来自公司披露的财报），因此2026E之后的任何差异都纯粹来自假设。大摩的收入和净利润高于瑞银，主要因为其假设发动机业务中AIDC（数据中心电力）发动机放量更快；到2028E两个模型的收入差约270亿元、净利润差约30亿元。",
        },
        "Growth & Margins": {
            "en": "Weichai is a truck-cycle business and it shows here: gross margin troughed at 17.8% in 2022 when heavy-truck volumes collapsed, then recovered with the cycle. Both banks forecast a stable ~22% gross margin, so the earnings growth they model comes from revenue mix — AIDC / large-bore engines earn ~26–27% gross margin versus ~9% for trucks, so every point of mix shift toward AIDC lifts the blended margin.",
            "zh": "潍柴是典型的重卡周期股，这里看得最清楚：2022年重卡销量崩塌时毛利率触底17.8%，之后随周期修复。两家银行均预测毛利率稳定在约22%，因此模型中的盈利增长来自收入结构——AIDC/大缸径发动机毛利率约26–27%，重卡仅约9%，结构每向AIDC倾斜一分，综合毛利率就抬升一分。",
        },
        "Per Share": {
            "en": "EPS, book value and dividends. The dividend is a core part of the story: the payout ratio has climbed from ~25% in 2019 to ~58% for 2025, and UBS assumes it keeps rising to 68% by 2030E. Compare DPS across the two banks to see how differently they treat capital return.",
            "zh": "每股收益、每股净资产与股利。分红是投资故事的核心之一：股利支付率已从2019年的约25%升至2025年的约58%，瑞银假设到2030E进一步升至68%。对比两家的每股股利可见其对股东回报假设的差异。",
        },
        "Balance Sheet": {
            "en": "Weichai runs a net-cash balance sheet — cash & equivalents of ~RMB69bn against minimal debt — which funds both the capacity build-out for large-bore/AIDC engines and the rising dividend. Working-capital items (receivables, inventories, payables) are the swing factors through the truck cycle.",
            "zh": "潍柴是净现金资产负债表——货币资金约690亿元而有息负债很少——同时支撑大缸径/AIDC发动机产能扩张和不断提高的分红。应收、存货、应付等营运资金项目随重卡周期波动。",
        },
        "Cash Flow": {
            "en": "Compare operating cash flow with net profit for earnings quality — OCF has run well above net profit in most years. Investing-outflow spikes mark acquisitions (2016 KION/PSI-related) and the 2024 step-up in investment; financing outflow is increasingly dividends.",
            "zh": "将经营现金流与净利润对比可检验盈利质量——多数年份经营现金流远高于净利润。投资流出的峰值对应并购（2016年与凯傲/PSI相关）及2024年投资加码；筹资流出则越来越多地是分红。",
        },
        "Returns & Gearing": {
            "en": "Ratios from the MS model. ROE sits in a 9–12% band, structurally diluted by the large cash pile (net debt/equity is deeply negative — net cash across the whole forecast). The AIDC thesis is partly an ROE story: redeploying profits into a highly-rated growth business rather than cash.",
            "zh": "来自大摩模型的比率。ROE处于9–12%区间，被庞大的现金储备结构性摊薄（净负债/权益深度为负，即整个预测期均为净现金）。AIDC逻辑的一部分正是ROE故事：把利润投入高估值成长业务而非趴在账上。",
        },
        "Efficiency": {
            "en": "Working-capital days from the MS model. The striking feature: payable days (~190–210) run far above receivable days (~55) — Weichai is substantially funded by supplier credit. MS holds these ratios roughly flat through the forecast.",
            "zh": "大摩模型的营运资金周转天数。最显著的特征是应付账款天数（约190–210天）远高于应收账款天数（约55天）——潍柴大量占用供应商信用。大摩在预测期内假设这些比率基本持平。",
        },
        "Valuation": {
            "en": "Trading multiples from the MS model (year-end closes). Note the 2025 re-rating as the AIDC story took hold — A-share P/E moved from ~10x (2024) to ~17x, and MS's HK$47 target implies ~27x 2026E, far above the historical band. The multiple, not the earnings, is where the AIDC debate lives.",
            "zh": "大摩模型的交易估值（按年末收盘价）。注意2025年随AIDC逻辑确立的估值重估——A股市盈率从2024年的约10倍升至约17倍，大摩47港元目标价隐含约27倍2026E市盈率，远超历史区间。AIDC之争主要体现在估值倍数而非盈利上。",
        },
        "segments": {
            "en": "Segment mix is the whole thesis in one chart. Engine and KION are the two biggest blocks; the AIDC opportunity (data-center backup diesel gensets, gas engines for primary power, SOFC fuel cells) sits inside the Engine segment — which is why Engine gross margin (~26–27%) runs three times the truck margin (~9%). The banks cut segments differently: UBS breaks out agri machinery (Lovol) and nets eliminations into Others.",
            "zh": "分部结构一图看懂整个投资逻辑。发动机和凯傲是最大的两块；AIDC机会（数据中心备用柴油发电机组、主电源燃气发动机、SOFC燃料电池）藏在发动机分部内——这也是发动机毛利率（约26–27%）三倍于重卡（约9%）的原因。两家分部口径不同：瑞银单列农机（雷沃），并将内部抵消并入“其他”。",
        },
        "aidc": {
            "en": "Both banks build the AIDC (AI data-center power) business bottom-up: units × ASP × margin. There are only ~3 years of actuals (2023–25), so almost everything on this page is assumption — read the indicator chips before the lines. Key finding: on like-for-like diesel gensets the two banks nearly agree (2028E revenue within ~1%, identical 2026E unit counts); MS's much larger AIDC number is gas engines and SOFC that UBS doesn't model at all, and the valuation gap (90x vs 15x discounted) does the rest.",
            "zh": "两家银行都自下而上地对AIDC（AI数据中心电力）业务建模：台数×单价×利润率。实际数据只有约3年（2023–25），因此本页几乎全部是假设——看曲线前先看指标标签。关键发现：在口径一致的柴油机组上，两家几乎一致（2028E收入相差约1%，2026E台数假设完全相同）；大摩更大的AIDC数字来自瑞银完全未建模的燃气发动机和SOFC，其余差距则来自估值倍数（90倍对15倍折现）。",
        },
        "sotp": {
            "en": "Sum-of-the-parts is where the two banks' targets split, and AIDC is the entire argument. Both value the traditional engine/truck/gearbox business at 9–13x 2026E earnings and the 46.5% KION stake near market value. The gap: MS treats data-center power as an AI-infrastructure growth asset — 90x its 2026E NP of RMB2.4bn = RMB213bn, 59% of group equity value (it models AIDC profit reaching RMB7.7bn, 38% of group, by 2028E). UBS instead takes 2030E power-gen profit of RMB9.8bn, caps it at 15x and discounts back at 9% = RMB114bn — and cut that value 24% in its April revision. That one line explains nearly all of the HK$47 vs HK$32 target gap.",
            "zh": "分部加总估值是两家目标价分歧的所在，而AIDC就是全部争论。两家对传统发动机/重卡/变速箱业务均按2026E盈利的9–13倍估值，对46.5%的凯傲股权按接近市值估值。差异在于：大摩把数据中心电力当作AI基础设施成长资产——2026E净利润24亿元给90倍=2,130亿元，占集团股权价值的59%（其模型中AIDC利润到2028E达77亿元、占集团38%）。瑞银则取2030E发电业务净利润98亿元，按15倍封顶再以9%折现=1,140亿元——且在4月的调整中将该值下调了24%。这一行差异几乎解释了47港元与32港元目标价的全部差距。",
        },
    },
}
