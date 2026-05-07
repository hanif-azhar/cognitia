import { useTranslation } from "react-i18next";
import { Circle, Triangle, Square } from "@/components/shapes/Shapes";
import { cn } from "@/lib/utils";

export type StepKey =
  | "consequences"
  | "activating"
  | "belief"
  | "distortions"
  | "testing"
  | "summary";

const STEPS: { key: StepKey; icon: "circle" | "triangle" | "square" | "dot" }[] = [
  { key: "consequences", icon: "circle" },
  { key: "activating", icon: "triangle" },
  { key: "belief", icon: "square" },
  { key: "distortions", icon: "dot" },
  { key: "testing", icon: "dot" },
];

export function EntryStepper({ current }: { current: StepKey }) {
  const { t } = useTranslation();
  const idx = STEPS.findIndex((s) => s.key === current);

  return (
    <div className="flex items-center gap-2 mb-6 overflow-x-auto pb-2">
      {STEPS.map((s, i) => {
        const active = i === idx;
        const done = i < idx;
        const Icon = s.icon === "circle" ? Circle : s.icon === "triangle" ? Triangle : Square;
        return (
          <div key={s.key} className="flex items-center gap-2 shrink-0">
            <div
              className={cn(
                "flex items-center gap-2 rounded-full border px-3 py-1.5 text-xs whitespace-nowrap",
                active
                  ? "border-ink dark:border-zinc-200 bg-ink text-white dark:bg-zinc-100 dark:text-ink"
                  : done
                    ? "border-zinc-300 dark:border-zinc-600 text-zinc-500"
                    : "border-zinc-200 dark:border-zinc-700 text-zinc-400",
              )}
            >
              {s.icon !== "dot" ? (
                <Icon size={14} filled={active || done} className={active ? "text-white dark:text-ink" : ""} />
              ) : (
                <span
                  className={cn(
                    "h-2 w-2 rounded-full",
                    active ? "bg-white dark:bg-ink" : done ? "bg-zinc-400" : "bg-zinc-300",
                  )}
                />
              )}
              <span className="font-medium">
                {t(`stepper.${s.key}` as const)}
              </span>
            </div>
            {i < STEPS.length - 1 && <span className="text-zinc-300">·</span>}
          </div>
        );
      })}
    </div>
  );
}
