from typing import Any, TypedDict, Dict, Union, Optional
from typing import final

__all__ = (
    "PlayerData", 
    "ClientData", 
    "ClientDataNullKeys", 
    "ClientRequest", 
    "ServerResponse",
    "Map"
)

Map = bytearray

class PlayerData(TypedDict):
    posx: int
    posy: int
    rot: Union[int, float]
    turret_rot: Union[int, float]


class BaseClientData(TypedDict):
    key: str
    id: int
    addres: list[str, int]
    client_timeout_ms: int

class ClientData(BaseClientData):
    player_data: Union[
        Dict,
        PlayerData
    ]

class ClientDataNullKeys(ClientData):
    """
    ClientData with `key`: None
    """
    key: None

@final
class ServerResponse(TypedDict):
    status: int
    response: Optional[Any]

class ClientRequest(TypedDict):
    request: str
    client_data: BaseClientData
    player_data: PlayerData
    request_body: Dict[str, Any]