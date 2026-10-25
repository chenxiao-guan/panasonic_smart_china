"""Experimental profile for Panasonic FV-54BD1C bathroom heaters.

The 54BD1C shares the 0820 cloud endpoints with the 54BA1C family.  The app
only exposes ventilation, cool-dry and Nanoe X, so this profile intentionally
does not expose heat / heat-dry.

Mode values follow the 54BA1C H5 client:
    APP_DELAY 0x20, APP_EXAIR_S 0x26, APP_COOLDRY_S 0x28, APP_NANOEX 0x2D.
If the device reports different values, adjust HVAC_MAPPING after checking the
``running_mode`` / ``raw_status`` attributes on the climate entity.
"""

from __future__ import annotations

from homeassistant.components.climate.const import HVACMode

from ..models import (
    ENTITY_KIND_BATHROOM_HEATER,
    PLATFORM_CLIMATE,
    PROTOCOL_BATHROOM_HEATER,
    PanasonicEndpoint,
    PanasonicProfile,
)

HVAC_MAPPING = {
    HVACMode.OFF: 0x00,
    HVACMode.FAN_ONLY: 0x26,
    HVACMode.DRY: 0x28,
}

# When the H5 client starts a mode it also sends that mode's remembered timer
# value.  Sending 255 ("no change") is accepted by the API but some devices
# ignore the whole command, so mirror the H5 behaviour here.
TIME_SET_MODE_KEYS = {
    0x26: "remAirHighTimeSet",
    0x27: "remAirLowTimeSet",
    0x28: "remCoolHighTimeSet",
    0x29: "remCoolLowTimeSet",
    0x2D: "remDegermTimeSet",
}

# Default payload copied from the official 54BA1C H5 client setData object.
# Every field set to 255 means "do not change"; only runningMode is replaced
# by the entity when the user selects a mode.
CONTROL_PAYLOAD_TEMPLATE = {
    "runningMode": 255,
    "warmTempset": 255,
    "windDirectionSet": 255,
    "windKindSet": 255,
    "timeSet": 255,
    "gasCheckSet": 255,
    "DIYnextRunningMode": 255,
    "DIYnextWarmTempset": 255,
    "DIYnextwindDirectionSet": 255,
    "DIYnextwindKindSet": 255,
    "DIYnextTimeSet": 255,
    "DIYnextStepNo": 5,
}

BATHROOM_HEATER_0820_FV_54BD1C_PROFILE = PanasonicProfile(
    profile_id="bathroom_heater_0820_fv_54bd1c",
    controller_model="FV-54BD1C",
    name="松下风暖浴霸 (FV-54BD1C)",
    category_ids=frozenset({"0820"}),
    model_ids=frozenset({"54BD1C", "FV-54BD1C"}),
    ha_platforms=(PLATFORM_CLIMATE,),
    entity_kind=ENTITY_KIND_BATHROOM_HEATER,
    protocol=PROTOCOL_BATHROOM_HEATER,
    status_endpoint=PanasonicEndpoint(
        path="ADevGetStatusInfoFV54BA1C",
        request_id=100,
        require_results=True,
        required_result_keys=frozenset({"runningMode"}),
    ),
    set_endpoint=PanasonicEndpoint(
        path="ADevSetStatusInfoFV54BA1C",
        request_id=52,
        require_results=False,
        allow_non_json_response=True,
    ),
    default_hvac_mode=HVACMode.FAN_ONLY,
    hvac_mapping=HVAC_MAPPING,
    control_payload_template=CONTROL_PAYLOAD_TEMPLATE,
    # No forced 15-minute timer for this model; use the remembered timer for
    # the selected mode instead.
    force_time_set_modes=frozenset(),
    time_set_mode_keys=TIME_SET_MODE_KEYS,
    # Nanoe X is exposed as a HA preset because it has no HVAC equivalent.
    nanoe_mode=0x2D,
    cookie_required=True,
)
