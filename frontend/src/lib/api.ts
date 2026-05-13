import axios from "axios";

export const api = axios.create({
  baseURL: "/api/v1",
  headers: { "Content-Type": "application/json" },
});

export type Distortion = {
  id: number;
  code: string;
  name_en: string;
  name_id: string;
  description_en: string;
  description_id: string;
  example_en: string;
  example_id: string;
};

export type Emotion = {
  id: number;
  code: string;
  name_en: string;
  name_id: string;
};

export type Entry = {
  id: string;
  created_at: string;
  updated_at: string;
  entry_date: string;
  situation: string | null;
  location: string | null;
  people_involved: string | null;
  automatic_thought: string | null;
  emotion_intensity: number;
  behavior: string | null;
  evidence_for: string | null;
  evidence_against: string | null;
  reality_test_response: string | null;
  pragmatic_check_response: string | null;
  alternative_action: string | null;
  reframed_thought: string | null;
  is_complete: boolean;
  language: string;
  distortion_ids: number[];
  emotion_ids: number[];
};

export type EntryPayload = Partial<Omit<Entry, "id" | "created_at" | "updated_at" | "is_complete">>;

export type AppSettings = {
  language: "en" | "id";
  daily_reminder_time: string | null;
  theme: "light" | "dark" | "auto";
  has_pin: boolean;
};

export type SettingsUpdate = Partial<{
  language: "en" | "id";
  daily_reminder_time: string | null;
  theme: "light" | "dark" | "auto";
  pin: string;
}>;

export type DistortionFrequency = {
  distortion_id: number;
  code: string;
  name_en: string;
  name_id: string;
  count: number;
};

export type EmotionTrendPoint = {
  bucket: string;
  emotion_id: number;
  code: string;
  name_en: string;
  name_id: string;
  avg_intensity: number;
  count: number;
};

export type StreakInfo = {
  current_streak: number;
  longest_streak: number;
  last_entry_date: string | null;
};

export type AnalyticsSummary = {
  total_entries: number;
  completed_entries: number;
  reframe_rate: number;
  average_intensity: number;
  top_distortions: DistortionFrequency[];
  top_emotions: EmotionTrendPoint[];
  streak: StreakInfo;
};

export type TherapistFeedback = {
  id: string;
  entry_id: string;
  author_name: string;
  note: string;
  created_at: string;
  updated_at: string;
};

export type TherapistFeedbackPayload = {
  author_name: string;
  note: string;
};

export type WinningMoment = {
  id: string;
  text: string;
  tag: string | null;
  moment_date: string;
  created_at: string;
  updated_at: string;
};

export type WinningMomentPayload = Partial<{
  text: string;
  tag: string | null;
  moment_date: string;
}>;

export type WeeklyRecap = {
  period_from: string;
  period_to: string;
  total_entries: number;
  completed_entries: number;
  completion_rate: number;
  top_distortions: DistortionFrequency[];
  dominant_emotion: EmotionTrendPoint | null;
  alert_distortion: DistortionFrequency | null;
};

export type DailyMood = {
  id: string;
  mood_date: string;
  score: number;
  note: string | null;
  created_at: string;
  updated_at: string;
};

export type DailyMoodPayload = {
  score: number;
  note?: string | null;
  mood_date?: string;
};

export type ReframeItem = {
  entry_id: string;
  entry_date: string;
  reframed_thought: string;
  automatic_thought: string | null;
  situation: string | null;
  distortion_ids: number[];
};

