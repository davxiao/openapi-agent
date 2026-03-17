# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import os

from google.adk.tools.openapi_tool.auth.auth_helpers import openid_url_to_scheme_credential
from google.adk.tools.openapi_tool.openapi_spec_parser.openapi_toolset import OpenAPIToolset
from google.adk.agents.llm_agent import Agent
from google.adk.auth.auth_schemes import OpenIdConnectWithConfig
from google.adk.auth.auth_credential import AuthCredential, AuthCredentialTypes, OAuth2Auth
from fastapi.openapi.models import OAuth2,OAuthFlows,OAuthFlowAuthorizationCode
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()


credential_dict = {
    "client_id": os.environ.get('OAUTH_CLIENT_ID'),
    "client_secret": os.environ.get('OAUTH_CLIENT_SECRET'),
}

auth_scheme, auth_credential = openid_url_to_scheme_credential(
    openid_url=os.environ.get('OIDC_CONFIG_URL'),
    credential_dict=credential_dict,
    scopes=['agent:time','openid','offline_access'],
)

# Open API spec
file_path = "./agent/openapi.yaml"
file_content = None

try:
  with open(file_path, "r") as file:
    file_content = file.read()
except FileNotFoundError:
  # so that the execution does not continue when the file is not found.
  raise FileNotFoundError(f"Error: The API Spec '{file_path}' was not found.")

# Example with a YAML string
openapi_spec_yaml = file_content
time_toolset = OpenAPIToolset(
  spec_str=openapi_spec_yaml,
  spec_str_type="yaml",
  auth_scheme=auth_scheme,
  auth_credential=auth_credential,
)


root_agent = Agent(
  model='gemini-3-flash-preview',
  name='openapi_time_agent',
  description=
  "An agent that can get the current time in various cities using the get_time_agent.",
  instruction=
  ("You are a helpful assistant that can retrieve the current time in various cities. "
  "To get the current time in a city, use the tools 'time_toolset'."
  ),
  tools=[time_toolset],  # Pass the toolset
)
