from hansken_extraction_plugin.api.extraction_plugin import MetaExtractionPlugin
from hansken_extraction_plugin.api.plugin_info import Author, MaturityLevel, PluginId, PluginInfo
from hansken_extraction_plugin.runtime.extraction_plugin_runner import run_with_hanskenpy
from logbook import Logger
import requests
log = Logger(__name__)


class Plugin(MetaExtractionPlugin):

    def plugin_info(self):
        plugin_info = PluginInfo(
            id=PluginId(domain='politie.nl', category='crypto', name='wallet-balance-fetcher'),
            version='1.0.0',
            description='This plugin fetches the wallet balance for various kinds of wallet addresses',
            author=Author('Benjamin Martens', 'benjamin.martens@politie.nl', 'Politie'),
            maturity=MaturityLevel.PROOF_OF_CONCEPT,
            webpage_url='',  # e.g. url to the code repository of your plugin
            matcher='type:cryptocurrencyWallet',  # add the query for the types of traces your plugin should match
            license='Apache License 2.0'
        )
        return plugin_info

    def process(self, trace):
        # Define api keys
        api_key_polygon = 'FK7RKY9PXEBVSXJM9WDHZBNAQI3TKBJUDH'
        api_key_cmc = '86b827db-b994-4df3-9339-1a2da01f8e7f'
        log.info(f"processing trace {trace.get('name')}")

        # Fetch data from hansken
        wallet_address = trace.get('cryptocurrencyWallet.misc.address')
        if wallet_address:

            # Fetch matic value
            payload = {
                'Accept': 'application/json',
                'Accept-Encoding': 'deflate, gzip',
                'X-CMC_PRO_API_KEY': f'{api_key_cmc}'
            }

            cmc_url = f'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest?slug=polygon&convert=USD'
            r_to_cmc = requests.get(cmc_url, headers=payload)
            r_to_cmc = r_to_cmc.json()
            matic_usd_value = r_to_cmc['data']['3890']['quote']['USD']['price']

            # Fetch polygon balance
            polygon_url = f'https://api.polygonscan.com/api?module=account&action=balance&address={wallet_address}&apikey={api_key_polygon}'
            r_to_polygon = requests.get(polygon_url)
            balance = r_to_polygon.json()
            matic_balance = int(balance['result']) / 10e17

            # Calculate USD wallet value and store in Hansken
            wallet_dollar_value = matic_balance * matic_usd_value
            # trace.update("crypto.matic.value", wallet_dollar_value)
            trace.update("account.misc", {"balance": str(matic_balance), "dollar_value" : str(wallet_dollar_value)})




if __name__ == '__main__':
    # optional main method to run your plugin with Hansken.py
    # see detail at:
    #  https://netherlandsforensicinstitute.github.io/hansken-extraction-plugin-sdk-documentation/latest/dev/python/hanskenpy.html
    run_with_hanskenpy(Plugin,
                       endpoint='http://localhost:9091/gatekeeper/',
                       keystore='http://localhost:9090/kestore/',
                       project='ab73dccd-eea5-4025-8de8-670f3f2c5e5f')
