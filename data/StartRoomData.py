import copy
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Callable, Dict, List, Optional, cast

from ..DoorRando import BEAM_TO_LOCK_MAPPING

from ..Items import SuitUpgrade, get_item_for_options
from ..data.AreaNames import MetroidPrimeArea
from ..data.RoomNames import RoomName

if TYPE_CHECKING:
    from .. import MetroidPrimeWorld

BEAM_ITEMS = [SuitUpgrade.Power_Beam, SuitUpgrade.Ice_Beam, SuitUpgrade.Wave_Beam, SuitUpgrade.Plasma_Beam]


class StartRoomDifficulty(Enum):
    Normal = -1
    Safe = 0
    Dangerous = 1
    Buckle_Up = 2


@dataclass
class StartRoomLoadout:
    loadout: List[SuitUpgrade] = field(default_factory=list)
    item_rules: List[Dict[str, List[SuitUpgrade]]] = field(default_factory=list)
    starting_beam: SuitUpgrade = SuitUpgrade.Power_Beam
    """List of locations that can have a list of possible required items for that location"""


@dataclass
class StartRoomData:
    area: MetroidPrimeArea
    loadouts: List[StartRoomLoadout] = field(default_factory=list)
    difficulty: StartRoomDifficulty = StartRoomDifficulty.Safe
    selected_loadout: Optional[StartRoomLoadout] = None
    name: Optional[str] = None
    is_eligible: Callable[['MetroidPrimeWorld'], bool] = lambda world: True
    allowed_elevators: Optional[Dict[str, Dict[str, List[str]]]] = None
    denied_elevators: Optional[Dict[str, Dict[str, List[str]]]] = None
    force_starting_beam: Optional[bool] = False
    local_early_items: Optional[List[SuitUpgrade]] = None
    """Used for situations where starting beam cannot be randomized, disqualifies a room from being selected when randomizing blue doors is on"""

    no_power_beam_door_on_starting_level: Optional[bool] = False
    """Used when the starting beam is required to not be insta bk'd"""


