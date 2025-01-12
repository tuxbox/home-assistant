"""Controme client."""

from logging import getLogger

from aiohttp import ClientSession

from .const import API_RESPONSE_FIELD_TEMPERATURE

_LOGGER = getLogger(__name__)


class ContromeEntity:
    """base controme entity."""

    def __init__(self, id: str, name: str, floor: str, room: str) -> None:
        """Initialize the entity."""
        self._state: float = 0.0
        self._id = id
        self._name = name
        self._floor = floor
        self._room = room
        self._last_updated: str | None = None

    @property
    def id(self) -> str:
        """Get the id of the entity."""
        return self._id

    @id.setter
    def id(self, value: str) -> None:
        """Set the id of the entity."""
        self._id = value

    @property
    def name(self) -> str:
        """Get the name of the entity."""
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        """Set the id of the entity."""
        self._name = value

    @property
    def floor(self) -> str:
        """Get the floor of the entity."""
        return self._floor

    @floor.setter
    def floor(self, value: str) -> None:
        """Set the id of the entity."""
        self._floor = value

    @property
    def room(self) -> str:
        """Get the room of the entity."""
        return self._room

    @room.setter
    def room(self, value: str) -> None:
        """Set the id of the entity."""
        self._room = value

    @property
    def state(self) -> float:
        """Get the state of the entity."""
        return self._state

    @state.setter
    def state(self, value: float) -> None:
        """Set the id of the entity."""
        self._state = value

    @property
    def last_updated(self) -> str | None:
        """Get the last updated time of the entity."""
        return self._last_updated

    @last_updated.setter
    def last_updated(self, value: str) -> None:
        """Set the id of the entity."""
        self._last_updated = value

    def format_value(self, value: float) -> str:
        """Format a value to conform with the Controme API limitations."""
        result = "00.00"
        if value is not None:
            int_value = int(value)
            # Weird calculation of decimals due to stupid controme api limitations
            decimal_value = int((value - int(value)) * 10000)
            if decimal_value < 625:
                decimal_value = 0
            elif decimal_value < 1875:
                decimal_value = 12
            elif decimal_value < 3125:
                decimal_value = 25
            elif decimal_value < 4375:
                decimal_value = 37
            elif decimal_value < 5625:
                decimal_value = 50
            elif decimal_value < 6875:
                decimal_value = 62
            elif decimal_value < 8125:
                decimal_value = 75
            elif decimal_value < 9375:
                decimal_value = 87
            else:
                int_value = int_value + 1
                decimal_value = 0
            result = f"{int_value:02d}.{decimal_value:02d}"
        return result


class ContromeSensor(ContromeEntity):
    """Representation of a Controme entity."""

    def __init__(self, id: str, name: str, floor: str, room: str) -> None:
        """Initialize the entity."""
        super().__init__(id, name, floor, room)
        self._state = 0.0

    @property
    def state(self) -> float:
        """Get the state of the entity."""
        return self._state

    @state.setter
    def state(self, value: float) -> None:
        """Set the state of the entity."""
        self._state = value

    def get_formatted_state(self) -> str:
        """Get the formatted state of the entity."""
        return self.format_value(self._state)


class ContromeThermostat(ContromeSensor):
    """Representation of a Controme thermostat."""

    def __init__(self, id: str, name: str, floor: str, room: str) -> None:
        """Initialize the thermostat."""
        super().__init__(id, name, floor, room)
        self._state = 0.0
        self._target_state = 0.0

    @property
    def target_state(self) -> float:
        """Get the target state of the thermostat."""
        return self._target_state

    @target_state.setter
    def target_state(self, value: float) -> None:
        """Set the target state of the thermostat."""
        self._target_state = value

    def get_formatted_target_state(self) -> str:
        """Get the formatted target state of the thermostat."""
        return self.format_value(self._target_state)


class ContromeClient:
    """Controme client."""

    def __init__(
        self,
        session: ClientSession,
        host: str,
        port: int,
        username: str,
        password: str,
        home_id: int,
    ) -> None:
        """Initialize the client."""
        self._session = session
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._home_id = home_id

    async def get_entities(self, room_id: str = "") -> list[ContromeEntity]:
        """Get all entities."""
        suffix = ""
        if room_id != "":
            suffix = f"{room_id}/"
        async with self._session.get(
            f"http://{self._host}/get/json/v1/{self._home_id}/temps/{suffix}"
        ) as response:
            if response.status == 200:
                data = await response.json()
                entities: list[ContromeEntity] = []
                for etage in data:
                    floor = etage["etagenname"]
                    for raum in etage["raeume"]:
                        thermostat = ContromeThermostat(
                            id=raum["id"],
                            name=raum["name"],
                            floor=floor,
                            room=raum["name"],
                        )
                        thermostat.target_state = raum["solltemperatur"]
                        # just to work around a codespell error
                        thermostat.state = raum[
                            API_RESPONSE_FIELD_TEMPERATURE[
                                0 : len(API_RESPONSE_FIELD_TEMPERATURE) - 1
                            ]
                        ]
                        for sensor in raum["sensoren"]:
                            if sensor["raumtemperatursensor"]:
                                cs = ContromeSensor(
                                    id=sensor["name"],
                                    name=f"Isttemperatur {raum["name"]}",
                                    floor=floor,
                                    room=raum["name"],
                                )
                                cs.state = round(sensor["wert"], 1)
                                cs = sensor["letzte_uebertragung"]
                                thermostat.last_updated = sensor["letzte_uebertragung"]
                                entities.append(cs)
                            else:
                                s = ContromeSensor(
                                    id=sensor["name"],
                                    name=f'{sensor["beschreibung"]} {raum["name"]}',
                                    floor=floor,
                                    room=raum["name"],
                                )
                                s.state = round(sensor["wert"], 1)
                                s.last_updated = sensor["letzte_uebertragung"]
                                entities.append(s)

                        entities.append(thermostat)
        return entities

    async def update_state(self, sensor: ContromeSensor) -> None:
        """Update the state of a sensor."""
        # value = sensor.get_formatted_state()

    async def update_target_state(self, thermostat: ContromeThermostat) -> None:
        """Update the target state of a thermostat."""
        # target_value = thermostat.get_formatted_target_state()
        # print(target_value)
