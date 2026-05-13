import { useTranslation } from "react-i18next";
import { useQuery } from "@tanstack/react-query";
import { Activity, AlertCircle } from "lucide-react";

import { apiClient } from "@/lib/api";
import { useUI } from "@/stores/uiStore";

export default function WeeklyPatternCard() {
  const { t } = useTranslation();
  const { language } = useUI();
  const { data: recap } = useQuery({
    queryKey: ["analytics", "weekly-recap"],
    queryFn: apiClient.weeklyRecap,
  });

  const top = recap?.top_distortions ?? [];
  const maxCount = top.reduce((m, d) => Math.max(m, d.count), 0) || 1;
  const completionPct = Math.round((recap?.completion_rate ?? 0) * 100);

  return (
    <section className="card">
      <div className="flex items-center gap-2 mb-2">
        <Activity size={18} className="text-indigo-500" />
        <h2 className="text-sm font-medium uppercase tracking-wide text-zinc-500">
          {t("weekly.title")}
        </h2>
      </div>
      <p className="text-xs text-zinc-500 mb-3">{t("weekly.subtitle")}</p>

      {!recap || recap.total_entries === 0 ? (
        <p className="text-sm text-zinc-500 italic">{t("weekly.empty")}</p>
      ) : (
        <>
          {recap.alert_distortion && (
            <div className="mb-4 rounded-xl border border-amber-200 bg-amber-50 dark:border-amber-900/50 dark:bg-amber-950/30 p-3 flex gap-2">
              <AlertCircle
                size={16}
                className="text-amber-600 dark:text-amber-400 mt-0.5 shrink-0"
              />
              <p className="text-sm text-amber-900 dark:text-amber-200">
                {t("weekly.alert", {
                  name:
                    language === "id"
                      ? recap.alert_distortion.name_id
                      : recap.alert_distortion.name_en,
                })}
              </p>
            </div>
          )}

          <ul className="space-y-2 mb-4">
            {top.map((d) => {
              const name = language === "id" ? d.name_id : d.name_en;
              const pct = (d.count / maxCount) * 100;
              return (
                <li key={d.distortion_id} className="flex items-center gap-3">
                  <span className="flex-1 text-sm truncate">{name}</span>
                  <div className="w-32 h-2 rounded-full bg-zinc-200 dark:bg-zinc-700 overflow-hidden">
                    <div
                      className="h-full bg-indigo-500"
                      style={{ width: `${pct}%` }}
                    />
                  </div>
                  <span className="chip text-xs min-w-[2.5rem] justify-center">
                    {d.count}
                  </span>
                </li>
              );
            })}
          </ul>

          <div className="grid grid-cols-3 gap-2 text-xs">
            <div className="rounded-lg bg-zinc-50 dark:bg-zinc-800/50 p-2">
              <div className="text-zinc-500">{t("weekly.entriesThisWeek")}</div>
              <div className="font-serif text-lg">{recap.total_entries}</div>
            </div>
            <div className="rounded-lg bg-zinc-50 dark:bg-zinc-800/50 p-2">
              <div className="text-zinc-500">{t("weekly.completionRate")}</div>
              <div className="font-serif text-lg">{completionPct}%</div>
            </div>
            <div className="rounded-lg bg-zinc-50 dark:bg-zinc-800/50 p-2">
              <div className="text-zinc-500">{t("weekly.dominantEmotion")}</div>
              <div className="font-serif text-lg truncate">
                {recap.dominant_emotion
                  ? language === "id"
                    ? recap.dominant_emotion.name_id
                    : recap.dominant_emotion.name_en
                  : "—"}
              </div>
            </div>
          </div>
        </>
      )}
    </section>
  );
}
