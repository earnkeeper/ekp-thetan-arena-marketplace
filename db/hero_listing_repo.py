from ekp_sdk.db import MgClient
from pymongo import UpdateOne
import time

class HeroListingRepo:
    def __init__(
        self,
        mg_client: MgClient
    ):
        self.mg_client = mg_client

        self.collection = self.mg_client.db['hero_listings']
        self.collection.create_index("id", unique=True)
        self.collection.create_index("token_id")
    
    def find_all(self):
        start = time.perf_counter()
        
        results = list(
            self.collection
            .find()
        )
        
        print(f"⏱  [HeroListingRepo.find_all({len(results)})] {time.perf_counter() - start:0.3f}s")
        
        return results
    
    def save(self, models, overwrite = False):
        if not len(models):
            return

        start = time.perf_counter()
        
        if overwrite:
            self.collection.drop()
            self.collection.insert_many(models)
        else:
            self.collection.bulk_write(
                list(map(lambda model: UpdateOne({"id": model["id"]}, {"$set": model}, True), models))
            )
        
        print(f"⏱  [RentalListingRepo.save({len(models)})] {time.perf_counter() - start:0.3f}s")
