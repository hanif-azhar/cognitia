import { useNavigate, useParams, Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Edit3, Trash2, ArrowLeft, FileDown, Loader2 } from "lucide-react";

import { apiClient, downloadBlob } from "@/lib/api";
import { useUI } from "@/stores/uiStore";
import { formatDate } from "@/lib/utils";
import { Circle, Square, Triangle } from "@/components/shapes/Shapes";
import TherapistFeedbackSection from "@/components/entry/TherapistFeedbackSection";

export default function EntryDetail() {
  const { id } = useParams();
  const { t } = useTranslation();
  const { language } = useUI();
  const navigate = useNavigate();
  const qc = useQueryClient();

  const { data: entry } = useQuery({
    queryKey: ["entry", id],
    queryFn: () => apiClient.getEntry(id!),
    enabled: !!id,
  });
  const { data: distortions = [] } = useQuery({
    queryKey: ["distortions"],
    queryFn: apiClient.listDistortions,
  });
  const { data: emotions = [] } = useQuery({
    queryKey: ["emotions"],
    queryFn: apiClient.listEmotions,
  });

  const del = useMutation({
    mutationFn: () => apiClient.deleteEntry(id!),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["entries"] });
      navigate("/entries");
    },
  });
  const exportPdf = useMutation({
    mutationFn: () => apiClient.entryPdf(id!, language),
    onSuccess: (blob) => {
      const date = entry?.entry_date ?? "entry";
      downloadBlob(blob, `cognitia-entry-${date}-${id!.slice(0, 8)}.pdf`);
    },
  });

  if (!entry) return <div className="text-zinc-500">…</div>;

  const distMap = new Map(distortions.map((d) => [d.id, d]));
  const emoMap = new Map(emotions.map((e) => [e.id, e]));
  const distNames = entry.distortion_ids
    .map((i) => distMap.get(i))
    .filter(Boolean)
    .map((d) => (language === "id" ? d!.name_id : d!.name_en));
  const emoNames = entry.emotion_ids
    .map((i) => emoMap.get(i))
    .filter(Boolean)
    .map((e) => (language === "id" ? e!.name_id : e!.name_en));

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Link to="/entries" className="btn-ghost">
          <ArrowLeft size={16} />
        </Link>
        <div className="text-sm text-zinc-500">{formatDate(entry.entry_date, language)}</div>
        <div className="ml-auto flex gap-2">
          <button
            type="button"
            className="btn-ghost"
            onClick={() => exportPdf.mutate()}
            disabled={exportPdf.isPending}
          >
            {exportPdf.isPending ? (
              <Loader2 size={16} className="mr-1 animate-spin" />
            ) : (
              <FileDown size={16} className="mr-1" />
            )}
            {exportPdf.isPending ? t("actions.exporting") : t("actions.downloadPdf")}
          </button>
          <Link to={`/new/${entry.id}`} className="btn-ghost">
            <Edit3 size={16} className="mr-1" />
            {t("actions.edit")}
          </Link>
          <button
            type="button"
            className="btn-ghost text-red-600"
            onClick={() => {
              if (window.confirm(t("entries.deleteConfirm"))) del.mutate();
            }}
          >
            <Trash2 size={16} className="mr-1" />
            {t("actions.delete")}
          </button>
        </div>
      </div>

      <Section icon={<Circle size={18} filled />} title={t("stepper.consequences")}>
        <p className="text-sm">
          {emoNames.length ? emoNames.join(", ") : "—"}
          {" · "}
          <span className="text-circle font-semibold">{entry.emotion_intensity}/10</span>
        </p>
        {entry.behavior && <p className="text-sm mt-2 whitespace-pre-wrap">{entry.behavior}</p>}
      </Section>

      <Section icon={<Triangle size={18} filled />} title={t("stepper.activating")}>
        <p className="text-sm whitespace-pre-wrap">{entry.situation || "—"}</p>
        {(entry.location || entry.people_involved) && (
          <p className="text-xs text-zinc-500 mt-2">
            {[entry.location, entry.people_involved].filter(Boolean).join(" · ")}
          </p>
        )}
      </Section>

      <Section icon={<Square size={18} filled />} title={t("stepper.belief")}>
        <p className="italic whitespace-pre-wrap">"{entry.automatic_thought || "—"}"</p>
        {distNames.length > 0 && (
          <div className="flex flex-wrap gap-1.5 mt-3">
            {distNames.map((n) => (
              <span key={n} className="chip">{n}</span>
            ))}
          </div>
        )}
      </Section>

      {(entry.evidence_for || entry.evidence_against) && (
        <div className="grid md:grid-cols-2 gap-4">
          {entry.evidence_for && (
            <div className="card">
              <p className="text-xs uppercase tracking-wide text-emerald-700 dark:text-emerald-400 mb-2">
                {t("testing.evidenceFor")}
              </p>
              <p className="text-sm whitespace-pre-wrap">{entry.evidence_for}</p>
            </div>
          )}
          {entry.evidence_against && (
            <div className="card">
              <p className="text-xs uppercase tracking-wide text-rose-700 dark:text-rose-400 mb-2">
                {t("testing.evidenceAgainst")}
              </p>
              <p className="text-sm whitespace-pre-wrap">{entry.evidence_against}</p>
            </div>
          )}
        </div>
      )}

      {entry.reality_test_response && (
        <Section title={t("testing.realityTest")}>
          <p className="text-sm whitespace-pre-wrap">{entry.reality_test_response}</p>
        </Section>
      )}
      {entry.pragmatic_check_response && (
        <Section title={t("testing.pragmatic")}>
          <p className="text-sm whitespace-pre-wrap">{entry.pragmatic_check_response}</p>
        </Section>
      )}
      {entry.alternative_action && (
        <Section title={t("testing.alternative")}>
          <p className="text-sm whitespace-pre-wrap">{entry.alternative_action}</p>
        </Section>
      )}

      {entry.reframed_thought && (
        <div className="card border-l-4 border-l-emerald-500">
          <p className="text-xs uppercase tracking-wide text-emerald-700 dark:text-emerald-400 mb-2">
            {t("testing.reframed")}
          </p>
          <p className="font-serif text-lg whitespace-pre-wrap">{entry.reframed_thought}</p>
        </div>
      )}

      <TherapistFeedbackSection entryId={entry.id} />
    </div>
  );
}

function Section({ icon, title, children }: { icon?: React.ReactNode; title: string; children: React.ReactNode }) {
  return (
    <div className="card">
      <div className="flex items-center gap-2 mb-2">
        {icon}
        <h3 className="text-sm font-medium uppercase tracking-wide text-zinc-500">{title}</h3>
      </div>
      <div>{children}</div>
    </div>
  );
}
