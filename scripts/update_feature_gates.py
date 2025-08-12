#!/usr/bin/env python3
##
# This script has been tested with python 3.11
#
# Usage:
# python3 

import argparse
import sys
import tempfile
import os
import platform
import typing
import shutil
import subprocess
import dataclasses
import pathlib
import itertools
import typing


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
REL_PATH_FEATURE_DOC_DIR = (
        "content/en/docs/reference/command-line-tools-reference/feature-gates/"
)

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

    def __init__(self, yaml_entry: dict[str, dict[str, any]]):
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
class Stages: 
    stage: str
    default_value: bool
    from_version: str
    to_version: str

SFG = typing.TypeVar('SFG', bound='SiteFeatureGate')

@dataclasses.dataclass
class SiteFeatureGate:
    filename: str
    header: str
    footer: str

    @classmethod
    def from_file(cls, file: typing.TextIO, verbose: True) -> SFG:
        return cls(header="", footer="", filename="")

    @classmethod
    def from_yaml_feature_gate(cls, yaml_fg: YamlFeatureGate) -> SFG:
        return cls()

    def render_markdown(self):
        pass


def clone_kubernetes(verbose: bool) -> str:
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
    res = subprocess.call(
            cmd, shell=True,
            stdout=None if verbose else subprocess.DEVNULL,
            stderr=None if verbose else subprocess.DEVNULL)

    if res != 0:
        print("[Error] Failed cloning kubernetes/kubernetes")
        raise RuntimeError

    return work_dir


def parse_yaml_feature_gates(k_root: str, verbose: bool) -> [YamlFeatureGate]:
    """Given the path to the kubernetes dir, parses the feature gates."""
    with open(os.path.join(k_root, REL_PATH_FEATURE_LIST), 'r') as f:   
        fg_yaml = yaml.full_load(f)
        fgs = []

        for entry in fg_yaml:
            fgs += [YamlFeatureGate(entry)]

        return fgs


def parse_site_feature_gates(
        website_root: str, verbose: bool) -> [SiteFeatureGate]:
    """Parse feature gates from the website documentation.

    Given the path to the root of the website repo, parses the feature gates
    from the English version of the documentation."""
    fgs = []

    for l in os.listdir(os.path.join(website_root, REL_PATH_FEATURE_DOC_DIR)):
        with open(os.path.join(website_root, REL_PATH_FEATURE_DOC_DIR, l)) as f:
            fgs += [SiteFeatureGate.from_file(f, verbose)]

    return fgs


def main():
    if len(error_msgs):
        for msg in error_msgs:
            print("[Error] {}".format(msg))
        return 1

    parser = argparse.ArgumentParser(
            prog='Update Feature Gates',
            description='Updates the feature gates documentation')
    parser.add_argument('--dry_run', type=bool, default=False)
    parser.add_argument('-v', '--verbose', type=bool, default=False)
    args = parser.parse_args()
    print(args.verbose)

    try:
        tmpdir = clone_kubernetes(args.verbose)
        yaml_fgs = parse_yaml_feature_gates(
                os.path.join(tmpdir, "kubernetes"), args.verbose)

        script_path = pathlib.Path(os.path.dirname(os.path.realpath(__file__)))
        site_fgs = parse_site_feature_gates(
                script_path.parent.absolute(), args.verbose)

        print("Work done, deleting kubernetes repo")
        shutil.rmtree(tmpdir)
    except Exception as err:
        print("Unexpected error: {}".format(err))
        return 1
    finally:
        if os.path.exists(tmpdir):
            shutil.rmtree(tmpdir)

    return 0


if __name__ == '__main__':
    sys.exit(main())
