from Fill import distribute_items_restrictive
from ..Items import SuitUpgrade
from ..DoorRando import DoorLockType

from ..config import make_config
from ..data.AreaNames import MetroidPrimeArea
from ..data.RoomNames import RoomName
from . import MetroidPrimeTestBase
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from .. import MetroidPrimeWorld


class TestNoDoorRando(MetroidPrimeTestBase):
    options = {
        "door_color_randomization": "none",
    }

    def test_all_door_types_are_not_randomized(self):
        self.world.generate_early()
        world: "MetroidPrimeWorld" = self.world
        self.assertEqual(world.door_color_mapping, None)

    def test_starting_beam_is_power(self):
        self.world.generate_early()
        world: "MetroidPrimeWorld" = self.world
        distribute_items_restrictive(world.multiworld)
        config = make_config(world)
        self.assertTrue(config["gameConfig"]["startingItems"]["powerBeam"] == 1)
        self.assertEqual(
            config["gameConfig"]["startingBeam"],
            "Power",
            "Starting beam should be Power",
        )


class TestStartingBeamRandoWithNoDoorRando(MetroidPrimeTestBase):
    options = {
        "door_color_randomization": "none",
        "randomize_starting_beam": True,
        "include_power_beam_doors": True,
    }


class TestGlobalDoorRando(MetroidPrimeTestBase):
    options = {
        "door_color_randomization": "global",
    }

    def test_all_door_types_are_randomized_globally(self):
        self.world.generate_early()
        world: "MetroidPrimeWorld" = self.world
        first_mapping = None
        assert world.door_color_mapping
        self.assertTrue(
            len(world.door_color_mapping) > 0, "Door color mapping should not be empty"
        )
        for area in MetroidPrimeArea:
            if world.door_color_mapping[area.value].type_mapping is None:
                continue
            if first_mapping is None:
                first_mapping = world.door_color_mapping[area.value].type_mapping
                for original, new in first_mapping.items():
                    self.assertNotEqual(
                        original, new, "Door color should be randomized"
                    )
            else:
                self.assertEqual(
                    first_mapping,
                    world.door_color_mapping[area.value].type_mapping,
                    "Door color should be the same for all areas",
                )

    def test_door_colors_are_updated_in_config(self):
        self.world.generate_early()
        world: "MetroidPrimeWorld" = self.world
        distribute_items_restrictive(world.multiworld)
        config = make_config(world)
        self.assertNotEqual(
            config["levelData"]["Chozo Ruins"]["rooms"]["Ruined Shrine"]["doors"]["0"][
                "shieldType"
            ],
            DoorLockType.Wave.value,
        )


class TestRegionalDoorRando(MetroidPrimeTestBase):
    options = {
        "door_color_randomization": "regional",
    }

    def test_all_door_types_are_randomized_across_a_region(self):
        self.world.generate_early()
        world: "MetroidPrimeWorld" = self.world
        first_mapping = None
        assert world.door_color_mapping
        self.assertTrue(
            len(world.door_color_mapping) > 0, "Door color mapping should not be empty"
        )
        same_areas: List[MetroidPrimeArea] = []
        for area in MetroidPrimeArea:
            if world.door_color_mapping[area.value].type_mapping is None:
                continue
            if first_mapping is None:
                first_mapping = world.door_color_mapping[area.value].type_mapping
                for original, new in first_mapping.items():
                    self.assertNotEqual(
                        original, new, "Door color should be randomized"
                    )
            elif first_mapping == world.door_color_mapping[area.value].type_mapping:
                same_areas.append(area)
        self.assertTrue(
            len(same_areas) < 4,
            "Door color should be different for each area generally",
        )

    def test_door_colors_are_updated_in_config(self):
        self.world.generate_early()
        world: "MetroidPrimeWorld" = self.world
        distribute_items_restrictive(world.multiworld)
        config = make_config(world)
        self.assertNotEqual(
            config["levelData"]["Chozo Ruins"]["rooms"]["Ruined Shrine"]["doors"]["0"][
                "shieldType"
            ],
            DoorLockType.Wave.value,
        )


class TestDoorRandoWithDifferentStartRoomNonRequiredBeam(MetroidPrimeTestBase):
    options = {
        "door_color_randomization": "global",
        "starting_room_name": RoomName.Tower_Chamber.value,
    }

    def test_starting_beam_is_not_wave(self):
        self.world.generate_early()
        world: "MetroidPrimeWorld" = self.world
        distribute_items_restrictive(world.multiworld)
        config = make_config(world)
        self.assertTrue(config["gameConfig"]["startingItems"]["wave"] == 0)
        self.assertNotEqual(
            config["gameConfig"]["startingBeam"],
            "Wave",
            "Starting beam should not be Wave",
        )


class TestDoorRandoWithDifferentStartRoomWithRequiredBeam(MetroidPrimeTestBase):
    options = {
        "door_color_randomization": "global",
        "starting_room_name": RoomName.Save_Station_B.value,
    }

    def test_starting_beam_is_not_wave(self):
        self.world.generate_early()
        world: "MetroidPrimeWorld" = self.world
        distribute_items_restrictive(world.multiworld)
        config = make_config(world)
        self.assertTrue(config["gameConfig"]["startingItems"]["plasma"] == 1)
        self.assertEqual(
            config["gameConfig"]["startingBeam"],
            "Plasma",
            "Starting beam should be Plasm",
        )


