from ccxt_template.execution.simulator import PaperBroker
from ccxt_template.data.repository import Repository
from ccxt_template.logger import logger


class PortfolioManager:
    def __init__(self, broker: PaperBroker, repo: Repository):
        self._broker = broker
        self._repo = repo

    def snapshot(self) -> None:
        state = self._broker.get_portfolio_state()
        self._repo.save_portfolio_snapshot(state)
        logger.info(
            f"Portfolio | cash={state.cash:.2f} equity={state.equity:.2f} "
            f"realized_pnl={state.realized_pnl:.2f} unrealized_pnl={state.unrealized_pnl:.2f}"
        )
