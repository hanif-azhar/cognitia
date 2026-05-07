import { useTranslation } from "react-i18next";
import type { Entry } from "@/lib/api";
import { Square } from "@/components/shapes/Shapes";

type Props = {
  entry: Partial<Entry>;
  onChange: (patch: Partial<Entry>) => void;
};

export function StepBelief({ entry, onChange }: Props) {
  const { t } = useTranslation();
  return (
    <div className="space-y-6">
      <div className="flex items-start gap-3">
        <Square size={28} filled />
        <div>
          <h2 className="text-2xl font-serif">{t("belief.title")}</h2>
          <p className="text-zinc-500 mt-1">{t("belief.subtitle")}</p>
        </div>
      </div>

      <div className="card space-y-3">
        <label className="text-sm font-medium">{t("belief.thought")}</label>
        <textarea
          className="input min-h-[140px]"
          value={entry.automatic_thought ?? ""}
          placeholder={t("belief.thoughtPlaceholder")}
          onChange={(e) => onChange({ automatic_thought: e.target.value })}
        />
      </div>

      <div className="card space-y-3">
        <p className="text-xs uppercase tracking-wide text-zinc-500">{t("belief.tags")}</p>
        <div className="flex flex-wrap gap-2">
          <span className="chip">{t("belief.tagAutomatic")}</span>
          <span className="chip">{t("belief.tagIrrational")}</span>
          <span className="chip">{t("belief.tagUnhelpful")}</span>
        </div>
      </div>
    </div>
  );
}
