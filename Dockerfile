FROM registry.access.redhat.com/ubi8/python-39:latest

ARG WORK_DIR=/tts

WORKDIR $WORK_DIR

# RUN useradd -ms /bin/bash app

# Copy application files
COPY app.py $WORK_DIR
COPY requirements.txt $WORK_DIR

RUN mkdir -p $WORK_DIR/audio $WORK_DIR/uploads

RUN chgrp -R 0 $WORK_DIR && \
    chmod -R g+rwX $WORK_DIR

# Install Python dependencies
RUN pip3 install -r requirements.txt

# Expose the port Flask is running on
EXPOSE 5000

# Ensure the container runs as a non-root user
USER 1001
RUN chown -R 1001:0 $WORK_DIR/audio $WORK_DIR/uploads

CMD ["python3", "-m", "flask", "run", "--host=0.0.0.0"]
