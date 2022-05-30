from typing import TypedDict


class HeroListingModel(TypedDict):
    id: str
    updated: int
    battle_cap: int
    battle_cap_max: int
    battles_used: int
    battle_color: str
    created: int
    dmg: int
    hp: int
    last_modified: int
    level: int
    name: str
    owner_address: str
    owner_id: str
    price: float
    price_per_battle: float
    price_symbol: str
    rarity: int
    ref_id: str
    role: str
    skin_id: int
    skin_name: str
    status_id: int
    token_id: str
    trophy_class: int
    type: int