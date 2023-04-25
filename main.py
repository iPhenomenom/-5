import sys
import asyncio
import aiohttp
from datetime import datetime, timedelta

class ExchangeRateFetcher:
    def __init__(self, days_back):
        self.days_back = days_back
        self.url = 'https://api.privatbank.ua/p24api/exchange_rates?json&date='

    async def fetch(self, session, date):
        async with session.get(self.url + date) as response:
            return await response.json()

    async def fetch_rates(self):
        async with aiohttp.ClientSession() as session:
            tasks = []
            for i in range(self.days_back):
                date = (datetime.now() - timedelta(days=i)).strftime('%d.%m.%Y')
                tasks.append(asyncio.ensure_future(self.fetch(session, date)))
            results = await asyncio.gather(*tasks)
            return self.format_results(results)

    def format_results(self, results):
        formatted = []
        for r in results:
            rates = {'EUR': {}, 'USD': {}}
            for c in r['exchangeRate']:
                if c['currency'] == 'EUR':
                    rates['EUR']['sale'] = c['saleRateNB']
                    rates['EUR']['purchase'] = c['purchaseRateNB']
                elif c['currency'] == 'USD':
                    rates['USD']['sale'] = c['saleRateNB']
                    rates['USD']['purchase'] = c['purchaseRateNB']
            formatted.append({r['date']: rates})
        return formatted

def main():
    try:
        days_back = int(sys.argv[1])
    except (IndexError, ValueError):
        print('Usage: py main.py <days>')
        return

    if days_back > 10:
        print('Error: cannot fetch exchange rates for more than 10 days.')
        return

    fetcher = ExchangeRateFetcher(days_back)
    loop = asyncio.get_event_loop()
    results = loop.run_until_complete(fetcher.fetch_rates())
    print(results)

if __name__ == '__main__':
    main()
