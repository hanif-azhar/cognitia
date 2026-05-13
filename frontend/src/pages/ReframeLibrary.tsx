import { useState } from "react";
import { useTranslation } from "react-i18next";
import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { BookOpen, RefreshCw, ArrowRight } from "lucide-react";

import { apiClient, type Distortion } from "@/lib/api";
import { useUI } from "@/stores/uiStore";
import { formatDate } from "@/lib/utils";

export default function ReframeLibrary() {
  const { t } = useTranslation();
  const { language } = useUI();
  const [shuffleKey, setShuffleKey] = useState(0);

  const { data: items = [] } = useQuery({
    queryKey: ["reframes", "list"],
    queryFn: () => apiClient.listReframes({ limit: 200 }),
  });
  const { data: distortions = [] } = useQuery({
    queryKey: ["distortions"],
    queryFn: apiClient.listDistortions,
  });
  const { data: random, refetch } = useQuery({
    queryKey: ["reframes", "random", shuffleKey],
    queryFn: apiClient.randomReframe,
    enabled: items.length > 0,
  });

  const distMap = new Map<number, Distortion>(distortions.map((d) => [d.id, d]));

  return (
    <div className="space-y-6">
      <section>
        <h1 className="text-3xl md:text-4xl font-serif italic">
          {t("library.title")}
        </h1>
        <p className="text-zinc-500 mt-2">{t("library.subtitle")}</p>
      </section>

      {items.length === 0 ? (
        <div className="card text-zinc-500">{t("library.empty")}</div>
      ) : (
        <>
          {random && (
            <section className="card border-l-4 border-l-emerald-500">
              <div className="flex items-center gap-2 mb-2">
                <BookOpen size={18} className="text-emerald-600" />
                <h2 className="text-sm font-medium uppercase tracking-wide text-zinc-500">
                  {t("library.dashboardTitle")}
                </h2>
                <button
                  type="button"
                  className="ml-auto btn-ghost px-2 py-1"
                  onClick={() => {
                    setShuffleKey((k) => k + 1);
                    refetch();
                  }}
                  aria-label={t("library.shuffle")}
                  title={t("library.shuffle")}
                >
                  <RefreshCw size={14} className="mr-1" />
                  {t("library.shuffle")}
                </button>
              </div>
              <p className="font-serif text-xl whitespace-pre-wrap text-emerald-800 dark:text-emerald-300">
                {random.reframed_thought}
              </p>
              {random.automatic_thought && (
                <p className="text-sm text-zinc-500 italic mt-2">
                  ↑ {random.automatic_thought}
                </p>
              )}
              <p className="text-xs text-zinc-500 mt-2">
                <Link
                  to={`/entries/${random.entry_id}`}
                  className="hover:underline"
                >
                  {formatDate(random.entry_date, language)}
                </Link>
              </p>
            </section>
          )}

          <ul className="space-y-3">
            {items.map((item) => {
              const names = item.distortion_ids
                .map((i) => distMap.get(i))
                .filter((d): d is Distortion => Boolean(d))
                .map((d) => (language === "id" ? d.name_id : d.name_en));
              return (
                <li key={item.entry_id} className="card">
                  <div className="flex items-center gap-2 text-xs text-zinc-500 mb-2">
                    <BookOpen size={12} className="text-emerald-500" />
                    <span>{formatDate(item.entry_date, language)}</span>
                    <Link
                      to={`/entries/${item.entry_id}`}
                      className="ml-auto btn-ghost px-2 py-1 text-xs"
                    >
                      {t("library.openEntry")}
                      <ArrowRight size={12} className="ml-1" />
                    </Link>
                  </div>
                  <p className="font-serif text-lg whitespace-pre-wrap text-emerald-800 dark:text-emerald-300">
                    {item.reframed_thought}
                  </p>
                  {item.automatic_thought && (
                    <p className="text-xs text-zinc-500 italic mt-2">
                      <span className="uppercase tracking-wide not-italic mr-1">
                        {t("library.originalThought")}:
                      </span>
                      "{item.automatic_thought}"
                    </p>
                  )}
                  {names.length > 0 && (
                    <div className="flex flex-wrap gap-1.5 mt-3">
                      {names.map((n) => (
                        <span key={n} className="chip text-xs">
                          {n}
                        </span>
                      ))}
                    </div>
                  )}
                </li>
              );
            })}
          </ul>
        </>
      )}
    </div>
  );
}
