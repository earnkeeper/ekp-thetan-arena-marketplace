
from decouple import AutoConfig
from ekp_sdk import BaseContainer
from db.hero_listing_repo import HeroListingRepo

from listener.listener_service import ListenerService


class ListenerContainer(BaseContainer):
    def __init__(self):
        config = AutoConfig('.env')

        super().__init__(config)

        self.hero_listing_repo = HeroListingRepo(
            mg_client=self.mg_client
        )
        
        self.listener_service = ListenerService(
            hero_listing_repo=self.hero_listing_repo,
            web3_service=self.web3_service
        )
