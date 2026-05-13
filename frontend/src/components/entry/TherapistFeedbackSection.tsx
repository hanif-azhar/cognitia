import { useState } from "react";
import { useTranslation } from "react-i18next";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Edit3, Trash2, MessageSquare, Save, X } from "lucide-react";

import { apiClient, type TherapistFeedback } from "@/lib/api";
import { useUI } from "@/stores/uiStore";
import { formatDate } from "@/lib/utils";

export default function TherapistFeedbackSection({ entryId }: { entryId: string }) {
  const { t } = useTranslation();
  const { language } = useUI();
  const qc = useQueryClient();

  const { data: items = [] } = useQuery({
    queryKey: ["feedback", entryId],
    queryFn: () => apiClient.listFeedback(entryId),
  });

  const [authorName, setAuthorName] = useState("");
  const [note, setNote] = useState("");

  const create = useMutation({
    mutationFn: () =>
      apiClient.createFeedback(entryId, { author_name: authorName, note }),
    onSuccess: () => {
      setAuthorName("");
      setNote("");
      qc.invalidateQueries({ queryKey: ["feedback", entryId] });
    },
  });
  const del = useMutation({
    mutationFn: (id: string) => apiClient.deleteFeedback(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["feedback", entryId] }),
  });

  const canSave = authorName.trim().length > 0 && note.trim().length > 0;

  return (
    <div className="card">
      <div className="flex items-center gap-2 mb-2">
        <MessageSquare size={18} className="text-zinc-500" />
        <h3 className="text-sm font-medium uppercase tracking-wide text-zinc-500">
          {t("feedback.title")}
        </h3>
      </div>
      <p className="text-xs text-zinc-500 mb-4">{t("feedback.subtitle")}</p>

      {items.length === 0 ? (
        <p className="text-sm text-zinc-500 italic">{t("feedback.empty")}</p>
      ) : (
        <ul className="space-y-3 mb-5">
          {items.map((fb) => (
            <FeedbackItem
              key={fb.id}
              fb={fb}
              language={language}
              onDelete={() => {
                if (window.confirm(t("feedback.deleteConfirm"))) del.mutate(fb.id);
              }}
              onUpdated={() =>
                qc.invalidateQueries({ queryKey: ["feedback", entryId] })
              }
            />
          ))}
        </ul>
      )}

      <div className="border-t border-zinc-200 dark:border-zinc-800 pt-4 space-y-3">
        <p className="text-xs uppercase tracking-wide text-zinc-500">
          {t("feedback.addTitle")}
        </p>
        <input
          type="text"
          className="input"
          placeholder={t("feedback.authorPlaceholder")}
          aria-label={t("feedback.authorName")}
          value={authorName}
          onChange={(e) => setAuthorName(e.target.value)}
        />
        <textarea
          className="input min-h-[100px]"
          placeholder={t("feedback.notePlaceholder")}
          aria-label={t("feedback.note")}
          value={note}
          onChange={(e) => setNote(e.target.value)}
        />
        <button
          type="button"
          className="btn-primary"
          disabled={!canSave || create.isPending}
          onClick={() => create.mutate()}
        >
          <Save size={16} className="mr-1" />
          {t("feedback.save")}
        </button>
      </div>
    </div>
  );
}

function FeedbackItem({
  fb,
  language,
  onDelete,
  onUpdated,
}: {
  fb: TherapistFeedback;
  language: "en" | "id";
  onDelete: () => void;
  onUpdated: () => void;
}) {
  const { t } = useTranslation();
  const [editing, setEditing] = useState(false);
  const [authorName, setAuthorName] = useState(fb.author_name);
  const [note, setNote] = useState(fb.note);

  const update = useMutation({
    mutationFn: () =>
      apiClient.updateFeedback(fb.id, { author_name: authorName, note }),
    onSuccess: () => {
      setEditing(false);
      onUpdated();
    },
  });

  if (editing) {
    return (
      <li className="rounded-lg border border-zinc-200 dark:border-zinc-800 p-3 space-y-2">
        <input
          type="text"
          className="input"
          value={authorName}
          onChange={(e) => setAuthorName(e.target.value)}
        />
        <textarea
          className="input min-h-[80px]"
          value={note}
          onChange={(e) => setNote(e.target.value)}
        />
        <div className="flex gap-2">
          <button
            type="button"
            className="btn-primary"
            disabled={update.isPending}
            onClick={() => update.mutate()}
          >
            <Save size={14} className="mr-1" />
            {t("actions.save")}
          </button>
          <button
            type="button"
            className="btn-ghost"
            onClick={() => {
              setEditing(false);
              setAuthorName(fb.author_name);
              setNote(fb.note);
            }}
          >
            <X size={14} className="mr-1" />
            {t("actions.cancel")}
          </button>
        </div>
      </li>
    );
  }

  return (
    <li className="rounded-lg border border-zinc-200 dark:border-zinc-800 p-3">
      <div className="flex items-center gap-2 text-xs text-zinc-500 mb-1">
        <span className="font-semibold text-ink dark:text-zinc-200">
          {fb.author_name}
        </span>
        <span>·</span>
        <span>{formatDate(fb.created_at.slice(0, 10), language)}</span>
        <div className="ml-auto flex gap-1">
          <button
            type="button"
            className="btn-ghost px-2 py-1"
            onClick={() => setEditing(true)}
            aria-label={t("actions.edit")}
          >
            <Edit3 size={14} />
          </button>
          <button
            type="button"
            className="btn-ghost px-2 py-1 text-red-600"
            onClick={onDelete}
            aria-label={t("actions.delete")}
          >
            <Trash2 size={14} />
          </button>
        </div>
      </div>
      <p className="text-sm whitespace-pre-wrap">{fb.note}</p>
    </li>
  );
}
