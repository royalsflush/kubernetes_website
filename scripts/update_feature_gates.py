#!/usr/bin/env python3
##
# This script has been tested with python 3.11

import sys
import tempfile
import os
import platform
import typing
import shutil
import subprocess
import dataclasses


error_msgs: [str] = []

# pip should be installed when Python is installed, but just in case...
if not (shutil.which('pip') or shutil.which('pip3')):
    error_msgs.append(
        "Install pip so you can install PyYAML. https://pip.pypa.io/en/stable/installation")

reqs = subprocess.check_output([sys.executable, '-m', 'pip', 'freeze'])
installed_packages = [r.decode().split('==')[0] for r in reqs.split()]
if 'PyYAML' not in installed_packages:
    error_msgs.append(
        "Please ensure the PyYAML package is installed; see https://pypi.org/project/PyYAML")
else:
    import yaml


K_REPO = "https://github.com/kubernetes/kubernetes.git"
K_BRANCH = "master"
REL_PATH_FEATURE_LIST = (
        "test/compatibility_lifecycle/reference/versioned_feature_list.yaml"
)


@dataclasses.dataclass
class VersionedSpec:
    default: bool
    lock_to_default: bool
    pre_release: str
    version: str


@dataclasses.dataclass
class FeatureGate:
    name: str
    versioned_specs: [VersionedSpec] = dataclasses.field(default_factory=list)


def clone_kubernetes() -> str:
    """Clones the kubernetes/kubernetes repo to tmp/."""
    try:
        work_dir = tempfile.mkdtemp(
            dir='/tmp' if platform.system() == 'Darwin' else tempfile.gettempdir()
    )
    except OSError as ose:
        print("[Error] Unable to create temp work_dir {}; error: {}"
              .format(work_dir, ose))
        raise ose

    print("Working dir {}".format(work_dir))
    
    os.chdir(work_dir)
    print("Cloning repo...")

    cmd = "git clone --depth=1 -b {0} {1}".format(K_BRANCH, K_REPO)
    res = subprocess.call(cmd, shell=True)
    if res != 0:
        print("[Error] Failed cloning kubernetes/kubernetes")
        raise RuntimeError

    return work_dir


def parse_feature_gates(k_root: str) -> [FeatureGate]:
    """Given the path to the kubernetes dir, parses the feature gates."""
    with open(os.path.join(k_root, REL_PATH_FEATURE_LIST), 'r') as f:   
        fg_yaml = yaml.full_load(f)
        fgs = []

        for entry in fg_yaml:
            fg = FeatureGate(entry['name'])

            for specs_entry in entry['versionedSpecs']:
                vs = VersionedSpec(
                        specs_entry['default'],
                        specs_entry['lockToDefault'],
                        specs_entry['preRelease'],
                        specs_entry['version']
                )
                fg.versioned_specs += [vs]
                pass

            fgs += [fg]

        print(fgs)
        return fgs


def main():
    if len(error_msgs):
        for msg in error_msgs:
            print("[Error] {}".format(msg))
        return 1

    try:
        tmpdir = clone_kubernetes()
        parse_feature_gates(os.path.join(tmpdir, "kubernetes"))

        print("Work done, deleting kubernetes repo")
        shutil.rmtree(tmpdir)
    except Exception as err:
        if os.path.exists(tmpdir):
            shutil.rmtree(tmpdir)

        print("Unexpected error: {}".format(err))
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
