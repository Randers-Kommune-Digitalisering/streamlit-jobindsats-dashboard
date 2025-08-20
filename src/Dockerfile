FROM python:3.10-slim

# Set dir and user
ENV GROUP_NAME=src
ENV HOME=/src
ENV GROUP_ID=11000
ENV USER_ID=11001
ENV PORT=8080

# Add user
RUN if ! getent group src; then addgroup --gid 11000 src; fi && \
    adduser $USER_ID -u USER_ID -D -G src -h /src

# Install packages
RUN apt-get update && apt-get install --yes --no-install-recommends build-essential libmariadb-dev libpq-dev

# Copy files and set working dir
COPY . $HOME
WORKDIR $HOME

# Set permissions
RUN chown -R $USER_ID:$GROUP_ID /src && chmod -R 775 /src

# Install python packages
RUN pip install --upgrade pip setuptools wheel
RUN pip install -r requirements.txt

# Open port
EXPOSE $PORT

# Set user
USER $USER_ID

ENTRYPOINT ["streamlit", "run", "main.py", "--server.port", "8080"]