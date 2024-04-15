FROM registry.access.redhat.com/ubi8/python-39:latest

WORKDIR /deployment

# Copy application files
COPY app.py /deployment
COPY requirements.txt /deployment

# Install Python dependencies
RUN pip3 install -r requirements.txt

# Expose the port Flask is running on
EXPOSE 5000

# Ensure the container runs as a non-root user
USER 1001

CMD ["python3", "-m", "flask", "run", "--host=0.0.0.0"]
