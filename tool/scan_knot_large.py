import csv
import sys
from dataclasses import dataclass

sys.path.insert(0, ".")

from src.models import Candle
from src.patterns import PATTERN_LIBRARY


DATA_FILE = "data/1000PEPE_USDT_1m_1year.csv"

STARTING_CAPITAL = 10.00

RISK_PERCENT = 0.01
MAX_LEVERAGE = 10.0

FEE_RATE = 0.0005
SLIPPAGE_RATE = 0.0002

TARGETS_R = [1.0, 2.0, 3.0]

MAX_HOLDING_CANDLES = 60

ACTIVE_PATTERNS = [
    "KNOT",
    "THREE_CANDLE_MOMENTUM",
]


@dataclass
class Position:
    pattern_name: str
    direction: str
    entry_index: int
    entry_price: float
    stop_price: float
    risk_per_unit: float
    risk_amount: float
    target_price: float
    quantity: float
    entry_fee: float
    notional: float


def load_candles():
    candles = []

    with open(DATA_FILE, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            candles.append(
                Candle(
                    timestamp=int(row["timestamp"]),
                    open=float(row["open"]),
                    high=float(row["high"]),
                    low=float(row["low"]),
                    close=float(row["close"]),
                    volume=float(row["volume"]),
                )
            )

    return candles


def get_window_size(pattern_name):
    if pattern_name == "THREE_CANDLE_MOMENTUM":
        return 3

    return 4


def get_direction(pattern_name, window):

    if pattern_name == "KNOT":
        return "SHORT"

    if pattern_name == "THREE_CANDLE_MOMENTUM":

        if window[-1].close > window[-1].open:
            return "LONG"

        if window[-1].close < window[-1].open:
            return "SHORT"

    return None


def apply_entry_slippage(price, direction):

    if direction == "LONG":
        return price * (1 + SLIPPAGE_RATE)

    return price * (1 - SLIPPAGE_RATE)


def apply_exit_slippage(price, direction):

    if direction == "LONG":
        return price * (1 - SLIPPAGE_RATE)

    return price * (1 + SLIPPAGE_RATE)


def calculate_open_notional(open_positions):

    return sum(
        position.notional
        for position in open_positions
    )


def create_position(
    pattern_name,
    window,
    market_entry_price,
    capital,
    target_r,
    entry_index,
    open_positions,
):

    direction = get_direction(
        pattern_name,
        window,
    )

    if direction is None:
        return None

    entry_price = apply_entry_slippage(
        market_entry_price,
        direction,
    )

    if direction == "LONG":

        stop_price = min(
            candle.low for candle in window
        )

        risk_per_unit = (
            entry_price - stop_price
        )

    else:

        stop_price = max(
            candle.high for candle in window
        )

        risk_per_unit = (
            stop_price - entry_price
        )

    if risk_per_unit <= 0:
        return None

    # ------------------------------------------------------
    # Desired position based on 1% account risk
    # ------------------------------------------------------

    risk_amount = capital * RISK_PERCENT

    risk_based_quantity = (
        risk_amount / risk_per_unit
    )

    # ------------------------------------------------------
    # Maximum portfolio notional
    # ------------------------------------------------------

    maximum_portfolio_notional = (
        capital * MAX_LEVERAGE
    )

    current_open_notional = (
        calculate_open_notional(
            open_positions
        )
    )

    remaining_notional = (
        maximum_portfolio_notional
        - current_open_notional
    )

    if remaining_notional <= 0:
        return None

    # Quantity allowed by leverage.
    leverage_limited_quantity = (
        remaining_notional / entry_price
    )

    quantity = min(
        risk_based_quantity,
        leverage_limited_quantity,
    )

    if quantity <= 0:
        return None

    actual_risk_amount = (
        quantity * risk_per_unit
    )

    if direction == "LONG":

        target_price = (
            entry_price
            + risk_per_unit * target_r
        )

    else:

        target_price = (
            entry_price
            - risk_per_unit * target_r
        )

    notional = (
        quantity * entry_price
    )

    entry_fee = (
        notional * FEE_RATE
    )

    return Position(
        pattern_name=pattern_name,
        direction=direction,
        entry_index=entry_index,
        entry_price=entry_price,
        stop_price=stop_price,
        risk_per_unit=risk_per_unit,
        risk_amount=actual_risk_amount,
        target_price=target_price,
        quantity=quantity,
        entry_fee=entry_fee,
        notional=notional,
    )


def close_position(
    position,
    market_exit_price,
):

    exit_price = apply_exit_slippage(
        market_exit_price,
        position.direction,
    )

    if position.direction == "LONG":

        price_pnl = (
            exit_price
            - position.entry_price
        ) * position.quantity

    else:

        price_pnl = (
            position.entry_price
            - exit_price
        ) * position.quantity

    exit_notional = (
        position.quantity * exit_price
    )

    exit_fee = (
        exit_notional * FEE_RATE
    )

    total_fees = (
        position.entry_fee
        + exit_fee
    )

    net_pnl = (
        price_pnl
        - total_fees
    )

    return net_pnl, total_fees


def simulate(
    candles,
    pattern_name,
    target_r,
):

    capital = STARTING_CAPITAL

    open_positions = []
    completed_trades = []

    total_fees = 0.0

    pattern_count = 0
    skipped_leverage = 0

    peak_capital = capital
    max_drawdown = 0.0

    max_simultaneous_positions = 0
    max_total_notional = 0.0

    pattern_function = PATTERN_LIBRARY[
        pattern_name
    ]

    window_size = get_window_size(
        pattern_name
    )

    for index in range(len(candles)):

        current_candle = candles[index]

        # ==================================================
        # 1. MANAGE EXISTING POSITIONS
        # ==================================================

        remaining_positions = []

        for position in open_positions:

            candles_held = (
                index - position.entry_index
            )

            exit_market_price = None
            result = None

            if position.direction == "LONG":

                stop_hit = (
                    current_candle.low
                    <= position.stop_price
                )

                target_hit = (
                    current_candle.high
                    >= position.target_price
                )

                # Conservative assumption:
                # if both are touched on the same candle,
                # stop is treated as first.
                if stop_hit:

                    exit_market_price = (
                        position.stop_price
                    )

                    result = "LOSS"

                elif target_hit:

                    exit_market_price = (
                        position.target_price
                    )

                    result = "WIN"

            else:

                stop_hit = (
                    current_candle.high
                    >= position.stop_price
                )

                target_hit = (
                    current_candle.low
                    <= position.target_price
                )

                if stop_hit:

                    exit_market_price = (
                        position.stop_price
                    )

                    result = "LOSS"

                elif target_hit:

                    exit_market_price = (
                        position.target_price
                    )

                    result = "WIN"

            # ==================================================
            # TIMEOUT
            # ==================================================

            if (
                result is None
                and candles_held >= MAX_HOLDING_CANDLES
            ):

                exit_market_price = (
                    current_candle.close
                )

                result = "TIMEOUT"

            # ==================================================
            # CLOSE POSITION
            # ==================================================

            if result is not None:

                pnl, fees = close_position(
                    position,
                    exit_market_price,
                )

                capital += pnl

                total_fees += fees

                completed_trades.append(
                    {
                        "pattern": position.pattern_name,
                        "result": result,
                        "pnl": pnl,
                        "risk": position.risk_amount,
                        "notional": position.notional,
                    }
                )

            else:

                remaining_positions.append(
                    position
                )

        open_positions = remaining_positions

        # ==================================================
        # 2. FIND NEW SIGNAL
        # ==================================================

        if index >= len(candles) - 1:
            continue

        if index + 1 < window_size:
            continue

        window = candles[
            index + 1 - window_size:
            index + 1
        ]

        if not pattern_function(window):
            continue

        pattern_count += 1

        entry_index = index + 1

        market_entry_price = candles[
            entry_index
        ].open

        position = create_position(
            pattern_name=pattern_name,
            window=window,
            market_entry_price=market_entry_price,
            capital=capital,
            target_r=target_r,
            entry_index=entry_index,
            open_positions=open_positions,
        )

        if position is None:
            skipped_leverage += 1
            continue

        # Entry fee immediately reduces account balance.
        capital -= position.entry_fee

        total_fees += position.entry_fee

        open_positions.append(
            position
        )

        max_simultaneous_positions = max(
            max_simultaneous_positions,
            len(open_positions),
        )

        total_open_notional = (
            calculate_open_notional(
                open_positions
            )
        )

        max_total_notional = max(
            max_total_notional,
            total_open_notional,
        )

        # ==================================================
        # 3. DRAWDOWN
        # ==================================================

        if capital > peak_capital:
            peak_capital = capital

        drawdown = (
            (peak_capital - capital)
            / peak_capital
        )

        max_drawdown = max(
            max_drawdown,
            drawdown,
        )

        if capital <= 0:
            break

    # ======================================================
    # FORCE CLOSE REMAINING POSITIONS
    # ======================================================

    if candles:

        final_price = candles[-1].close

        for position in open_positions:

            pnl, fees = close_position(
                position,
                final_price,
            )

            capital += pnl

            total_fees += fees

            completed_trades.append(
                {
                    "pattern": position.pattern_name,
                    "result": "END_OF_DATA",
                    "pnl": pnl,
                    "risk": position.risk_amount,
                    "notional": position.notional,
                }
            )

    return (
        capital,
        completed_trades,
        pattern_count,
        skipped_leverage,
        max_drawdown,
        max_simultaneous_positions,
        max_total_notional,
        total_fees,
    )


def print_result(
    target_r,
    final_capital,
    trades,
    pattern_count,
    skipped_leverage,
    max_drawdown,
    max_positions,
    max_total_notional,
    total_fees,
):

    wins = sum(
        1
        for trade in trades
        if trade["result"] == "WIN"
    )

    losses = sum(
        1
        for trade in trades
        if trade["result"] == "LOSS"
    )

    timeouts = sum(
        1
        for trade in trades
        if trade["result"] == "TIMEOUT"
    )

    end_of_data = sum(
        1
        for trade in trades
        if trade["result"] == "END_OF_DATA"
    )

    total_pnl = (
        final_capital
        - STARTING_CAPITAL
    )

    return_percent = (
        total_pnl
        / STARTING_CAPITAL
    ) * 100

    decided = wins + losses

    if decided > 0:

        win_rate = (
            wins / decided
        ) * 100

    else:

        win_rate = 0.0

    print()
    print(
        f"  {target_r:.0f}R"
    )

    print(
        f"    Final capital         : ${final_capital:.4f}"
    )

    print(
        f"    Return                : {return_percent:.2f}%"
    )

    print(
        f"    Trades                : {len(trades):,}"
    )

    print(
        f"    Pattern occurrences   : {pattern_count:,}"
    )

    print(
        f"    Skipped by leverage   : {skipped_leverage:,}"
    )

    print(
        f"    Wins                  : {wins:,}"
    )

    print(
        f"    Losses                : {losses:,}"
    )

    print(
        f"    Timeouts              : {timeouts:,}"
    )

    print(
        f"    End of data           : {end_of_data:,}"
    )

    print(
        f"    Win rate              : {win_rate:.2f}%"
    )

    print(
        f"    Max drawdown          : {max_drawdown * 100:.2f}%"
    )

    print(
        f"    Max simultaneous pos. : {max_positions}"
    )

    print(
        f"    Max total notional    : ${max_total_notional:.4f}"
    )

    print(
        f"    Total fees            : ${total_fees:.4f}"
    )


def main():

    print()
    print(
        "================================================"
    )

    print(
        "     LEVERAGE-CONSTRAINED BACKTEST"
    )

    print(
        "================================================"
    )

    print()

    print("Loading historical data...")

    candles = load_candles()

    print(
        f"Loaded candles: {len(candles):,}"
    )

    print()

    print(
        f"Starting capital : ${STARTING_CAPITAL:.2f}"
    )

    print(
        f"Risk per trade   : {RISK_PERCENT * 100:.2f}%"
    )

    print(
        f"Maximum leverage : {MAX_LEVERAGE:.1f}x"
    )

    print(
        f"Fee per side     : {FEE_RATE * 100:.3f}%"
    )

    print(
        f"Slippage per side: {SLIPPAGE_RATE * 100:.3f}%"
    )

    print(
        f"Max holding      : {MAX_HOLDING_CANDLES} minutes"
    )

    print(
        "Multiple positions: YES"
    )

    print()

    print("Active patterns:")

    for pattern in ACTIVE_PATTERNS:

        print(
            f"  - {pattern}"
        )

    for pattern_name in ACTIVE_PATTERNS:

        print()
        print()

        print(
            "================================================"
        )

        print(
            f" {pattern_name}"
        )

        print(
            "================================================"
        )

        for target_r in TARGETS_R:

            (
                final_capital,
                trades,
                pattern_count,
                skipped_leverage,
                max_drawdown,
                max_positions,
                max_total_notional,
                total_fees,
            ) = simulate(
                candles,
                pattern_name,
                target_r,
            )

            print_result(
                target_r=target_r,
                final_capital=final_capital,
                trades=trades,
                pattern_count=pattern_count,
                skipped_leverage=skipped_leverage,
                max_drawdown=max_drawdown,
                max_positions=max_positions,
                max_total_notional=max_total_notional,
                total_fees=total_fees,
            )

    print()
    print(
        "================================================"
    )

    print(
        "Backtest complete."
    )

    print(
        "================================================"
    )


if __name__ == "__main__":
    main()