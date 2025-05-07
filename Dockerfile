# Stage 1: Builder
FROM python:3.12.10-alpine as builder

# Set up the working directory
WORKDIR /usr/src/parser

# Install dependencies required to build Python packages
RUN apk --no-cache add \
    gcc \
    jpeg-dev \
    libc-dev \
    libffi-dev \
    musl-dev \
    python3-dev \
    zlib-dev \
    && pip install --no-cache-dir poetry==1.8.5

# Copy only the poetry configuration files
COPY pyproject.toml poetry.lock ./

# Install dependencies with poetry and export to requirements.txt
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi \
    && poetry export -f requirements.txt --output requirements.txt --without-hashes

# Create wheels directory and generate wheels for all dependencies
RUN mkdir -p /usr/src/ai-api-service/wheels \
    && pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/ai-api-service/wheels -r requirements.txt

# Stage 2: Final image
FROM python:3.12.10-alpine

# Environment variables
ENV USER=Parser \
    PYTHONWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Create a non-root user and necessary directories
RUN mkdir -p /home/$USER \
    && addgroup -S $USER && adduser -S $USER -G $USER

# Set up the application home and working directories
ENV HOME=/home/$USER
ENV APP_HOME=/home/$USER/parser
RUN mkdir $APP_HOME
WORKDIR $APP_HOME

# Copy dependencies and install them
COPY --from=builder /usr/src/parser/wheels /wheels
COPY --from=builder /usr/src/parser/requirements.txt .
RUN pip install --no-cache-dir /wheels/*

# Copy the application code
COPY . $APP_HOME

# Set permissions and user for security
RUN chown -R $USER:$USER $APP_HOME
USER $USER

# Specify the run command for the container
RUN chmod +x $APP_HOME/fastapi-entrypoint.sh
