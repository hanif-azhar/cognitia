import { useState } from "react";
import { useTranslation } from "react-i18next";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Sparkles, Trash2, Edit3, Save, X, Plus } from "lucide-react";

import { apiClient, type WinningMoment } from "@/lib/api";
import { useUI } from "@/stores/uiStore";
import { formatDate, todayISO } from "@/lib/utils";

export default function WinsPage() {
  const { t } = useTranslation();
  const { language } = useUI();
  const qc = useQueryClient();

  const [text, setText] = useState("");
  const [tag, setTag] = useState("");
  const [momentDate, setMomentDate] = useState(todayISO());

  const { data: wins = [] } = useQuery({
    queryKey: ["wins"],
    queryFn: () => apiClient.listWins({ limit: 200 }),
  });

  const create = useMutation({
    mutationFn: () =>
      apiClient.createWin({
        text,
        tag: tag.trim() ? tag.trim() : null,
        moment_date: momentDate,
      }),
    onSuccess: () => {
      setText("");
      setTag("");
      qc.invalidateQueries({ queryKey: ["wins"] });
      qc.invalidateQueries({ queryKey: ["wins", "random"] });
    },
  });

  const canSave = text.trim().length > 0;

  return (
    <div className="space-y-8">
      <section>
        <h1 className="text-3xl md:text-4xl font-serif italic">
          {t("wins.title")}
        </h1>
        <p className="text-zinc-500 mt-2">{t("wins.subtitle")}</p>
      </section>

      <section className="card space-y-3">
        <div className="flex items-center gap-2">
          <Sparkles size={18} className="text-amber-500" />
          <h2 className="text-sm font-medium uppercase tracking-wide text-zinc-500">
            {t("wins.todayPrompt")}
          </h2>
        </div>
        <textarea
          className="input min-h-[80px]"
          placeholder={t("wins.addPlaceholder")}
          value={text}
          onChange={(e) => setText(e.target.value)}
        />
        <div className="grid sm:grid-cols-2 gap-3">
          <input
            type="text"
            className="input"
            placeholder={t("wins.tagPlaceholder")}
            aria-label={t("wins.tag")}
            value={tag}
            onChange={(e) => setTag(e.target.value)}
          />
          <input
            type="date"
            className="input"
            aria-label={t("wins.date")}
            value={momentDate}
            onChange={(e) => setMomentDate(e.target.value)}
          />
        </div>
        <div>
          <button
            type="button"
            className="btn-primary"
            disabled={!canSave || create.isPending}
            onClick={() => create.mutate()}
          >
            <Plus size={16} className="mr-1" />
            {t("wins.logWin")}
          </button>
        </div>
      </section>

      <section>
        {wins.length === 0 ? (
          <div className="card text-zinc-500">{t("wins.empty")}</div>
        ) : (
          <ul className="space-y-3">
            {wins.map((w) => (
              <WinItem key={w.id} win={w} language={language} />
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}

function WinItem({ win, language }: { win: WinningMoment; language: "en" | "id" }) {
  const { t } = useTranslation();
  const qc = useQueryClient();
  const [editing, setEditing] = useState(false);
  const [text, setText] = useState(win.text);
  const [tag, setTag] = useState(win.tag ?? "");

  const update = useMutation({
    mutationFn: () =>
      apiClient.updateWin(win.id, {
        text,
        tag: tag.trim() ? tag.trim() : null,
      }),
    onSuccess: () => {
      setEditing(false);
      qc.invalidateQueries({ queryKey: ["wins"] });
      qc.invalidateQueries({ queryKey: ["wins", "random"] });
    },
  });
  const del = useMutation({
    mutationFn: () => apiClient.deleteWin(win.id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["wins"] });
      qc.invalidateQueries({ queryKey: ["wins", "random"] });
    },
  });

  if (editing) {
    return (
      <li className="card space-y-3">
        <textarea
          className="input min-h-[80px]"
          value={text}
          onChange={(e) => setText(e.target.value)}
        />
        <input
          type="text"
          className="input"
          placeholder={t("wins.tagPlaceholder")}
          value={tag}
          onChange={(e) => setTag(e.target.value)}
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
              setText(win.text);
              setTag(win.tag ?? "");
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
    <li className="card">
      <div className="flex items-center gap-2 text-xs text-zinc-500">
        <Sparkles size={12} className="text-amber-500" />
        <span>{formatDate(win.moment_date, language)}</span>
        {win.tag && <span className="chip text-xs">{win.tag}</span>}
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
            onClick={() => {
              if (window.confirm(t("wins.deleteConfirm"))) del.mutate();
            }}
            aria-label={t("actions.delete")}
          >
            <Trash2 size={14} />
          </button>
        </div>
      </div>
      <p className="mt-2 text-sm whitespace-pre-wrap">{win.text}</p>
    </li>
  );
}
