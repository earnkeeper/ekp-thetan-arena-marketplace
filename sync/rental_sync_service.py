import logging
from typing import List
from ekp_sdk.services import CacheService
from datetime import datetime
from db.rental_listing_model import RentalListingModel
from dateutil import parser
import math
from db.rental_listing_repo import RentalListingRepo

from shared.thetan_api_service import ThetanApiService

CACHE_MARKET_RENTAL_LAST_FULL_UPDATE = "CACHE_MARKET_RENTAL_LAST_FULL_UPDATE"


class RentalSyncService:
    def __init__(
        self,
        cache_service: CacheService,
        rental_listing_repo: RentalListingRepo,
        thetan_api_service: ThetanApiService,
        fetch_limit: int
    ):
        self.cache_service = cache_service
        self.rental_listing_repo = rental_listing_repo
        self.thetan_api_service = thetan_api_service
        self.fetch_limit = fetch_limit

    async def sync(self):

        last_full_update = await self.cache_service.get(CACHE_MARKET_RENTAL_LAST_FULL_UPDATE)

        do_full_update = (not last_full_update) or (
            (datetime.now().timestamp() - last_full_update) > 1800)

        if do_full_update:
            logging.warn("Performing full update")

        existing_documents: List[RentalListingModel] = []

        existing_document_ids = []

        if not do_full_update:
            existing_documents = self.rental_listing_repo.find_all()

        fetch_until = 0

        for doc in existing_documents:

            existing_document_ids.append(doc["id"])

            if ("lastModified" in doc) and doc["lastModified"] > fetch_until:
                fetch_until = doc["lastModified"]

        dtos = await self.thetan_api_service.get_latest_market_rentals(fetch_until, self.fetch_limit)

        new_documents: List[RentalListingModel] = self.map_rental_listings(dtos)

        logging.warn(
            f"Fetched new market rental documents, length: {len(new_documents)}"
        )

        self.rental_listing_repo.save(new_documents, do_full_update)

        if do_full_update:
            await self.cache_service.set(
                CACHE_MARKET_RENTAL_LAST_FULL_UPDATE,
                datetime.now().timestamp()
            )

    def map_rental_listings(self, dtos):
        documents: List[RentalListingModel] = []
        
        now = datetime.now().timestamp()

        for dto in dtos:
            price = dto["rentOutInfo"]["price"]["value"] / \
                math.pow(10, dto["rentOutInfo"]["price"]["decimals"])

            type = dto["heroTypeId"]

            skin_id = dto["skinId"]

            if type > 0:
                skin_id = skin_id - (type * 100) + (type * 1000)

            price_per_battle = None

            if dto["battleCap"] > 0:
                price_per_battle = price / dto["battleCap"]

            document: RentalListingModel = {
                "id": dto["id"],
                "updated": now,
                "battleCap": dto["battleCap"],
                "created": parser.parse(dto["created"]).timestamp(),
                "daysCap": dto["rentOutInfo"]["periodHours"] / 24,
                "dmg": dto["dmg"],
                "hp": dto["hp"],
                "lastModified": parser.parse(dto["lastModified"]).timestamp(),
                "level": dto["level"],
                "name": dto["name"],
                "ownerAddress": dto["ownerAddress"],
                "ownerId": dto["ownerId"],
                "price": price,
                "pricePerBattle": price_per_battle,
                "priceSymbol": dto["name"],
                "rarity": dto["heroRarity"],
                "refId": dto["refId"],
                "role": dto["heroRole"],
                "skinId": skin_id,
                "skinName": dto["skinName"],
                "statusId": dto["status"],
                "tokenId": dto["tokenId"],
                "trophyClass": dto["trophyClass"],
                "type": dto["heroTypeId"],
            }

            documents.append(document)

        return documents