export const apiClient = {
  listEntries: async (params: Record<string, string | number | undefined> = {}) =>
    (await api.get<Entry[]>("/entries", { params })).data,
  getEntry: async (id: string) => (await api.get<Entry>(`/entries/${id}`)).data,
  createEntry: async (data: EntryPayload) => (await api.post<Entry>("/entries", data)).data,
  updateEntry: async (id: string, data: EntryPayload) =>
    (await api.patch<Entry>(`/entries/${id}`, data)).data,
  deleteEntry: async (id: string) => (await api.delete(`/entries/${id}`)).data,
  completeEntry: async (id: string) => (await api.post<Entry>(`/entries/${id}/complete`)).data,
  listDistortions: async () => (await api.get<Distortion[]>("/distortions")).data,
  listEmotions: async () => (await api.get<Emotion[]>("/emotions")).data,
  getSettings: async () => (await api.get<AppSettings>("/settings")).data,
  updateSettings: async (data: SettingsUpdate) =>
    (await api.patch<AppSettings>("/settings", data)).data,
  distortionFrequency: async () =>
    (await api.get<DistortionFrequency[]>("/analytics/distortion-frequency")).data,
  emotionTrend: async (granularity: "day" | "week" | "month" = "week") =>
    (await api.get<EmotionTrendPoint[]>("/analytics/emotion-trend", { params: { granularity } })).data,
  streak: async () => (await api.get<StreakInfo>("/analytics/streak")).data,
  summary: async () => (await api.get<AnalyticsSummary>("/analytics/summary")).data,
  entryPdf: async (id: string, lang?: "en" | "id") =>
    (await api.get(`/entries/${id}/pdf`, { params: lang ? { lang } : {}, responseType: "blob" }))
      .data as Blob,
  insightsPdf: async (lang: "en" | "id" = "en") =>
    (await api.get(`/analytics/pdf`, { params: { lang }, responseType: "blob" })).data as Blob,
  listFeedback: async (entryId: string) =>
    (await api.get<TherapistFeedback[]>(`/entries/${entryId}/feedback`)).data,
  createFeedback: async (entryId: string, data: TherapistFeedbackPayload) =>
    (await api.post<TherapistFeedback>(`/entries/${entryId}/feedback`, data)).data,
  updateFeedback: async (id: string, data: Partial<TherapistFeedbackPayload>) =>
    (await api.patch<TherapistFeedback>(`/feedback/${id}`, data)).data,
  deleteFeedback: async (id: string) => (await api.delete(`/feedback/${id}`)).data,
  listWins: async (params: Record<string, string | number | undefined> = {}) =>
    (await api.get<WinningMoment[]>("/wins", { params })).data,
  randomWin: async () =>
    (await api.get<WinningMoment | null>("/wins/random")).data,
  createWin: async (data: WinningMomentPayload) =>
    (await api.post<WinningMoment>("/wins", data)).data,
  updateWin: async (id: string, data: WinningMomentPayload) =>
    (await api.patch<WinningMoment>(`/wins/${id}`, data)).data,
  deleteWin: async (id: string) => (await api.delete(`/wins/${id}`)).data,
  weeklyRecap: async () =>
    (await api.get<WeeklyRecap>("/analytics/weekly-recap")).data,
  getTodayMood: async () =>
    (await api.get<DailyMood | null>("/mood/today")).data,
  listMoods: async (params: Record<string, string | number | undefined> = {}) =>
    (await api.get<DailyMood[]>("/mood", { params })).data,
  createMood: async (data: DailyMoodPayload) =>
    (await api.post<DailyMood>("/mood", data)).data,
  updateMood: async (id: string, data: Partial<DailyMoodPayload>) =>
    (await api.patch<DailyMood>(`/mood/${id}`, data)).data,
  listReframes: async (params: Record<string, string | number | undefined> = {}) =>
    (await api.get<ReframeItem[]>("/reframes", { params })).data,
  randomReframe: async () =>
    (await api.get<ReframeItem | null>("/reframes/random")).data,
  sessionSummaryPdf: async (
    from: string,
    to: string,
    lang: "en" | "id" = "en",
  ) =>
    (
      await api.get(`/analytics/session-summary/pdf`, {
        params: { from, to, lang },
        responseType: "blob",
      })
    ).data as Blob,
};

export function downloadBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
