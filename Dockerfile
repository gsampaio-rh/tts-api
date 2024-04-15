FROM registry.access.redhat.com/ubi8/python-39:latest

# Create a directory for your app files
USER root

ARG WORK_DIR=/deployment

WORKDIR $WORK_DIR

# Copy application files
COPY app.py $WORK_DIR
COPY requirements.txt $WORK_DIR

RUN mkdir -p $WORK_DIR/audio $WORK_DIR/uploads

RUN chown -R 1001 $WORK_DIR && \
    chown -R 1001 $WORK_DIR && \
    chgrp -R 0 $WORK_DIR && \
    chmod -R g+rwX $WORK_DIR


# Install Python dependencies
RUN pip3 install -r requirements.txt

# Expose the port Flask is running on
EXPOSE 5000

# Ensure the container runs as a non-root user
USER 1001

CMD ["python3", "-m", "flask", "run", "--host=0.0.0.0"]
