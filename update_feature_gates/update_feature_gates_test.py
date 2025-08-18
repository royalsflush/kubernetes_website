import unittest
import unittest.mock

import update_feature_gates
from model import YamlFeatureGate, SiteFeatureGate, VersionedSpec


YAML_TEST = '''
- name: AggregatedDiscoveryRemoveBetaType
  versionedSpecs:
  - default: false
    lockToDefault: false
    preRelease: GA
    version: "1.0"
  - default: true
    lockToDefault: false
    preRelease: Deprecated
    version: "1.33"
'''


class TestUpdateFeatureGates(unittest.TestCase):
    def test_yaml_parse(self):
        expected = YamlFeatureGate(name="AggregatedDiscoveryRemoveBetaType",
                                    versioned_specs=[
                            VersionedSpec(default=False,
                                          lock_to_default=False,
                                          pre_release="GA",
                                          version="1.0"),
                            VersionedSpec(default=True,
                                          lock_to_default=False,
                                          pre_release="Deprecated",
                                          version="1.33")
                        
                        ])

        with unittest.mock.patch(
                'builtins.open',
                unittest.mock.mock_open(read_data=YAML_TEST)) as file:
            fgs = update_feature_gates.parse_yaml_feature_gates(
                'k_root', False)
            file.assert_called_once_with(
                'k_root/test/compatibility_lifecycle/'
                'reference/versioned_feature_list.yaml', 'r')


if __name__ == '__main__':
    unittest.main()
