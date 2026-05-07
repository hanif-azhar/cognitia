import { useTranslation } from "react-i18next";
import type { Distortion, Entry } from "@/lib/api";
import { useUI } from "@/stores/uiStore";
import { cn } from "@/lib/utils";
import { Check } from "lucide-react";

type Props = {
  entry: Partial<Entry>;
  distortions: Distortion[];
  onChange: (patch: Partial<Entry>) => void;
};

export function StepDistortions({ entry, distortions, onChange }: Props) {
  const { t } = useTranslation();
  const { language } = useUI();

  const selected = new Set(entry.distortion_ids ?? []);
  function toggle(id: number) {
    const next = new Set(selected);
    if (next.has(id)) next.delete(id);
    else next.add(id);
    onChange({ distortion_ids: Array.from(next) });
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-serif">{t("distortions.title")}</h2>
        <p className="text-zinc-500 mt-1">{t("distortions.subtitle")}</p>
      </div>

      <div className="grid md:grid-cols-2 gap-3">
        {distortions.map((d) => {
          const on = selected.has(d.id);
          const name = language === "id" ? d.name_id : d.name_en;
          const desc = language === "id" ? d.description_id : d.description_en;
          const ex = language === "id" ? d.example_id : d.example_en;
          return (
            <button
              key={d.id}
              type="button"
              onClick={() => toggle(d.id)}
              className={cn(
                "text-left card transition",
                on
                  ? "border-square ring-2 ring-square/30"
                  : "hover:border-zinc-300 dark:hover:border-zinc-600",
              )}
            >
              <div className="flex items-start justify-between gap-3 mb-2">
                <h3 className="font-serif text-lg">{name}</h3>
                {on && (
                  <span className="text-square">
                    <Check size={18} />
                  </span>
                )}
              </div>
              <p className="text-sm text-zinc-600 dark:text-zinc-300">{desc}</p>
              <p className="text-xs italic text-zinc-500 mt-3">
                <span className="not-italic font-medium">{t("distortions.example")}: </span>
                "{ex}"
              </p>
            </button>
          );
        })}
      </div>
    </div>
  );
}
