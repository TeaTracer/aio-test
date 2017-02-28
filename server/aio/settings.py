import yaml

config_file_path = "config.yaml"

with open(config_file_path) as f:
    settings = yaml.load(f.read())
