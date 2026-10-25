
import { useEffect, useRef, useState } from "react";
import {
  ChevronDown,
  Globe,
  Paperclip,
  SendHorizontal,
  Sparkles,
} from "lucide-react";

const SEARCH_MODES = ["Search mode", "Fast", "Deep research"];

const ChatInput = ({
  value,
  setValue,
  onSubmit,
  disabled,
  loading,
  onAttachClick,
  floating = false,
  inputRef,
}) => {
  const [mode, setMode] = useState(SEARCH_MODES[0]);
  const [modeOpen, setModeOpen] = useState(false);
  const menuRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        setModeOpen(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleKeyDown = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      onSubmit();
    }
  };

  return (
    <form
      onSubmit={(event) => {
        event.preventDefault();
        onSubmit();
      }}
      className={
        floating
          ? "w-full"
          : "border-t border-slate-200/80 bg-white p-3 sm:p-4 dark:border-white/[0.07] dark:bg-[#101522]"
      }
    >
      <div className="mx-auto w-full max-w-4xl">
        <div className="rounded-2xl border border-slate-200 bg-white shadow-sm transition focus-within:border-blue-400 focus-within:ring-4 focus-within:ring-blue-500/[0.08] dark:border-white/[0.12] dark:bg-[#171d2b] dark:focus-within:border-blue-500/60 dark:focus-within:ring-blue-500/[0.08]">
          <textarea
            ref={inputRef}
            value={value}
            onChange={(event) => setValue(event.target.value)}
            disabled={disabled || loading}
            rows={1}
            placeholder={
              disabled
                ? "Document is still processing…"
                : "Ask anything about your documents..."
            }
            className="max-h-40 min-h-[58px] w-full resize-none bg-transparent px-4 pt-4 text-sm leading-6 text-slate-900 outline-none placeholder:text-slate-400 disabled:cursor-not-allowed disabled:opacity-60 dark:text-slate-100 dark:placeholder:text-slate-500"
            onKeyDown={handleKeyDown}
          />

          <div className="flex flex-wrap items-center justify-between gap-2 px-3 pb-3 pt-1">
            <div className="flex min-w-0 flex-wrap items-center gap-1.5">
              <button
                type="button"
                onClick={onAttachClick}
                title="Attach a document"
                className="flex h-9 w-9 items-center justify-center rounded-xl text-slate-500 transition hover:bg-slate-100 hover:text-slate-800 dark:text-slate-400 dark:hover:bg-white/[0.07] dark:hover:text-white"
              >
                <Paperclip className="h-4 w-4" />
              </button>

              <button
                type="button"
                title="Web search is not currently connected"
                aria-label="Web search (not currently connected)"
                className="flex h-9 w-9 items-center justify-center rounded-xl text-slate-400 transition hover:bg-slate-100 hover:text-slate-600 dark:text-slate-500 dark:hover:bg-white/[0.07] dark:hover:text-slate-300"
              >
                <Globe className="h-4 w-4" />
              </button>

              <div className="relative" ref={menuRef}>
                <button
                  type="button"
                  onClick={() => setModeOpen((open) => !open)}
                  aria-expanded={modeOpen}
                  className="flex items-center gap-1.5 rounded-xl border border-slate-200 px-3 py-2 text-xs font-medium text-slate-600 transition hover:bg-slate-50 dark:border-white/10 dark:text-slate-300 dark:hover:bg-white/[0.05]"
                >
                  {mode}
                  <ChevronDown
                    className={`h-3.5 w-3.5 transition ${
                      modeOpen ? "rotate-180" : ""
                    }`}
                  />
                </button>

                {modeOpen && (
                  <div className="absolute bottom-full left-0 z-30 mb-2 w-44 overflow-hidden rounded-xl border border-slate-200 bg-white py-1 shadow-xl dark:border-white/10 dark:bg-[#1b2232]">
                    {SEARCH_MODES.map((option) => (
                      <button
                        key={option}
                        type="button"
                        onClick={() => {
                          setMode(option);
                          setModeOpen(false);
                        }}
                        className={`block w-full px-3 py-2.5 text-left text-xs transition ${
                          mode === option
                            ? "bg-blue-50 font-semibold text-blue-700 dark:bg-blue-500/10 dark:text-blue-300"
                            : "text-slate-600 hover:bg-slate-50 dark:text-slate-300 dark:hover:bg-white/[0.05]"
                        }`}
                      >
                        {option}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>

            <div className="flex items-center gap-2">
              <button
                type="button"
                title="Smart suggestions are not currently connected"
                aria-label="Smart suggestions (not currently connected)"
                className="flex h-9 w-9 items-center justify-center rounded-xl border border-slate-200 text-slate-500 transition hover:bg-slate-100 hover:text-slate-700 dark:border-white/10 dark:text-slate-400 dark:hover:bg-white/[0.06] dark:hover:text-slate-200"
              >
                <Sparkles className="h-4 w-4" />
              </button>

              <button
                type="submit"
                disabled={disabled || loading || !value.trim()}
                className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-blue-600 text-white shadow-sm transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:bg-slate-200 disabled:text-slate-400 disabled:shadow-none dark:disabled:bg-white/10 dark:disabled:text-slate-600"
                aria-label="Send question"
                title="Send message"
              >
                <SendHorizontal className="h-4 w-4" />
              </button>
            </div>
          </div>
        </div>

        <p className="mt-2 text-center text-[11px] text-slate-400 dark:text-slate-500">
          DocuMind AI answers using your selected documents. Check important
          details against the original sources.
        </p>
      </div>
    </form>
  );
};

export default ChatInput;