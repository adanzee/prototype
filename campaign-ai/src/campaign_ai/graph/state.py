from typing import TypedDict


class CampaignState(TypedDict, total=False):
    agency_id: str
    client_brand_id: str

    brief: str
    result: dict

    revision: int