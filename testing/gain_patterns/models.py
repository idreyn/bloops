from dataclasses import dataclass
from os import path, mkdir
import json

here_directory = path.abspath(path.dirname(__file__))
experiments_directory = path.join(here_directory, "experiments")
recordings_directory = path.join(here_directory, "recordings")


@dataclass
class ExperimentEntry:
    experiment: "Experiment"
    azimuth: int
    trial: int

    @property
    def wav_file_path(self):
        return path.join(
            recordings_directory,
            self.experiment.name,
            f"a{self.azimuth}_t{self.trial}.wav",
        )
    
    @property
    def wav_file_exists(self):
        return path.isfile(self.wav_file_path)


@dataclass
class Experiment:
    name: str
    min_freq: int
    max_freq: int
    freq_spacing: int
    tone_length_us: int
    silence_length_us: int
    min_azimuth: int = 0
    max_azimuth: int = 90
    azimuth_spacing: int = 10
    trials_per_azimuth: int = 3
    sample_rate: int = 192000

    def __post_init__(self):
        wavs_path = path.join(
            recordings_directory,
            self.name,
        )
        if not path.exists(wavs_path):
            mkdir(wavs_path)

    @property
    def frequencies(self):
        return list(
            range(
                self.min_freq,
                self.max_freq + self.freq_spacing,
                self.freq_spacing,
            )
        )

    @property
    def azimuths(self):
        return list(
            range(
                self.min_azimuth,
                self.max_azimuth + self.azimuth_spacing,
                self.azimuth_spacing,
            )
        )

    @property
    def json_file_path(self):
        return Experiment.path_by_name(self.name)

    @staticmethod
    def path_by_name(name: str):
        return path.join(experiments_directory, f"{name}.json")

    @staticmethod
    def load_by_name(name: str):
        contents = open(Experiment.path_by_name(name)).read()
        contents = json.loads(contents)
        props = contents["properties"]
        return Experiment(
            name=props["name"],
            sample_rate=props["sample_rate"],
            min_freq=props["min_freq"],
            max_freq=props["max_freq"],
            freq_spacing=props["freq_spacing"],
            tone_length_us=props["tone_length_us"],
            silence_length_us=props["silence_length_us"],
            min_azimuth=props["min_azimuth"],
            max_azimuth=props["max_azimuth"],
            azimuth_spacing=props["azimuth_spacing"],
            trials_per_azimuth=props["trials_per_azimuth"],
        )

    # def collect_entry(self, entry: ExperimentEntry):
    #     self.wav_files.setdefault(entry.azimuth, {})
    #     self.wav_files[entry.azimuth].setdefault(entry.trial, {})
    #     self.wav_files[entry.azimuth][entry.trial] = True

    def save(self):
        res = {
            "properties": {
                "name": self.name,
                "sample_rate": self.sample_rate,
                "min_freq": self.min_freq,
                "max_freq": self.max_freq,
                "freq_spacing": self.freq_spacing,
                "silence_length_us": self.silence_length_us,
                "tone_length_us": self.tone_length_us,
                "min_azimuth": self.min_azimuth,
                "max_azimuth": self.max_azimuth,
                "azimuth_spacing": self.azimuth_spacing,
                "trials_per_azimuth": self.trials_per_azimuth,
            },
        }
        open(self.json_file_path, "w").write(json.dumps(res, indent=2))
