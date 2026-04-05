import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Image,
  Dimensions,
} from 'react-native';
import { ChevronRight, Camera, Search, Heart } from 'lucide-react-native';

const { width } = Dimensions.get('window');

const colors = {
  primary: '#23472b',
  primaryContainer: '#3a5f41',
  tertiaryFixed: '#b9f0ba',
  surface: '#f8faf6',
  surfaceContainerLowest: '#ffffff',
  surfaceContainerLow: '#f2f4f0',
  text: '#191c1a',
};

const ONBOARDING_SLIDES = [
  {
    id: '1',
    title: 'Identify Any Plant',
    description: 'Snap a photo of any plant or flower. Our AI suggests the closest matching species.',
    icon: Camera,
  },
  {
    id: '2',
    title: 'Get Expert Care Tips',
    description: 'Learn exactly how to care for your plants with personalized watering, light, and fertilizer schedules.',
    icon: Heart,
  },
  {
    id: '3',
    title: 'Track Your Collection',
    description: 'Build your own digital garden. Set reminders and watch your plants thrive.',
    icon: Search,
  },
];

export default function OnboardingScreen({ navigate }: { navigate: (s: string) => void }) {
  const [currentSlide, setCurrentSlide] = useState(0);

  const Icon = ONBOARDING_SLIDES[currentSlide].icon;
  const isLastSlide = currentSlide === ONBOARDING_SLIDES.length - 1;

  const handleNext = () => {
    if (isLastSlide) {
      navigate('HOME');
    } else {
      setCurrentSlide(currentSlide + 1);
    }
  };

  return (
    <View style={styles.container}>
      {/* Background Image */}
      <Image
        source={{ uri: 'https://images.unsplash.com/photo-1459411552884-841db9b3cc2a?w=800&q=80' }}
        style={styles.backgroundImage}
        blurRadius={2}
      />
      <View style={styles.overlay} />

      {/* Content */}
      <View style={styles.content}>
        {/* Icon */}
        <View style={styles.iconContainer}>
          <View style={styles.iconCircle}>
            <Icon size={40} color={colors.primary} strokeWidth={1.5} />
          </View>
        </View>

        {/* Title & Description */}
        <Text style={styles.title}>{ONBOARDING_SLIDES[currentSlide].title}</Text>
        <Text style={styles.description}>{ONBOARDING_SLIDES[currentSlide].description}</Text>

        {/* Progress Dots */}
        <View style={styles.dotsContainer}>
          {ONBOARDING_SLIDES.map((_, index) => (
            <View
              key={index}
              style={[
                styles.dot,
                index === currentSlide && styles.activeDot,
              ]}
            />
          ))}
        </View>
      </View>

      {/* Bottom Button */}
      <View style={styles.footer}>
        <TouchableOpacity style={styles.button} onPress={handleNext} activeOpacity={0.9}>
          <Text style={styles.buttonText}>{isLastSlide ? 'Get Started' : 'Next'}</Text>
          <View style={styles.buttonIcon}>
            <ChevronRight size={20} color={colors.primary} strokeWidth={2} />
          </View>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.surface },
  backgroundImage: { ...StyleSheet.absoluteFillObject, width: '100%', height: '100%' },
  overlay: { ...StyleSheet.absoluteFillObject, backgroundColor: 'rgba(248,250,246,0.85)' },
  content: { flex: 1, justifyContent: 'center', alignItems: 'center', paddingHorizontal: 32 },
  iconContainer: { marginBottom: 32 },
  iconCircle: { width: 96, height: 96, borderRadius: 48, backgroundColor: colors.surfaceContainerLowest, alignItems: 'center', justifyContent: 'center', shadowColor: colors.primary, shadowOffset: { width: 0, height: 0 }, shadowOpacity: 0.08, shadowRadius: 32, elevation: 4 },
  title: { fontSize: 32, fontWeight: '700', color: colors.text, textAlign: 'center', marginBottom: 16, letterSpacing: -0.5 },
  description: { fontSize: 16, color: colors.primaryContainer, textAlign: 'center', lineHeight: 24, maxWidth: width * 0.8 },
  dotsContainer: { flexDirection: 'row', marginTop: 40 },
  dot: { width: 8, height: 8, borderRadius: 4, backgroundColor: 'rgba(35,71,43,0.2)', marginHorizontal: 4 },
  activeDot: { backgroundColor: colors.primary, width: 24 },
  footer: { paddingHorizontal: 24, paddingBottom: 48 },
  button: { backgroundColor: colors.primary, borderRadius: 16, paddingVertical: 18, paddingHorizontal: 24, flexDirection: 'row', alignItems: 'center', justifyContent: 'center', shadowColor: colors.primary, shadowOffset: { width: 0, height: 4 }, shadowOpacity: 0.15, shadowRadius: 16, elevation: 8 },
  buttonText: { color: colors.surfaceContainerLowest, fontSize: 16, fontWeight: '600', marginRight: 8 },
  buttonIcon: { width: 32, height: 32, borderRadius: 8, backgroundColor: colors.tertiaryFixed, alignItems: 'center', justifyContent: 'center' },
});
