# Dockerfile for FridayGPT Discord Bot

# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make sure environment variables can be passed in
ENV DISCORD_TOKEN=your_token_here \
    TOGETHER_API_KEY=your_together_api_key_here

# Run the bot
CMD ["python", "main.py"]
