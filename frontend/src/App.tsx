import { Routes, Route } from "react-router-dom";
import Layout from "@/components/ui/Layout";
import Dashboard from "@/pages/Dashboard";
import NewEntry from "@/pages/NewEntry";
import EntryList from "@/pages/EntryList";
import EntryDetail from "@/pages/EntryDetail";
import Insights from "@/pages/Insights";
import SettingsPage from "@/pages/Settings";
import WinsPage from "@/pages/Wins";
import ReframeLibrary from "@/pages/ReframeLibrary";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Dashboard />} />
        <Route path="new" element={<NewEntry />} />
        <Route path="new/:id" element={<NewEntry />} />
        <Route path="entries" element={<EntryList />} />
        <Route path="entries/:id" element={<EntryDetail />} />
        <Route path="insights" element={<Insights />} />
        <Route path="wins" element={<WinsPage />} />
        <Route path="reframes" element={<ReframeLibrary />} />
        <Route path="settings" element={<SettingsPage />} />
      </Route>
    </Routes>
  );
}