all_start_rooms: Dict[str, StartRoomData] = {
    RoomName.Landing_Site.value: StartRoomData(difficulty=StartRoomDifficulty.Normal, area=MetroidPrimeArea.Tallon_Overworld, loadouts=[
        StartRoomLoadout(item_rules=[], starting_beam=SuitUpgrade.Power_Beam)],
        local_early_items=[SuitUpgrade.Missile_Launcher]
    ),
    RoomName.Arboretum.value: StartRoomData(
        area=MetroidPrimeArea.Chozo_Ruins,
        loadouts=[StartRoomLoadout(
            [SuitUpgrade.Missile_Launcher],
        )],
        is_eligible=lambda world: world.options.shuffle_scan_visor.value == False,
        local_early_items=[SuitUpgrade.Morph_Ball, SuitUpgrade.Scan_Visor]
    ),
    RoomName.Burn_Dome.value: StartRoomData(
        area=MetroidPrimeArea.Chozo_Ruins,
        loadouts=[StartRoomLoadout([SuitUpgrade.Morph_Ball],
                                   item_rules=[
            {
                'Chozo Ruins: Burn Dome - Incinerator Drone': [SuitUpgrade.Morph_Ball_Bomb],
                'Chozo Ruins: Burn Dome - Missile': [SuitUpgrade.Missile_Launcher]
            }
        ]
        )],
        difficulty=StartRoomDifficulty.Safe,
    ),
    RoomName.Ruined_Fountain.value: StartRoomData(
        area=MetroidPrimeArea.Chozo_Ruins,
        loadouts=[StartRoomLoadout([SuitUpgrade.Missile_Launcher])],
        local_early_items=[SuitUpgrade.Morph_Ball]
    ),
    RoomName.Save_Station_1.value: StartRoomData(
        area=MetroidPrimeArea.Chozo_Ruins,
        local_early_items=[SuitUpgrade.Morph_Ball],
        loadouts=[StartRoomLoadout(
            starting_beam=SuitUpgrade.Power_Beam,
            item_rules=[
                {"Chozo Ruins: Hive Totem": [SuitUpgrade.Missile_Launcher]}
            ])]),
    RoomName.Save_Station_2.value: StartRoomData(area=MetroidPrimeArea.Chozo_Ruins, loadouts=[StartRoomLoadout([SuitUpgrade.Missile_Launcher])]),
    RoomName.Tower_Chamber.value: StartRoomData(area=MetroidPrimeArea.Chozo_Ruins, loadouts=[StartRoomLoadout(
        starting_beam=SuitUpgrade.Wave_Beam,
        item_rules=[
            {
                "Chozo Ruins: Tower Chamber": [SuitUpgrade.Morph_Ball],
                "Chozo Ruins: Ruined Shrine - Plated Beetle": [SuitUpgrade.Morph_Ball_Bomb, SuitUpgrade.Main_Power_Bomb],
                "Chozo Ruins: Ruined Shrine - Lower Tunnel": [SuitUpgrade.Missile_Launcher],
            },
        ]
    )]),
    RoomName.Warrior_Shrine.value: StartRoomData(
        is_eligible=lambda world: world.options.disable_starting_room_bk_prevention.value != True,  # Varia suit is definitely required here
        area=MetroidPrimeArea.Magmoor_Caverns,
        loadouts=[
            StartRoomLoadout([SuitUpgrade.Varia_Suit, SuitUpgrade.Morph_Ball], [
                {
                    "Magmoor Caverns: Storage Cavern": [SuitUpgrade.Morph_Ball_Bomb],
                }
            ]),
        ],
    ),
    RoomName.East_Tower.value: StartRoomData(area=MetroidPrimeArea.Phendrana_Drifts, loadouts=[StartRoomLoadout(
        starting_beam=SuitUpgrade.Wave_Beam, loadout=[SuitUpgrade.Missile_Launcher],
        item_rules=[
            {
                "Phendrana Drifts: Phendrana Canyon": [SuitUpgrade.Space_Jump_Boots],
                "Phendrana Drifts: Research Lab Aether - Tank": [SuitUpgrade.Plasma_Beam]
            }
        ],
    )],
        is_eligible=lambda world: world.options.shuffle_scan_visor.value == False or world.multiworld.players > 1,
        no_power_beam_door_on_starting_level=True,
        difficulty=StartRoomDifficulty.Buckle_Up),

    RoomName.Save_Station_B.value: StartRoomData(
        area=MetroidPrimeArea.Phendrana_Drifts,
        force_starting_beam=True,
        loadouts=[
            StartRoomLoadout(
                starting_beam=SuitUpgrade.Plasma_Beam, loadout=[SuitUpgrade.Missile_Launcher],
                item_rules=[
                    {"Phendrana Drifts: Phendrana Shorelines - Behind Ice": [SuitUpgrade.Space_Jump_Boots]},
                ],
            )
        ],
        is_eligible=lambda world: world.options.shuffle_scan_visor.value == False or world.multiworld.players > 1,
    ),
    RoomName.Arbor_Chamber.value: StartRoomData(
        area=MetroidPrimeArea.Tallon_Overworld,
        loadouts=[StartRoomLoadout([SuitUpgrade.Missile_Launcher])],
        allowed_elevators={
            MetroidPrimeArea.Tallon_Overworld.value: {
                RoomName.Transport_to_Chozo_Ruins_West.value: [RoomName.Transport_to_Magmoor_Caverns_North.value, RoomName.Transport_to_Magmoor_Caverns_West.value],
                RoomName.Transport_to_Magmoor_Caverns_East.value: [RoomName.Transport_to_Tallon_Overworld_North.value, RoomName.Transport_to_Magmoor_Caverns_West.value, RoomName.Transport_to_Magmoor_Caverns_North.value],
            }
        }
    ),
    RoomName.Transport_to_Chozo_Ruins_East.value: StartRoomData(
        area=MetroidPrimeArea.Tallon_Overworld,
        loadouts=[StartRoomLoadout(
            starting_beam=SuitUpgrade.Ice_Beam, loadout=[SuitUpgrade.Morph_Ball],
            item_rules=[
                {
                    "Tallon Overworld: Overgrown Cavern": [SuitUpgrade.Missile_Launcher]
                }
            ],

        )],
        allowed_elevators={
            MetroidPrimeArea.Tallon_Overworld.value: {
                RoomName.Transport_to_Chozo_Ruins_West.value: [RoomName.Transport_to_Magmoor_Caverns_North.value, RoomName.Transport_to_Magmoor_Caverns_West.value],
                RoomName.Transport_to_Magmoor_Caverns_East.value: [RoomName.Transport_to_Tallon_Overworld_North.value, RoomName.Transport_to_Magmoor_Caverns_West.value, RoomName.Transport_to_Magmoor_Caverns_North.value],
            }
        }
    ),
    RoomName.Quarantine_Monitor.value: StartRoomData(area=MetroidPrimeArea.Phendrana_Drifts, loadouts=[StartRoomLoadout(
        starting_beam=SuitUpgrade.Wave_Beam,
        loadout=[SuitUpgrade.Thermal_Visor],
        item_rules=[
            {
                "Phendrana Drifts: Quarantine Monitor": [SuitUpgrade.Morph_Ball],
                "Phendrana Drifts: Quarantine Cave": [SuitUpgrade.Spider_Ball],
                "Phendrana Drifts: Ice Ruins East - Spider Track": [SuitUpgrade.Space_Jump_Boots],
                "Phendrana Drifts: Ruined Courtyard": [SuitUpgrade.Plasma_Beam]
            },
        ]
    )], difficulty=StartRoomDifficulty.Buckle_Up,
        is_eligible=lambda world: world.options.shuffle_scan_visor.value == False or world.multiworld.players > 1,
    ),
    RoomName.Sunchamber_Lobby.value: StartRoomData(
        area=MetroidPrimeArea.Chozo_Ruins,
        loadouts=[
            StartRoomLoadout([SuitUpgrade.Morph_Ball, SuitUpgrade.Missile_Launcher, SuitUpgrade.Morph_Ball_Bomb]),
        ],
        difficulty=StartRoomDifficulty.Buckle_Up
    ),

}


