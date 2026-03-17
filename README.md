

# Setting up and running

## Start the Openapi Time server (local)

cd time_app/

uv run uvicorn main:app --host 0.0.0.0 --port 8081

For testing, in a seperate shell, run `curl -X GET "http://localhost:8081/current_time?city=nyc" -H "Authorization: Bearer <replace-with-oauth2-access-token>"` to verify the server works properly.

In addition, try `curl -X GET "http://localhost:8081/current_time?city=nyc"`without  authorization header and the server should return `"Not authenticated"` as expected.

## Start the Root agent for testing (local)

cd adk_agents/

cp sample.env .env

### ⚠️ Make sure to update the relevant Okta values in adk_agent/.env file

### ⚠️ Make sure to update the adk_agent/agent/openapi.yaml and ensure the'servers' url is pointing to the service URL you are using (e.g. http://localhost:8081)

### Run the agent
uv run adk web . --host localhost --port=8085

In the input box, enter "what can you do" and it should trigger Okta OAuth flow. If encounter Okta error, please check the Okta configuration and ensure `http://localhost:8085/dev-ui/` is added in Okta as redirect URI.

## Optional - Deploy the Openapi Time server to Cloud Run

### Before you proceed, please make sure you've completed the local testing successfully.

./upload_secrets.sh

./deploy.sh

## Optional Start the Root agent for testing (remote)

cd adk_agents/

### ⚠️ Make sure to update the adk_agent/agent/openapi.yaml and ensure the'servers' url is pointing to the Cloud Run service URL (e.g. https://remote-time-openapi-112233831721.us-central1.run.app)

### Run the agent
uv run adk web . --host localhost --port=8085
