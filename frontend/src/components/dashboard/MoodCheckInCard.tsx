import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Heart, Edit3, Save } from "lucide-react";

import { apiClient } from "@/lib/api";

export default function MoodCheckInCard() {
  const { t } = useTranslation();
  const qc = useQueryClient();

  const { data: today } = useQuery({
    queryKey: ["mood", "today"],
    queryFn: apiClient.getTodayMood,
  });

  const [editing, setEditing] = useState(false);
  const [score, setScore] = useState(5);
  const [note, setNote] = useState("");

  useEffect(() => {
    if (today) {
      setScore(today.score);
      setNote(today.note ?? "");
    }
  }, [today]);

  const invalidate = () => {
    qc.invalidateQueries({ queryKey: ["mood", "today"] });
    qc.invalidateQueries({ queryKey: ["mood"] });
  };

  const create = useMutation({
    mutationFn: () =>
      apiClient.createMood({ score, note: note.trim() || null }),
    onSuccess: () => {
      setEditing(false);
      invalidate();
    },
  });
  const update = useMutation({
    mutationFn: () =>
      apiClient.updateMood(today!.id, { score, note: note.trim() || null }),
    onSuccess: () => {
      setEditing(false);
      invalidate();
    },
  });

  const showForm = editing || !today;

  return (
    <section className="card">
      <div className="flex items-center gap-2 mb-2">
        <Heart size={18} className="text-rose-500" />
        <h2 className="text-sm font-medium uppercase tracking-wide text-zinc-500">
          {today && !editing ? t("mood.savedToday") : t("mood.title")}
        </h2>
        {today && !editing && (
          <button
            type="button"
            className="ml-auto btn-ghost px-2 py-1 text-sm"
            onClick={() => setEditing(true)}
          >
            <Edit3 size={14} className="mr-1" />
            {t("mood.edit")}
          </button>
        )}
      </div>
      {!showForm && today ? (
        <div>
          <div className="flex items-baseline gap-2">
            <span className="text-4xl font-serif">{today.score}</span>
            <span className="text-zinc-500">/ 10</span>
          </div>
          {today.note && (
            <p className="mt-2 text-sm text-zinc-600 dark:text-zinc-300 whitespace-pre-wrap">
              {today.note}
            </p>
          )}
        </div>
      ) : (
        <div className="space-y-3">
          {!today && (
            <p className="text-sm text-zinc-500">{t("mood.subtitle")}</p>
          )}
          <div>
            <div className="flex items-center justify-between mb-1 text-xs text-zinc-500">
              <span>{t("mood.low")}</span>
              <span className="text-base font-serif text-ink dark:text-zinc-200">
                {score}
              </span>
              <span>{t("mood.high")}</span>
            </div>
            <input
              type="range"
              min={1}
              max={10}
              value={score}
              onChange={(e) => setScore(Number(e.target.value))}
              className="w-full accent-rose-500"
              aria-label={t("mood.scoreLabel")}
            />
          </div>
          <input
            type="text"
            className="input"
            placeholder={t("mood.notePlaceholder")}
            value={note}
            onChange={(e) => setNote(e.target.value)}
            maxLength={140}
          />
          <div className="flex gap-2">
            <button
              type="button"
              className="btn-primary"
              disabled={create.isPending || update.isPending}
              onClick={() => (today ? update.mutate() : create.mutate())}
            >
              <Save size={14} className="mr-1" />
              {t("mood.save")}
            </button>
            {today && editing && (
              <button
                type="button"
                className="btn-ghost"
                onClick={() => {
                  setEditing(false);
                  setScore(today.score);
                  setNote(today.note ?? "");
                }}
              >
                {t("actions.cancel")}
              </button>
            )}
          </div>
        </div>
      )}
    </section>
  );
}
