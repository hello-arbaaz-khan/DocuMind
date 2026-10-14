import { useEffect, useState } from "react";

const WORD = "Thinking"; // dots are rendered separately (total = 10 chars: T-h-i-n-k-i-n-g-.-.)

// Types out "Thinking.." one character at a time (starting from "T"),
// then keeps the trailing dots pulsing until the answer arrives.
// The component unmounts the moment the real answer renders.
const ThinkingText = () => {
  const total = WORD.length + 2;
  const [count, setCount] = useState(1); // starts at "T"

  useEffect(() => {
    if (count >= total) return undefined;

    const timer = window.setTimeout(() => {
      setCount((current) => Math.min(current + 1, total));
    }, 130);

    return () => window.clearTimeout(timer);
  }, [count]);

  const complete = count >= total;

  return (
    <span className="text-sm" role="status" aria-live="polite">
      <span className="tracking-wide text-slate-300">
        {WORD.slice(0, Math.min(count, WORD.length))}

        <span className={`think-dot ${complete ? "think-dot-pulse think-dot-1" : ""}`}>
          {count > WORD.length ? "." : ""}
        </span>
        <span className={`think-dot ${complete ? "think-dot-pulse think-dot-2" : ""}`}>
          {count > WORD.length + 1 ? "." : ""}
        </span>

        {!complete && (
          <span className="think-caret ml-0.5 inline-block h-3.5 w-[2px] translate-y-[2px] bg-slate-300" />
        )}
      </span>

      <style>{`
        .think-dot { display: inline-block; min-width: 0.3em; }
        .think-dot-pulse { animation: think-dot-pulse 1.1s ease-in-out infinite; }
        .think-dot-2 { animation-delay: 0.25s; }
        .think-caret { animation: think-caret-blink 0.8s step-end infinite; }
        @keyframes think-dot-pulse {
          0%, 100% { opacity: 0.2; transform: translateY(0); }
          50% { opacity: 1; transform: translateY(-2px); }
        }
        @keyframes think-caret-blink {
          0%, 100% { opacity: 0; }
          50% { opacity: 1; }
        }
      `}</style>
    </span>
  );
};

export default ThinkingText;