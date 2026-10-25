import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  LayoutDashboard,
  MessageCircle,
  FileText,
  Settings,
  Sparkles,
  UploadCloud,
  ChevronRight,
  ChevronsLeft,
  ChevronsRight,
  Clock,
  LogOut,
  MessageSquare,
  MoreVertical,
  PenSquare,
  Search,
  Trash2,
  BookOpen,
  X,
} from "lucide-react";

import { useAppContext } from "../../context/AppContext";
import { useAuth } from "../../context/AuthContext";
import { conversationApi } from "../../services/api";
import { PATHS } from "../../router/paths";
import DriveStatusBadge from "./DriveStatusBadge";

const NAV_ITEMS = [
  // { id: "dashboard", label: "Dashboard", icon: LayoutDashboard },
  { id: "search", label: "Advanced Search", icon: Search },
  { id: "chat", label: "AI Chat", icon: MessageCircle },
  { id: "documents", label: "Documents", icon: FileText },
  // { id: "drive", label: "Google Drive", icon: UploadCloud },
  // { id: "settings", label: "Settings", icon: Settings },
];

const timeAgo = (value) => {
  if (!value) return "";
  const date = new Date(value);
  const diff = Date.now() - date.getTime();

  if (!Number.isFinite(diff) || diff < 0) return "";

  const minutes = Math.floor(diff / 60000);
  if (minutes < 1) return "now";
  if (minutes < 60) return `${minutes}m`;

  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h`;

  const days = Math.floor(hours / 24);
  if (days < 7) return `${days}d`;

  return date.toLocaleDateString();
};

const Sidebar = ({
  onUploadClick = () => {},
  activeView = "chat",
  onNavigate = () => {},
  collapsed = false,
  onToggleCollapse = () => {},
}) => {
  const {
    conversations = [],
    activeConversation,
    loadingConversations,
    loadConversations,
    dispatch,
    addToast,
  } = useAppContext();

  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const [menuFor, setMenuFor] = useState(null);
  const [guideOpen, setGuideOpen] = useState(false);
  const menuRef = useRef(null);

  useEffect(() => {
    if (menuFor === null) return undefined;

    const handleClickOutside = (event) => {
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        setMenuFor(null);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [menuFor]);

  const handleNewChat = () => navigate(PATHS.newChat);

  const handleSelectConversation = (id) => {
    navigate(PATHS.chat(id));
  };

  const handleNavigation = (id) => {
    if (id === "chat") {
      navigate(PATHS.newChat);
      return;
    }

    if (id === "drive") {
      onNavigate("settings");
      return;
    }

    if (id === "dashboard") {
      // Dashboard route can be added separately without breaking existing routes.
      onNavigate("chat");
      return;
    }

    onNavigate(id);
  };

  const handleDeleteConversation = async (conversation, event) => {
    event?.stopPropagation?.();
    setMenuFor(null);

    const confirmed = window.confirm(
      `Delete "${conversation.title || "New chat"}" and all its messages? This cannot be undone.`
    );

    if (!confirmed) return;

    try {
      await conversationApi.delete(conversation.id);

      dispatch({
        type: "REMOVE_CONVERSATION",
        payload: conversation.id,
      });

      if (
        Number(activeConversation?.id) === Number(conversation.id)
      ) {
        navigate(PATHS.newChat, { replace: true });
      }

      addToast("Conversation deleted.", "success");
    } catch (error) {
      addToast(error?.message || "Could not delete conversation.", "error");
    }
  };

  const avatar = (
    user?.display_name ||
    user?.username ||
    user?.email ||
    "A"
  )
    .charAt(0)
    .toUpperCase();

  const activeClass =
    "bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-lg shadow-blue-950/20";

  const inactiveClass =
    "text-slate-300 hover:bg-white/5 hover:text-white";

  if (collapsed) {
    return (
      <aside className="flex h-full w-[76px] flex-col items-center gap-4 border-r border-white/5 bg-[#111b30] py-4">
        <img
          src="/icons/documind-ai.png"
          alt="DocuMind AI"
          className="h-10 w-10 rounded-xl object-contain"
        />

        <button
          type="button"
          onClick={onToggleCollapse}
          title="Expand sidebar"
          className="flex h-9 w-9 items-center justify-center rounded-lg text-slate-400 hover:bg-white/10 hover:text-white"
        >
          <ChevronsRight className="h-4 w-4" />
        </button>

        <button
          type="button"
          onClick={handleNewChat}
          title="New chat"
          className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-600 text-white hover:bg-blue-500"
        >
          <PenSquare className="h-4 w-4" />
        </button>

        <nav className="flex flex-col items-center gap-2">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            const selected =
              item.id === activeView ||
              (item.id === "chat" && activeView === "chat");

            return (
              <button
                key={item.id}
                type="button"
                title={item.label}
                onClick={() => handleNavigation(item.id)}
                className={`flex h-10 w-10 items-center justify-center rounded-xl ${
                  selected ? activeClass : inactiveClass
                }`}
              >
                <Icon className="h-4 w-4" />
              </button>
            );
          })}
        </nav>

        <div className="mt-auto flex flex-col items-center gap-2">
          <div className="flex h-9 w-9 items-center justify-center rounded-full bg-gradient-to-br from-blue-500 to-indigo-500 text-sm font-bold text-white">
            {avatar}
          </div>

          <button
            type="button"
            onClick={logout}
            title="Log out"
            className="flex h-9 w-9 items-center justify-center rounded-lg text-slate-400 hover:bg-red-500/10 hover:text-red-400"
          >
            <LogOut className="h-4 w-4" />
          </button>
        </div>
      </aside>
    );
  }

  return (
    <>
      <aside className="flex h-full w-full flex-col border-r border-white/5 bg-[#111b30] p-4 text-white lg:w-[300px]">
        {/* Brand */}
        <div className="mb-7 flex items-center justify-between gap-2">
          <div className="flex min-w-0 items-center gap-3">
            <img
              src="/icons/documind-ai.png"
              alt="DocuMind AI"
              className="h-11 w-11 shrink-0 rounded-xl object-contain"
            />

            <div className="min-w-0">
              <h1 className="truncate text-lg font-bold tracking-tight">
                DocuMind AI
              </h1>
              <p className="truncate text-xs text-slate-400">
                Your Documents. Smarter Answers.
              </p>
            </div>
          </div>

          <button
            type="button"
            onClick={onToggleCollapse}
            title="Collapse sidebar"
            className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg text-slate-400 hover:bg-white/10 hover:text-white"
          >
            <ChevronsLeft className="h-4 w-4" />
          </button>
        </div>

        {/* New Chat */}
        <button
          type="button"
          onClick={handleNewChat}
          className="mb-5 flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 px-4 py-3 text-sm font-semibold text-white shadow-lg shadow-blue-950/20 transition hover:from-blue-500 hover:to-indigo-500"
        >
          <PenSquare className="h-4 w-4" />
          New Chat
          <Sparkles className="ml-auto h-4 w-4 opacity-80" />
        </button>

        {/* Navigation */}
        <nav className="space-y-1">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            const selected =
              item.id === activeView ||
              (item.id === "chat" && activeView === "chat");

            return (
              <button
                key={item.id}
                type="button"
                onClick={() => handleNavigation(item.id)}
                className={`flex w-full items-center gap-3 rounded-xl px-3.5 py-3 text-sm font-medium transition ${
                  selected ? activeClass : inactiveClass
                }`}
              >
                <Icon className="h-[18px] w-[18px] shrink-0" />
                <span>{item.label}</span>

                {item.id === "drive" && (
                  <span className="ml-auto h-2 w-2 rounded-full bg-emerald-400" />
                )}
              </button>
            );
          })}
        </nav>

        {/* Recent Chats */}
        <div className="mt-7 flex items-center justify-between px-1">
          <h2 className="text-xs font-bold uppercase tracking-[0.12em] text-slate-400">
            Recent Chats
          </h2>

          <button
            type="button"
            onClick={loadConversations}
            title="Refresh conversations"
            aria-label="Refresh conversations"
            className="rounded-lg p-1.5 text-slate-400 transition hover:bg-white/10 hover:text-white"
          >
            <Clock className="h-3.5 w-3.5" />
          </button>
        </div>

        <div className="mt-3 min-h-0 flex-1 overflow-y-auto pr-1">
          {loadingConversations ? (
            <div className="space-y-2">
              {[0, 1, 2].map((item) => (
                <div
                  key={item}
                  className="h-10 animate-pulse rounded-xl bg-white/5"
                />
              ))}
            </div>
          ) : conversations.length > 0 ? (
            <div className="space-y-1">
              {conversations.map((conversation) => {
                const isActive =
                  Number(activeConversation?.id) ===
                  Number(conversation.id);

                return (
                  <div
                    key={conversation.id}
                    className="group relative"
                  >
                    <button
                      type="button"
                      onClick={() =>
                        handleSelectConversation(conversation.id)
                      }
                      title={conversation.title || "New chat"}
                      className={`flex w-full items-center gap-2.5 rounded-xl px-3 py-2.5 text-left transition ${
                        isActive
                          ? "bg-blue-500/15 text-blue-200"
                          : "text-slate-300 hover:bg-white/5 hover:text-white"
                      }`}
                    >
                      <MessageSquare className="h-4 w-4 shrink-0 text-slate-400" />

                      <span className="min-w-0 flex-1 truncate text-sm">
                        {conversation.title || "New chat"}
                      </span>

                      <span className="shrink-0 text-[11px] text-slate-500 group-hover:hidden">
                        {timeAgo(conversation.updated_at)}
                      </span>
                    </button>

                    <div
                      ref={
                        menuFor === conversation.id ? menuRef : undefined
                      }
                      className="absolute right-1 top-1/2 z-20 -translate-y-1/2 opacity-0 transition group-hover:opacity-100 focus-within:opacity-100"
                    >
                      <button
                        type="button"
                        onClick={(event) => {
                          event.stopPropagation();
                          setMenuFor(
                            menuFor === conversation.id
                              ? null
                              : conversation.id
                          );
                        }}
                        title="Conversation options"
                        aria-label="Conversation options"
                        className="flex h-7 w-7 items-center justify-center rounded-lg text-slate-400 hover:bg-white/10 hover:text-white"
                      >
                        <MoreVertical className="h-4 w-4" />
                      </button>

                      {menuFor === conversation.id && (
                        <div className="absolute right-0 top-full mt-1 w-48 overflow-hidden rounded-xl border border-white/10 bg-[#18243b] py-1 shadow-xl">
                          <button
                            type="button"
                            onClick={(event) =>
                              handleDeleteConversation(conversation, event)
                            }
                            className="flex w-full items-center gap-2.5 px-3.5 py-2.5 text-left text-sm text-red-300 transition hover:bg-red-500/10"
                          >
                            <Trash2 className="h-4 w-4" />
                            Delete conversation
                          </button>
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="rounded-xl border border-dashed border-white/10 px-3 py-5 text-center">
              <MessageCircle className="mx-auto mb-2 h-5 w-5 text-slate-500" />
              <p className="text-sm font-medium text-slate-300">
                No recent chats
              </p>
              <p className="mt-1 text-xs leading-5 text-slate-500">
                Start a new conversation to see it here.
              </p>
            </div>
          )}
        </div>

        {/* Google Drive connection */}
        <div className="mt-3 border-t border-white/10 pt-3">
          <DriveStatusBadge onNavigate={onNavigate} />
        </div>

        {/* Help card */}
        {/* <div className="mt-4 rounded-2xl border border-blue-400/15 bg-gradient-to-br from-blue-500/10 to-indigo-500/10 p-4">
          <div className="mb-3 flex h-9 w-9 items-center justify-center rounded-xl bg-blue-500/15 text-blue-300">
            <BookOpen className="h-4 w-4" />
          </div>

          <h3 className="text-sm font-semibold text-white">
            Need help?
          </h3>

          <p className="mt-1 text-xs leading-5 text-slate-400">
            Learn how to chat with your documents and get better answers.
          </p>

          <button
            type="button"
            onClick={() => setGuideOpen(true)}
            className="mt-3 flex items-center gap-1 text-xs font-semibold text-blue-300 transition hover:text-blue-200"
          >
            View Guide
            <ChevronRight className="h-3.5 w-3.5" />
          </button>

          <button
            type="button"
            onClick={onUploadClick}
            className="mt-3 flex w-full items-center justify-center gap-2 rounded-xl border border-white/10 bg-white/5 px-3 py-2.5 text-xs font-semibold text-slate-200 transition hover:bg-white/10"
          >
            <UploadCloud className="h-4 w-4" />
            Upload a Document
          </button>
        </div> */}

        {/* Account */}
        <div className="mt-4 flex items-center justify-between border-t border-white/10 pt-4">
          <div className="flex min-w-0 items-center gap-3">
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-blue-500 to-indigo-500 text-sm font-bold text-white">
              {avatar}
            </div>

            <div className="min-w-0">
              <p className="truncate text-sm font-semibold text-white">
                {user?.display_name || user?.username || "Account"}
              </p>
              <p className="truncate text-xs text-slate-400">
                {user?.email || ""}
              </p>
            </div>
          </div>

          <button
            type="button"
            onClick={logout}
            title="Log out"
            aria-label="Log out"
            className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl text-slate-400 transition hover:bg-red-500/10 hover:text-red-300"
          >
            <LogOut className="h-4 w-4" />
          </button>
        </div>
      </aside>

      {/* Guide modal */}
      {guideOpen && (
        <div
          className="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 p-4 backdrop-blur-sm"
          onMouseDown={(event) => {
            if (event.target === event.currentTarget) {
              setGuideOpen(false);
            }
          }}
        >
          <div
            role="dialog"
            aria-modal="true"
            aria-labelledby="documind-guide-title"
            className="w-full max-w-md rounded-2xl border border-slate-200 bg-white p-6 text-slate-900 shadow-2xl dark:border-white/10 dark:bg-[#111b30] dark:text-white"
          >
            <div className="mb-4 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-500/15 text-blue-500">
                  <BookOpen className="h-5 w-5" />
                </div>
                <h2
                  id="documind-guide-title"
                  className="text-lg font-bold"
                >
                  Getting started
                </h2>
              </div>

              <button
                type="button"
                onClick={() => setGuideOpen(false)}
                aria-label="Close guide"
                className="rounded-lg p-2 text-slate-500 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-white/10"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            <div className="space-y-4 text-sm leading-6 text-slate-600 dark:text-slate-300">
              <p>
                <strong>1. Upload your documents.</strong> Add PDF or other
                supported files using the Upload a Document button.
              </p>
              <p>
                <strong>2. Ask a question.</strong> Start a new chat and ask
                questions about your documents in natural language.
              </p>
              <p>
                <strong>3. Review your sources.</strong> Check the cited
                document sources to understand where answers came from.
              </p>
              <p>
                <strong>4. Reopen conversations.</strong> Use Recent Chats
                to return to a previous conversation.
              </p>
            </div>

            <button
              type="button"
              onClick={() => {
                setGuideOpen(false);
                onUploadClick();
              }}
              className="mt-6 flex w-full items-center justify-center gap-2 rounded-xl bg-blue-600 px-4 py-3 text-sm font-semibold text-white transition hover:bg-blue-500"
            >
              <UploadCloud className="h-4 w-4" />
              Upload a Document
            </button>
          </div>
        </div>
      )}
    </>
  );
};

export default Sidebar;