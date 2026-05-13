from datetime import date

from pydantic import BaseModel


class DistortionFrequency(BaseModel):
    distortion_id: int
    code: str
    name_en: str
    name_id: str
    count: int


class EmotionTrendPoint(BaseModel):
    bucket: date
    emotion_id: int
    code: str
    name_en: str
    name_id: str
    avg_intensity: float
    count: int


class StreakInfo(BaseModel):
    current_streak: int
    longest_streak: int
    last_entry_date: date | None


class AnalyticsSummary(BaseModel):
    total_entries: int
    completed_entries: int
    reframe_rate: float
    average_intensity: float
    top_distortions: list[DistortionFrequency]
    top_emotions: list[EmotionTrendPoint]
    streak: StreakInfo


class WeeklyRecap(BaseModel):
    period_from: date
    period_to: date
    total_entries: int
    completed_entries: int
    completion_rate: float
    top_distortions: list[DistortionFrequency]
    dominant_emotion: EmotionTrendPoint | None
    alert_distortion: DistortionFrequency | None
