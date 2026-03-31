/**
 * Plant Image Registry
 * Maps plant slugs to local images
 */

export const plantImages: Record<string, any> = {
  'monstera-deliciosa': require('./monstera.jpg'),
  'ficus-elastica': require('./ficus.jpg'),
  'calathea-ornata': require('./calathea.jpg'),
  'chinese-evergreen-aglaonema': require('./aglaonema.jpg'),
  'default': require('./monstera.jpg'),
};

export function getPlantImage(slug: string): any {
  return plantImages[slug] || plantImages['default'];
}
