#!/usr/bin/env python3
"""
North India Plant Guide - Complete Ingestion Pipeline
Ingests 75 plants into Qdrant (text + image embeddings)

USAGE: python ingest_plants.py
"""

import json
import re
import hashlib
from pathlib import Path
from typing import Optional

import requests
from PIL import Image
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import SparseVector
from sentence_transformers import SentenceTransformer


# =============================================================================
# CONFIGURATION
# =============================================================================
QDRANT_URL = "https://27aff9e6-8dae-4699-8803-9ee4fd06af81.eu-central-1-0.aws.cloud.qdrant.io"
QDRANT_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOlt7ImNvbGxlY3Rpb24iOiJwbGFudHMiLCJhY2Nlc3MiOiJydyJ9LHsiY29sbGVjdGlvbiI6InBsYW50LWltYWdlcyIsImFjY2VzcyI6InJ3In1dLCJleHAiOjE3NzcxNTcwNzZ9.4LibSPRSJmJ9FQcGTB6OnYfR7sYuNlGJE5qm2RHQfkk"

DATA_FILE = "/home/.z/chat-uploads/north_india_plant_care_guide_v1.1-2d77d796f9ae.json"
IMAGES_DIR = Path("/home/workspace/north_india_plant_guide/images")

PLANTS_COLLECTION = "plants"
IMAGES_COLLECTION = "plant-images"
DENSE_VECTOR_NAME = "plant-vector-dense"
SPARSE_VECTOR_NAME = "plant-vector-sparse"
IMAGE_VECTOR_NAME = "image-vector"
DENSE_DIM = 1536
IMAGE_DIM = 512
BATCH_SIZE = 10


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def slugify(text: str) -> str:
    """Convert plant name to URL-safe slug."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text


def extract_folder_num(folder_name: str) -> int:
    """Extract folder number from name like '01. Chinese Evergreen'."""
    match = re.match(r'^(\d+)', folder_name)
    return int(match.group(1)) if match else 0


def folder_to_plant_name(folder_name: str) -> str:
    """Convert folder name to plant name (remove numbering)."""
    # Remove leading number and period: "01. Chinese Evergreen _Aglaonema_" -> "Chinese Evergreen (Aglaonema)"
    name = re.sub(r'^\d+\.\s*', '', folder_name)
    name = name.replace('_', ' ').strip()
    # Convert "Plant Name (Alt)" format
    return name


def match_folder_to_plant(folder_name: str, plants: list[dict]) -> Optional[dict]:
    """Match a folder to a plant in the JSON data."""
    folder_num = extract_folder_num(folder_name)
    if folder_num == 0:
        return None
    
    # Plants are 1-indexed in order
    if folder_num <= len(plants):
        return plants[folder_num - 1]
    return None


def load_data() -> list[dict]:
    """Load plant data from JSON file."""
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['plants']


def build_text_blob(plant: dict) -> str:
    """Build combined text blob for embedding."""
    parts = []
    parts.append(f"Plant: {plant['plant_name']}")
    
    if plant.get('alternate_names'):
        parts.append(f"Also known as: {', '.join(plant['alternate_names'])}")
    
    parts.append(f"Category: {plant.get('category', 'Unknown')}")
    
    if plant.get('description'):
        parts.append(f"Description: {plant['description']}")
    
    if plant.get('care'):
        care = plant['care']
        parts.append("Care Instructions:")
        for key, value in care.items():
            if value:
                label = key.replace('_', ' ').title()
                parts.append(f"- {label}: {value}")
    
    if plant.get('common_problems'):
        parts.append("Common Problems and Solutions:")
        for problem in plant['common_problems']:
            symptom = problem.get('symptom', '')
            causes = ', '.join(problem.get('possible_causes', []))
            fix = problem.get('fix', '')
            prevention = problem.get('prevention', '')
            parts.append(f"- Problem: {symptom}")
            if causes:
                parts.append(f"  Causes: {causes}")
            if fix:
                parts.append(f"  Fix: {fix}")
            if prevention:
                parts.append(f"  Prevention: {prevention}")
    
    return '\n'.join(parts)


# =============================================================================
# EMBEDDING GENERATOR
# =============================================================================

class EmbeddingGenerator:
    def __init__(self):
        print("Loading embedding models...")
        self.dense_model = SentenceTransformer('sentence-transformers/all-MiniLM-L12-v2')
        self.clip_model = SentenceTransformer('clip-ViT-B-32')
        print("Models loaded successfully.")
    
    def get_dense_embedding(self, text: str) -> list[float]:
        """Generate dense embedding (384-dim mapped to 1536)."""
        embedding = self.dense_model.encode(text, normalize_embeddings=True)
        full_embedding = (embedding.tolist() * (1536 // 384 + 1))[:1536]
        return full_embedding
    
    def get_sparse_embedding(self, text: str) -> dict:
        """Generate sparse BM25-style embedding."""
        tokens = re.findall(r'\b\w+\b', text.lower())
        freq = {}
        for token in tokens:
            if len(token) > 2:
                freq[token] = freq.get(token, 0) + 1
        
        if not freq:
            return {"indices": [], "values": []}
        
        max_freq = max(freq.values())
        sorted_terms = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:50]
        
        indices, values = [], []
        for term, count in sorted_terms:
            tf = count / max_freq
            index = int(hashlib.md5(term.encode()).hexdigest()[:8], 16) % 100000
            indices.append(index)
            values.append(tf)
        
        return {"indices": indices, "values": values}
    
    def get_image_embedding(self, image_path: str) -> Optional[list[float]]:
        """Generate CLIP 512-dim image embedding from local file."""
        try:
            image = Image.open(image_path).convert('RGB')
            embedding = self.clip_model.encode(image, normalize_embeddings=True)
            return embedding.tolist()
        except Exception as e:
            print(f"  Failed to embed {image_path}: {e}")
            return None



# =============================================================================
# HTTP SEARCH (using requests directly for named vector support)
# =============================================================================

def http_search(collection: str, vector_name: str, vector: list[float], limit: int = 5) -> list:
    """Search using HTTP API with named vectors."""
    headers = {"api-key": QDRANT_API_KEY, "Content-Type": "application/json"}
    body = {
        "vector": {"name": vector_name, "vector": vector},
        "limit": limit,
        "with_payload": True
    }
    resp = requests.post(
        f"{QDRANT_URL}/collections/{collection}/points/search",
        headers=headers,
        json=body
    )
    if resp.status_code == 200:
        return resp.json().get("result", [])
    else:
        raise Exception(f"Search failed: {resp.text}")

# =============================================================================
# INGESTION FUNCTIONS
# =============================================================================

def verify_collections(client: QdrantClient):
    """Verify Qdrant collections exist."""
    for coll_name in [PLANTS_COLLECTION, IMAGES_COLLECTION]:
        resp = requests.get(
            f"{QDRANT_URL}/collections/{coll_name}",
            headers={'api-key': QDRANT_API_KEY}
        )
        if resp.status_code == 200:
            print(f"✓ Collection '{coll_name}' exists")
        else:
            raise Exception(f"Collection '{coll_name}' not found: {resp.text}")


def ingest_text_data(client: QdrantClient, embedder: EmbeddingGenerator, plants: list[dict]):
    """Ingest plant text data into Qdrant."""
    print(f"\nIngesting {len(plants)} plants into '{PLANTS_COLLECTION}'...")
    
    points = []
    for i, plant in enumerate(plants):
        plant_id = hash(slugify(plant["plant_name"])) % (10**12)  # Numeric ID
        text_blob = build_text_blob(plant)
        
        dense_vec = embedder.get_dense_embedding(text_blob)
        sparse_vec = embedder.get_sparse_embedding(text_blob)
        
        payload = {
            "plant_name": plant['plant_name'],
            "category": plant.get('category', ''),
            "slug": slugify(plant['plant_name']),
            "text_blob": text_blob
        }
        
        point = models.PointStruct(
            id=plant_id,
            vector={
                DENSE_VECTOR_NAME: dense_vec,
                SPARSE_VECTOR_NAME: SparseVector(
                    indices=sparse_vec["indices"],
                    values=sparse_vec["values"]
                )
            },
            payload=payload
        )
        points.append(point)
        
        if len(points) >= BATCH_SIZE or i == len(plants) - 1:
            client.upsert(
                collection_name=PLANTS_COLLECTION,
                points=points
            )
            print(f"  Uploaded batch of {len(points)} plants ({i + 1}/{len(plants)})")
            points = []
    
    print(f"✓ Text ingestion complete")


def ingest_image_data(client: QdrantClient, embedder: EmbeddingGenerator, plants: list[dict]):
    """Ingest plant reference images into Qdrant."""
    print(f"\nIngesting images into '{IMAGES_COLLECTION}'...")
    
    folders = sorted(IMAGES_DIR.iterdir(), key=lambda x: extract_folder_num(x.name))
    
    points = []
    total_images = 0
    
    for folder in folders:
        if not folder.is_dir():
            continue
        
        plant = match_folder_to_plant(folder.name, plants)
        if not plant:
            print(f"  Skipping unmatched folder: {folder.name}")
            continue
        
        plant_id_base = slugify(plant['plant_name'])
        image_files = sorted(folder.glob("*.jpg")) + sorted(folder.glob("*.png"))
        
        for img_idx, img_path in enumerate(image_files):
            embedding = embedder.get_image_embedding(str(img_path))
            if embedding is None:
                continue
            
            point_id = hash(f"{plant_id_base}:img{img_idx + 1}") % (10**12)
            point = models.PointStruct(
                id=point_id,
                vector={IMAGE_VECTOR_NAME: embedding},
                payload={
                    "plant_name": plant['plant_name'],
                    "plant_slug": plant_id_base,
                    "image_path": str(img_path),
                    "image_index": img_idx + 1
                }
            )
            points.append(point)
            total_images += 1
            
            if len(points) >= BATCH_SIZE:
                client.upsert(
                    collection_name=IMAGES_COLLECTION,
                    points=points
                )
                print(f"  Uploaded batch of {len(points)} images (total: {total_images})")
                points = []
    
    if points:
        client.upsert(collection_name=IMAGES_COLLECTION, points=points)
        print(f"  Uploaded final batch of {len(points)} images")
    
    print(f"✓ Image ingestion complete: {total_images} images from {len(folders)} plants")


# =============================================================================
# SEARCH TESTS
# =============================================================================

def test_text_search(client: QdrantClient, embedder: EmbeddingGenerator):
    """Test text search functionality."""
    print(f"\n{'='*60}")
    print("TESTING TEXT SEARCH")
    print('='*60)
    
    query = "yellow leaves on indoor plants"
    print(f"Query: '{query}'")
    
    dense_vec = embedder.get_dense_embedding(query)
    
    results = http_search(PLANTS_COLLECTION, DENSE_VECTOR_NAME, dense_vec, limit=5)
    
    print("\nTop 5 Text Search Results:")
    for i, result in enumerate(results, 1):
        print(f"  {i}. {result['payload'].get('plant_name', 'Unknown')} (score: {result['score']:.4f})")


def test_image_search(client: QdrantClient, embedder: EmbeddingGenerator, plants: list[dict]):
    """Test image search functionality."""
    print(f"\n{'='*60}")
    print("TESTING IMAGE SEARCH")
    print('='*60)
    
    # Find first plant with images
    test_folder = None
    for folder in sorted(IMAGES_DIR.iterdir(), key=lambda x: extract_folder_num(x.name)):
        if folder.is_dir():
            plant = match_folder_to_plant(folder.name, plants)
            if plant and list(folder.glob("*.jpg")):
                test_folder = folder
                test_plant = plant
                break
    
    if not test_folder:
        print("No test images found")
        return
    
    test_images = sorted(test_folder.glob("*.jpg"))
    if not test_images:
        print(f"No images in {test_folder}")
        return
    
    test_image = str(test_images[0])
    print(f"Using test image: {test_image}")
    
    embedding = embedder.get_image_embedding(test_image)
    if embedding is None:
        print("Failed to embed test image")
        return
    
    results = http_search(IMAGES_COLLECTION, IMAGE_VECTOR_NAME, embedding, limit=5)
    
    print("\nTop 5 Image Search Results:")
    for i, result in enumerate(results, 1):
        payload = result['payload']
        print(f"  {i}. {payload.get('plant_name', 'Unknown')} (score: {result['score']:.4f})")


# =============================================================================
# MAIN
# =============================================================================

def main():
    print("="*60)
    print("NORTH INDIA PLANT GUIDE - INGESTION PIPELINE")
    print("="*60)
    
    print(f"\nConnecting to Qdrant at {QDRANT_URL}...")
    client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
    print("Connected successfully.")
    
    print(f"\nLoading plant data from {DATA_FILE}...")
    plants = load_data()
    print(f"Loaded {len(plants)} plants.")
    
    embedder = EmbeddingGenerator()
    verify_collections(client)
    
    ingest_text_data(client, embedder, plants)
    ingest_image_data(client, embedder, plants)
    
    test_text_search(client, embedder)
    test_image_search(client, embedder, plants)
    
    print("\n" + "="*60)
    print("Text ingestion, image ingestion, and search tests completed successfully.")
    print("="*60)


if __name__ == "__main__":
    main()
