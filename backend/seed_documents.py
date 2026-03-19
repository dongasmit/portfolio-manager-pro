"""Sample SEBI compliance document for RAG testing."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import SessionLocal
from app.models.models import Document
from app.rag.pipeline import rag_pipeline


SEBI_CIRCULAR_TEXT = """
SECURITIES AND EXCHANGE BOARD OF INDIA
CIRCULAR NO. SEBI/HO/IMD/DF3/CIR/P/2024/001

Subject: Risk Management Framework for Portfolio Management Services

1. APPLICABILITY
This circular applies to all SEBI-registered Portfolio Managers offering discretionary
and non-discretionary portfolio management services.

2. ASSET ALLOCATION GUIDELINES
2.1 Equity Exposure Limits:
- Conservative portfolios: Maximum 40% equity exposure
- Moderate portfolios: Maximum 65% equity exposure
- Aggressive portfolios: Maximum 85% equity exposure

2.2 Single Stock Concentration:
- No single stock should exceed 15% of the total portfolio value
- No single sector should exceed 30% of the total portfolio value

2.3 Debt Allocation Requirements:
- Minimum 10% allocation to sovereign or AAA-rated debt instruments for all portfolio types
- Conservative portfolios must maintain minimum 50% in debt instruments

3. RISK MONITORING
3.1 Portfolio Managers must monitor the following risk metrics:
- Value at Risk (VaR) at 95% confidence level
- Maximum drawdown monitoring with 20% threshold
- Tracking error relative to benchmark indices

3.2 Quarterly rebalancing is mandatory when actual allocation deviates by more than 5%
from target allocation.

4. CLIENT SUITABILITY
4.1 Risk profiling must be conducted annually for all clients
4.2 Investment recommendations must align with the client's documented risk profile
4.3 Any deviation from the target allocation must be documented and communicated to the client

5. REPORTING REQUIREMENTS
5.1 Monthly portfolio statements must include:
- Current asset allocation breakdown
- XIRR and CAGR calculations
- Benchmark comparison
- Risk metrics summary

6. COMPLIANCE TIMELINE
This circular is effective from Q3 FY2024-25. All portfolio managers must ensure
compliance within 90 days of issuance.
"""

EARNINGS_REPORT_TEXT = """
Q3 FY2025 EARNINGS SUMMARY - NIFTY 50 KEY COMPANIES

TECHNOLOGY SECTOR:
- TCS: Revenue INR 64,259 Cr (+5.2% YoY), PAT INR 12,380 Cr (+8.1% YoY)
  Guidance: Maintain double-digit growth outlook. Strong deal pipeline of $12.2B TCV.
  Risk: High attrition at 13.2%, currency headwinds from strong dollar.

- Infosys: Revenue INR 41,764 Cr (+6.1% YoY), PAT INR 7,125 Cr (+6.5% YoY)
  Guidance: Revised upward to 4-4.5% CC growth. Large deal wins at $4.1B.
  Risk: Regulatory uncertainty, AI-driven disruption concerns.

FINANCIAL SECTOR:
- HDFC Bank: NII INR 30,110 Cr (+10.1% YoY), PAT INR 16,736 Cr (+35.3% YoY)
  Asset quality: GNPA at 1.24%, NNPA at 0.31% (improved).
  Risk: Deposit growth moderation, competitive pressure on margins.

- ICICI Bank: NII INR 20,371 Cr (+9.8% YoY), PAT INR 11,792 Cr (+18.5% YoY)
  Strong retail loan growth at 15.6%. Digital transactions up 42%.
  Risk: Unsecured lending book needs monitoring.

ENERGY SECTOR:
- Reliance Industries: Revenue INR 2,43,865 Cr (+7.3% YoY), PAT INR 18,951 Cr (+11.7% YoY)
  Jio subscribers at 482M. Retail expansion continues with 18,946 stores.
  Risk: Petrochemical margin compression, heavy capex in green energy.

CONSUMER SECTOR:
- Hindustan Unilever: Revenue INR 16,064 Cr (+2.1% YoY), PAT INR 2,984 Cr (+3.4% YoY)
  Volume growth recovery at 4%. Premium segment driving growth.
  Risk: Rural demand recovery slower than expected, input cost inflation.

- ITC: Revenue INR 19,446 Cr (+6.8% YoY), PAT INR 5,334 Cr (+8.2% YoY)
  FMCG business achieving breakeven. Hotel segment showing strong recovery.
  Risk: Tobacco regulation risk, ESG-related investor concerns.

MARKET OUTLOOK:
- Nifty 50 trading at 22.5x forward PE - slightly above historical average
- FII outflows continue but DII flows remain strong
- Earnings growth expectation: 12-14% for FY25
- Key risks: Global recession fears, oil price volatility, geopolitical tensions
"""


def seed_documents():
    db = SessionLocal()

    # Check if already seeded
    if db.query(Document).first():
        print("Documents already exist. Skipping.")
        db.close()
        return

    # SEBI Circular
    doc1 = Document(
        id="doc-sebi-001",
        filename="SEBI_Risk_Management_Circular_2024.txt",
        doc_type="sebi_circular",
        content_summary=SEBI_CIRCULAR_TEXT[:500],
    )
    db.add(doc1)
    db.flush()

    chunks1 = rag_pipeline.ingest_text(
        "doc-sebi-001",
        SEBI_CIRCULAR_TEXT,
        {"doc_id": "doc-sebi-001", "doc_type": "sebi_circular", "filename": "SEBI_Risk_Management_Circular_2024.txt"},
    )
    doc1.chunk_count = chunks1

    # Earnings Report
    doc2 = Document(
        id="doc-earnings-001",
        filename="Q3_FY2025_Earnings_Summary.txt",
        doc_type="earnings_report",
        content_summary=EARNINGS_REPORT_TEXT[:500],
    )
    db.add(doc2)
    db.flush()

    chunks2 = rag_pipeline.ingest_text(
        "doc-earnings-001",
        EARNINGS_REPORT_TEXT,
        {"doc_id": "doc-earnings-001", "doc_type": "earnings_report", "filename": "Q3_FY2025_Earnings_Summary.txt"},
    )
    doc2.chunk_count = chunks2

    db.commit()
    db.close()
    print(f"Documents seeded: SEBI circular ({chunks1} chunks), Earnings report ({chunks2} chunks)")


if __name__ == "__main__":
    seed_documents()
