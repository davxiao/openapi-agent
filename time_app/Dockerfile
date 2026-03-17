FROM python:3.14-slim

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY ./main.py /app/main.py

# Expose the port the app runs on
EXPOSE 8001

# Set the entrypoint command
CMD ["fastapi", "run", "/app/main.py", "--port", "8001"]
