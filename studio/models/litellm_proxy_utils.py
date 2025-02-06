from typing import List
import yaml
import subprocess
import os
import signal

import studio.consts as studio_consts
from studio.db.model import Model as StudioModel
import os
import signal
import psutil
import studio.consts as studio_consts


class LitellmModelParams:
    pass


class OpenAILitellmModelParams(LitellmModelParams):
    def __init__(self, model: str, api_key: str):
        self.model = model
        self.api_key = api_key

    @classmethod
    def from_dict(cls, model_dict: dict):
        return cls(model=model_dict["model"], api_key=model_dict["api_key"])

    def to_dict(self):
        return {"model": self.model, "api_key": self.api_key}


class CustomOpenAILitellmModelParams(OpenAILitellmModelParams):
    def __init__(self, model: str, api_key: str, api_base: str):
        self.api_base = api_base
        super().__init__(model, api_key)

    @classmethod
    def from_dict(cls, model_dict: dict):
        return cls(model=model_dict["model"], api_key=model_dict["api_key"], api_base=model_dict["api_base"])

    def to_dict(self):
        return super().to_dict() | {"api_base": self.api_base}


class AzureOpenAILitellmModelParams(OpenAILitellmModelParams):
    def __init__(self, model: str, api_key: str, api_base: str):
        self.api_base = api_base
        super().__init__(model, api_key)

    @classmethod
    def from_dict(cls, model_dict: dict):
        return cls(model=model_dict["model"], api_key=model_dict["api_key"], api_base=model_dict["api_base"])

    def to_dict(self):
        return super().to_dict() | {"api_base": self.api_base}


class LitellmModelEntry:
    def __init__(self, model_name: str, litellm_params: LitellmModelParams):
        self.model_name = model_name
        self.litellm_params = litellm_params

    @classmethod
    def from_dict(cls, model_dict: dict):
        model_name = model_dict["model_name"]
        model_params = model_dict["litellm_params"]
        if model_params["model"].startswith("openai"):
            if "api_base" in model_params:
                return cls(model_name, CustomOpenAILitellmModelParams.from_dict(model_params))
            else:
                return cls(model_name, OpenAILitellmModelParams.from_dict(model_params))
        elif model_params["model"].startswith("azure"):
            return cls(model_name, AzureOpenAILitellmModelParams.from_dict(model_params))
        else:
            raise ValueError(f"Invalid model type: {model_params['model']}")

    def to_dict(self):
        return {"model_name": self.model_name, "litellm_params": self.litellm_params.to_dict()}


class LitellmModelList:
    def __init__(self, model_list: List[LitellmModelParams]) -> None:
        self.model_list = model_list

    @classmethod
    def from_dict(cls, model_list_dict: dict):
        return cls([LitellmModelEntry.from_dict(model_entry) for model_entry in model_list_dict["model_list"]])

    def to_dict(self):
        return {"model_list": [model_entry.to_dict() for model_entry in self.model_list]}


def init_config_file():
    with open(studio_consts.DEFAULT_LITELLM_CONFIG_STORAGE_LOCATION, "w") as f:
        empty_config = LitellmModelList(model_list=list())
        empty_config_dict = empty_config.to_dict()
        yaml_string = yaml.dump(empty_config_dict)
        f.write(yaml_string)


def load_config_file() -> LitellmModelList:
    with open(studio_consts.DEFAULT_LITELLM_CONFIG_STORAGE_LOCATION, "r") as f:
        yaml_string = f.read()
        config = yaml.load(yaml_string, Loader=yaml.FullLoader)
        return LitellmModelList.from_dict(config)


def _create_model_entry(model: StudioModel) -> LitellmModelEntry:
    litellm_model_name = model.model_name
    if model.model_type == studio_consts.SupportedModelTypes.OPENAI:
        model_param = OpenAILitellmModelParams(model="openai/" + model.provider_model, api_key=model.api_key)
    elif model.model_type == studio_consts.SupportedModelTypes.OPENAI_COMPATIBLE:
        model_param = CustomOpenAILitellmModelParams(
            model="openai/" + model.provider_model, api_key=model.api_key, api_base=model.api_base
        )
    elif model.model_type == studio_consts.SupportedModelTypes.AZURE_OPENAI:
        model_param = AzureOpenAILitellmModelParams(
            model="azure/" + model.provider_model, api_key=model.api_key, api_base=model.api_base
        )
    else:
        raise ValueError(f"Invalid model type: {model.model_type}")
    return LitellmModelEntry(model_name=litellm_model_name, litellm_params=model_param)


