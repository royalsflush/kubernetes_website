import dataclasses
import yaml


@dataclasses.dataclass
class VersionedSpec:
    default: bool
    lock_to_default: bool
    pre_release: str
    version: str


@dataclasses.dataclass
class YamlFeatureGate:
    name: str
    versioned_specs: [VersionedSpec] = dataclasses.field(default_factory=list)

    @classmethod
    def from_yaml_entry(cls, yaml_entry: dict[str, dict[str, any]]):
        self.name = yaml_entry['name']
        self.versioned_specs = []

        for specs_entry in yaml_entry['versionedSpecs']:
            vs = VersionedSpec(
                    specs_entry['default'],
                    specs_entry['lockToDefault'],
                    specs_entry['preRelease'],
                    specs_entry['version']
            )
            self.versioned_specs += [vs]


    def convertToSite(self):
        pass


@dataclasses.dataclass
class SiteFeatureGate:
    metadata: str
    description: str

    def __init__(self, metadata: dict[str, dict[str, any]], description: str):
        self.metadata = metadata
        self.description = description

    def modify_metadata(self, yaml_fg: YamlFeatureGate) -> None:
        return cls()

    def render_to_dir(self, target_dir: str):
        print(yaml.dump(self.metadata,
                        sort_keys=False,
                        explicit_start=True,
                        explicit_end=False), end='')
        print('---', end='')
        print(self.description)
