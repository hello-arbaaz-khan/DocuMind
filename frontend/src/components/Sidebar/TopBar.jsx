
import { useEffect, useRef, useState } from "react";
import {
  ChevronDown,
  LogOut,
  Moon,
  Settings,
  Sun,
  Check,
} from "lucide-react";
import { useAuth } from "../../context/AuthContext";
import { useTheme } from "../../context/ThemeContext";

const TopBar = ({ onNavigate = () => {} }) => {
  const { user, logout } = useAuth();
  const { isDark, toggleTheme } = useTheme();
  const [menuOpen, setMenuOpen] = useState(false);
  const menuRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        setMenuOpen(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const displayName =
    user?.display_name || user?.username || user?.email || "Account";
  const initial = displayName.charAt(0).toUpperCase();

  return (
    <header className="relative z-20 flex h-16 shrink-0 items-center justify-between border-b border-slate-200/80 bg-white/95 px-4 backdrop-blur sm:px-6 dark:border-white/[0.07] dark:bg-[#101522]/95">
      <div className="flex min-w-0 items-center gap-3">
        <div className="hidden min-w-0 sm:block">
          <p className="truncate text-sm font-semibold text-slate-800 dark:text-slate-100">
            DocuMind AI
          </p>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            Your document workspace
          </p>
        </div>
      </div>

      <div className="flex items-center gap-2">
        <button
          type="button"
          onClick={toggleTheme}
          title={isDark ? "Switch to light mode" : "Switch to dark mode"}
          aria-label={isDark ? "Switch to light mode" : "Switch to dark mode"}
          className="flex h-10 w-10 items-center justify-center rounded-xl border border-slate-200 bg-white text-slate-600 transition hover:bg-slate-50 hover:text-slate-900 dark:border-white/10 dark:bg-white/[0.03] dark:text-slate-300 dark:hover:bg-white/[0.08] dark:hover:text-white"
        >
          {isDark ? (
            <Sun className="h-[18px] w-[18px]" />
          ) : (
            <Moon className="h-[18px] w-[18px]" />
          )}
        </button>

        <div className="relative" ref={menuRef}>
          <button
            type="button"
            onClick={() => setMenuOpen((open) => !open)}
            aria-expanded={menuOpen}
            aria-label="Open account menu"
            className="flex items-center gap-2 rounded-xl border border-transparent py-1 pl-1 pr-2 transition hover:border-slate-200 hover:bg-slate-50 dark:hover:border-white/10 dark:hover:bg-white/[0.04]"
          >
            <span className="flex h-9 w-9 items-center justify-center rounded-full bg-gradient-to-br from-blue-600 to-indigo-600 text-sm font-bold text-white shadow-sm">
              {initial}
            </span>

            <span className="hidden max-w-32 text-left sm:block">
              <span className="block truncate text-sm font-semibold text-slate-700 dark:text-slate-200">
                {displayName}
              </span>
              <span className="block text-left text-[11px] text-slate-400 dark:text-slate-500">
                Account
              </span>
            </span>

            <ChevronDown
              className={`h-4 w-4 text-slate-400 transition ${
                menuOpen ? "rotate-180" : ""
              }`}
            />
          </button>

          {menuOpen && (
            <div className="absolute right-0 top-12 z-50 w-64 overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-xl shadow-slate-900/10 dark:border-white/10 dark:bg-[#1a2030] dark:shadow-black/30">
              <div className="border-b border-slate-100 px-4 py-4 dark:border-white/[0.07]">
                <div className="flex items-center gap-3">
                  <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-blue-600 to-indigo-600 text-sm font-bold text-white">
                    {initial}
                  </span>
                  <div className="min-w-0">
                    <p className="truncate text-sm font-semibold text-slate-800 dark:text-white">
                      {displayName}
                    </p>
                    {user?.email && (
                      <p className="truncate text-xs text-slate-500 dark:text-slate-400">
                        {user.email}
                      </p>
                    )}
                  </div>
                </div>

                <div className="mt-3 flex items-center gap-2 rounded-lg bg-emerald-50 px-2.5 py-2 text-xs font-medium text-emerald-700 dark:bg-emerald-500/10 dark:text-emerald-300">
                  <Check className="h-3.5 w-3.5" />
                  Signed in
                </div>
              </div>

              <div className="p-1.5">
                <button
                  type="button"
                  onClick={() => {
                    setMenuOpen(false);
                    onNavigate("settings");
                  }}
                  className="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-left text-sm text-slate-700 transition hover:bg-slate-100 dark:text-slate-200 dark:hover:bg-white/[0.06]"
                >
                  <Settings className="h-4 w-4 text-slate-500 dark:text-slate-400" />
                  Settings
                </button>

                <button
                  type="button"
                  onClick={() => {
                    setMenuOpen(false);
                    logout();
                  }}
                  className="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-left text-sm text-red-600 transition hover:bg-red-50 dark:text-red-300 dark:hover:bg-red-500/10"
                >
                  <LogOut className="h-4 w-4" />
                  Log out
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};

export default TopBar;