class TestDoorPlando(MetroidPrimeTestBase):
    # TODO: rework the data structure here so you don't have to do area and type_mapping
    options = {
        "door_color_randomization": "regional",
        "door_color_mapping": {
            "Chozo Ruins": {
                "area": "Chozo Ruins",
                "type_mapping": {
                    "Wave Beam": "Ice Beam",
                    "Ice Beam": "Plasma Beam",
                    "Plasma Beam": "Wave Beam",
                },
            },
            "Magmoor Caverns": {
                "area": "Magmoor Caverns",
                "type_mapping": {
                    "Wave Beam": "Plasma Beam",
                    "Ice Beam": "Wave Beam",
                    "Plasma Beam": "Ice Beam",
                },
            },
            "Phendrana Drifts": {
                "area": "Phendrana Drifts",
                "type_mapping": {
                    "Wave Beam": "Plasma Beam",
                    "Ice Beam": "Wave Beam",
                    "Plasma Beam": "Ice Beam",
                },
            },
            "Tallon Overworld": {
                "area": "Tallon Overworld",
                "type_mapping": {
                    "Wave Beam": "Plasma Beam",
                    "Ice Beam": "Wave Beam",
                    "Plasma Beam": "Ice Beam",
                },
            },
            "Phazon Mines": {
                "area": "Phazon Mines",
                "type_mapping": {
                    "Wave Beam": "Plasma Beam",
                    "Ice Beam": "Wave Beam",
                    "Plasma Beam": "Ice Beam",
                },
            },
        },
    }

    def test_door_mapping_gets_set_from_plando(self):
        self.world.generate_early()
        world: "MetroidPrimeWorld" = self.world
        assert world.door_color_mapping
        self.assertTrue(
            len(world.door_color_mapping) > 0, "Door color mapping should not be empty"
        )
        for area in MetroidPrimeArea:
            self.assertEqual(world.door_color_mapping[area.value].type_mapping, world.options.door_color_mapping.get(area.value).get("type_mapping"), "Door color mapping should be set from plando")  # type: ignore


class TestGlobalDoorRandoWithBombAndPowerDoors(MetroidPrimeTestBase):
    options = {
        "door_color_randomization": "global",
        "include_morph_ball_bomb_doors": True,
        "include_power_beam_doors": True,
    }

    def test_bomb_doors_are_applied_to_single_region_that_is_not_start(self):
        world: "MetroidPrimeWorld" = self.world
        world.options.door_color_mapping.value = None  # type: ignore
        world.generate_early()
        bomb_door_region = None

        assert world.door_color_mapping
        for area, mapping in world.door_color_mapping.items():
            if DoorLockType.Bomb.value in mapping.type_mapping.values():
                if bomb_door_region is None:
                    bomb_door_region = area
                else:
                    self.fail("Bomb doors should only be applied to a single region")

        self.assertIsNotNone(
            bomb_door_region, "Bomb doors should be applied to one region"
        )
        self.assertNotEqual(
            bomb_door_region,
            MetroidPrimeArea.Tallon_Overworld.value,
            "Bomb doors should not be applied to the starting region",
        )

    def test_power_beam_doors_are_included_in_at_least_one_region(self):
        self.world.generate_early()
        world: "MetroidPrimeWorld" = self.world
        power_beam_door_found = False

        assert world.door_color_mapping
        for mapping in world.door_color_mapping.values():
            if DoorLockType.Power_Beam.value in mapping.type_mapping.values():
                power_beam_door_found = True
                break

        self.assertTrue(
            power_beam_door_found,
            "Power beam doors should be included in at least one region",
        )


class TestRegionalobalDoorRandoWithBombAndPowerDoors(MetroidPrimeTestBase):
    options = {
        "door_color_randomization": "regional",
        "include_morph_ball_bomb_doors": True,
        "include_power_beam_doors": True,
    }

    def test_bomb_doors_are_applied_to_single_region_that_is_not_start(self):
        world: "MetroidPrimeWorld" = self.world
        world.generate_early()
        bomb_door_region = None

        assert world.door_color_mapping
        for area, mapping in world.door_color_mapping.items():
            if DoorLockType.Bomb.value in mapping.type_mapping.values():
                if bomb_door_region is None:
                    bomb_door_region = area
                else:
                    self.fail("Bomb doors should only be applied to a single region")

        self.assertIsNotNone(
            bomb_door_region, "Bomb doors should be applied to one region"
        )
        self.assertNotEqual(
            bomb_door_region,
            MetroidPrimeArea.Tallon_Overworld.value,
            "Bomb doors should not be applied to the starting region",
        )


class TestBeamRandoWithDoorRando(MetroidPrimeTestBase):
    options = {
        "door_color_randomization": "regional",
        "include_power_beam_doors": True,
        "randomize_starting_beam": True,
    }

    def test_when_power_beam_is_not_starting_beam_and_power_beam_doors_are_included_the_new_starting_beam_doors_are_not_included(
        self,
    ):
        world: "MetroidPrimeWorld" = self.world
        world.options.door_color_mapping.value = None  # type: ignore
        world.generate_early()

        assert world.starting_room_data.selected_loadout
        # Check if the starting beam is not the power beam
        starting_beam = world.starting_room_data.selected_loadout.starting_beam
        self.assertNotEqual(
            starting_beam,
            SuitUpgrade.Power_Beam.value,
            "Starting beam should not be the power beam",
        )

        new_starting_beam_doors_found = False

        assert world.door_color_mapping
        for _, mapping in world.door_color_mapping.items():
            if starting_beam.value in mapping.type_mapping.values():
                new_starting_beam_doors_found = True
                break

        self.assertFalse(
            new_starting_beam_doors_found,
            "New starting beam doors should not be included when power beam doors are included",
        )
