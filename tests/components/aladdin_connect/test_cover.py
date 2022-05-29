"""Test the Aladdin Connect Cover."""
from datetime import timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from homeassistant.components.aladdin_connect.const import DOMAIN
from homeassistant.components.cover import DOMAIN as COVER_DOMAIN
from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import (
    ATTR_ENTITY_ID,
    CONF_PASSWORD,
    CONF_USERNAME,
    SERVICE_CLOSE_COVER,
    SERVICE_OPEN_COVER,
    STATE_CLOSED,
    STATE_CLOSING,
    STATE_OPEN,
    STATE_OPENING,
)
from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component
from homeassistant.util.dt import utcnow

from tests.common import MockConfigEntry, async_fire_time_changed

YAML_CONFIG = {"username": "test-user", "password": "test-password"}

DEVICE_CONFIG_OPEN = {
    "device_id": 533255,
    "door_number": 1,
    "name": "home",
    "status": "open",
    "link_status": "Connected",
}

DEVICE_CONFIG_OPENING = {
    "device_id": 533255,
    "door_number": 1,
    "name": "home",
    "status": "opening",
    "link_status": "Connected",
}

DEVICE_CONFIG_CLOSED = {
    "device_id": 533255,
    "door_number": 1,
    "name": "home",
    "status": "closed",
    "link_status": "Connected",
}

DEVICE_CONFIG_CLOSING = {
    "device_id": 533255,
    "door_number": 1,
    "name": "home",
    "status": "closing",
    "link_status": "Connected",
}

DEVICE_CONFIG_DISCONNECTED = {
    "device_id": 533255,
    "door_number": 1,
    "name": "home",
    "status": "open",
    "link_status": "Disconnected",
}

DEVICE_CONFIG_BAD = {
    "device_id": 533255,
    "door_number": 1,
    "name": "home",
    "status": "open",
}
DEVICE_CONFIG_BAD_NO_DOOR = {
    "device_id": 533255,
    "door_number": 2,
    "name": "home",
    "status": "open",
    "link_status": "Disconnected",
}


async def test_setup_get_doors_errors(hass: HomeAssistant) -> None:
    """Test component setup Get Doors Errors."""
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        data=YAML_CONFIG,
        unique_id="test-id",
    )
    config_entry.add_to_hass(hass)
    with patch(
        "homeassistant.components.aladdin_connect.cover.AladdinConnectClient.login",
        return_value=True,
    ), patch(
        "homeassistant.components.aladdin_connect.cover.AladdinConnectClient.get_doors",
        return_value=None,
    ):
        assert await hass.config_entries.async_setup(config_entry.entry_id) is True
        await hass.async_block_till_done()
        assert len(hass.states.async_all()) == 0


async def test_setup_login_error(
    hass: HomeAssistant, mock_aladdinconnect_api: MagicMock
) -> None:
    """Test component setup Login Errors."""
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        data=YAML_CONFIG,
        unique_id="test-id",
    )
    config_entry.add_to_hass(hass)
    mock_aladdinconnect_api.login.return_value = False
    with patch(
        "homeassistant.components.aladdin_connect.cover.AladdinConnectClient",
        return_value=mock_aladdinconnect_api,
    ):

        assert await hass.config_entries.async_setup(config_entry.entry_id) is False


async def test_setup_component_noerror(hass: HomeAssistant) -> None:
    """Test component setup No Error."""
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        data=YAML_CONFIG,
        unique_id="test-id",
    )
    config_entry.add_to_hass(hass)
    with patch(
        "homeassistant.components.aladdin_connect.cover.AladdinConnectClient.login",
        return_value=True,
    ):

        assert await hass.config_entries.async_setup(config_entry.entry_id)
        await hass.async_block_till_done()

    assert config_entry.state == ConfigEntryState.LOADED
    assert len(hass.config_entries.async_entries(DOMAIN)) == 1


async def test_cover_open(
    hass: HomeAssistant,
    mock_aladdinconnect_api: MagicMock,
) -> None:
    """Test component setup open cover cover."""
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        data=YAML_CONFIG,
        unique_id="test-id",
    )
    config_entry.add_to_hass(hass)

    assert await async_setup_component(hass, "homeassistant", {})
    await hass.async_block_till_done()
    mock_aladdinconnect_api.get_door_status = AsyncMock(return_value=STATE_OPEN)
    with patch(
        "homeassistant.components.aladdin_connect.AladdinConnectClient",
        return_value=mock_aladdinconnect_api,
    ):
        await hass.config_entries.async_setup(config_entry.entry_id)
        await hass.async_block_till_done()

    assert config_entry.state == ConfigEntryState.LOADED
    assert len(hass.config_entries.async_entries(DOMAIN)) == 1
    assert COVER_DOMAIN in hass.config.components

    await hass.services.async_call(
        COVER_DOMAIN,
        SERVICE_OPEN_COVER,
        {ATTR_ENTITY_ID: "cover.home"},
        blocking=True,
    )
    await hass.async_block_till_done()
    assert hass.states.get("cover.home").state == STATE_OPEN


