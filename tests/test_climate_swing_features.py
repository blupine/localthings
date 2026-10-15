"""Swing controls follow each unit's available options."""

import pytest
from homeassistant.components.climate import ClimateEntityFeature

from custom_components.localthings.climate import LocalThingsClimate
from custom_components.localthings.registry.entities import ClimateDesc
from tests.test_subdevice_discovery import _coordinator, _discover


@pytest.mark.parametrize(
    "fixture",
    [
        "airconditioner_tp2x_rac_20k",
        "airconditioner_windfree_oscillation",
        "airconditioner_artik051_dongle_fac_18k",
    ],
)
async def test_swing_fallback_channels_keep_their_controls(hass, fixture):
    coordinator = _coordinator(hass)
    await _discover(coordinator, fixture)
    for bound in coordinator.bound:
        if isinstance(bound.desc, ClimateDesc):
            entity = LocalThingsClimate(coordinator, bound)
            assert entity.swing_modes
            assert entity.supported_features & ClimateEntityFeature.SWING_MODE


async def test_swing_feature_updates_when_options_arrive_later(hass):
    coordinator = _coordinator(hass)
    await _discover(coordinator, "airconditioner_fac_bora")
    bound = next(b for b in coordinator.bound if isinstance(b.desc, ClimateDesc))
    entity = LocalThingsClimate(coordinator, bound)
    assert entity.swing_modes == []
    before = entity.supported_features
    assert not before & ClimateEntityFeature.SWING_MODE

    coordinator._observe.apply(
        "/wind/direction/vs/0",
        {
            "x.com.samsung.da.modes": "Fix",
            "x.com.samsung.da.supportedModes": ["Fix", "Up_And_Low"],
        },
        source="poll",
    )
    assert entity.swing_modes == ["off", "vertical"]
    assert entity.supported_features == before | ClimateEntityFeature.SWING_MODE
