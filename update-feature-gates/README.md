# update_feature_gates.py

This script will fetch the last feature list from kubernetes/kubernetes (in
test/compatibility_lifecycle/reference/versioned_feature_list.yaml from the 
master branch) and use it to update the website documentation.

It has three cases it covers:

1. If both the site and YAML have a particular feature, it just updates the 
stages information from the YAML.
1. If only the site has the feature, it marks it as "removed".
1. If only the YAML has the feature, it creates a new feature in the site with
the exact match of the YAML and an empty description.

Usage:

```
python3 update_feature_gates.py
```
