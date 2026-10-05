import { useEffect } from 'react';
import { StyleSheet, View } from 'react-native';
import Svg, { Circle, Ellipse, Path } from 'react-native-svg';
import Animated, {
  cancelAnimation,
  Easing,
  useAnimatedStyle,
  useSharedValue,
  withRepeat,
  withSequence,
  withTiming,
} from 'react-native-reanimated';
import { useColors } from '@/hooks/useColors';

export type RobinMode = 'idle' | 'listening' | 'responding';

type Props = {
  mode: RobinMode;
};

export function RobinAvatar({ mode }: Props) {
  const colors = useColors();
  const float = useSharedValue(0);
  const pulse = useSharedValue(0);

  useEffect(() => {
    float.value = withRepeat(
      withSequence(
        withTiming(-4, { duration: 1500, easing: Easing.inOut(Easing.quad) }),
        withTiming(0, { duration: 1500, easing: Easing.inOut(Easing.quad) }),
      ),
      -1,
      false,
    );
    return () => cancelAnimation(float);
  }, [float]);

  useEffect(() => {
    cancelAnimation(pulse);
    if (mode === 'listening') {
      pulse.value = withRepeat(
        withTiming(1, { duration: 1050, easing: Easing.inOut(Easing.quad) }),
        -1,
        true,
      );
    } else {
      pulse.value = withTiming(0, { duration: 240 });
    }
    return () => cancelAnimation(pulse);
  }, [mode, pulse]);

  const floatStyle = useAnimatedStyle(() => ({
    transform: [{ translateY: float.value }],
  }));
  const pulseStyle = useAnimatedStyle(() => ({
    opacity: 0.12 + pulse.value * 0.34,
    transform: [{ scale: 0.92 + pulse.value * 0.12 }],
  }));

  return (
    <View
      accessible
      accessibilityLabel={`Robin character, ${mode}`}
      style={styles.stage}
    >
      <Animated.View
        pointerEvents="none"
        style={[
          styles.signalRing,
          { borderColor: colors.primary },
          pulseStyle,
        ]}
      />
      <View
        pointerEvents="none"
        style={[
          styles.backdrop,
          { backgroundColor: colors.secondary },
        ]}
      />
      <Animated.View style={[styles.figure, floatStyle]}>
        <Svg width={176} height={176} viewBox="0 0 220 220">
          <Path
            d="M34 208c2-34 25-52 53-58l23 18 24-18c29 7 51 26 53 58H34Z"
            fill={colors.robinClothes}
          />
          <Path
            d="m87 151 23 17 24-17 11 10-35 36-34-36 11-10Z"
            fill={colors.robinHighlight}
          />
          <Path
            d="M65 81c-8-28 7-59 31-68 26-10 62-1 72 29 6 17-1 44-1 66v47c-8 18-25 31-40 35-23 6-50-7-62-29V81Z"
            fill={colors.robinHair}
          />
          <Path
            d="M73 81c0-26 14-46 38-50 24-5 44 10 45 37l-5 53c-4 23-20 40-41 40-20 0-35-18-39-41l2-39Z"
            fill={colors.robinSkin}
          />
          <Ellipse cx="72" cy="111" rx="8" ry="13" fill={colors.robinSkin} />
          <Ellipse cx="153" cy="111" rx="8" ry="13" fill={colors.robinSkin} />
          <Path
            d="M67 78c2-35 24-57 55-54 23 2 39 19 44 43-11-3-19-11-24-22-14 17-35 26-63 26l-1 31c-5-6-9-14-11-24Z"
            fill={colors.robinHair}
          />
          <Path
            d="M69 79c-14 21-14 53-10 79-10-10-16-26-16-46 0-27 10-51 28-66l-2 33Z"
            fill={colors.robinHair}
          />
          <Path
            d="M151 80c15 18 16 51 11 78 10-10 16-27 16-47 0-24-9-48-27-63l2 32Z"
            fill={colors.robinHair}
          />
          <Path
            d="M86 108c5-4 11-4 16 0"
            fill="none"
            stroke={colors.robinHair}
            strokeWidth="3"
            strokeLinecap="round"
          />
          <Path
            d="M121 108c5-4 11-4 16 0"
            fill="none"
            stroke={colors.robinHair}
            strokeWidth="3"
            strokeLinecap="round"
          />
          <Ellipse cx="99" cy="119" rx="4.5" ry="6" fill={colors.robinEyes} />
          <Ellipse cx="128" cy="119" rx="4.5" ry="6" fill={colors.robinEyes} />
          <Circle cx="100" cy="117" r="1.5" fill={colors.robinHighlight} />
          <Circle cx="129" cy="117" r="1.5" fill={colors.robinHighlight} />
          <Path
            d="M111 120c-1 7-3 11-1 13"
            fill="none"
            stroke={colors.accentForeground}
            strokeWidth="2"
            strokeLinecap="round"
          />
          <Path
            d={mode === 'responding' ? 'M101 143c6 7 14 7 20 0' : 'M103 143c5 4 11 4 16 0'}
            fill="none"
            stroke={colors.accentForeground}
            strokeWidth="2.5"
            strokeLinecap="round"
          />
          <Path
            d="M91 177c8 7 20 10 30 8"
            fill="none"
            stroke={colors.robinHighlight}
            strokeWidth="3"
            strokeLinecap="round"
            opacity="0.8"
          />
        </Svg>
      </Animated.View>
      <View
        style={[
          styles.statusDot,
          {
            backgroundColor: mode === 'listening' ? colors.accent : colors.primary,
            borderColor: colors.background,
          },
        ]}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  stage: {
    alignItems: 'center',
    height: 184,
    justifyContent: 'center',
    width: 184,
  },
  backdrop: {
    borderRadius: 100,
    height: 156,
    opacity: 0.8,
    position: 'absolute',
    width: 156,
  },
  signalRing: {
    borderRadius: 100,
    borderWidth: 1,
    height: 174,
    position: 'absolute',
    width: 174,
  },
  figure: {
    alignItems: 'center',
    height: 176,
    justifyContent: 'center',
    width: 176,
  },
  statusDot: {
    borderRadius: 8,
    borderWidth: 3,
    bottom: 14,
    height: 16,
    position: 'absolute',
    right: 20,
    width: 16,
  },
});
