from typing import Optional
import requests
import json
import os
from pydantic.dataclasses import dataclass
from pydantic import Field
import config
import time
import requests

@dataclass(frozen=True)
class API():
    api_base: str = Field(
      default_factory=lambda: config.get_current_llm(config.RUN)["api_base"],
      frozen=True
    )
    api_key_env_var: str = Field(
      default_factory=lambda: config.get_current_llm(config.RUN)["api_key_env_var"],
      frozen=True
    )
    model: str = Field(
        default_factory=lambda: config.get_current_llm(config.RUN)["model"],
      frozen=True
    )
      
    def equals(self, other: "API") -> bool:
        return self.api_base == other.api_base and self.api_key_env_var == other.api_key_env_var

    def completion(self,
                   messages: list[dict],
                   stream: Optional[bool] = None,
                   max_tokens: Optional[int] = None,
                   temperature: Optional[float] = None,
                   presence_penalty: Optional[float] = None,
                   frequency_penalty: Optional[float] = None,
                   **kwargs: dict) -> requests.Response:
                
        for message in messages:
            if message["content"] == "":
                raise ValueError("Message content cannot be empty")

        config_params = config.get_config()[config.RUN]["api_parameters"]
        params = {
            "stream": stream,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "presence_penalty": presence_penalty,
            "frequency_penalty": frequency_penalty,
            **kwargs
        }

        params = {k: v if v is not None else config_params[k] for k, v in params.items()}

        for k, v in config_params.items():
            if k not in params:
                params[k] = v

        request_body = {
            "model": self.model,
            "messages": messages,
            **params
        }
        print("REQUEST BODY:")
        print(json.dumps(request_body, indent=2))
        try:
            response = requests.post(
                url=self.api_base,
                headers={
                  "Authorization": f"Bearer {os.environ[self.api_key_env_var]}",
                  # "HTTP-Referer": "<YOUR_SITE_URL>",  # Optional. Site URL for rankings on openrouter.ai.
                  # "X-Title": "<YOUR_SITE_NAME>",  # Optional. Site title for rankings on openrouter.ai.
                },
                data=json.dumps(request_body)
              )

            # response.raise_for_status()
            return response
        except Exception as e:
            print(f"Error: {e}")
            return None

    def safe_completion(self, messages, **kwargs):
        for attempt in range(5):
            try:
                return self.completion(messages, **kwargs)
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:
                    wait = 2 ** attempt
                    print(f"Rate limited. Retrying in {wait} seconds...")
                    time.sleep(wait)
                else:
                    raise
        raise Exception("Too many retries due to rate limiting.")