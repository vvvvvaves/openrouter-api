import yaml
import json
import os
from yaml.loader import SafeLoader


PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(PROJECT_ROOT, 'config.yaml')
LLM_PATH = os.path.join(PROJECT_ROOT, 'llm.yaml')
RUN = "deploy"

def get_config(run: str = RUN) -> dict:
    with open(CONFIG_PATH, 'r') as f:
        config_data = list(yaml.load_all(f, Loader=SafeLoader))[0]
    return config_data

def get_response_format(run: str = RUN) -> dict:
    config_data = get_config(run)
    with open(config_data[run]["response_format"], 'r') as f:
        schema = json.load(f)
    return schema

def get_llm_config(run: str = RUN) -> dict:
    with open(LLM_PATH, 'r') as f:
        llm_data = list(yaml.load_all(f, Loader=SafeLoader))[0]
    return llm_data

def get_current_llm(run: str = RUN) -> dict:
    config_data = get_config(run)
    llm_data = get_llm_config(run)

    for model in llm_data['llm_apis']:
        if model['model'] == config_data[run]["model"]:
            return model

def get_api(run: str = RUN) -> "API":
    from api import API
    return API(**get_current_llm(run))