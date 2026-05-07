import { useTranslation } from "react-i18next";
import type { Entry } from "@/lib/api";

type Props = {
  entry: Partial<Entry>;
  onChange: (patch: Partial<Entry>) => void;
};

export function StepTesting({ entry, onChange }: Props) {
  const { t } = useTranslation();
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-serif">{t("testing.title")}</h2>
      </div>

      <div className="grid md:grid-cols-2 gap-4">
        <div className="card space-y-2">
          <label className="text-sm font-medium text-emerald-700 dark:text-emerald-400">
            {t("testing.evidenceFor")}
          </label>
          <textarea
            className="input min-h-[140px]"
            value={entry.evidence_for ?? ""}
            placeholder={t("testing.evidencePlaceholder")}
            onChange={(e) => onChange({ evidence_for: e.target.value })}
          />
        </div>
        <div className="card space-y-2">
          <label className="text-sm font-medium text-rose-700 dark:text-rose-400">
            {t("testing.evidenceAgainst")}
          </label>
          <textarea
            className="input min-h-[140px]"
            value={entry.evidence_against ?? ""}
            placeholder={t("testing.evidencePlaceholder")}
            onChange={(e) => onChange({ evidence_against: e.target.value })}
          />
        </div>
      </div>

      <div className="card space-y-2">
        <label className="text-sm font-medium">{t("testing.realityTest")}</label>
        <textarea
          className="input min-h-[100px]"
          value={entry.reality_test_response ?? ""}
          placeholder={t("testing.realityPlaceholder")}
          onChange={(e) => onChange({ reality_test_response: e.target.value })}
        />
      </div>

      <div className="card space-y-2">
        <label className="text-sm font-medium">{t("testing.pragmatic")}</label>
        <textarea
          className="input min-h-[80px]"
          value={entry.pragmatic_check_response ?? ""}
          placeholder={t("testing.pragmaticPlaceholder")}
          onChange={(e) => onChange({ pragmatic_check_response: e.target.value })}
        />
      </div>

      <div className="card space-y-2">
        <label className="text-sm font-medium">{t("testing.alternative")}</label>
        <textarea
          className="input min-h-[80px]"
          value={entry.alternative_action ?? ""}
          placeholder={t("testing.alternativePlaceholder")}
          onChange={(e) => onChange({ alternative_action: e.target.value })}
        />
      </div>

      <div className="card space-y-2 border-l-4 border-l-emerald-500">
        <label className="text-sm font-medium text-emerald-700 dark:text-emerald-400">
          {t("testing.reframed")}
        </label>
        <textarea
          className="input min-h-[120px]"
          value={entry.reframed_thought ?? ""}
          placeholder={t("testing.reframedPlaceholder")}
          onChange={(e) => onChange({ reframed_thought: e.target.value })}
        />
      </div>
    </div>
  );
}
