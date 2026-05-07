import { useEffect, useMemo, useRef, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ArrowLeft, ArrowRight, Check, Loader2, Save } from "lucide-react";

import { apiClient, type Entry, type EntryPayload } from "@/lib/api";
import { useUI } from "@/stores/uiStore";
import { todayISO } from "@/lib/utils";
import { EntryStepper, type StepKey } from "@/components/entry/EntryStepper";
import { StepConsequences } from "@/components/entry/StepConsequences";
import { StepActivating } from "@/components/entry/StepActivating";
import { StepBelief } from "@/components/entry/StepBelief";
import { StepDistortions } from "@/components/entry/StepDistortions";
import { StepTesting } from "@/components/entry/StepTesting";
import { Circle, Square, Triangle } from "@/components/shapes/Shapes";

const ORDER: StepKey[] = ["consequences", "activating", "belief", "distortions", "testing", "summary"];

export default function NewEntry() {
  const { id: routeId } = useParams();
  const navigate = useNavigate();
  const { t } = useTranslation();
  const { language } = useUI();
  const queryClient = useQueryClient();

  const [step, setStep] = useState<StepKey>("consequences");
  const [entryId, setEntryId] = useState<string | null>(routeId ?? null);
  const [draft, setDraft] = useState<Partial<Entry>>({
    entry_date: todayISO(),
    emotion_intensity: 0,
    emotion_ids: [],
    distortion_ids: [],
    language,
  });
  const dirtyRef = useRef(false);
  const [saveError, setSaveError] = useState<string | null>(null);

  const { data: distortions = [] } = useQuery({
    queryKey: ["distortions"],
    queryFn: apiClient.listDistortions,
  });
  const { data: emotions = [] } = useQuery({
    queryKey: ["emotions"],
    queryFn: apiClient.listEmotions,
  });

  const { data: existing } = useQuery({
    queryKey: ["entry", routeId],
    queryFn: () => apiClient.getEntry(routeId!),
    enabled: !!routeId,
  });

  useEffect(() => {
    if (existing) {
      setDraft(existing);
      setEntryId(existing.id);
    }
  }, [existing]);

  const createMut = useMutation({
    mutationFn: (data: EntryPayload) => apiClient.createEntry(data),
    onSuccess: (e) => {
      setEntryId(e.id);
      queryClient.invalidateQueries({ queryKey: ["entries"] });
    },
  });
  const updateMut = useMutation({
    mutationFn: (data: EntryPayload) => apiClient.updateEntry(entryId!, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["entries"] });
      queryClient.invalidateQueries({ queryKey: ["entry", entryId] });
    },
  });
  const completeMut = useMutation({
    mutationFn: () => apiClient.completeEntry(entryId!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["entries"] });
      queryClient.invalidateQueries({ queryKey: ["analytics"] });
    },
  });

  function patch(p: Partial<Entry>) {
    setDraft((d) => ({ ...d, ...p }));
    dirtyRef.current = true;
  }

  async function save(): Promise<string | null> {
    if (!dirtyRef.current && entryId) return entryId;
    const payload: EntryPayload = {
      entry_date: draft.entry_date,
      situation: draft.situation,
      location: draft.location,
      people_involved: draft.people_involved,
      automatic_thought: draft.automatic_thought,
      emotion_intensity: draft.emotion_intensity,
      behavior: draft.behavior,
      evidence_for: draft.evidence_for,
      evidence_against: draft.evidence_against,
      reality_test_response: draft.reality_test_response,
      pragmatic_check_response: draft.pragmatic_check_response,
      alternative_action: draft.alternative_action,
      reframed_thought: draft.reframed_thought,
      distortion_ids: draft.distortion_ids,
      emotion_ids: draft.emotion_ids,
      language: draft.language ?? language,
    };
    if (entryId) {
      await updateMut.mutateAsync(payload);
      dirtyRef.current = false;
      return entryId;
    }
    const created = await createMut.mutateAsync(payload);
    dirtyRef.current = false;
    return created.id;
  }

  async function next() {
    await save();
    const i = ORDER.indexOf(step);
    if (i < ORDER.length - 1) setStep(ORDER[i + 1]);
  }

  function back() {
    const i = ORDER.indexOf(step);
    if (i > 0) setStep(ORDER[i - 1]);
  }

  async function saveAndExit() {
    await save();
    navigate("/entries");
  }

  async function saveAndComplete() {
    const id = await save();
    if (id) await completeMut.mutateAsync();
    navigate(id ? `/entries/${id}` : "/entries");
  }

  const isSummary = step === "summary";
  const isLastInputStep = step === "testing";

  const distortionLookup = useMemo(
    () => new Map(distortions.map((d) => [d.id, d])),
    [distortions],
  );
  const emotionLookup = useMemo(
    () => new Map(emotions.map((e) => [e.id, e])),
    [emotions],
  );

  return (
    <div>
      <EntryStepper current={isSummary ? "testing" : step} />

      {step === "consequences" && (
        <StepConsequences entry={draft} emotions={emotions} onChange={patch} />
      )}
      {step === "activating" && <StepActivating entry={draft} onChange={patch} />}
      {step === "belief" && <StepBelief entry={draft} onChange={patch} />}
      {step === "distortions" && (
        <StepDistortions entry={draft} distortions={distortions} onChange={patch} />
      )}
      {step === "testing" && <StepTesting entry={draft} onChange={patch} />}
      {step === "summary" && (
        <SummaryView
          entry={draft}
          distortions={Array.from(distortionLookup.values())}
          emotions={Array.from(emotionLookup.values())}
        />
      )}

      <div className="mt-8 flex flex-wrap items-center gap-3 sticky bottom-0 py-4 bg-canvas/80 dark:bg-zinc-900/80 backdrop-blur border-t border-zinc-200/60 dark:border-zinc-800/60">
        <button type="button" className="btn-ghost" onClick={back} disabled={step === "consequences"}>
          <ArrowLeft size={16} className="mr-1" />
          {t("actions.back")}
        </button>
        <button type="button" className="btn-ghost" onClick={saveAndExit}>
          <Save size={16} className="mr-1" />
          {t("actions.saveAndExit")}
        </button>
        <div className="ml-auto flex items-center gap-2">
          {!isSummary && (
            <button type="button" className="btn-primary" onClick={next}>
              {isLastInputStep ? t("actions.next") : t("actions.next")}
              <ArrowRight size={16} className="ml-1" />
            </button>
          )}
          {isSummary && (
            <>
              <button type="button" className="btn-ghost" onClick={saveAndExit}>
                {t("actions.saveAsDraft")}
              </button>
              <button type="button" className="btn-primary" onClick={saveAndComplete}>
                <Check size={16} className="mr-1" />
                {t("actions.saveAndComplete")}
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

function SummaryView({
  entry,
  distortions,
  emotions,
}: {
  entry: Partial<Entry>;
  distortions: { id: number; name_en: string; name_id: string }[];
  emotions: { id: number; name_en: string; name_id: string }[];
}) {
  const { t } = useTranslation();
  const { language } = useUI();
  const distMap = new Map(distortions.map((d) => [d.id, d]));
  const emoMap = new Map(emotions.map((e) => [e.id, e]));

  const emotionNames = (entry.emotion_ids ?? [])
    .map((id) => emoMap.get(id))
    .filter(Boolean)
    .map((e) => (language === "id" ? e!.name_id : e!.name_en));
  const distortionNames = (entry.distortion_ids ?? [])
    .map((id) => distMap.get(id))
    .filter(Boolean)
    .map((d) => (language === "id" ? d!.name_id : d!.name_en));

  return (
    <div className="space-y-5">
      <div>
        <h2 className="text-2xl font-serif">{t("summary.title")}</h2>
        <p className="text-zinc-500 mt-1">{t("summary.subtitle")}</p>
      </div>

      <div className="card">
        <div className="flex items-center gap-2 mb-2">
          <Circle size={18} filled />
          <span className="text-sm font-medium">{t("stepper.consequences")}</span>
        </div>
        <p className="text-sm">
          {emotionNames.length ? emotionNames.join(", ") : t("summary.noEmotions")}
          {" · "}
          <span className="text-circle font-semibold">{entry.emotion_intensity ?? 0}/10</span>
        </p>
        {entry.behavior && <p className="text-sm mt-2 text-zinc-600 dark:text-zinc-300">{entry.behavior}</p>}
      </div>

      <div className="card">
        <div className="flex items-center gap-2 mb-2">
          <Triangle size={18} filled />
          <span className="text-sm font-medium">{t("stepper.activating")}</span>
        </div>
        <p className="text-sm whitespace-pre-wrap">{entry.situation || "—"}</p>
        {(entry.location || entry.people_involved) && (
          <p className="text-xs text-zinc-500 mt-2">
            {[entry.location, entry.people_involved].filter(Boolean).join(" · ")}
          </p>
        )}
      </div>

      <div className="card">
        <div className="flex items-center gap-2 mb-2">
          <Square size={18} filled />
          <span className="text-sm font-medium">{t("stepper.belief")}</span>
        </div>
        <p className="text-sm whitespace-pre-wrap italic">"{entry.automatic_thought || "—"}"</p>
        {distortionNames.length > 0 && (
          <div className="flex flex-wrap gap-1.5 mt-3">
            {distortionNames.map((n) => (
              <span key={n} className="chip">{n}</span>
            ))}
          </div>
        )}
      </div>

      {entry.reframed_thought && (
        <div className="card border-l-4 border-l-emerald-500">
          <span className="text-sm font-medium text-emerald-700 dark:text-emerald-400">
            {t("testing.reframed")}
          </span>
          <p className="text-base font-serif mt-2 whitespace-pre-wrap">{entry.reframed_thought}</p>
        </div>
      )}
    </div>
  );
}
