import { Feather } from '@expo/vector-icons';
import * as Haptics from 'expo-haptics';
import { LinearGradient } from 'expo-linear-gradient';
import { StatusBar } from 'expo-status-bar';
import { useEffect, useState } from 'react';
import {
  Alert,
  Keyboard,
  Platform,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
  useColorScheme,
} from 'react-native';
import { KeyboardAvoidingView } from 'react-native-keyboard-controller';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { RobinAvatar, type RobinMode } from '@/components/RobinAvatar';
import { useColors } from '@/hooks/useColors';

type Message = {
  id: string;
  role: 'user' | 'robin';
  text: string;
};

function localReply(command: string): string {
  const text = command.trim().toLocaleLowerCase();

  if (/\b(call|ring)\b/.test(text) && /\b(me|remind|reminder)\b/.test(text)) {
    return 'Outbound calls are not connected yet. I did not schedule a call or save a reminder. Twilio setup is still pending.';
  }

  if (/^(status|check status|health|are you there)[?.! ]*$/.test(text)) {
    return 'This phone companion is open and ready. No Windows computer is paired, so no PC command has been sent or executed.';
  }

  if (/\b(help|what can you do)\b/.test(text)) {
    return 'For now, I can report this phone’s status and explain setup. PC actions stay off until the Windows runtime is paired. Calls stay off until Twilio is connected.';
  }

  if (/\b(pair|connect|computer|windows|pc|laptop)\b/.test(text)) {
    return 'The Windows runtime has not been paired with this phone yet. I have not created pairing credentials or sent anything to a computer.';
  }

  return 'This phone is not connected to your Windows computer yet. I did not send or execute that command.';
}

function SafetyNotice() {
  const colors = useColors();

  return (
    <View style={[styles.safetyNotice, { borderColor: colors.border, backgroundColor: colors.card }]}>
      <View style={[styles.safetyIcon, { backgroundColor: colors.secondary }]}>
        <Feather name="shield" size={16} color={colors.primary} />
      </View>
      <View style={styles.safetyCopy}>
        <Text style={[styles.safetyTitle, { color: colors.foreground }]}>Command-only by design</Text>
        <Text style={[styles.safetyText, { color: colors.mutedForeground }]}>
          No background actions. Payment actions and bulk photo access are blocked.
        </Text>
      </View>
    </View>
  );
}

function MessageBubble({ message }: { message: Message }) {
  const colors = useColors();
  const isUser = message.role === 'user';

  return (
    <View style={[styles.messageRow, isUser && styles.userMessageRow]}>
      <View
        style={[
          styles.messageBubble,
          {
            backgroundColor: isUser ? colors.primary : colors.card,
            borderColor: isUser ? colors.primary : colors.border,
          },
        ]}
      >
        <Text style={[styles.messageText, { color: isUser ? colors.primaryForeground : colors.foreground }]}>
          {message.text}
        </Text>
      </View>
    </View>
  );
}

