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


### Important Instructions
### for testing, start the server using the following command:
### uv run uvicorn main:app --host 0.0.0.0 --port 8081
### then use the following to verify the server works properly:
### curl -X GET "http://0.0.0.0:8081/current_time?city=nyc" -H "Authorization: Bearer abcdefg123456"
###



from functools import wraps
import os

from dotenv import load_dotenv
import jwt

from fastapi import FastAPI, Response, status, Header, Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import FileResponse
import uvicorn
from datetime import datetime
import pytz
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
import requests


# Load environment variables from .env file
load_dotenv()


# Initialize components globally for reuse (caching)
geolocator = Nominatim(user_agent="city_time_app")
tf = TimezoneFinder()


app = FastAPI()
security = HTTPBearer()
# Instantiate the core logic class




def get_current_time(city_name: str) -> Dict[str, Any]:
  """
  Retrieves the current time for any city globally.
  Uses geocoding to find coordinates and timezonefinder for IANA lookup.
  """
  try:
    # 1. Geocode city name to coordinates
    location = geolocator.geocode(city_name, language='en', timeout=10)

    if not location:
      logger.warning(f"Could not resolve location for city: {city_name}")
      return {"status": "error", "message": "Location not found"}

    # 2. Find the timezone name from coordinates
    timezone_str = tf.timezone_at(lng=location.longitude, lat=location.latitude)

    if not timezone_str:
      return {
        "status": "error",
        "message": "Timezone could not be determined"
      }

    # 3. Calculate time using pytz
    timezone = pytz.timezone(timezone_str)
    now = datetime.now(timezone)

    return {
      "status": "success",
      "data": {
        "input_city": city_name,
        "resolved_address": location.address,
        "timezone": timezone_str,
        "time_24h": now.strftime("%H:%M"),
        "time_12h": now.strftime("%I:%M %p"),
        "date": now.strftime("%Y-%m-%d"),
        "utc_offset": now.strftime("%z")
      }
    }
  except Exception as e:
    logger.error(f"Error fetching time for {city}: {str(e)}")
    return {"status": "error", "message": "Internal server error"}

def introspect_token(token, introspection_url, rs_client_id, rs_client_secret):
  """
  Introspects an OAuth 2.0 token using the provided credentials.
  """
  
  # Data to be sent in the POST body
  data = {
    'token': token,
    'token_type_hint': 'access_token'
  }
  
  try:
    # Perform the POST request with Basic Authentication
    response = requests.post(
        introspection_url,
        data=data,
        auth=(rs_client_id, rs_client_secret),
        timeout=10
    )
    
    # Raise an exception for HTTP error statuses (4xx or 5xx)
    response.raise_for_status()
    
    # Parse and return the JSON response
    return response.json()
      
  except requests.exceptions.RequestException as e:
    print(f"Error during token introspection: {e}")
    return None

### treat this function as pseduo code, do not modify this function
def is_token_valid(token: str):
  """
  Validates a JWT token
  """
  if not token:
    return False, "Token is empty."

  introspection_url=f"https://{os.getenv("OKTA_DOMAIN")}/oauth2/{os.getenv("OKTA_AUTH_SERVER_ID")}/v1/introspect"
  response_json=introspect_token(token, introspection_url, os.getenv("OKTA_RS_CLIENT_ID"), os.getenv("OKTA_RS_CLIENT_SECRET"))
  
  if response_json is None or response_json.get("active") is False:
    print("Invalid Token", token)
    return False, "Token is invalid."
  
  print(response_json)

  return True, "Token is valid."


async def verify_token(auth: HTTPAuthorizationCredentials = Security(security)):
  """
  Dependency to verify the JWT token from the Authorization header.
  """
  token = auth.credentials
  is_valid, message = is_token_valid(token)

  if not is_valid:
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=message,
    )
  return token

@app.get("/")
async def root():
  return {"message": "This is an openapi server that requires Oauth authentication."}


""" 
@app.get("/openapi.yaml")
async def get_openapi_yaml_file(response: Response = None):
  # Path to your YAML file
  file_path = "./openapi.yaml"

  # Check if file exists
  if not os.path.exists(file_path):
    response.status_code = status.HTTP_404_NOT_FOUND
    return {"error": "File not found"}

  # Serve the file with correct media_type
  return FileResponse(
    path=file_path, 
    media_type="application/yaml"
  ) 
"""

@app.get("/current_time")
async def get_details(city: str | None = None, response: Response = None, token: str = Depends(verify_token)):
  if not city:
    response.status_code = status.HTTP_400_BAD_REQUEST
    return (
        {
            "error": True,
            "data": None,
            "message": "Please provide a valid city name.",
        }
    )

  details = get_current_time(city_name=city)

  if details:
    return (
        {
            "error": False,
            "data": details,
            "message": "City current time retrieved successfully.",
        }
    )
  else:
    response.status_code = status.HTTP_404_NOT_FOUND
    return {"error": True, "data": None, "message": 'City current time not found'}
