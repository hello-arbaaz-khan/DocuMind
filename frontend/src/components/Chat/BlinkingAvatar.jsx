// Animated "thinking" face shown while the answer is being generated:
// the eyes blink periodically and the pupils drift side to side.
// When the answer arrives, ChatMessage swaps this back to the static
// Bot icon — so blinking naturally "stops".
const BlinkingAvatar = () => (
  <div
    className="mt-1 flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-violet-600/20"
    role="status"
    aria-label="Assistant is thinking"
  >
    <div className="flex items-center gap-1.5">
      <div className="blink-eye flex h-3.5 w-3 items-center justify-center rounded-full bg-violet-200 dark:bg-violet-300">
        <div className="blink-pupil h-1.5 w-1.5 rounded-full bg-violet-900" />
      </div>
      <div className="blink-eye flex h-3.5 w-3 items-center justify-center rounded-full bg-violet-200 dark:bg-violet-300">
        <div className="blink-pupil h-1.5 w-1.5 rounded-full bg-violet-900" />
      </div>
    </div>

    <style>{`
      .blink-eye {
        animation: blink-eye-blink 3.2s ease-in-out infinite;
        transform-origin: center;
      }
      .blink-pupil {
        animation: blink-pupil-look 2.6s ease-in-out infinite;
      }
      @keyframes blink-eye-blink {
        0%, 90%, 100% { transform: scaleY(1); }
        94% { transform: scaleY(0.1); }
      }
      @keyframes blink-pupil-look {
        0%, 100% { transform: translateX(0); }
        25% { transform: translateX(-2px); }
        55% { transform: translateX(2px); }
        80% { transform: translateX(0); }
      }
    `}</style>
  </div>
);

export default BlinkingAvatar;