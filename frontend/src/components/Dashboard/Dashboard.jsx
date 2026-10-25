
import {
  ArrowDownRight,
  ArrowRight,
  ArrowUpRight,
  Clock3,
  FileText,
  FileUp,
  FolderOpen,
  MessageCircle,
  Search,
  Sparkles,
  CheckCircle2,
  File,
  FileSpreadsheet,
  FileImage,
  FileType,
} from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useAppContext } from "../../context/AppContext";
import { useAuth } from "../../context/AuthContext";
import { PATHS } from "../../router/paths";

const formatDate = (value) => {
  if (!value) return "Recently added";

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "Recently added";

  return date.toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
};

const getFileIcon = (document) => {
  const name = (document?.name || document?.filename || "").toLowerCase();
  const type = (document?.file_type || document?.mime_type || "").toLowerCase();

  if (type.includes("pdf") || name.endsWith(".pdf")) return FileText;
  if (type.includes("spreadsheet") || /\.(xlsx?|csv)$/.test(name)) {
    return FileSpreadsheet;
  }
  if (type.includes("image") || /\.(png|jpe?g|webp)$/.test(name)) {
    return FileImage;
  }
  if (/\.(docx?|txt|md)$/.test(name)) return FileType;

  return File;
};

const fileColors = [
  "bg-red-50 text-red-600 dark:bg-red-500/10 dark:text-red-300",
  "bg-blue-50 text-blue-600 dark:bg-blue-500/10 dark:text-blue-300",
  "bg-emerald-50 text-emerald-600 dark:bg-emerald-500/10 dark:text-emerald-300",
  "bg-violet-50 text-violet-600 dark:bg-violet-500/10 dark:text-violet-300",
];

