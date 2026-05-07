import { useTranslation } from "react-i18next";
import type { Entry } from "@/lib/api";
import { Triangle } from "@/components/shapes/Shapes";

type Props = {
  entry: Partial<Entry>;
  onChange: (patch: Partial<Entry>) => void;
};

export function StepActivating({ entry, onChange }: Props) {
  const { t } = useTranslation();
  return (
    <div className="space-y-6">
      <div className="flex items-start gap-3">
        <Triangle size={28} filled />
        <div>
          <h2 className="text-2xl font-serif">{t("activating.title")}</h2>
          <p className="text-zinc-500 mt-1">{t("activating.subtitle")}</p>
        </div>
      </div>

      <div className="card space-y-3">
        <label className="text-sm font-medium">{t("activating.situation")}</label>
        <textarea
          className="input min-h-[140px]"
          value={entry.situation ?? ""}
          placeholder={t("activating.situationPlaceholder")}
          onChange={(e) => onChange({ situation: e.target.value })}
        />
      </div>

      <div className="grid md:grid-cols-2 gap-4">
        <div className="card space-y-2">
          <label className="text-sm font-medium">{t("activating.location")}</label>
          <input
            type="text"
            className="input"
            value={entry.location ?? ""}
            onChange={(e) => onChange({ location: e.target.value })}
          />
        </div>
        <div className="card space-y-2">
          <label className="text-sm font-medium">{t("activating.people")}</label>
          <input
            type="text"
            className="input"
            value={entry.people_involved ?? ""}
            onChange={(e) => onChange({ people_involved: e.target.value })}
          />
        </div>
      </div>

      <div className="card space-y-2 max-w-xs">
        <label className="text-sm font-medium">{t("activating.date")}</label>
        <input
          type="date"
          className="input"
          value={entry.entry_date ?? ""}
          onChange={(e) => onChange({ entry_date: e.target.value })}
        />
      </div>
    </div>
  );
}
