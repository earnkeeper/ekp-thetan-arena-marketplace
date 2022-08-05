import logging
from typing import List
from ekp_sdk.services import CacheService
from datetime import datetime
from db.hero_listing_repo import HeroListingRepo
from db.hero_listing_model import HeroListingModel
from dateutil import parser
import math

from shared.thetan_api_service import ThetanApiService

CACHE_MARKET_HERO_LAST_FULL_UPDATE = "CACHE_MARKET_HERO_LAST_FULL_UPDATE"


class HeroSyncService:
    def __init__(
        self,
        cache_service: CacheService,
        hero_listing_repo: HeroListingRepo,
        thetan_api_service: ThetanApiService,
        fetch_limit: int
    ):
        self.cache_service = cache_service
        self.hero_listing_repo = hero_listing_repo
        self.thetan_api_service = thetan_api_service
        self.fetch_limit = fetch_limit

    async def sync(self):

        last_full_update = await self.cache_service.get(CACHE_MARKET_HERO_LAST_FULL_UPDATE)

        do_full_update = (not last_full_update) or (
            (datetime.now().timestamp() - last_full_update) > 1800)

        if do_full_update:
            logging.warn("Performing full update")

        existing_documents: List[HeroListingModel] = []

        existing_document_ids = []

        if not do_full_update:
            existing_documents = self.hero_listing_repo.find_all()

        fetch_until = 0

        for doc in existing_documents:

            existing_document_ids.append(doc["id"])

            if ("timestamp" in doc) and doc["timestamp"] > fetch_until:
                fetch_until = doc["timestamp"]

        dtos = await self.thetan_api_service.get_latest_market_heroes(fetch_until, self.fetch_limit)

        new_documents: List[HeroListingModel] = self.map_hero_listings(dtos)

        logging.warn(
            f"Fetched new market buy documents, length: {len(new_documents)}"
        )

        self.hero_listing_repo.save(new_documents, do_full_update)

        if do_full_update:
            await self.cache_service.set(
                CACHE_MARKET_HERO_LAST_FULL_UPDATE,
                datetime.now().timestamp()
            )

    def map_hero_listings(self, dtos):
        documents: List[HeroListingModel] = []
        now = datetime.now().timestamp()

        for dto in dtos:
            price = dto["systemCurrency"]["value"] / \
                math.pow(10, dto["systemCurrency"]["decimals"])

            type = dto["heroTypeId"]

            skin_id = dto["skinId"]

            if type > 0:
                skin_id = skin_id - (type * 100) + (type * 1000)

            battle_color = "success"

            if (dto["battleCap"] / dto["battleCapMax"]) < 0.2:
                battle_color = "danger"
            elif (dto["battleCap"] / dto["battleCapMax"]) < 0.4:
                battle_color = "warning"

            price_per_battle = None

            if dto["battleCap"] > 0:
                price_per_battle = price / dto["battleCap"]

            document: HeroListingModel = {
                "id": dto["id"],
                "updated": now,
                "battleCap": dto["battleCap"],
                "battleCapMax": dto["battleCapMax"],
                "battlesUsed": dto["battleCapMax"] - dto["battleCap"],
                "battleColor": battle_color,
                "created": parser.parse(dto["created"]).timestamp(),
                "dmg": dto["dmg"],
                "hp": dto["hp"],
                "timestamp": parser.parse(dto["timestamp"]).timestamp(),
                "level": dto["level"],
                "name": dto["name"],
                "ownerAddress": dto["ownerAddress"],
                "ownerId": dto["ownerId"],
                "price": price,
                "pricePerBattle": price_per_battle,
                "priceSymbol": dto["systemCurrency"]["name"],
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
