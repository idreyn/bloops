import json
import deepmerge
from typing import Mapping, Literal
from pydantic import BaseModel

from robin.constants import BASE_PATH
from robin.echolocation.pulse import Pulse


class EmitterConfig(BaseModel):
    front_gain: float = 1
    side_gain: float = 1
    ms_front_delay: int = 0
    ms_warmup_time: int = 25


class MicrophoneConfig(BaseModel):
    reverse_channels: bool = False
    left_gain: float = 1  # Not implemented yet
    right_gain: float = 1  # Not implemented yet


class EcholocationConfig(BaseModel):
    ms_silence_before: int = 1
    ms_record_duration: int = 100
    slowdown: int = 20
    playback: bool = True
    emission_gain: float = 1
    noisereduce: bool = False  # Not implemented yet
    emitters: EmitterConfig
    microphones: MicrophoneConfig


class SaveConfig(BaseModel):
    save_pulse: bool = True
    save_recording: bool = True
    save_resampled: bool = True
    save_camera_image: bool = False
    file_prefix: str = ""


class RemoteConfig(BaseModel):
    remote_name: str
    remote_keys: Mapping[str, Literal["current"] | Pulse]


class BatcaveConfig(BaseModel):
    self_host: bool = True
    host: str | None = None
    build_dev: bool = False


class ConfigRoot(BaseModel):
    generated_at: int | None = None
    pulse: Pulse
    echolocation: EcholocationConfig
    save: SaveConfig
    remote: RemoteConfig
    batcave: BatcaveConfig


class Config(object):
    filename: str
    current: ConfigRoot

    def __init__(self, filename: str):
        content = open(filename, "r").read()
        self.filename = filename
        self.current = ConfigRoot.model_validate_json(content)

    def update_config_json(self, json: dict, and_save: bool):
        updated = deepmerge.always_merger.merge(self.current.model_dump(), json)
        self.current = ConfigRoot.model_validate(updated, strict=True)
        if and_save:
            json_str = self.current.model_dump_json(indent=4)
            open(self.filename, "w").write(json_str)


def update_config_schema():
    schema = ConfigRoot.model_json_schema()
    schema_str = json.dumps(schema, indent=4)
    open(f"{BASE_PATH}/config.schema.json", "w").write(schema_str)
