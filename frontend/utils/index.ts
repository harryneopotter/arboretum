import { ImageSourcePropType } from 'react-native';

const PLANT_IMAGES: Record<string, ImageSourcePropType> = {
  monstera: require('../assets/images/monstera.jpg'),
  ficus: require('../assets/images/ficus.jpg'),
  calathea: require('../assets/images/calathea.jpg'),
  aloe: require('../assets/images/aloe.jpg'),
  avatar: require('../assets/images/avatar.jpg'),
};

export function getPlantImage(name: string): ImageSourcePropType {
  const key = name.toLowerCase().replace(/\.[^.]+$/, '');
  return PLANT_IMAGES[key] ?? PLANT_IMAGES.monstera;
}
