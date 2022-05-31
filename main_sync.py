
import asyncio
import logging

from decouple import AutoConfig
from ekp_sdk import BaseContainer

from db.hero_listing_repo import HeroListingRepo
from db.rental_listing_repo import RentalListingRepo
from shared.thetan_api_service import ThetanApiService
from sync.hero_sync_service import HeroSyncService
from sync.rental_sync_service import RentalSyncService



class AppContainer(BaseContainer):
    def __init__(self):
        config = AutoConfig('.env')

        FETCH_LIMIT = config("FETCH_LIMIT", cast=int, default=None)
        
        super().__init__(config)

        # DB

        self.hero_listing_repo = HeroListingRepo(
            mg_client=self.mg_client,
        )

        self.rental_listing_repo = RentalListingRepo(
            mg_client=self.mg_client,
        )

        # Services
        
        self.thetan_api_service = ThetanApiService(
            rest_client=self.rest_client
        )
        
        self.hero_sync_service = HeroSyncService(
            cache_service=self.cache_service,
            hero_listing_repo=self.hero_listing_repo,
            thetan_api_service=self.thetan_api_service,
            fetch_limit=FETCH_LIMIT
        )

        self.rental_sync_service = RentalSyncService(
            cache_service=self.cache_service,
            rental_listing_repo=self.rental_listing_repo,
            thetan_api_service=self.thetan_api_service,
            fetch_limit=FETCH_LIMIT
        )
        
if __name__ == '__main__':
    container = AppContainer()

    logging.warn("🚀 Application Start")

    loop = asyncio.get_event_loop()
    
    futures = [
        container.hero_sync_service.sync(),
        container.rental_sync_service.sync(),
    ]
        
    loop.run_until_complete(
        asyncio.gather(*futures)
    )

