"""
Agentic AI Portfolio Agent.

This agent can:
1. Answer questions about portfolios using RAG context
2. Calculate required trades for rebalancing
3. Execute rebalancing by updating the database
4. Retrieve compliance guidelines before making decisions
"""
import json
from datetime import datetime, date
from decimal import Decimal
from typing import Optional
from sqlalchemy.orm import Session

from app.models.models import (
    Client, Portfolio, Holding, Transaction, AgentAction, AssetType, TransactionType
)
from app.services.portfolio_service import get_portfolio_summary, get_client_summary
from app.services.kite_service import kite_service
from app.rag.pipeline import rag_pipeline
from app.agent.gemini_client import gemini_client
from app.config import get_settings

settings = get_settings()


class PortfolioAgent:
    """AI agent that takes actions on portfolios based on natural language instructions."""

    def __init__(self, db: Session):
        self.db = db
        self.actions_taken: list[dict] = []
        self.context_used: list[str] = []

    async def process(self, message: str, client_id: Optional[str] = None) -> dict:
        """Process a natural language message and take appropriate actions."""
        message_lower = message.lower()

        # Step 1: Determine intent
        intent = self._classify_intent(message_lower)

        # Step 2: Retrieve relevant RAG context
        rag_context = self._retrieve_context(message)

        # Step 3: Execute based on intent
        if intent == "rebalance":
            result = await self._handle_rebalance(message, client_id, rag_context)
        elif intent == "query_portfolio":
            result = await self._handle_portfolio_query(message, client_id)
        elif intent == "compliance_check":
            result = await self._handle_compliance_check(message, rag_context)
        elif intent == "risk_analysis":
            result = await self._handle_risk_analysis(client_id)
        elif intent == "market_update":
            result = await self._handle_market_update(client_id)
        else:
            result = await self._handle_general_query(message, client_id, rag_context)

        # Log the action
        self._log_action(
            client_id=client_id,
            action_type=intent,
            description=message,
            result=result,
        )

        return {
            "response": result,
            "actions_taken": self.actions_taken,
            "context_used": self.context_used,
        }

    def _classify_intent(self, message: str) -> str:
        """Classify the user's intent from their message."""
        rebalance_keywords = ["rebalance", "reallocate", "adjust allocation", "change allocation", "shift to"]
        portfolio_keywords = ["portfolio", "holdings", "show me", "what is", "how is", "performance", "xirr", "cagr", "returns"]
        compliance_keywords = ["compliance", "sebi", "regulation", "guideline", "circular", "rule"]
        risk_keywords = ["risk", "exposure", "concentration", "diversif"]
        market_keywords = ["market", "price", "refresh", "update price", "latest price"]

        if any(k in message for k in rebalance_keywords):
            return "rebalance"
        if any(k in message for k in compliance_keywords):
            return "compliance_check"
        if any(k in message for k in risk_keywords):
            return "risk_analysis"
        if any(k in message for k in market_keywords):
            return "market_update"
        if any(k in message for k in portfolio_keywords):
            return "query_portfolio"
        return "general"

    def _retrieve_context(self, question: str) -> list[dict]:
        """Retrieve relevant documents from RAG pipeline."""
        results = rag_pipeline.query(question, n_results=3)
        for r in results:
            self.context_used.append(
                f"[{r['metadata'].get('doc_type', 'unknown')}] "
                f"{r['content'][:200]}... (relevance: {r['relevance_score']})"
            )
        return results

    async def _generate_llm_response(
        self, user_message: str, structured_data: str, task_context: str, fallback: str
    ) -> str:
        """Generate an LLM-powered response, falling back to structured data if unavailable."""
        llm_response = await gemini_client.generate_response(
            user_message=user_message,
            structured_data=structured_data,
            task_context=task_context,
        )
        return llm_response if llm_response else fallback

    async def _handle_rebalance(
        self, message: str, client_id: Optional[str], rag_context: list[dict]
    ) -> str:
        """Handle portfolio rebalancing requests."""
        if not client_id:
            # Try to extract client name from message
            client = self._find_client_by_name(message)
            if not client:
                return (
                    "I need to know which client to rebalance. "
                    "Please specify a client name or ID."
                )
            client_id = client.id
        else:
            client = self.db.query(Client).filter(Client.id == client_id).first()

        if not client:
            return f"Client not found with ID: {client_id}"

        # Parse target allocation from message
        target_equity, target_debt = self._parse_allocation(message)
        if target_equity is None:
            target_equity = client.target_equity_pct
            target_debt = client.target_debt_pct

        # Get current portfolio state
        summary = get_client_summary(self.db, client_id)
        if not summary.get("portfolios"):
            return f"No portfolios found for client {client.name}."

        # Check RAG context for any compliance constraints
        compliance_notes = []
        for ctx in rag_context:
            if ctx.get("metadata", {}).get("doc_type") in ("sebi_circular", "risk_guideline"):
                compliance_notes.append(ctx["content"][:300])

        # Calculate current allocation
        current_equity = 0
        current_debt = 0
        current_other = 0
        total_value = summary["total_current_value"]

        for port_summary in summary["portfolios"]:
            alloc = port_summary.get("asset_allocation_value", {})
            current_equity += alloc.get("equity", 0) + alloc.get("etf", 0)
            current_debt += alloc.get("debt", 0) + alloc.get("mutual_fund", 0)
            current_other += alloc.get("gold", 0) + alloc.get("cash", 0)

        if total_value == 0:
            return f"Client {client.name} has no portfolio value to rebalance."

        current_equity_pct = round(current_equity / total_value * 100, 2)
        current_debt_pct = round(current_debt / total_value * 100, 2)

        # Calculate required changes
        target_equity_value = total_value * target_equity / 100
        target_debt_value = total_value * target_debt / 100
        equity_change = target_equity_value - current_equity
        debt_change = target_debt_value - current_debt

        # Build the rebalancing plan
        trades = []
        if equity_change > 0:
            trades.append(f"BUY equity worth INR {abs(equity_change):,.2f}")
        elif equity_change < 0:
            trades.append(f"SELL equity worth INR {abs(equity_change):,.2f}")

        if debt_change > 0:
            trades.append(f"BUY debt instruments worth INR {abs(debt_change):,.2f}")
        elif debt_change < 0:
            trades.append(f"SELL debt instruments worth INR {abs(debt_change):,.2f}")

        # Update client's target allocation in the database
        client.target_equity_pct = target_equity
        client.target_debt_pct = target_debt
        self.db.commit()

        self.actions_taken.append({
            "action": "rebalance_calculated",
            "client": client.name,
            "current_allocation": {
                "equity": current_equity_pct,
                "debt": current_debt_pct,
            },
            "target_allocation": {
                "equity": target_equity,
                "debt": target_debt,
            },
            "trades_required": trades,
            "updated_db": True,
        })

        # Build structured data for LLM
        structured = f"""## Rebalancing Plan for {client.name}

Current Allocation: Equity {current_equity_pct}% | Debt {current_debt_pct}%
Target Allocation: Equity {target_equity}% | Debt {target_debt}%
Total Portfolio Value: INR {total_value:,.2f}

Required Trades:
"""
        for trade in trades:
            structured += f"- {trade}\n"

        if compliance_notes:
            structured += "\nCompliance Context:\n"
            for note in compliance_notes:
                structured += f"- {note[:300]}\n"

        structured += "\nNote: Target allocation has been updated in the database."

        return await self._generate_llm_response(
            user_message=message,
            structured_data=structured,
            task_context="Portfolio rebalancing — the trades have been calculated and the target allocation was updated in the database. Summarize the plan clearly.",
            fallback=structured,
        )

    async def _handle_portfolio_query(self, message: str, client_id: Optional[str]) -> str:
        """Handle portfolio queries - show holdings, XIRR, etc."""
        if not client_id:
            client = self._find_client_by_name(message)
            if not client:
                # Show all clients overview
                clients = self.db.query(Client).all()
                if not clients:
                    return "No clients found in the system."

                structured = "All Clients Overview:\n\n"
                for c in clients:
                    summary = get_client_summary(self.db, c.id)
                    structured += f"{c.name} (Risk: {c.risk_profile})\n"
                    structured += f"  Invested: INR {summary['total_invested']:,.2f}\n"
                    structured += f"  Current Value: INR {summary['total_current_value']:,.2f}\n"
                    structured += f"  P&L: {summary['total_pnl_pct']:.2f}%\n\n"

                return await self._generate_llm_response(
                    user_message=message,
                    structured_data=structured,
                    task_context="Overview of all clients and their portfolio performance.",
                    fallback=structured,
                )
            client_id = client.id

        summary = get_client_summary(self.db, client_id)
        client = self.db.query(Client).filter(Client.id == client_id).first()

        structured = f"Portfolio Summary for {client.name}:\n\n"
        structured += f"Total Invested: INR {summary['total_invested']:,.2f}\n"
        structured += f"Current Value: INR {summary['total_current_value']:,.2f}\n"
        structured += f"P&L: INR {summary['total_pnl']:,.2f} ({summary['total_pnl_pct']:.2f}%)\n\n"

        for port in summary.get("portfolios", []):
            s = port["summary"]
            structured += f"Portfolio: {port['portfolio_name']}\n"
            structured += f"  Invested: INR {s['total_invested']:,.2f}\n"
            structured += f"  Current: INR {s['total_current_value']:,.2f}\n"
            if s.get("xirr"):
                structured += f"  XIRR: {s['xirr']}%\n"
            if s.get("cagr"):
                structured += f"  CAGR: {s['cagr']}%\n"
            structured += f"  Holdings: {s['holdings_count']}\n"

            if port.get("holdings"):
                structured += "  Top Holdings:\n"
                for h in port["holdings"][:10]:
                    structured += (
                        f"    {h['symbol']} ({h['name']}): "
                        f"Qty {h['quantity']:.0f}, "
                        f"Avg INR {h['avg_buy_price']:,.2f}, "
                        f"Current INR {h['current_price']:,.2f}, "
                        f"P&L {h['pnl_pct']:.1f}%\n"
                    )
            structured += "\n"

        return await self._generate_llm_response(
            user_message=message,
            structured_data=structured,
            task_context="Portfolio query — provide a clear summary of the client's portfolio performance and holdings.",
            fallback=structured,
        )

    async def _handle_compliance_check(self, message: str, rag_context: list[dict]) -> str:
        """Handle compliance-related queries using RAG context."""
        if not rag_context:
            return (
                "No compliance documents found in the system. "
                "Please upload SEBI circulars or risk guidelines first using the document upload feature."
            )

        structured = "Compliance documents retrieved:\n\n"
        for i, ctx in enumerate(rag_context, 1):
            doc_type = ctx.get("metadata", {}).get("doc_type", "unknown")
            filename = ctx.get("metadata", {}).get("filename", "unknown")
            relevance = ctx.get("relevance_score", 0)
            structured += f"Source {i}: {filename} (type: {doc_type}, relevance: {relevance:.2%})\n"
            structured += f"Content: {ctx['content'][:800]}\n\n"

        return await self._generate_llm_response(
            user_message=message,
            structured_data=structured,
            task_context="Compliance query — synthesize the retrieved SEBI circular / regulation documents into a clear, actionable answer. Cite the source documents.",
            fallback=structured,
        )

    async def _handle_risk_analysis(self, client_id: Optional[str]) -> str:
        """Analyze portfolio risk and concentration."""
        if not client_id:
            return "Please specify a client for risk analysis."

        summary = get_client_summary(self.db, client_id)
        client = self.db.query(Client).filter(Client.id == client_id).first()

        if not summary.get("portfolios"):
            return f"No portfolio data for {client.name}."

        # Gather all structured risk data
        all_holdings = []
        for port in summary["portfolios"]:
            all_holdings.extend(port.get("holdings", []))

        total_value = summary["total_current_value"]
        if total_value == 0:
            return f"No holdings to analyze for {client.name}."

        structured = f"Risk Analysis Data for {client.name}:\n\n"
        structured += f"Risk Profile: {client.risk_profile}\n"
        structured += f"Target Allocation: Equity {client.target_equity_pct}% / Debt {client.target_debt_pct}%\n"
        structured += f"Total Portfolio Value: INR {total_value:,.2f}\n\n"

        # Position concentration
        structured += "Position Concentration (top 5):\n"
        for h in sorted(all_holdings, key=lambda x: x["current_value"], reverse=True)[:5]:
            pct = h["current_value"] / total_value * 100
            flag = " [HIGH CONCENTRATION]" if pct > 20 else ""
            structured += f"  {h['symbol']}: {pct:.1f}% of portfolio (INR {h['current_value']:,.2f}){flag}\n"

        # Sector concentration
        sector_totals = {}
        for h in all_holdings:
            sector = h.get("sector", "other")
            sector_totals[sector] = sector_totals.get(sector, 0) + h["current_value"]

        structured += "\nSector Concentration:\n"
        for sector, value in sorted(sector_totals.items(), key=lambda x: x[1], reverse=True):
            pct = value / total_value * 100
            flag = " [HIGH CONCENTRATION]" if pct > 30 else ""
            structured += f"  {sector}: {pct:.1f}% (INR {value:,.2f}){flag}\n"

        # Warnings
        warnings = []
        for h in all_holdings:
            pct = h["current_value"] / total_value * 100
            if pct > 25:
                warnings.append(f"Single-stock concentration risk: {h['symbol']} at {pct:.1f}%")
        for sector, value in sector_totals.items():
            pct = value / total_value * 100
            if pct > 40:
                warnings.append(f"Sector concentration risk: {sector} at {pct:.1f}%")

        if warnings:
            structured += "\nWarnings:\n"
            for w in warnings:
                structured += f"  - {w}\n"
        else:
            structured += "\nNo concentration warnings. Portfolio appears well-diversified.\n"

        return await self._generate_llm_response(
            user_message=f"Analyze risk for {client.name}",
            structured_data=structured,
            task_context="Risk analysis — provide a narrative assessment of portfolio risk, concentration issues, and recommendations based on the client's risk profile.",
            fallback=structured,
        )

    async def _handle_market_update(self, client_id: Optional[str]) -> str:
        """Refresh market prices for holdings."""
        if client_id:
            portfolios = self.db.query(Portfolio).filter(Portfolio.client_id == client_id).all()
        else:
            portfolios = self.db.query(Portfolio).all()

        total_updated = 0
        for p in portfolios:
            updated = await kite_service.refresh_holdings_prices(self.db, p.id)
            total_updated += updated

        self.actions_taken.append({
            "action": "prices_refreshed",
            "holdings_updated": total_updated,
        })

        return f"Market prices refreshed for {total_updated} holdings across {len(portfolios)} portfolios."

    async def _handle_general_query(
        self, message: str, client_id: Optional[str], rag_context: list[dict]
    ) -> str:
        """Handle general queries with RAG context if available."""
        structured = ""

        if rag_context:
            structured += "Relevant documents found:\n\n"
            for ctx in rag_context[:2]:
                structured += f"- {ctx['content'][:500]}\n\n"

        if client_id:
            summary = get_client_summary(self.db, client_id)
            structured += f"\nCurrent client portfolio value: INR {summary['total_current_value']:,.2f}\n"

        capabilities = (
            "Available capabilities:\n"
            "- Portfolio queries: 'Show me John\'s portfolio'\n"
            "- Rebalancing: 'Rebalance to 60% equity / 40% debt'\n"
            "- Risk analysis: 'Analyze risk for client'\n"
            "- Compliance checks: 'What do SEBI guidelines say about...'\n"
            "- Market updates: 'Refresh market prices'\n"
        )

        if not structured:
            structured = capabilities

        return await self._generate_llm_response(
            user_message=message,
            structured_data=structured + "\n" + capabilities,
            task_context="General query — answer the user's question conversationally. If the question doesn't match a specific feature, describe what you can do.",
            fallback=capabilities if not structured else structured,
        )

    def _find_client_by_name(self, message: str) -> Optional[Client]:
        """Try to find a client mentioned in the message."""
        clients = self.db.query(Client).all()
        for client in clients:
            if client.name.lower() in message.lower():
                return client
            # Also check first name
            first_name = client.name.split()[0].lower()
            if first_name in message.lower() and len(first_name) > 2:
                return client
        return None

    def _parse_allocation(self, message: str) -> tuple[Optional[float], Optional[float]]:
        """Parse target allocation percentages from message."""
        import re

        # Pattern: "60% equity / 40% debt" or "60/40 equity debt"
        patterns = [
            r"(\d+)\s*%?\s*(?:equity|eq).*?(\d+)\s*%?\s*(?:debt|de|fixed)",
            r"(\d+)\s*/\s*(\d+)",
            r"(\d+)\s*%\s*equity",
        ]

        for pattern in patterns:
            match = re.search(pattern, message.lower())
            if match:
                equity = float(match.group(1))
                debt = float(match.group(2)) if match.lastindex >= 2 else (100 - equity)
                if 0 <= equity <= 100 and 0 <= debt <= 100:
                    return equity, debt
        return None, None

    def _log_action(self, client_id: Optional[str], action_type: str, description: str, result: str):
        """Log the agent action to the database."""
        action = AgentAction(
            client_id=client_id,
            action_type=action_type,
            description=description,
            parameters=json.dumps({"actions": self.actions_taken}),
            result=result[:2000],  # Truncate long results
            status="completed",
        )
        self.db.add(action)
        self.db.commit()