const StatCard = ({
  title,
  value,
  description,
  icon: Icon,
  iconClass,
  trendIcon: TrendIcon,
}) => (
  <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm shadow-slate-900/[0.02] transition hover:-translate-y-0.5 hover:shadow-md dark:border-white/[0.08] dark:bg-[#171f31] dark:shadow-black/10">
    <div className="flex items-start justify-between gap-3">
      <div>
        <p className="text-sm font-medium text-slate-500 dark:text-slate-400">
          {title}
        </p>
        <p className="mt-3 text-3xl font-bold tracking-tight text-slate-900 dark:text-white">
          {value}
        </p>
      </div>

      <div
        className={`flex h-11 w-11 items-center justify-center rounded-xl ${iconClass}`}
      >
        <Icon className="h-5 w-5" />
      </div>
    </div>

    <div className="mt-4 flex items-center gap-1.5 text-xs text-slate-500 dark:text-slate-400">
      {TrendIcon && (
        <TrendIcon className="h-3.5 w-3.5 text-emerald-600 dark:text-emerald-400" />
      )}
      <span>{description}</span>
    </div>
  </div>
);

const QuickAction = ({ icon: Icon, title, description, onClick, tone }) => (
  <button
    type="button"
    onClick={onClick}
    className="group flex min-h-[116px] items-start gap-4 rounded-2xl border border-slate-200 bg-white p-4 text-left transition hover:border-blue-300 hover:shadow-md hover:shadow-blue-900/[0.04] dark:border-white/[0.08] dark:bg-[#171f31] dark:hover:border-blue-400/40"
  >
    <div
      className={`flex h-11 w-11 shrink-0 items-center justify-center rounded-xl ${tone}`}
    >
      <Icon className="h-5 w-5" />
    </div>

    <div className="min-w-0 flex-1">
      <h3 className="text-sm font-semibold text-slate-900 dark:text-white">
        {title}
      </h3>
      <p className="mt-1.5 text-xs leading-5 text-slate-500 dark:text-slate-400">
        {description}
      </p>
      <span className="mt-2 inline-flex items-center gap-1 text-xs font-semibold text-blue-600 dark:text-blue-400">
        Open <ArrowRight className="h-3.5 w-3.5 transition group-hover:translate-x-1" />
      </span>
    </div>
  </button>
);

const Dashboard = ({ onUploadClick, onNavigate = () => {} }) => {
  const navigate = useNavigate();
  const { documents = [], conversations = [], loadingDocuments } = useAppContext();
  const { user } = useAuth();

  const name =
    user?.display_name?.split(" ")[0] ||
    user?.username?.split(" ")[0] ||
    "there";

  const processedDocuments = documents.filter((doc) => {
    const status = String(doc.status || doc.processing_status || "").toLowerCase();
    return (
      status === "processed" ||
      status === "completed" ||
      status === "success" ||
      status === "ready"
    );
  }).length;

  const recentDocuments = [...documents]
    .sort((a, b) => {
      const dateA = new Date(a.updated_at || a.created_at || 0).getTime();
      const dateB = new Date(b.updated_at || b.created_at || 0).getTime();
      return dateB - dateA;
    })
    .slice(0, 5);

  const openChat = () => navigate(PATHS.newChat);
  const openDocuments = () => onNavigate("documents");
  const openSearch = () => onNavigate("search");

  return (
    <main className="min-h-full bg-slate-50 px-4 py-6 sm:px-6 lg:px-8 dark:bg-[#101522]">
      <div className="mx-auto max-w-[1440px] space-y-7">
        {/* Welcome header */}
        <section className="flex flex-col justify-between gap-5 sm:flex-row sm:items-center">
          <div>
            <div className="mb-2 inline-flex items-center gap-2 rounded-full border border-blue-100 bg-blue-50 px-3 py-1.5 text-xs font-medium text-blue-700 dark:border-blue-400/20 dark:bg-blue-500/10 dark:text-blue-300">
              <Sparkles className="h-3.5 w-3.5" />
              Your intelligent workspace
            </div>

            <h1 className="text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl dark:text-white">
              Welcome back, {name}!
            </h1>

            <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-500 dark:text-slate-400">
              Your documents, insights, and conversations — all in one place.
              What would you like to work on today?
            </p>
          </div>

          <button
            type="button"
            onClick={onUploadClick}
            className="inline-flex h-11 shrink-0 items-center justify-center gap-2 rounded-xl bg-blue-600 px-5 text-sm font-semibold text-white shadow-sm shadow-blue-600/20 transition hover:bg-blue-500"
          >
            <FileUp className="h-4 w-4" />
            Upload Document
          </button>
        </section>

        {/* Overview */}
        <section>
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-base font-bold text-slate-900 dark:text-white">
              Workspace Overview
            </h2>
            <span className="text-xs text-slate-500 dark:text-slate-400">
              Your current workspace
            </span>
          </div>

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
            <StatCard
              title="Total Documents"
              value={loadingDocuments ? "—" : documents.length}
              description="Documents in your workspace"
              icon={FileText}
              iconClass="bg-blue-50 text-blue-600 dark:bg-blue-500/10 dark:text-blue-300"
            />

            <StatCard
              title="Processed Documents"
              value={loadingDocuments ? "—" : processedDocuments}
              description="Ready to use in AI chat"
              icon={CheckCircle2}
              iconClass="bg-emerald-50 text-emerald-600 dark:bg-emerald-500/10 dark:text-emerald-300"
              trendIcon={ArrowUpRight}
            />

            <StatCard
              title="Conversations"
              value={conversations.length}
              description="Saved conversations"
              icon={MessageCircle}
              iconClass="bg-violet-50 text-violet-600 dark:bg-violet-500/10 dark:text-violet-300"
            />

            <StatCard
              title="Google Drive"
              value="Connect"
              description="Manage your Drive connection in Settings"
              icon={FolderOpen}
              iconClass="bg-amber-50 text-amber-600 dark:bg-amber-500/10 dark:text-amber-300"
            />
          </div>
        </section>

        {/* Quick actions */}
        <section>
          <div className="mb-4">
            <h2 className="text-base font-bold text-slate-900 dark:text-white">
              Quick Actions
            </h2>
            <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
              Jump straight into what you need.
            </p>
          </div>

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
            <QuickAction
              icon={MessageCircle}
              title="Ask AI"
              description="Ask questions and get answers from your documents."
              onClick={openChat}
              tone="bg-blue-50 text-blue-600 dark:bg-blue-500/10 dark:text-blue-300"
            />

            <QuickAction
              icon={UploadCloud}
              title="Upload Files"
              description="Add a new document to your workspace."
              onClick={onUploadClick}
              tone="bg-violet-50 text-violet-600 dark:bg-violet-500/10 dark:text-violet-300"
            />

            <QuickAction
              icon={FolderOpen}
              title="Browse Documents"
              description="Find and manage your uploaded files."
              onClick={openDocuments}
              tone="bg-emerald-50 text-emerald-600 dark:bg-emerald-500/10 dark:text-emerald-300"
            />

            <QuickAction
              icon={Search}
              title="Advanced Search"
              description="Search your document collection for useful details."
              onClick={openSearch}
              tone="bg-amber-50 text-amber-600 dark:bg-amber-500/10 dark:text-amber-300"
            />
          </div>
        </section>

        {/* Recent documents */}
        <section className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm shadow-slate-900/[0.02] dark:border-white/[0.08] dark:bg-[#171f31]">
          <div className="flex flex-col justify-between gap-3 border-b border-slate-100 px-5 py-4 sm:flex-row sm:items-center dark:border-white/[0.07]">
            <div>
              <h2 className="text-base font-bold text-slate-900 dark:text-white">
                Recent Documents
              </h2>
              <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
                The latest files in your workspace
              </p>
            </div>

            <button
              type="button"
              onClick={openDocuments}
              className="inline-flex items-center gap-1.5 self-start text-sm font-semibold text-blue-600 hover:text-blue-700 sm:self-auto dark:text-blue-400 dark:hover:text-blue-300"
            >
              View all <ArrowRight className="h-4 w-4" />
            </button>
          </div>

          {loadingDocuments ? (
            <div className="space-y-3 p-5">
              {[1, 2, 3].map((item) => (
                <div
                  key={item}
                  className="h-14 animate-pulse rounded-xl bg-slate-100 dark:bg-white/[0.04]"
                />
              ))}
            </div>
          ) : recentDocuments.length ? (
            <div className="divide-y divide-slate-100 dark:divide-white/[0.06]">
              {recentDocuments.map((doc, index) => {
                const Icon = getFileIcon(doc);
                const title = doc.name || doc.filename || "Untitled document";
                const status = String(
                  doc.status || doc.processing_status || ""
                ).toLowerCase();

                const isReady = [
                  "processed",
                  "completed",
                  "success",
                  "ready",
                ].includes(status);

                return (
                  <button
                    key={doc.id ?? `${title}-${index}`}
                    type="button"
                    onClick={openDocuments}
                    className="flex w-full items-center gap-3 px-5 py-4 text-left transition hover:bg-slate-50 dark:hover:bg-white/[0.025]"
                  >
                    <div
                      className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-xl ${
                        fileColors[index % fileColors.length]
                      }`}
                    >
                      <Icon className="h-5 w-5" />
                    </div>

                    <div className="min-w-0 flex-1">
                      <p className="truncate text-sm font-semibold text-slate-800 dark:text-slate-100">
                        {title}
                      </p>
                      <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
                        {formatDate(doc.updated_at || doc.created_at)}
                      </p>
                    </div>

                    <span
                      className={`hidden items-center gap-1.5 rounded-full px-2.5 py-1 text-[11px] font-medium sm:inline-flex ${
                        isReady
                          ? "bg-emerald-50 text-emerald-700 dark:bg-emerald-500/10 dark:text-emerald-300"
                          : "bg-amber-50 text-amber-700 dark:bg-amber-500/10 dark:text-amber-300"
                      }`}
                    >
                      <span
                        className={`h-1.5 w-1.5 rounded-full ${
                          isReady ? "bg-emerald-500" : "bg-amber-500"
                        }`}
                      />
                      {isReady ? "Ready" : status || "Processing"}
                    </span>

                    <ArrowRight className="h-4 w-4 shrink-0 text-slate-300 dark:text-slate-600" />
                  </button>
                );
              })}
            </div>
          ) : (
            <div className="flex flex-col items-center px-6 py-12 text-center">
              <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-slate-100 text-slate-400 dark:bg-white/[0.05] dark:text-slate-500">
                <FileText className="h-6 w-6" />
              </div>

              <h3 className="mt-4 text-sm font-semibold text-slate-800 dark:text-slate-100">
                Your documents will appear here
              </h3>

              <p className="mt-1 max-w-sm text-xs leading-5 text-slate-500 dark:text-slate-400">
                Upload your first document to start asking questions and
                exploring your files with DocuMind AI.
              </p>

              <button
                type="button"
                onClick={onUploadClick}
                className="mt-4 inline-flex items-center gap-2 rounded-xl bg-blue-600 px-4 py-2.5 text-xs font-semibold text-white transition hover:bg-blue-500"
              >
                <FileUp className="h-4 w-4" />
                Upload your first document
              </button>
            </div>
          )}
        </section>

        {/* Bottom note */}
        <div className="flex items-start gap-3 rounded-xl border border-blue-100 bg-blue-50/70 px-4 py-3.5 dark:border-blue-400/15 dark:bg-blue-500/[0.06]">
          <Sparkles className="mt-0.5 h-4 w-4 shrink-0 text-blue-600 dark:text-blue-300" />
          <p className="text-xs leading-5 text-slate-600 dark:text-slate-300">
            <span className="font-semibold text-slate-800 dark:text-white">
              Tip:
            </span>{" "}
            For better answers, make sure your documents have finished
            processing before asking questions.
          </p>
        </div>
      </div>
    </main>
  );
};

export default Dashboard;
