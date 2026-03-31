
# PLANT CARE API REFERENCE

## JSON Structure

All plants follow this exact structure:

```json
{
  "plant_name": "string",
  "alternate_names": ["string"],
  "category": "string",
  "description": "string",
  "care": {
    "watering_frequency": "string",
    "light_requirements": "string",
    "soil_type": "string",
    "temperature_range": "string",
    "fertilizer": "string",
    "humidity": "string"
  },
  "common_problems": [
    {
      "symptom": "string",
      "possible_causes": ["string"],
      "fix": "string",
      "prevention": "string"
    }
  ],
  "reference_images": [
    {
      "url": "string",
      "description": "string"
    }
  ]
}
```

## Categories

- Indoor Climber
- Indoor Foliage
- Indoor Succulent
- Indoor Tropical
- Indoor Decorative
- Balcony Flowering
- Balcony Herb
- Balcony Fruiting
- Succulent

## Available Plants (28 total)

1. Money Plant (Pothos)
2. Snake Plant (Sansevieria)
3. Aloe Vera
4. Jade Plant (Crassula Ovata)
5. ZZ Plant (Zamioculcas Zamiifolia)
6. Spider Plant (Chlorophytum Comosum)
7. Peace Lily (Spathiphyllum)
8. Areca Palm (Dypsis Lutescens)
9. Rubber Plant (Ficus Elastica)
10. Syngonium Podophyllum
11. Philodendron Heartleaf
12. Bougainvillea
13. Hibiscus (Hibiscus Rosa-Sinensis)
14. Jasmine Mogra
15. Tulsi (Holy Basil)
16. Marigold
17. Curry Leaf Plant
18. Mint (Pudina)
19. Lemon Plant (Citrus Limon)
20. Rose
21. Fern (Nephrolepis Exaltata)
22. Anthurium
23. Orchid (Phalaenopsis)
24. Ficus Bonsai
25. Echeveria
26. Haworthia
27. Sedum
28. Crassula (Jade Plant)

## Data Points Per Plant

- Plant Name: 1
- Alternate Names: 3-4 (including Hindi)
- Category: 1
- Description: 1
- Care Instructions: 6 aspects
- Common Problems: 5 entries
- Images: 3 URLs
- **Total: ~15-20 data points per plant**

## Search Capabilities

- Search by plant_name
- Search by alternate_names (including Hindi)
- Filter by category
- Filter by care requirements
- Search within problems (symptom matching)

## Image URLs

All images are royalty-free from:
- Unsplash
- Pexels
- Pixabay

No attribution required. Free for commercial use.
