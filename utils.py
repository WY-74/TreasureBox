import yaml


## Open yaml file
def load_yaml_map(path: str):
    with open(path, 'r') as f:
        map = yaml.safe_load(f)
    return map
