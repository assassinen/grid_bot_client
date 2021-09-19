from binance.exchange import BinanceExchangeInterface

api_key = "TdY4v7EsjOPUiaVobmqkEeFlmM07TAaxAwGaatiDerNtmgJ8h24SQ8g6xhx0t9gA"
api_secret = "ytZ5kSkf2re9fj7rBITd68QvgVEQJVarPIpMuValiHzxAtXu2v3YQG1WK8691SUu"
OPTIONS_URL = 'https://vapi.binance.com/vapi'

client = BinanceExchangeInterface(key=api_key,
                                   secret=api_secret,
                                   base_url=OPTIONS_URL,
                                   api_url="v1",
                                   instrument="BTC-210924-50000-C")

print(client.get_positions())