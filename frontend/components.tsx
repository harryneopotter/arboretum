import React from 'react';
import { 
  View, 
  Text, 
  TouchableOpacity, 
  StyleSheet, 
} from 'react-native';
import { colors, spacing, borderRadius, shadows } from './theme';

interface AmbientCardProps {
  children: React.ReactNode;
  style?: any;
  onPress?: () => void;
}

export const AmbientCard: React.FC<AmbientCardProps> = ({ children, style, onPress }) => (
  <TouchableOpacity
    onPress={onPress}
    disabled={!onPress}
    style={[styles.ambientCard, onPress && styles.ambientCardTouchable, style]}
    activeOpacity={0.8}
  >
    {children}
  </TouchableOpacity>
);

interface ButtonProps {
  children: React.ReactNode;
  variant?: 'primary' | 'secondary' | 'outline';
  style?: any;
  onPress?: () => void;
  icon?: React.ReactNode;
}

export const Button: React.FC<ButtonProps> = ({ children, variant = 'primary', style, onPress, icon }) => {
  const buttonStyles = [
    styles.button,
    variant === 'primary' && styles.buttonPrimary,
    variant === 'secondary' && styles.buttonSecondary,
    variant === 'outline' && styles.buttonOutline,
    style,
  ];

  return (
    <TouchableOpacity onPress={onPress} style={buttonStyles} activeOpacity={0.8}>
      {icon && <View style={styles.buttonIcon}>{icon}</View>}
      <Text style={[
        styles.buttonText,
        variant === 'primary' && styles.buttonTextPrimary,
        variant === 'secondary' && styles.buttonTextSecondary,
        variant === 'outline' && styles.buttonTextOutline,
      ]}>
        {children}
      </Text>
    </TouchableOpacity>
  );
};

interface LabelProps {
  children: React.ReactNode;
  style?: any;
}

export const Label: React.FC<LabelProps> = ({ children, style }) => (
  <Text style={[styles.label, style]}>{children}</Text>
);

export const IconButton: React.FC<{ icon: React.ReactNode; onPress: () => void; style?: any }> = 
  ({ icon, onPress, style }) => (
  <TouchableOpacity onPress={onPress} style={[styles.iconButton, style]} activeOpacity={0.8}>
    {icon}
  </TouchableOpacity>
);

const styles = StyleSheet.create({
  ambientCard: {
    backgroundColor: colors.surface,
    borderRadius: borderRadius.xl,
    padding: spacing.lg,
    ...shadows.card,
  },
  ambientCardTouchable: {},
  button: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.base,
    borderRadius: borderRadius.base,
    marginVertical: spacing.sm,
  },
  buttonPrimary: {
    backgroundColor: colors.primary,
    ...shadows.button,
  },
  buttonSecondary: {
    backgroundColor: colors.surfaceDarker,
  },
  buttonOutline: {
    backgroundColor: 'transparent',
    borderWidth: 1,
    borderColor: 'rgba(25, 28, 26, 0.15)',
  },
  buttonIcon: {
    marginRight: spacing.sm,
  },
  buttonText: {
    fontSize: 16,
    fontWeight: '600',
  },
  buttonTextPrimary: {
    color: colors.surface,
  },
  buttonTextSecondary: {
    color: colors.text,
  },
  buttonTextOutline: {
    color: colors.text,
  },
  label: {
    fontSize: 12,
    fontWeight: '700',
    letterSpacing: 0.5,
    textTransform: 'uppercase',
    color: colors.primaryDark,
  },
  iconButton: {
    width: 48,
    height: 48,
    borderRadius: borderRadius['2xl'],
    backgroundColor: 'rgba(255, 255, 255, 0.7)',
    alignItems: 'center',
    justifyContent: 'center',
    ...shadows.card,
  },
});
