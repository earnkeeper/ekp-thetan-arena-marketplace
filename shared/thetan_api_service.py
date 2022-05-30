from ekp_sdk.services import RestClient, Limiter
from dateutil import parser


class ThetanApiService:
    def __init__(
        self,
        rest_client: RestClient
    ):
        self.rest_client = rest_client
        self.base_url = "https://data.thetanarena.com/thetan/v1"
        self.limiter = Limiter(1000, 1)
        self.page_size = 50

    async def get_latest_market_heroes(self, later_than, limit=None):
        url = f"{self.base_url}/nif/search?tab=heroes&sort=Latest"

        cursor = 0

        dtos = []

        while True:
            paged_url = f"{url}&from={cursor}&size={self.page_size}"

            new_dtos = await self.rest_client.get(paged_url, lambda data, text: data["data"], self.limiter)

            filtered_dtos = []

            for dto in new_dtos:
                if parser.parse(dto["lastModified"]).timestamp() > later_than:
                    filtered_dtos.append(dto)
                    dtos.append(dto)

            cursor += self.page_size

            if limit and (cursor >= limit):
                break

            if len(filtered_dtos) < self.page_size:
                break

        return dtos
