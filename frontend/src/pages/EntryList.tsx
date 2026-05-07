import { useState } from "react";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useQuery } from "@tanstack/react-query";
import { Search } from "lucide-react";

import { apiClient } from "@/lib/api";
import { useUI } from "@/stores/uiStore";
import { formatDate } from "@/lib/utils";
import { Circle, Square, Triangle } from "@/components/shapes/Shapes";

export default function EntryList() {
  const { t } = useTranslation();
  const { language } = useUI();
  const [search, setSearch] = useState("");
  const [distortion, setDistortion] = useState<number | "">("");
  const [emotion, setEmotion] = useState<number | "">("");

  const { data: distortions = [] } = useQuery({
    queryKey: ["distortions"],
    queryFn: apiClient.listDistortions,
  });
  const { data: emotions = [] } = useQuery({
    queryKey: ["emotions"],
    queryFn: apiClient.listEmotions,
  });

  const params: Record<string, string | number | undefined> = {};
  if (search.trim()) params.search = search.trim();
  if (distortion !== "") params.distortion = distortion;
  if (emotion !== "") params.emotion = emotion;

  const { data: entries = [] } = useQuery({
    queryKey: ["entries", params],
    queryFn: () => apiClient.listEntries(params),
  });

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-serif">{t("entries.title")}</h1>

      <div className="card grid md:grid-cols-3 gap-3">
        <div className="relative md:col-span-1">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-zinc-400" />
          <input
            type="text"
            placeholder={t("entries.search")}
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="input pl-9"
          />
        </div>
        <select
          className="input"
          value={distortion}
          onChange={(e) => setDistortion(e.target.value ? Number(e.target.value) : "")}
        >
          <option value="">{t("entries.filterDistortion")} — {t("entries.all")}</option>
          {distortions.map((d) => (
            <option key={d.id} value={d.id}>
              {language === "id" ? d.name_id : d.name_en}
            </option>
          ))}
        </select>
        <select
          className="input"
          value={emotion}
          onChange={(e) => setEmotion(e.target.value ? Number(e.target.value) : "")}
        >
          <option value="">{t("entries.filterEmotion")} — {t("entries.all")}</option>
          {emotions.map((em) => (
            <option key={em.id} value={em.id}>
              {language === "id" ? em.name_id : em.name_en}
            </option>
          ))}
        </select>
      </div>

      {entries.length === 0 ? (
        <div className="card text-zinc-500">{t("entries.empty")}</div>
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
                  <span className="ml-auto chip">
                    {e.is_complete ? t("entries.complete") : t("entries.draft")}
                  </span>
                </div>
                <p className="mt-2 line-clamp-2 text-sm">
                  {e.automatic_thought || e.situation || "—"}
                </p>
                {e.reframed_thought && (
                  <p className="mt-1 text-sm italic text-emerald-700 dark:text-emerald-400 line-clamp-1">
                    → {e.reframed_thought}
                  </p>
                )}
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
