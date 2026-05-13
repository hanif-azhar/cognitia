import { useTranslation } from "react-i18next";
import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { BookOpen, RefreshCw } from "lucide-react";

import { apiClient } from "@/lib/api";
import { useUI } from "@/stores/uiStore";
import { formatDate } from "@/lib/utils";

export default function ReframeLibraryCard() {
  const { t } = useTranslation();
  const { language } = useUI();
  const { data: item, refetch } = useQuery({
    queryKey: ["reframes", "random"],
    queryFn: apiClient.randomReframe,
  });

  return (
    <section className="card border-l-4 border-l-emerald-500">
      <div className="flex items-center gap-2 mb-2">
        <BookOpen size={18} className="text-emerald-600" />
        <h2 className="text-sm font-medium uppercase tracking-wide text-zinc-500">
          {t("library.dashboardTitle")}
        </h2>
        <div className="ml-auto flex gap-2">
          {item && (
            <button
              type="button"
              className="btn-ghost px-2 py-1"
              onClick={() => refetch()}
              aria-label={t("library.shuffle")}
              title={t("library.shuffle")}
            >
              <RefreshCw size={14} />
            </button>
          )}
          <Link to="/reframes" className="btn-ghost px-2 py-1 text-sm">
            {t("nav.library")} →
          </Link>
        </div>
      </div>
      {item ? (
        <>
          <p className="font-serif text-lg whitespace-pre-wrap text-emerald-800 dark:text-emerald-300">
            {item.reframed_thought}
          </p>
          {item.automatic_thought && (
            <p className="text-xs text-zinc-500 italic mt-2 line-clamp-1">
              ↑ {item.automatic_thought}
            </p>
          )}
          <p className="text-xs text-zinc-500 mt-1">
            <Link to={`/entries/${item.entry_id}`} className="hover:underline">
              {formatDate(item.entry_date, language)}
            </Link>
          </p>
        </>
      ) : (
        <p className="text-sm text-zinc-500">{t("library.empty")}</p>
      )}
    </section>
  );
}
