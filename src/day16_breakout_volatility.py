import pandas as pd
import requests


INITIAL_CAPITAL = 100
FEE_RATE = 0.001


def get_binance_data(symbol="BTCUSDT", interval="1h", limit=1000):
    url = "https://api.binance.com/api/v3/klines"

    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": limit
    }

    response = requests.get(url, params=params)
    response.raise_for_status()

    raw_data = response.json()

    data = pd.DataFrame(
        raw_data,
        columns=[
            "open_time",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "close_time",
            "quote_asset_volume",
            "number_of_trades",
            "taker_buy_base_volume",
            "taker_buy_quote_volume",
            "ignore"
        ]
    )

    data["open_time"] = pd.to_datetime(
        data["open_time"],
        unit="ms"
    )

    numeric_columns = [
        "open",
        "high",
        "low",
        "close",
        "volume"
    ]

    data[numeric_columns] = data[numeric_columns].astype(float)

    return data


def create_strategy(data):
    data = data.copy()

    # 1시간 수익률
    data["return"] = data["close"].pct_change()

    # 현재 봉을 제외한 이전 24시간 최고가
    data["rolling_high"] = (
        data["high"]
        .rolling(window=24)
        .max()
        .shift(1)
    )

    # 최근 24시간 변동성
    data["volatility"] = (
        data["return"]
        .rolling(window=24)
        .std()
    )

    # 최근 7일 평균 변동성
    data["volatility_avg"] = (
        data["volatility"]
        .rolling(window=168)
        .mean()
    )

    # 돌파 여부
    data["breakout"] = (
        data["close"] > data["rolling_high"]
    )

    # 변동성 확대 여부
    data["vol_expansion"] = (
        data["volatility"] > data["volatility_avg"]
    )

    # 최종 매매 신호
    data["signal"] = (
        data["breakout"]
        &
        data["vol_expansion"]
    ).astype(int)

    return data


def backtest(data):
    data = data.copy()

    # 미래 데이터 사용 방지
    data["position"] = data["signal"].shift(1).fillna(0)

    # 전략 수익률
    data["strategy_return"] = (
        data["position"]
        * data["return"]
    )

    # 포지션 변경
    data["trade"] = (
        data["position"]
        .diff()
        .abs()
        .fillna(0)
    )

    # 거래 수수료
    data["fee"] = (
        data["trade"]
        * FEE_RATE
    )

    data["strategy_return_after_fee"] = (
        data["strategy_return"]
        - data["fee"]
    )

    # 누적 자산
    data["equity"] = (
        INITIAL_CAPITAL
        * (1 + data["strategy_return_after_fee"]).cumprod()
    )

    # Buy & Hold
    data["buy_hold_equity"] = (
        INITIAL_CAPITAL
        * (1 + data["return"].fillna(0)).cumprod()
    )

    return data


def calculate_metrics(data):
    final_value = data["equity"].iloc[-1]

    profit_loss = (
        final_value
        - INITIAL_CAPITAL
    )

    strategy_return = (
        final_value / INITIAL_CAPITAL - 1
    ) * 100

    buy_hold_final = data["buy_hold_equity"].iloc[-1]

    buy_hold_return = (
        buy_hold_final / INITIAL_CAPITAL - 1
    ) * 100

    running_max = data["equity"].cummax()

    drawdown = (
        data["equity"] / running_max
        - 1
    )

    mdd = drawdown.min() * 100

    trades = int(
        data["trade"].sum()
    )

    long_hours = int(
        data["position"].sum()
    )

    breakout_count = int(
        data["breakout"].sum()
    )

    vol_expansion_count = int(
        data["vol_expansion"].sum()
    )

    signal_count = int(
        data["signal"].sum()
    )

    print("\n===== Day 16: Breakout + Volatility Expansion =====")

    print(f"Initial Capital       : ${INITIAL_CAPITAL:.2f}")
    print(f"Final Value           : ${final_value:.2f}")
    print(f"Profit / Loss         : ${profit_loss:.2f}")

    print(f"Strategy Return       : {strategy_return:.2f}%")
    print(f"Buy & Hold Return     : {buy_hold_return:.2f}%")
    print(f"Buy & Hold Final      : ${buy_hold_final:.2f}")

    print(f"MDD                   : {mdd:.2f}%")

    print(f"Trades                : {trades}")
    print(f"Long Hours            : {long_hours}")

    print(f"Breakout Hours        : {breakout_count}")
    print(f"Vol Expansion Hours   : {vol_expansion_count}")
    print(f"Final Signal Hours    : {signal_count}")


def main():
    data = get_binance_data()

    data = create_strategy(data)

    data = backtest(data)

    data = data.dropna()

    calculate_metrics(data)

    print("\n===== Latest Market State =====")

    latest = data.iloc[-1]

    print(f"BTC Price        : ${latest['close']:.2f}")
    print(f"Rolling High     : ${latest['rolling_high']:.2f}")
    print(f"Volatility       : {latest['volatility']:.6f}")
    print(f"Volatility Avg   : {latest['volatility_avg']:.6f}")
    print(f"Breakout         : {latest['breakout']}")
    print(f"Vol Expansion    : {latest['vol_expansion']}")
    print(f"Signal           : {int(latest['signal'])}")


if __name__ == "__main__":
    main()