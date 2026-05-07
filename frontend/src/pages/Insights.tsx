import { useTranslation } from "react-i18next";
import { useMutation, useQuery } from "@tanstack/react-query";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { FileDown, Loader2 } from "lucide-react";

import { apiClient, downloadBlob } from "@/lib/api";
import { useUI } from "@/stores/uiStore";
import { useMemo } from "react";

export default function Insights() {
  const { t } = useTranslation();
  const { language } = useUI();

  const { data: freq = [] } = useQuery({
    queryKey: ["analytics", "freq"],
    queryFn: apiClient.distortionFrequency,
  });
  const { data: trend = [] } = useQuery({
    queryKey: ["analytics", "trend"],
    queryFn: () => apiClient.emotionTrend("week"),
  });
  const { data: summary } = useQuery({
    queryKey: ["analytics", "summary"],
    queryFn: apiClient.summary,
  });
  const { data: entries = [] } = useQuery({
    queryKey: ["entries", { limit: 200 }],
    queryFn: () => apiClient.listEntries({ limit: 200 }),
  });

  const freqData = freq.map((d) => ({
    name: language === "id" ? d.name_id : d.name_en,
    count: d.count,
  }));

  const trendData = useMemo(() => {
    const buckets = new Map<string, Record<string, number | string>>();
    for (const t of trend) {
      const key = t.bucket;
      const row = buckets.get(key) ?? { bucket: key };
      const name = language === "id" ? t.name_id : t.name_en;
      row[name] = Math.round(t.avg_intensity * 10) / 10;
      buckets.set(key, row);
    }
    return Array.from(buckets.values()).sort((a, b) =>
      String(a.bucket).localeCompare(String(b.bucket)),
    );
  }, [trend, language]);

  const emotionKeys = useMemo(() => {
    const set = new Set<string>();
    for (const t of trend) set.add(language === "id" ? t.name_id : t.name_en);
    return Array.from(set);
  }, [trend, language]);

  const heatmap = useMemo(() => buildHeatmap(entries.map((e) => e.entry_date)), [entries]);

  const reframeRate = summary ? Math.round((summary.reframe_rate || 0) * 100) : 0;

  const exportPdf = useMutation({
    mutationFn: () => apiClient.insightsPdf(language),
    onSuccess: (blob) => {
      const today = new Date().toISOString().slice(0, 10);
      downloadBlob(blob, `cognitia-insights-${today}.pdf`);
    },
  });

  return (
    <div className="space-y-6">
      <div className="flex items-start gap-4">
        <div className="flex-1">
          <h1 className="text-3xl font-serif">{t("insights.title")}</h1>
          <p className="text-zinc-500 mt-1">{t("insights.subtitle")}</p>
        </div>
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
      </div>

      <div className="grid md:grid-cols-3 gap-3">
        <div className="card">
          <div className="text-xs uppercase tracking-wide text-zinc-500">{t("insights.reframeRate")}</div>
          <div className="text-3xl font-serif mt-2">{reframeRate}%</div>
          <div className="h-2 mt-2 rounded-full bg-zinc-200 dark:bg-zinc-700 overflow-hidden">
            <div className="h-full bg-emerald-500" style={{ width: `${reframeRate}%` }} />
          </div>
        </div>
        <div className="card">
          <div className="text-xs uppercase tracking-wide text-zinc-500">
            {t("dashboard.streakCurrent")}
          </div>
          <div className="text-3xl font-serif mt-2">
            {summary?.streak.current_streak ?? 0} <span className="text-base text-zinc-500">{t("dashboard.days")}</span>
          </div>
        </div>
        <div className="card">
          <div className="text-xs uppercase tracking-wide text-zinc-500">
            {t("dashboard.streakLongest")}
          </div>
          <div className="text-3xl font-serif mt-2">
            {summary?.streak.longest_streak ?? 0} <span className="text-base text-zinc-500">{t("dashboard.days")}</span>
          </div>
        </div>
      </div>

      <div className="card">
        <h2 className="font-serif text-lg mb-3">{t("insights.distortionFrequency")}</h2>
        {freqData.length === 0 ? (
          <p className="text-zinc-500 text-sm">{t("insights.noData")}</p>
        ) : (
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={freqData} margin={{ left: 4, right: 4 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(0,0,0,0.06)" />
                <XAxis dataKey="name" tick={{ fontSize: 11 }} interval={0} angle={-15} textAnchor="end" height={60} />
                <YAxis allowDecimals={false} tick={{ fontSize: 11 }} />
                <Tooltip />
                <Bar dataKey="count" fill="#3B82F6" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>

      <div className="card">
        <h2 className="font-serif text-lg mb-3">{t("insights.emotionTrend")}</h2>
        {trendData.length === 0 ? (
          <p className="text-zinc-500 text-sm">{t("insights.noData")}</p>
        ) : (
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={trendData} margin={{ left: 4, right: 4 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(0,0,0,0.06)" />
                <XAxis dataKey="bucket" tick={{ fontSize: 11 }} />
                <YAxis domain={[0, 10]} tick={{ fontSize: 11 }} />
                <Tooltip />
                <Legend wrapperStyle={{ fontSize: 11 }} />
                {emotionKeys.map((k, i) => (
                  <Line
                    key={k}
                    type="monotone"
                    dataKey={k}
                    stroke={LINE_COLORS[i % LINE_COLORS.length]}
                    strokeWidth={2}
                    dot={false}
                  />
                ))}
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>

      <div className="card">
        <h2 className="font-serif text-lg mb-3">{t("insights.calendarHeatmap")}</h2>
        <Heatmap data={heatmap} />
      </div>
    </div>
  );
}

const LINE_COLORS = [
  "#EF4444", "#3B82F6", "#A855F7", "#10B981", "#F59E0B", "#06B6D4", "#EC4899", "#84CC16",
];

function buildHeatmap(dates: string[]) {
  const counts = new Map<string, number>();
  for (const d of dates) counts.set(d, (counts.get(d) ?? 0) + 1);
  const today = new Date();
  const days: { date: string; count: number }[] = [];
  for (let i = 89; i >= 0; i--) {
    const d = new Date(today);
    d.setDate(today.getDate() - i);
    const iso = d.toISOString().slice(0, 10);
    days.push({ date: iso, count: counts.get(iso) ?? 0 });
  }
  return days;
}

function Heatmap({ data }: { data: { date: string; count: number }[] }) {
  const max = Math.max(1, ...data.map((d) => d.count));
  const cols: { date: string; count: number }[][] = [];
  for (let i = 0; i < data.length; i += 7) cols.push(data.slice(i, i + 7));
  return (
    <div className="flex gap-1 overflow-x-auto">
      {cols.map((week, ci) => (
        <div key={ci} className="flex flex-col gap-1">
          {week.map((d) => {
            const intensity = d.count === 0 ? 0 : d.count / max;
            return (
              <div
                key={d.date}
                title={`${d.date}: ${d.count}`}
                className="h-3 w-3 rounded-sm"
                style={{
                  backgroundColor:
                    d.count === 0
                      ? "rgba(0,0,0,0.06)"
                      : `rgba(16, 185, 129, ${0.25 + intensity * 0.7})`,
                }}
              />
            );
          })}
        </div>
      ))}
    </div>
  );
}