async def test_cover_close(
    hass: HomeAssistant,
    mock_aladdinconnect_api: MagicMock,
) -> None:
    """Test component setup close cover."""
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        data=YAML_CONFIG,
        unique_id="test-id",
    )
    config_entry.add_to_hass(hass)

    assert await async_setup_component(hass, "homeassistant", {})
    await hass.async_block_till_done()
    mock_aladdinconnect_api.get_door_status = AsyncMock(return_value=STATE_CLOSED)
    with patch(
        "homeassistant.components.aladdin_connect.AladdinConnectClient",
        return_value=mock_aladdinconnect_api,
    ):
        await hass.config_entries.async_setup(config_entry.entry_id)
        await hass.async_block_till_done()

    assert config_entry.state == ConfigEntryState.LOADED
    assert len(hass.config_entries.async_entries(DOMAIN)) == 1
    assert COVER_DOMAIN in hass.config.components

    await hass.services.async_call(
        COVER_DOMAIN,
        SERVICE_CLOSE_COVER,
        {ATTR_ENTITY_ID: "cover.home"},
        blocking=True,
    )
    await hass.async_block_till_done()
    assert hass.states.get("cover.home").state == STATE_CLOSED


async def test_cover_closing(
    hass: HomeAssistant,
    mock_aladdinconnect_api: MagicMock,
) -> None:
    """Test component setup close cover."""
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        data=YAML_CONFIG,
        unique_id="test-id",
    )
    config_entry.add_to_hass(hass)

    assert await async_setup_component(hass, "homeassistant", {})
    await hass.async_block_till_done()

    mock_aladdinconnect_api.get_door_status = AsyncMock(return_value=STATE_CLOSING)

    with patch(
        "homeassistant.components.aladdin_connect.AladdinConnectClient",
        return_value=mock_aladdinconnect_api,
    ):
        await hass.config_entries.async_setup(config_entry.entry_id)
        await hass.async_block_till_done()

    assert config_entry.state == ConfigEntryState.LOADED
    assert len(hass.config_entries.async_entries(DOMAIN)) == 1
    assert COVER_DOMAIN in hass.config.components

    await hass.async_block_till_done()
    async_fire_time_changed(
        hass,
        utcnow() + timedelta(seconds=300),
    )
    await hass.async_block_till_done()
    assert hass.states.get("cover.home").state == STATE_CLOSING


async def test_cover_openning(
    hass: HomeAssistant,
    mock_aladdinconnect_api: MagicMock,
) -> None:
    """Test component setup close cover."""
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        data=YAML_CONFIG,
        unique_id="test-id",
    )
    config_entry.add_to_hass(hass)

    assert await async_setup_component(hass, "homeassistant", {})
    await hass.async_block_till_done()

    mock_aladdinconnect_api.get_door_status = AsyncMock(return_value=STATE_OPENING)

    with patch(
        "homeassistant.components.aladdin_connect.AladdinConnectClient",
        return_value=mock_aladdinconnect_api,
    ):
        await hass.config_entries.async_setup(config_entry.entry_id)
        await hass.async_block_till_done()

    assert config_entry.state == ConfigEntryState.LOADED
    assert len(hass.config_entries.async_entries(DOMAIN)) == 1
    assert COVER_DOMAIN in hass.config.components

    await hass.async_block_till_done()
    async_fire_time_changed(
        hass,
        utcnow() + timedelta(seconds=300),
    )
    await hass.async_block_till_done()
    assert hass.states.get("cover.home").state == STATE_OPENING


async def test_yaml_import(
    hass: HomeAssistant,
    caplog: pytest.LogCaptureFixture,
    mock_aladdinconnect_api: MagicMock,
):
    """Test setup YAML import."""
    assert COVER_DOMAIN not in hass.config.components

    with patch(
        "homeassistant.components.aladdin_connect.config_flow.AladdinConnectClient",
        return_value=mock_aladdinconnect_api,
    ):
        await async_setup_component(
            hass,
            COVER_DOMAIN,
            {
                COVER_DOMAIN: {
                    "platform": DOMAIN,
                    "username": "test-user",
                    "password": "test-password",
                }
            },
        )
        await hass.async_block_till_done()
    assert hass.config_entries.async_entries(DOMAIN)
    assert "Configuring Aladdin Connect through yaml is deprecated" in caplog.text

    assert hass.config_entries.async_entries(DOMAIN)
    config_data = hass.config_entries.async_entries(DOMAIN)[0].data
    assert config_data[CONF_USERNAME] == "test-user"
    assert config_data[CONF_PASSWORD] == "test-password"


async def test_callback(
    hass: HomeAssistant,
    mock_aladdinconnect_api: MagicMock,
):
    """Test callback from Aladdin Connect API."""
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        data=YAML_CONFIG,
        unique_id="test-id",
    )
    config_entry.add_to_hass(hass)

    assert await async_setup_component(hass, "homeassistant", {})
    await hass.async_block_till_done()

    mock_aladdinconnect_api.get_door_status = AsyncMock(return_value=STATE_CLOSING)

    with patch(
        "homeassistant.components.aladdin_connect.AladdinConnectClient",
        return_value=mock_aladdinconnect_api,
    ):
        await hass.config_entries.async_setup(config_entry.entry_id)
        await hass.async_block_till_done()

    with patch(
        "homeassistant.components.aladdin_connect.AladdinConnectClient._call_back",
        AsyncMock(return_value={"door": 1, "door_status": "opening"}),
    ):
        mock_calls = mock_aladdinconnect_api.register_callback.mock_calls

        callback = mock_calls[0][1][0]
        await callback()

    assert hass.states.get("cover.home").state == STATE_CLOSING
