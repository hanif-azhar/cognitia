import { NavLink, Outlet, useLocation, useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useEffect } from "react";
import { Languages, Moon, Sun, Plus } from "lucide-react";

import { useUI } from "@/stores/uiStore";
import { ShapeTrio } from "@/components/shapes/Shapes";
import { cn } from "@/lib/utils";

export default function Layout() {
  const { t, i18n } = useTranslation();
  const { language, setLanguage, theme, setTheme } = useUI();
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    if (i18n.language !== language) i18n.changeLanguage(language);
  }, [language, i18n]);

  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      const target = e.target as HTMLElement;
      if (target?.tagName === "INPUT" || target?.tagName === "TEXTAREA") return;
      if (e.key === "n" || e.key === "N") {
        e.preventDefault();
        navigate("/new");
      }
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [navigate]);

  const navItems = [
    { to: "/", label: t("nav.dashboard"), end: true },
    { to: "/entries", label: t("nav.entries") },
    { to: "/insights", label: t("nav.insights") },
    { to: "/settings", label: t("nav.settings") },
  ];

  return (
    <div className="min-h-screen flex flex-col">
      <header className="sticky top-0 z-10 backdrop-blur border-b border-zinc-200/70 dark:border-zinc-800/70 bg-canvas/70 dark:bg-zinc-900/70">
        <div className="max-w-5xl mx-auto px-5 py-4 flex items-center gap-4">
          <NavLink to="/" className="flex items-center gap-3 group">
            <ShapeTrio />
            <div className="leading-tight">
              <div className="font-serif text-lg italic">{t("app.name")}</div>
            </div>
          </NavLink>
          <nav className="ml-6 hidden md:flex items-center gap-1 text-sm">
            {navItems.map((n) => (
              <NavLink
                key={n.to}
                to={n.to}
                end={n.end}
                className={({ isActive }) =>
                  cn(
                    "px-3 py-1.5 rounded-lg",
                    isActive
                      ? "bg-zinc-200/70 dark:bg-zinc-800 text-ink dark:text-white"
                      : "text-zinc-600 dark:text-zinc-400 hover:bg-zinc-100 dark:hover:bg-zinc-800/50",
                  )
                }
              >
                {n.label}
              </NavLink>
            ))}
          </nav>
          <div className="ml-auto flex items-center gap-2">
            <button
              type="button"
              className="btn-ghost"
              onClick={() => setLanguage(language === "en" ? "id" : "en")}
              title={t("settings.language")}
            >
              <Languages size={16} />
              <span className="ml-1.5 text-xs uppercase tracking-wide">{language}</span>
            </button>
            <button
              type="button"
              className="btn-ghost"
              onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
              title={t("settings.theme")}
            >
              {theme === "dark" ? <Sun size={16} /> : <Moon size={16} />}
            </button>
            <NavLink to="/new" className="btn-primary">
              <Plus size={16} className="mr-1" />
              {t("nav.new")}
            </NavLink>
          </div>
        </div>
        <nav className="md:hidden border-t border-zinc-200/60 dark:border-zinc-800/60 px-3 py-2 flex gap-1 overflow-x-auto text-sm">
          {navItems.map((n) => (
            <NavLink
              key={n.to}
              to={n.to}
              end={n.end}
              className={({ isActive }) =>
                cn(
                  "px-3 py-1.5 rounded-lg whitespace-nowrap",
                  isActive
                    ? "bg-zinc-200/70 dark:bg-zinc-800"
                    : "text-zinc-600 dark:text-zinc-400",
                )
              }
            >
              {n.label}
            </NavLink>
          ))}
        </nav>
      </header>
      <main key={location.pathname} className="flex-1">
        <div className="max-w-5xl mx-auto px-5 py-8">
          <Outlet />
        </div>
      </main>
      <footer className="py-6 text-center text-xs text-zinc-500">
        {t("app.tagline")}
      </footer>
    </div>
  );
}
