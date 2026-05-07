import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { apiClient, type SettingsUpdate } from "@/lib/api";
import { useUI } from "@/stores/uiStore";

export default function SettingsPage() {
  const { t, i18n } = useTranslation();
  const { setLanguage, setTheme } = useUI();
  const qc = useQueryClient();
  const { data } = useQuery({ queryKey: ["settings"], queryFn: apiClient.getSettings });

  const [pin, setPin] = useState("");
  const [reminder, setReminder] = useState<string>("");

  useEffect(() => {
    if (data?.daily_reminder_time) setReminder(data.daily_reminder_time.slice(0, 5));
  }, [data?.daily_reminder_time]);

  const update = useMutation({
    mutationFn: (p: SettingsUpdate) => apiClient.updateSettings(p),
    onSuccess: (s) => {
      qc.setQueryData(["settings"], s);
      i18n.changeLanguage(s.language);
      setLanguage(s.language);
      setTheme(s.theme);
    },
  });

  if (!data) return <div className="text-zinc-500">…</div>;

  return (
    <div className="max-w-2xl space-y-6">
      <h1 className="text-3xl font-serif">{t("settings.title")}</h1>

      <div className="card space-y-3">
        <label className="text-sm font-medium">{t("settings.language")}</label>
        <div className="flex gap-2">
          {(["en", "id"] as const).map((l) => (
            <button
              key={l}
              type="button"
              className={`btn ${data.language === l ? "btn-primary" : "btn-ghost"}`}
              onClick={() => update.mutate({ language: l })}
            >
              {l === "en" ? "English" : "Bahasa Indonesia"}
            </button>
          ))}
        </div>
      </div>

      <div className="card space-y-3">
        <label className="text-sm font-medium">{t("settings.theme")}</label>
        <div className="flex gap-2">
          {(["light", "dark", "auto"] as const).map((th) => (
            <button
              key={th}
              type="button"
              className={`btn ${data.theme === th ? "btn-primary" : "btn-ghost"}`}
              onClick={() => update.mutate({ theme: th })}
            >
              {t(`settings.theme${th[0].toUpperCase()}${th.slice(1)}` as const)}
            </button>
          ))}
        </div>
      </div>

      <div className="card space-y-3">
        <label className="text-sm font-medium">{t("settings.reminder")}</label>
        <p className="text-xs text-zinc-500">{t("settings.reminderHelp")}</p>
        <div className="flex gap-2 items-center">
          <input
            type="time"
            value={reminder}
            onChange={(e) => setReminder(e.target.value)}
            className="input max-w-[140px]"
          />
          <button
            type="button"
            className="btn-primary"
            onClick={() => update.mutate({ daily_reminder_time: reminder ? `${reminder}:00` : null })}
          >
            {t("actions.save")}
          </button>
        </div>
      </div>

      <div className="card space-y-3">
        <label className="text-sm font-medium">{t("settings.pin")}</label>
        <p className="text-xs text-zinc-500">{t("settings.pinHelp")}</p>
        <div className="flex items-center gap-2">
          <span className="chip">{data.has_pin ? t("settings.pinSet") : t("settings.pinNone")}</span>
        </div>
        <div className="flex gap-2 items-center">
          <input
            type="password"
            value={pin}
            onChange={(e) => setPin(e.target.value)}
            placeholder="••••"
            className="input max-w-[160px]"
          />
          <button
            type="button"
            className="btn-primary"
            onClick={() => {
              update.mutate({ pin });
              setPin("");
            }}
          >
            {t("actions.save")}
          </button>
          {data.has_pin && (
            <button
              type="button"
              className="btn-ghost text-red-600"
              onClick={() => update.mutate({ pin: "" })}
            >
              {t("actions.delete")}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
