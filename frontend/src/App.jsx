import { useMemo, useState } from "react";
import { Outlet, useLocation } from "react-router-dom";
import Toast from "./components/Common/Toast";
import Sidebar from "./components/Sidebar/Sidebar";
import TopBar from "./components/Sidebar/TopBar";
import UploadModal from "./components/Upload/UploadModal";
import { usePolling } from "./hooks/usePolling";
import { useDriveAutoSync } from "./hooks/useDriveAutoSync";
import { useViewNavigate, viewFromPath } from "./router/paths";

// Authenticated layout: sidebar + top bar around whichever page the URL
// selects (see Root.jsx for the route table and routes/pages.jsx for pages).
const App = () => {
  const [uploadOpen, setUploadOpen] = useState(false);
  const location = useLocation();
  const navigateToView = useViewNavigate();
  useDriveAutoSync();
  usePolling();

  const view = viewFromPath(location.pathname);
  const outletContext = useMemo(
    () => ({ openUpload: () => setUploadOpen(true), navigateToView }),
    [navigateToView]
  );

  return (
    <div className="h-screen overflow-hidden bg-white text-slate-900 dark:bg-brand-bg dark:text-white">
      <div className="flex h-full flex-col lg:flex-row">
        <div className="h-[42vh] min-h-[330px] lg:h-full">
          <Sidebar onUploadClick={() => setUploadOpen(true)} activeView={view} onNavigate={navigateToView} />
        </div>

        <div className="flex min-h-0 flex-1 flex-col">
          <TopBar onNavigate={navigateToView} />

          <div className="min-h-0 flex-1 overflow-y-auto">
            <Outlet context={outletContext} />
          </div>
        </div>
      </div>
      <UploadModal open={uploadOpen} onClose={() => setUploadOpen(false)} />
      <Toast />
    </div>
  );
};

export default App;