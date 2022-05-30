import asyncio
import json
import logging
from ast import literal_eval
from datetime import datetime
from typing import List

from ekp_sdk.domain import Log
from ekp_sdk.dto import Web3LogDto
from ekp_sdk.services import  Web3Service
from web3 import Web3

from db.hero_listing_repo import HeroListingRepo

THETAN_MARKET_ADDRESS = '0x7bf5d1dec7e36d5b4e9097b48a1b9771e6c96aa4'
THETAN_MATCH_TOPIC = '0x7ec91832f8e94cceb462065487af39394e7520f22662d527e383864c041380cf'
THETAN_RENT_HERO_ADDRESS = '0xbd69abdcc8acdafca69c96e10141f573842b40e4'
THETAN_RENT_HERO_TOPIC = '0x4423ff8e8b83bff529877c64c877338e79961f611b0b4fb3213a73b9ace6df7f'


class ListenerService:
    def __init__(
        self,
        hero_listing_repo: HeroListingRepo,
        web3_service: Web3Service,
    ):
        self.hero_listing_repo = hero_listing_repo
        self.web3_service = web3_service

    def listen(self):

        hero_filter = self.web3_service.get_filter({
            "address": Web3.toChecksumAddress(THETAN_MARKET_ADDRESS),
            "topics": [THETAN_MATCH_TOPIC]
        })

        loop = asyncio.get_event_loop()

        loop.run_until_complete(
            asyncio.gather(
                self.filter_loop(hero_filter, 2),
            )
        )

    async def filter_loop(self, filter, poll_interval):
        while True:
            try:
                for new_event in filter.get_new_entries():
                    await self.process_hero_sale(json.loads(Web3.toJSON(new_event)))

                await asyncio.sleep(poll_interval)
            except Exception as e:
                logging.error("🚨 error while listening for events", e)
                quit()

    async def process_hero_sale(self, log_dto: Web3LogDto):
        print(log_dto)
        token_id = literal_eval(log_dto["topics"][0])

        logging.warn(
            f"Received market match log for token id and transaction hash: ${token_id} - ${log_dto['transactionHash']}"
        )
        self.hero_listing_repo.remove_by_token_id(token_id)