def refresh_models_to_config(models: List[StudioModel]):
    config = LitellmModelList(model_list=list())
    model_entries = [_create_model_entry(model) for model in models]
    config.model_list.extend(model_entries)
    with open(studio_consts.DEFAULT_LITELLM_CONFIG_STORAGE_LOCATION, "w") as f:
        yaml_string = yaml.dump(config.to_dict())
        f.write(yaml_string)


def add_model_to_config(model: StudioModel):
    config = load_config_file()
    model_entry = _create_model_entry(model)
    config.model_list.append(model_entry)
    with open(studio_consts.DEFAULT_LITELLM_CONFIG_STORAGE_LOCATION, "w") as f:
        yaml_string = yaml.dump(config.to_dict())
        f.write(yaml_string)


def delete_model_from_config(studio_model_name: str):
    config = load_config_file()
    litellm_model_name = studio_model_name
    config.model_list = [
        model_entry for model_entry in config.model_list if model_entry.model_name != litellm_model_name
    ]
    with open(studio_consts.DEFAULT_LITELLM_CONFIG_STORAGE_LOCATION, "w") as f:
        yaml_string = yaml.dump(config.to_dict())
        f.write(yaml_string)


def edit_model_in_config(model: StudioModel):
    litellm_model_name = model.model_name
    config = load_config_file()
    model_entry = _create_model_entry(model)
    config.model_list = [
        model_entry for model_entry in config.model_list if model_entry.model_name != litellm_model_name
    ]
    config.model_list.append(model_entry)
    with open(studio_consts.DEFAULT_LITELLM_CONFIG_STORAGE_LOCATION, "w") as f:
        yaml_string = yaml.dump(config.to_dict())
        f.write(yaml_string)


# Litellm Proxy Server Operations

_litellm_subprocess = None


def restart_litellm_server():
    global _litellm_subprocess
    if _litellm_subprocess:
        _litellm_subprocess.terminate()

    def preexec_function():
        # Make the subprocess its own session leader
        os.setsid()

    _litellm_subprocess = subprocess.Popen(
        [
            "litellm",
            "--port",
            studio_consts.DEFAULT_LITELLM_SERVER_PORT,
            "--config",
            studio_consts.DEFAULT_LITELLM_CONFIG_STORAGE_LOCATION,
        ],
        preexec_fn=preexec_function,
    )


def stop_litellm_server():
    """
    Stops all LiteLLM servers by terminating related subprocesses and cleaning up configuration storage.
    """
    print("Attempting to stop all LiteLLM servers...")

    global _litellm_subprocess

    # Step 1: Terminate the specific _litellm_subprocess, if running
    try:
        if _litellm_subprocess and _litellm_subprocess.poll() is None:
            print(f"Stopping LiteLLM subprocess with PID: {_litellm_subprocess.pid}")
            os.killpg(os.getpgid(_litellm_subprocess.pid), signal.SIGTERM)
            # Wait for graceful termination
            _litellm_subprocess.wait(timeout=10)
            print("Specific LiteLLM subprocess stopped successfully.")
        else:
            print("No active _litellm_subprocess found or it has already been terminated.")
        _litellm_subprocess = None  # Clear the global subprocess reference
    except Exception as e:
        print(f"Error stopping specific LiteLLM subprocess: {e}")

    # Step 2: Identify and terminate all LiteLLM-related processes
    try:
        for proc in psutil.process_iter(["pid", "name", "cmdline"]):
            if "litellm" in (proc.info["name"] or "").lower() or any(
                "litellm" in arg.lower() for arg in (proc.info["cmdline"] or [])
            ):
                print(f"Terminating LiteLLM process: PID={proc.info['pid']} Name={proc.info['name']}")
                # Terminate process group
                os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
        print("All LiteLLM processes terminated successfully.")
    except Exception as e:
        print(f"Error terminating LiteLLM processes: {e}")

    # Step 3: Remove the LiteLLM configuration file
    try:
        config_file = studio_consts.DEFAULT_LITELLM_CONFIG_STORAGE_LOCATION
        if os.path.exists(config_file):
            os.remove(config_file)
            print(f"Removed LiteLLM configuration file: {config_file}")
        else:
            print(f"No configuration file found at: {config_file}")
    except Exception as e:
        print(f"Error removing configuration file: {e}")