def get_random_start_room_by_difficulty(world: 'MetroidPrimeWorld', difficulty: int) -> StartRoomData:
    """Returns a random start room based on difficulty as well as a random loadout from that room"""
    available_room_names = [name for name, room in all_start_rooms.items() if room.difficulty.value == difficulty and room.is_eligible(world)]
    room_name = world.random.choice(available_room_names)
    return get_starting_room_by_name(world, room_name)


def get_starting_room_by_name(world: 'MetroidPrimeWorld', room_name: str) -> StartRoomData:
    """Returns a start room based on name"""
    # Prevent us from modifying the original room data
    room = copy.deepcopy(all_start_rooms[room_name])
    room.name = room_name
    if len(room.loadouts) == 0:
        room.selected_loadout = StartRoomLoadout([SuitUpgrade.Power_Beam])
    else:
        room.selected_loadout = world.random.choice(room.loadouts)
    return room


def _has_elevator_rando(world: 'MetroidPrimeWorld') -> bool:
    return cast(bool, world.options.elevator_randomization)


def _has_no_pre_scan_elevators_with_shuffle_scan(world: 'MetroidPrimeWorld') -> bool:
    return world.options.pre_scan_elevators.value == False and cast(bool, world.options.shuffle_scan_visor)


def _has_options_that_allow_more_landing_site_checks(world: 'MetroidPrimeWorld') -> bool:
    return (cast(str, world.options.blast_shield_randomization.value) != world.options.blast_shield_randomization.option_none or world.options.trick_difficulty.value != -1) and not world.options.elevator_randomization


