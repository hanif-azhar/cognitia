import { useTranslation } from "react-i18next";
import type { Emotion, Entry } from "@/lib/api";
import { useUI } from "@/stores/uiStore";
import { Circle } from "@/components/shapes/Shapes";
import { cn } from "@/lib/utils";

type Props = {
  entry: Partial<Entry>;
  emotions: Emotion[];
  onChange: (patch: Partial<Entry>) => void;
};

export function StepConsequences({ entry, emotions, onChange }: Props) {
  const { t } = useTranslation();
  const { language } = useUI();

  const selected = new Set(entry.emotion_ids ?? []);
  function toggle(id: number) {
    const next = new Set(selected);
    if (next.has(id)) next.delete(id);
    else next.add(id);
    onChange({ emotion_ids: Array.from(next) });
  }

  return (
    <div className="space-y-6">
      <div className="flex items-start gap-3">
        <Circle size={28} filled />
        <div>
          <h2 className="text-2xl font-serif">{t("consequences.title")}</h2>
          <p className="text-zinc-500 mt-1">{t("consequences.subtitle")}</p>
        </div>
      </div>

      <div className="card space-y-3">
        <label className="text-sm font-medium">{t("consequences.emotions")}</label>
        <div className="flex flex-wrap gap-2">
          {emotions.map((e) => {
            const on = selected.has(e.id);
            return (
              <button
                key={e.id}
                type="button"
                onClick={() => toggle(e.id)}
                className={cn(
                  "rounded-full px-3 py-1.5 text-sm border transition",
                  on
                    ? "bg-circle/10 border-circle text-circle"
                    : "bg-white dark:bg-zinc-800 border-zinc-200 dark:border-zinc-700 text-zinc-600 dark:text-zinc-300 hover:border-zinc-400",
                )}
              >
                {language === "id" ? e.name_id : e.name_en}
              </button>
            );
          })}
        </div>
      </div>

      <div className="card space-y-3">
        <div className="flex items-center justify-between">
          <label className="text-sm font-medium">{t("consequences.intensity")}</label>
          <span className="text-2xl font-serif text-circle">{entry.emotion_intensity ?? 0}</span>
        </div>
        <input
          type="range"
          min={0}
          max={10}
          value={entry.emotion_intensity ?? 0}
          onChange={(e) => onChange({ emotion_intensity: Number(e.target.value) })}
          className="w-full accent-circle"
        />
        <div className="flex justify-between text-xs text-zinc-400">
          <span>0</span><span>5</span><span>10</span>
        </div>
      </div>

      <div className="card space-y-3">
        <label className="text-sm font-medium">{t("consequences.behavior")}</label>
        <textarea
          className="input min-h-[100px]"
          value={entry.behavior ?? ""}
          placeholder={t("consequences.behaviorPlaceholder")}
          onChange={(e) => onChange({ behavior: e.target.value })}
        />
      </div>
    </div>
  );
}
