FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080 \
    HF_HOME=/root/.cache/huggingface \
    TRANSFORMERS_CACHE=/root/.cache/huggingface/transformers \
    TORCH_HOME=/root/.cache/huggingface/torch

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential gcc curl \
    && rm -rf /var/lib/apt/lists/*

# Pre-download CLIP model during build to avoid runtime download and rate limits
RUN pip install --no-cache-dir torch transformers huggingface_hub \
    && python -c "from transformers import CLIPModel, CLIPProcessor; CLIPProcessor.from_pretrained('openai/clip-vit-base-patch32'); CLIPModel.from_pretrained('openai/clip-vit-base-patch32')" \
    && rm -rf /root/.cache/huggingface/hub/*/saves  # Remove checkpoint savers to reduce size

COPY app/requirements.txt /app/app/requirements.txt
RUN pip install --no-cache-dir -r /app/app/requirements.txt

COPY app /app/app

EXPOSE 8080

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
