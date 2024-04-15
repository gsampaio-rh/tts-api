FROM registry.access.redhat.com/ubi8/python-39:latest

ARG WORK_DIR=/app/tts

WORKDIR $WORK_DIR

# Copy application files
COPY app.py $WORK_DIR
COPY requirements.txt $WORK_DIR

# Install Python dependencies
RUN pip3 install -r requirements.txt

# Create directories and set appropriate permissions
RUN chown -R 1001:0 $WORK_DIR
# RUN mkdir -p /deployment/audio /deployment/uploads && \
#     chmod 777 /deployment/audio /deployment/uploads

# Expose the port Flask is running on
EXPOSE 5000

# Ensure the container runs as a non-root user
USER 1001

CMD ["python3", "-m", "flask", "run", "--host=0.0.0.0"]
