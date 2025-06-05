import json
import os
import time
import yaml

from openai import AzureOpenAI
from openai import OpenAI
from termcolor import colored
import openai
from azure.identity import DefaultAzureCredential, get_bearer_token_provider



class LLM:
    def __init__(self, model_name, config_file="llm_config.yaml", verbose=False):
        self.model_name = model_name
        self.verbose = verbose
        self.count = 0
        self.error_count = 0
        self.context_length = 4000

        # Load the configuration from the YAML file
        with open(config_file, "r") as f:
            config = yaml.safe_load(f)

        if os.path.exists("api_key.json"):
            self.key_dict = json.load(open("api_key.json"))
        else:
            self.key_dict = {}

        if self.model_name in config:
            model_config = config[self.model_name]

            if model_config["bearer_token"]:
                token_provider = get_bearer_token_provider(
                    DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
                )
                
                self.client = AzureOpenAI(
                    azure_endpoint = model_config["endpoint"],
                    azure_ad_token_provider=token_provider,
                    api_version= model_config["api_version"]
                    )
            else:
                print("Please include an API key in api_key.json or use bearer authentication in llm_config.yaml")

        elif "llama" in self.model_name:
            print("Using Llama")
            # llama-2-70b-chat-19
            self.client = OpenAI(api_key=self.key_dict["llama31"], base_url="https://gcr-llama31-70b-instruct.westus3.inference.ml.azure.com")

        elif "mistral" in self.model_name:
            print("Using Mistral")
            # mistralai-mixtral-8x7b-instru-7
            self.client = OpenAI(api_key=self.key_dict["mistral"], base_url="https://mistralai-8x7b-instruct-v01.westus3.inference.ml.azure.com/v1")
        elif "phi" in self.model_name:
            print("Using Phi")
            # phi-3-medium-128k-instruct-1
            self.client = OpenAI(api_key=self.key_dict["phi"], base_url="")
        else:
            print("Using GPT-3.5")
            self.client = AzureOpenAI(api_key=self.key_dict["gpt-35"], azure_endpoint="https://gcraoai7sw1.openai.azure.com", api_version="2024-02-15-preview")


    def __call__(self, message, *args, **kwargs):
        # Trim message content to context length
        for i, m in enumerate(message):
            message[i]["content"] = message[i]["content"][:self.context_length]

        if self.verbose:
            # Message is a list of dictionaries with role and content keys.
            # Color each role differently.
            print(message)
            for m in message:
                if m["role"] == "user":
                    print(colored(f"{m['content']}\n", "cyan"))
                elif m["role"] == "assistant":
                    print(colored(f"{m['content']}\n", "green"))
                elif m["role"] == "system":
                    print(colored(f"{m['content']}\n", "yellow"))
                else:
                    print(colored(f"Unknown role: {m['content']}\n", "red"))

        self.count += 1
        while True:
            try:
                if "llama" in self.model_name or "mistral" in self.model_name:
                    message = self.merge_messages(message)
                    return_response = self.client.chat.completions.create(model = self.model_name, messages = message, max_tokens=10000).choices[0].message.content
                else:
                    return_response = self.client.chat.completions.create(model = self.model_name, messages = message).choices[0].message.content
                break
            except openai.BadRequestError as exception:
                print(colored(f"BadRequestError: {exception}", "red"))
                raise exception
            except Exception as e:
                print(colored(f"Error: {e}", "red"))
                self.error_count += 1
                time.sleep(10 * self.error_count)

                if self.error_count > 1000:
                    raise Exception("Too many errors, exiting)")

        if self.count % 100 == 0:
            time.sleep(10)

        if self.verbose:
            print(colored(return_response, "green"))

        return return_response

    def merge_messages(self, messages):
        messages_out = []

        if "llama" in self.model_name:
            # merge first 3 system messages
            contents = ""
            for message in messages[:3]:
                contents += message["content"] + "\n\n"

            messages_out.append({"role": "system", "content": contents.strip()})
            messages_out.extend(messages[3:])
        elif "mistral" in self.model_name:
            # merge first 4 messages (3 system + 1 user) into one
            contents = ""
            for message in messages[:4]:
                contents += message["content"] + "\n\n"

            messages_out.append({"role": "user", "content": contents.strip()})
            messages_out.extend(messages[4:])

        return messages_out
