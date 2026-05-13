import { useTranslation } from "react-i18next";
import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { Plus, Flame, BookOpen, CheckCircle2, Sparkles, RefreshCw } from "lucide-react";

import { apiClient } from "@/lib/api";
import { useUI } from "@/stores/uiStore";
import { formatDate } from "@/lib/utils";
import { Circle, Square, Triangle } from "@/components/shapes/Shapes";

export default function Dashboard() {
  const { t } = useTranslation();
  const { language } = useUI();
  const { data: summary } = useQuery({
    queryKey: ["analytics", "summary"],
    queryFn: apiClient.summary,
  });
  const { data: entries = [] } = useQuery({
    queryKey: ["entries", { limit: 5 }],
    queryFn: () => apiClient.listEntries({ limit: 5 }),
  });
  const { data: cherishWin, refetch: refetchCherish } = useQuery({
    queryKey: ["wins", "random"],
    queryFn: apiClient.randomWin,
  });

  return (
    <div className="space-y-8">
      <section>
        <h1 className="text-3xl md:text-4xl font-serif italic">{t("dashboard.greeting")}</h1>
        <p className="text-zinc-500 mt-2">{t("dashboard.subtitle")}</p>
        <Link to="/new" className="btn-primary mt-5">
          <Plus size={16} className="mr-1" />
          {t("dashboard.newEntry")}
        </Link>
      </section>

      <section className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <StatCard
          icon={<Flame size={18} className="text-orange-500" />}
          label={t("dashboard.streakCurrent")}
          value={`${summary?.streak.current_streak ?? 0} ${t("dashboard.days")}`}
        />
        <StatCard
          icon={<Flame size={18} className="text-amber-500" />}
          label={t("dashboard.streakLongest")}
          value={`${summary?.streak.longest_streak ?? 0} ${t("dashboard.days")}`}
        />
        <StatCard
          icon={<BookOpen size={18} className="text-zinc-500" />}
          label={t("dashboard.totalEntries")}
          value={`${summary?.total_entries ?? 0}`}
        />
        <StatCard
          icon={<CheckCircle2 size={18} className="text-emerald-500" />}
          label={t("dashboard.completed")}
          value={`${summary?.completed_entries ?? 0}`}
        />
      </section>

      <section className="card border-l-4 border-l-amber-400">
        <div className="flex items-center gap-2 mb-2">
          <Sparkles size={18} className="text-amber-500" />
          <h2 className="text-sm font-medium uppercase tracking-wide text-zinc-500">
            {t("wins.cherishTitle")}
          </h2>
          <div className="ml-auto flex gap-2">
            {cherishWin && (
              <button
                type="button"
                className="btn-ghost px-2 py-1"
                onClick={() => refetchCherish()}
                aria-label={t("wins.shuffle")}
                title={t("wins.shuffle")}
              >
                <RefreshCw size={14} />
              </button>
            )}
            <Link to="/wins" className="btn-ghost px-2 py-1 text-sm">
              {t("nav.wins")} →
            </Link>
          </div>
        </div>
        {cherishWin ? (
          <>
            <p className="font-serif text-lg whitespace-pre-wrap">{cherishWin.text}</p>
            <p className="text-xs text-zinc-500 mt-2">
              {formatDate(cherishWin.moment_date, language)}
              {cherishWin.tag && <span className="ml-2 chip text-xs">{cherishWin.tag}</span>}
            </p>
          </>
        ) : (
          <p className="text-sm text-zinc-500">
            {t("wins.cherishEmpty")}{" "}
            <Link to="/wins" className="underline">
              {t("wins.logWin")}
            </Link>
          </p>
        )}
      </section>

      <section>
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-xl font-serif">{t("dashboard.recent")}</h2>
          <Link to="/entries" className="text-sm text-zinc-500 hover:text-ink">→</Link>
        </div>
        {entries.length === 0 ? (
          <div className="card text-zinc-500">{t("dashboard.empty")}</div>
        ) : (
          <ul className="space-y-3">
            {entries.map((e) => (
              <li key={e.id}>
                <Link to={`/entries/${e.id}`} className="card block hover:shadow-md transition">
                  <div className="flex items-center gap-2 text-xs text-zinc-500">
                    <Circle size={12} filled />
                    <Triangle size={12} filled />
                    <Square size={12} filled />
                    <span className="ml-2">{formatDate(e.entry_date, language)}</span>
                    {!e.is_complete && (
                      <span className="ml-auto chip text-xs">{t("entries.draft")}</span>
                    )}
                  </div>
                  <p className="mt-2 text-sm line-clamp-2">
                    {e.automatic_thought || e.situation || "—"}
                  </p>
                  {e.reframed_thought && (
                    <p className="mt-2 text-sm font-serif italic text-emerald-700 dark:text-emerald-400 line-clamp-1">
                      → {e.reframed_thought}
                    </p>
                  )}
                </Link>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}

function StatCard({ icon, label, value }: { icon: React.ReactNode; label: string; value: string }) {
  return (
    <div className="card">
      <div className="flex items-center gap-2 text-xs uppercase tracking-wide text-zinc-500">
        {icon}
        <span>{label}</span>
      </div>
      <div className="mt-2 text-2xl font-serif">{value}</div>
    </div>
  );
}
