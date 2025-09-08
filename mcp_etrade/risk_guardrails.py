"""Risk management guardrails for order placement."""

from typing import Dict, Any, Optional, Tuple


class RiskGuardrails:
    """Risk management validation for trading operations."""
    
    def __init__(self):
        self.daily_trades = {}  # Track daily trades per account
        self.daily_risk = {}    # Track daily risk per account
        self.daily_losses = {}  # Track actual daily losses per account
    
    def validate_order_risk(
        self, 
        account_id: str,
        order_value: float,
        risk_amount: float,
        account_balance: float,
        risk_percentage: float = 1.0,
        current_daily_loss: float = 0.0
    ) -> Tuple[bool, str]:
        """
        Validate if order meets risk management criteria.
        
        Args:
            current_daily_loss: Actual losses so far today (from Colosseum)
        
        Returns: (is_valid, error_message)
        """
        max_daily_risk = account_balance * (risk_percentage / 100)
        
        # Get current daily risk for account
        current_daily_risk = self.daily_risk.get(account_id, 0.0)
        
        # Total exposure = potential risk + actual losses
        total_daily_exposure = current_daily_risk + risk_amount + current_daily_loss
        
        if total_daily_exposure > max_daily_risk:
            return False, f"Order would exceed daily risk limit. Current risk: ${current_daily_risk:.2f}, Actual losses: ${current_daily_loss:.2f}, Proposed: ${risk_amount:.2f}, Max: ${max_daily_risk:.2f}"
        
        # Check if order value is reasonable relative to account size
        if order_value > account_balance * 0.5:  # No single order > 50% of account
            return False, f"Order value ${order_value:.2f} exceeds 50% of account balance ${account_balance:.2f}"
        
        return True, "Order passes risk validation"
    
    def record_trade(self, account_id: str, risk_amount: float):
        """Record a trade for daily risk tracking."""
        if account_id not in self.daily_risk:
            self.daily_risk[account_id] = 0.0
        
        self.daily_risk[account_id] += risk_amount
    
    def record_actual_loss(self, account_id: str, loss_amount: float):
        """Record actual loss (called by Colosseum when trade closes)."""
        if account_id not in self.daily_losses:
            self.daily_losses[account_id] = 0.0
        
        self.daily_losses[account_id] += loss_amount
    
    def get_daily_risk_status(self, account_id: str, account_balance: float, risk_percentage: float = 1.0, current_daily_loss: float = 0.0) -> Dict[str, Any]:
        """Get current daily risk status for an account."""
        max_daily_risk = account_balance * (risk_percentage / 100)
        current_risk = self.daily_risk.get(account_id, 0.0)
        tracked_losses = self.daily_losses.get(account_id, 0.0)
        
        # Use the higher of tracked losses or provided current loss
        actual_losses = max(tracked_losses, current_daily_loss)
        
        total_exposure = current_risk + actual_losses
        remaining_risk = max_daily_risk - total_exposure
        
        return {
            "accountId": account_id,
            "maxDailyRisk": max_daily_risk,
            "currentDailyRisk": current_risk,
            "actualDailyLosses": actual_losses,
            "totalDailyExposure": total_exposure,
            "remainingDailyRisk": remaining_risk,
            "riskUtilization": (total_exposure / max_daily_risk) * 100 if max_daily_risk > 0 else 0,
            "canTrade": remaining_risk > 0
        }
    
    def reset_daily_risk(self, account_id: str):
        """Reset daily risk tracking (call at market open)."""
        if account_id in self.daily_risk:
            self.daily_risk[account_id] = 0.0
        if account_id in self.daily_losses:
            self.daily_losses[account_id] = 0.0


# Global instance for the server
risk_manager = RiskGuardrails()