def init_starting_room_data(world: 'MetroidPrimeWorld'):
    difficulty = world.options.starting_room.value
    yaml_name = world.options.starting_room_name.value
    world.prefilled_item_map = {}
    if yaml_name:
        if yaml_name in all_start_rooms:
            world.starting_room_data = get_starting_room_by_name(world, yaml_name)
        else:
            world.starting_room_data = StartRoomData(name=world.options.starting_room_name.value)
            world.starting_room_data.loadouts = [StartRoomLoadout(loadout=[SuitUpgrade.Power_Beam])]
    else:
        if world.options.starting_room.value == StartRoomDifficulty.Normal.value:
            if (_has_elevator_rando(world) or _has_no_pre_scan_elevators_with_shuffle_scan(world)) and not _has_options_that_allow_more_landing_site_checks(world):
                # Can't start at landing site since there are no pickups without tricks
                world.starting_room_data = get_starting_room_by_name(world, RoomName.Save_Station_1.value)

            else:
                world.starting_room_data = get_starting_room_by_name(world, RoomName.Landing_Site.value)
            # Give the randomizer more flexibility if they have options that allow more starting_room checks
            if _has_options_that_allow_more_landing_site_checks(world):
                world.options.disable_starting_room_bk_prevention.value = True
        else:
            world.starting_room_data = get_random_start_room_by_difficulty(world, difficulty)
        world.options.starting_room_name.value = world.starting_room_data.name


def init_starting_loadout(world: 'MetroidPrimeWorld'):
    disable_bk_prevention = world.options.disable_starting_room_bk_prevention.value
   # Clear non starting beam upgrades out of loadout
    if disable_bk_prevention:
        world.starting_room_data.selected_loadout.loadout = []

    # Update the loadout with the correct items based on options (progressive upgrades, missile launcher, etc.)
    updated_loadout = []
    for item in world.starting_room_data.selected_loadout.loadout:
        updated_loadout.append(get_item_for_options(world, item))
    world.starting_room_data.selected_loadout.loadout = updated_loadout

    # If we are preventing bk then set a few items for prefill if available
    if not disable_bk_prevention:
        for mapping in world.starting_room_data.selected_loadout.item_rules:
            for location_name, potential_items in mapping.items():
                required_item = get_item_for_options(world, world.random.choice(potential_items))
                world.prefilled_item_map[location_name] = required_item.value
        if world.starting_room_data.local_early_items:
            for item in world.starting_room_data.local_early_items:
                options_item = get_item_for_options(world, item)
                if options_item not in world.starting_room_data.selected_loadout.loadout:
                    world.multiworld.local_early_items[world.player][options_item] = 1


def init_starting_beam(world: 'MetroidPrimeWorld'):
    loadout_beam = world.starting_room_data.selected_loadout.starting_beam

    def replace_starting_beam(new_beam: SuitUpgrade):
        if loadout_beam != None:
            world.starting_room_data.selected_loadout.starting_beam = new_beam
        world.options.starting_beam.value = new_beam.value

    # Use the starting beam if it was set in the options (or for UT)
    if world.options.starting_beam.value is not None and world.options.starting_beam.value != "none":
        new_beam = SuitUpgrade.get_by_value(world.options.starting_beam)
        if new_beam != None:
            replace_starting_beam(new_beam)

    # Remap beam to a new color based on door randomization
    elif world.options.door_color_randomization != "none" and loadout_beam != None and loadout_beam != SuitUpgrade.Power_Beam and not world.starting_room_data.force_starting_beam:
        # replace the beam with whatever the new one should be mapped to
        original_door_color = BEAM_TO_LOCK_MAPPING[loadout_beam].value
        # Select new beam based off of what the original color is now mapped to
        new_beam = None
        for original, new in world.door_color_mapping[world.starting_room_data.area.value].type_mapping.items():
            if original == original_door_color:
                # Find the beam that corresponds to the new color
                for beam in BEAM_ITEMS:
                    if BEAM_TO_LOCK_MAPPING[beam].value == new:
                        new_beam = beam
                        break
                break
        replace_starting_beam(new_beam)

    # Randomize starting beam if enabled
    elif world.options.randomize_starting_beam and not world.starting_room_data.force_starting_beam:
        new_beam = world.random.choice([beam for beam in BEAM_ITEMS if beam != SuitUpgrade.Power_Beam])
        replace_starting_beam(new_beam)

    # Hive mecha needs to be disabled if we don't have power beam in vanilla start locations (otherwise no checks can be reached)
    # TODO: Make this use the new starting beam data
    if (world.starting_room_data.name == RoomName.Landing_Site.value or world.starting_room_data.name == RoomName.Save_Station_1.value) and world.starting_room_data.selected_loadout.starting_beam != SuitUpgrade.Power_Beam:
        world.options.remove_hive_mecha.value = True