export default function HomeScreen() {
  const colors = useColors();
  const scheme = useColorScheme();
  const insets = useSafeAreaInsets();
  const [draft, setDraft] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [mode, setMode] = useState<RobinMode>('idle');

  useEffect(() => {
    if (mode !== 'responding') return;
    const timer = setTimeout(() => setMode('idle'), 1250);
    return () => clearTimeout(timer);
  }, [mode]);

  const topInset = Platform.OS === 'web' ? Math.max(insets.top, 67) : insets.top;
  const bottomInset = Platform.OS === 'web' ? Math.max(insets.bottom, 34) : insets.bottom;

  const sendCommand = (value = draft) => {
    const text = value.trim();
    if (!text) return;

    Keyboard.dismiss();
    void Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light).catch(() => undefined);
    const now = Date.now().toString();
    const response: Message = {
      id: `${now}-robin`,
      role: 'robin',
      text: localReply(text),
    };
    const userMessage: Message = {
      id: `${now}-user`,
      role: 'user',
      text,
    };
    setMessages((current) =>
      [...current, userMessage, response].slice(-6),
    );
    setDraft('');
    setMode('responding');
  };

  const showSafetyDetails = () => {
    Alert.alert(
      'Your command boundary',
      'ROBIN only reacts to a command you submit. This phone is not paired to a PC, so commands are not forwarded. Payments, GPay, and bulk photo access are blocked.',
      [{ text: 'Understood' }],
    );
  };

  return (
    <LinearGradient
      colors={[colors.background, colors.background, colors.card]}
      locations={[0, 0.68, 1]}
      style={styles.root}
    >
      <StatusBar style={scheme === 'dark' ? 'light' : 'dark'} />
      <KeyboardAvoidingView
        style={styles.keyboard}
        behavior="padding"
        keyboardVerticalOffset={0}
      >
        <ScrollView
          contentContainerStyle={[
            styles.content,
            { paddingTop: topInset + 12, paddingBottom: 18 },
          ]}
          keyboardShouldPersistTaps="handled"
          showsVerticalScrollIndicator={false}
        >
          <View style={styles.header}>
            <View style={styles.brandBlock}>
              <View style={[styles.brandMark, { backgroundColor: colors.primary }]}>
                <Feather name="command" size={17} color={colors.primaryForeground} />
              </View>
              <View>
                <Text style={[styles.brand, { color: colors.foreground }]}>ROBIN</Text>
                <Text style={[styles.brandSub, { color: colors.mutedForeground }]}>COMPANION</Text>
              </View>
            </View>
            <Pressable
              accessibilityRole="button"
              accessibilityLabel="Show safety details"
              onPress={showSafetyDetails}
              style={({ pressed }) => [styles.iconButton, pressed && styles.pressed]}
              testID="safety-details"
            >
              <Feather name="shield" size={20} color={colors.foreground} />
            </Pressable>
          </View>

          <View style={styles.hero}>
            <View style={styles.heroCopy}>
              <View style={[styles.readyPill, { backgroundColor: colors.secondary }]}>
                <View style={[styles.readyDot, { backgroundColor: colors.primary }]} />
                <Text style={[styles.readyLabel, { color: colors.secondaryForeground }]}>
                  {mode === 'responding' ? 'RESPONSE READY' : 'WAITING FOR YOU'}
                </Text>
              </View>
              <Text style={[styles.heroTitle, { color: colors.foreground }]}>
                Here when{'\n'}you ask.
              </Text>
              <Text style={[styles.heroSub, { color: colors.mutedForeground }]}>
                Your words set the pace.{'\n'}Nothing runs on its own.
              </Text>
            </View>
            <RobinAvatar mode={mode} />
          </View>

          <View style={styles.statusGrid}>
            <View style={[styles.statusCard, { backgroundColor: colors.card, borderColor: colors.border }]}>
              <View style={styles.statusCardTop}>
                <View style={[styles.statusIcon, { backgroundColor: colors.secondary }]}>
                  <Feather name="monitor" size={16} color={colors.primary} />
                </View>
                <Text style={[styles.statusEyebrow, { color: colors.mutedForeground }]}>WINDOWS DESKTOP</Text>
              </View>
              <Text style={[styles.statusValue, { color: colors.foreground }]}>Not paired</Text>
              <Text style={[styles.statusDescription, { color: colors.mutedForeground }]}>
                Commands stay on this phone.
              </Text>
            </View>
            <View style={[styles.statusCard, { backgroundColor: colors.card, borderColor: colors.border }]}>
              <View style={styles.statusCardTop}>
                <View style={[styles.statusIcon, { backgroundColor: colors.secondary }]}>
                  <Feather name="phone" size={16} color={colors.accent} />
                </View>
                <Text style={[styles.statusEyebrow, { color: colors.mutedForeground }]}>OUTBOUND CALLS</Text>
              </View>
              <Text style={[styles.statusValue, { color: colors.foreground }]}>Not connected</Text>
              <Text style={[styles.statusDescription, { color: colors.mutedForeground }]}>
                No call or reminder was scheduled.
              </Text>
            </View>
          </View>

          <SafetyNotice />

          <View style={styles.commandsHeader}>
            <View>
              <Text style={[styles.sectionTitle, { color: colors.foreground }]}>Your command</Text>
              <Text style={[styles.sectionHint, { color: colors.mutedForeground }]}>
                Enter a request. Nothing leaves this phone yet.
              </Text>
            </View>
            {messages.length > 0 && (
              <Pressable
                accessibilityRole="button"
                accessibilityLabel="Clear conversation"
                onPress={() => setMessages([])}
                style={({ pressed }) => [styles.clearButton, pressed && styles.pressed]}
                testID="clear-conversation"
              >
                <Feather name="x" size={17} color={colors.mutedForeground} />
              </Pressable>
            )}
          </View>

          {messages.length === 0 ? (
            <View style={styles.suggestions}>
              <Pressable
                onPress={() => sendCommand('status')}
                style={({ pressed }) => [
                  styles.suggestion,
                  { borderColor: colors.border, backgroundColor: colors.card },
                  pressed && styles.pressed,
                ]}
                testID="quick-status"
              >
                <Feather name="activity" size={15} color={colors.primary} />
                <Text style={[styles.suggestionText, { color: colors.foreground }]}>Check status</Text>
                <Feather name="arrow-up-right" size={14} color={colors.mutedForeground} />
              </Pressable>
              <Pressable
                onPress={() => sendCommand('How do I connect my PC?')}
                style={({ pressed }) => [
                  styles.suggestion,
                  { borderColor: colors.border, backgroundColor: colors.card },
                  pressed && styles.pressed,
                ]}
                testID="quick-pairing-info"
              >
                <Feather name="link-2" size={15} color={colors.primary} />
                <Text style={[styles.suggestionText, { color: colors.foreground }]}>Pairing status</Text>
                <Feather name="arrow-up-right" size={14} color={colors.mutedForeground} />
              </Pressable>
            </View>
          ) : (
            <View style={styles.messages} testID="conversation">
              {messages.map((message) => (
                <MessageBubble key={message.id} message={message} />
              ))}
            </View>
          )}
        </ScrollView>

        <View
          style={[
            styles.composerWrap,
            {
              backgroundColor: colors.background,
              borderTopColor: colors.border,
              paddingBottom: bottomInset + 10,
            },
          ]}
        >
          <View style={[styles.composer, { backgroundColor: colors.card, borderColor: colors.border }]}>
            <TextInput
              accessibilityLabel="Type a command for Robin"
              onChangeText={setDraft}
              onSubmitEditing={() => sendCommand()}
              placeholder="Type a command for Robin"
              placeholderTextColor={colors.mutedForeground}
              returnKeyType="send"
              style={[styles.input, { color: colors.foreground }]}
              value={draft}
              maxLength={600}
              testID="command-input"
            />
            <Pressable
              accessibilityRole="button"
              accessibilityLabel="Send command"
              disabled={!draft.trim()}
              onPress={() => sendCommand()}
              style={({ pressed }) => [
                styles.sendButton,
                { backgroundColor: draft.trim() ? colors.primary : colors.muted },
                pressed && draft.trim() ? styles.sendPressed : undefined,
              ]}
              testID="send-command"
            >
              <Feather
                name="arrow-up"
                size={19}
                color={draft.trim() ? colors.primaryForeground : colors.mutedForeground}
              />
            </Pressable>
          </View>
          <Text style={[styles.composerNote, { color: colors.mutedForeground }]}>
            Private on this phone · no background actions
          </Text>
        </View>
      </KeyboardAvoidingView>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  root: {
    flex: 1,
  },
  keyboard: {
    flex: 1,
  },
  content: {
    paddingHorizontal: 22,
  },
  header: {
    alignItems: 'center',
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 28,
  },
  brandBlock: {
    alignItems: 'center',
    flexDirection: 'row',
    gap: 11,
  },
  brandMark: {
    alignItems: 'center',
    borderRadius: 13,
    height: 36,
    justifyContent: 'center',
    width: 36,
  },
  brand: {
    fontSize: 14,
    fontWeight: '700',
    letterSpacing: 2.4,
  },
  brandSub: {
    fontSize: 9,
    fontWeight: '600',
    letterSpacing: 1.6,
    marginTop: 2,
  },
  iconButton: {
    alignItems: 'center',
    height: 42,
    justifyContent: 'center',
    width: 42,
  },
  pressed: {
    opacity: 0.72,
  },
  hero: {
    alignItems: 'center',
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 22,
    minHeight: 188,
  },
  heroCopy: {
    flex: 1,
    paddingRight: 2,
  },
  readyPill: {
    alignItems: 'center',
    alignSelf: 'flex-start',
    borderRadius: 20,
    flexDirection: 'row',
    gap: 7,
    marginBottom: 14,
    paddingHorizontal: 10,
    paddingVertical: 7,
  },
  readyDot: {
    borderRadius: 4,
    height: 7,
    width: 7,
  },
  readyLabel: {
    fontSize: 9,
    fontWeight: '700',
    letterSpacing: 1.2,
  },
  heroTitle: {
    fontSize: 36,
    fontWeight: '700',
    letterSpacing: -1.2,
    lineHeight: 39,
  },
  heroSub: {
    fontSize: 13,
    lineHeight: 19,
    marginTop: 10,
  },
  statusGrid: {
    flexDirection: 'row',
    gap: 10,
    marginBottom: 12,
  },
  statusCard: {
    borderRadius: 18,
    borderWidth: 1,
    flex: 1,
    minHeight: 128,
    padding: 14,
  },
  statusCardTop: {
    alignItems: 'center',
    flexDirection: 'row',
    gap: 8,
    marginBottom: 12,
  },
  statusIcon: {
    alignItems: 'center',
    borderRadius: 10,
    height: 28,
    justifyContent: 'center',
    width: 28,
  },
  statusEyebrow: {
    flexShrink: 1,
    fontSize: 8,
    fontWeight: '700',
    letterSpacing: 0.65,
  },
  statusValue: {
    fontSize: 14,
    fontWeight: '700',
    marginBottom: 4,
  },
  statusDescription: {
    fontSize: 10,
    lineHeight: 14,
  },
  safetyNotice: {
    alignItems: 'center',
    borderRadius: 16,
    borderWidth: 1,
    flexDirection: 'row',
    gap: 11,
    marginBottom: 24,
    paddingHorizontal: 13,
    paddingVertical: 12,
  },
  safetyIcon: {
    alignItems: 'center',
    borderRadius: 11,
    height: 32,
    justifyContent: 'center',
    width: 32,
  },
  safetyCopy: {
    flex: 1,
  },
  safetyTitle: {
    fontSize: 11,
    fontWeight: '700',
    marginBottom: 3,
  },
  safetyText: {
    fontSize: 10,
    lineHeight: 14,
  },
  commandsHeader: {
    alignItems: 'center',
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 13,
  },
  sectionTitle: {
    fontSize: 19,
    fontWeight: '700',
    letterSpacing: -0.3,
  },
  sectionHint: {
    fontSize: 11,
    marginTop: 3,
  },
  clearButton: {
    alignItems: 'center',
    height: 36,
    justifyContent: 'center',
    width: 36,
  },
  suggestions: {
    gap: 9,
    marginBottom: 10,
  },
  suggestion: {
    alignItems: 'center',
    borderRadius: 14,
    borderWidth: 1,
    flexDirection: 'row',
    gap: 10,
    minHeight: 47,
    paddingHorizontal: 13,
  },
  suggestionText: {
    flex: 1,
    fontSize: 12,
    fontWeight: '600',
  },
  messages: {
    gap: 9,
    marginBottom: 12,
  },
  messageRow: {
    alignItems: 'flex-start',
    flexDirection: 'row',
  },
  userMessageRow: {
    justifyContent: 'flex-end',
  },
  messageBubble: {
    borderRadius: 16,
    borderWidth: 1,
    maxWidth: '92%',
    paddingHorizontal: 13,
    paddingVertical: 10,
  },
  messageText: {
    fontSize: 12,
    lineHeight: 18,
  },
  composerWrap: {
    borderTopWidth: 1,
    paddingHorizontal: 18,
    paddingTop: 12,
  },
  composer: {
    alignItems: 'center',
    borderRadius: 18,
    borderWidth: 1,
    flexDirection: 'row',
    minHeight: 54,
    paddingLeft: 16,
    paddingRight: 7,
  },
  input: {
    flex: 1,
    fontSize: 14,
    minHeight: 48,
    paddingVertical: 13,
  },
  sendButton: {
    alignItems: 'center',
    borderRadius: 13,
    height: 40,
    justifyContent: 'center',
    width: 40,
  },
  sendPressed: {
    opacity: 0.78,
    transform: [{ scale: 0.96 }],
  },
  composerNote: {
    fontSize: 9,
    letterSpacing: 0.25,
    paddingTop: 8,
    textAlign: 'center',
  },
});
