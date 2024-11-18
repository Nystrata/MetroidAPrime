from dataclasses import dataclass, field
from typing import Callable, List, Optional, TYPE_CHECKING
from .Tricks import TrickInfo
from BaseClasses import CollectionState
from .AreaNames import MetroidPrimeArea
from .RoomNames import RoomName
from ..DoorRando import DoorLockType

if TYPE_CHECKING:
    from .. import MetroidPrimeWorld
    from ..BlastShieldRando import BlastShieldType


@dataclass
class DoorData:
    default_destination: Optional[RoomName]
    defaultLock: DoorLockType = DoorLockType.Blue
    blast_shield: Optional["BlastShieldType"] = None
    lock: Optional[DoorLockType] = None
    # TODO: Remove destination, not going to pursue room rando
    destination: Optional[RoomName] = None
    destination_area: Optional[MetroidPrimeArea] = (
        None  # Used for rooms that have the same name in different areas like Transport Tunnel A
    )
    rule_func: Optional[Callable[["MetroidPrimeWorld", CollectionState], bool]] = None
    tricks: List[TrickInfo] = field(default_factory=list)
    exclude_from_rando: bool = (
        False  # Used primarily for door rando when a door doesn't actually exist
    )
    sub_region_door_index: Optional[int] = (
        None  # Used when this door also provides access to another door in the target room
    )
    sub_region_access_override: Optional[
        Callable[["MetroidPrimeWorld", CollectionState], bool]
    ] = None  # Used to override the access check for reaching this door, if necessary when connecting it to a sub region

    def get_destination_region_name(self):
        assert self.default_destination is not None
        destination = (
            self.destination.value
            if self.destination is not None
            else self.default_destination.value
        )
        if self.destination_area is not None:
            return f"{self.destination_area.value}: {destination}"
        return destination


def get_door_data_by_room_names(
    source_room: RoomName,
    target_room: RoomName,
    area: MetroidPrimeArea,
    world: "MetroidPrimeWorld",
) -> Optional[tuple[DoorData, int]]:
    region_data = world.game_region_data.get(area)

    assert region_data is not None

    source_room_data = region_data.rooms.get(source_room)
    if not source_room_data:
        return None

    # Retrieve the target room data
    target_room_data = region_data.rooms.get(target_room)
    if not target_room_data:
        return None

    # Iterate through the doors in the source room to find a matching door
    for door_id, door_data in source_room_data.doors.items():
        if door_data.default_destination == target_room:
            return door_data, door_id

    return None
