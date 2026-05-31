# Use an official lightweight Python image
FROM python:3.10-slim

# Set the working directory inside the cloud container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your bot's files into the container
COPY . .

# Expose the dynamic port for the keep_alive server
EXPOSE 8080

# Run the bot script
CMD ["python", "bot.py"]