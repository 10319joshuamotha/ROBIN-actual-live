/**
 * Semantic design tokens for the mobile app.
 *
 * These tokens mirror the naming conventions used in web artifacts (index.css)
 * so that multi-artifact projects share a cohesive visual identity.
 *
 * Replace the placeholder values below with values that match the project's
 * brand. If a sibling web artifact exists, read its index.css and convert the
 * HSL values to hex so both artifacts use the same palette.
 *
 * To add dark mode, add a `dark` key with the same token names.
 * The useColors() hook will automatically pick it up.
 */

const colors = {
  light: {
    text: '#172621',
    tint: '#47775c',
    background: '#f2efe6',
    foreground: '#172621',
    card: '#fbf9f2',
    cardForeground: '#172621',
    primary: '#47775c',
    primaryForeground: '#f7f5ec',
    secondary: '#e3e9de',
    secondaryForeground: '#274235',
    muted: '#e8e5dc',
    mutedForeground: '#768078',
    accent: '#d98b5f',
    accentForeground: '#281b16',
    destructive: '#ba4c43',
    destructiveForeground: '#ffffff',
    border: '#dadcd2',
    input: '#dadcd2',
    robinHair: '#253229',
    robinSkin: '#e8c1a5',
    robinClothes: '#32564e',
    robinEyes: '#527b66',
    robinHighlight: '#f4e7ce',
  },
  dark: {
    text: '#f1f2e9',
    tint: '#9dc17a',
    background: '#0b1917',
    foreground: '#f1f2e9',
    card: '#142522',
    cardForeground: '#f1f2e9',
    primary: '#9dc17a',
    primaryForeground: '#102219',
    secondary: '#1e322d',
    secondaryForeground: '#dce9d5',
    muted: '#1b2a27',
    mutedForeground: '#99aaa0',
    accent: '#e5a077',
    accentForeground: '#22150f',
    destructive: '#ff7f72',
    destructiveForeground: '#2b0f0b',
    border: '#2a3a34',
    input: '#33443d',
    robinHair: '#101f1e',
    robinSkin: '#e8bfa2',
    robinClothes: '#426d5e',
    robinEyes: '#b0d694',
    robinHighlight: '#fcedd6',
  },
  radius: 18,
};

export default colors;
