# This code was developed with the assistance of ChatGPT-4o (OpenAI)

FROM python:3.10-slim

# Installer les outils de compilation
RUN apt update && apt install -y \
    build-essential \
    cython3 \
    git \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Installer les modules Python nécessaires
RUN pip install --no-cache-dir -U pip cython numpy joblib==0.9.4 h5py

# Créer et copier l'app
WORKDIR /app
COPY . /app

# Compiler le module Cython
RUN python setup.py build_ext -i

# Entrée par défaut : shell
CMD ["bash"]

