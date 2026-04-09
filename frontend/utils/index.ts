import { ImageSourcePropType } from 'react-native';
import { API_URL } from '../api/client';

export type PlantImageLike = {
  image_url?: string;
  reference_images?: Array<{
    url?: string;
    image_url?: string;
    path?: string;
  }>;
  slug?: string;
  plant_name?: string;
};

const PLANT_IMAGES: Record<string, ImageSourcePropType> = {
  monstera: require('../assets/images/monstera.jpg'),
  ficus: require('../assets/images/ficus.jpg'),
  calathea: require('../assets/images/calathea.jpg'),
  aloe: require('../assets/images/aloe.jpg'),
  avatar: require('../assets/images/avatar.jpg'),
};

const PLANT_IMAGE_ALIASES: Record<string, keyof typeof PLANT_IMAGES> = {
  'monstera-deliciosa': 'monstera',
  'monstera': 'monstera',
  'rubber-plant': 'ficus',
  'ficus-elastica': 'ficus',
  'ficus': 'ficus',
  'pinstripe': 'calathea',
  'calathea-ornata': 'calathea',
  'calathea': 'calathea',
  'aloe-vera': 'aloe',
  'aloe-vera-plant': 'aloe',
  'aloe': 'aloe',
  'parlour-palm': 'ficus',
  'bamboo-palm': 'calathea',
  'boston-fern-variant': 'aloe',
  'kentia-palm': 'ficus',
  'kalanchoe-indoor': 'aloe',
  'kalanchoe-blossfeldiana': 'aloe',
  'adenium-desert-rose': 'aloe',
  'graptopetalum': 'aloe',
  'ponytail-palm': 'ficus',
};

export function getPlantImage(name: string): ImageSourcePropType {
  const key = name.toLowerCase().replace(/\.[^.]+$/, '');
  const resolvedKey = PLANT_IMAGE_ALIASES[key] || key;
  return PLANT_IMAGES[resolvedKey] ?? PLANT_IMAGES.monstera;
}

export function getBestPlantImage(plant?: PlantImageLike): ImageSourcePropType {
  // Try local assets first using slug/name mapping
  if (plant?.slug || plant?.plant_name) {
    const fallback = getPlantImage(plant.slug || plant.plant_name);
    // Check if we got something other than the default monstera
    if (fallback !== PLANT_IMAGES.monstera) {
      return fallback;
    }
  }

  // Use static backend URLs for plant images (served via /static/plant-images/{slug}/image_1.jpg)
  if (plant?.slug) {
    return { uri: `${API_URL}/static/plant-images/${plant.slug}/image_1.jpg` };
  }

  // Final fallback to default
  return PLANT_IMAGES.monstera;
}
