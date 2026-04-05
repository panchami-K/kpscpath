from pydantic import BaseModel, field_validator, model_validator
from datetime import date
from typing import Optional


VALID_EXAMS = {"KAS", "PSI", "FDA", "SDA", "KES", "other"}
VALID_LANGS = {"kn", "en"}

MONTH_NAMES_EN = {
    1: "January", 2: "February", 3: "March", 4: "April",
    5: "May", 6: "June", 7: "July", 8: "August",
    9: "September", 10: "October", 11: "November", 12: "December"
}
MONTH_NAMES_KN = {
    1: "ಜನವರಿ", 2: "ಫೆಬ್ರವರಿ", 3: "ಮಾರ್ಚ್", 4: "ಏಪ್ರಿಲ್",
    5: "ಮೇ", 6: "ಜೂನ್", 7: "ಜುಲೈ", 8: "ಆಗಸ್ಟ್",
    9: "ಸೆಪ್ಟೆಂಬರ್", 10: "ಅಕ್ಟೋಬರ್", 11: "ನವೆಂಬರ್", 12: "ಡಿಸೆಂಬರ್"
}
STAGE_LABELS_KN = {
    "prelims": "ಪ್ರಿಲಿಮ್ಸ್",
    "mains": "ಮೇನ್ಸ್",
    "interview": "ಸಂದರ್ಶನ",
    "written": "ಲಿಖಿತ ಪರೀಕ್ಷೆ",
}


def _normalize_time(v: str) -> str:
    """
    Accept both '9:00' and '09:00' formats.
    Normalises to 'HH:MM' zero-padded form.
    """
    parts = v.strip().split(":")
    if len(parts) != 2:
        raise ValueError("Time must be H:MM or HH:MM format e.g. 9:00 or 09:00")
    h_str, m_str = parts
    if not h_str.isdigit() or not m_str.isdigit():
        raise ValueError("Time must be H:MM or HH:MM format e.g. 9:00 or 09:00")
    h, m = int(h_str), int(m_str)
    if not (0 <= h <= 23):
        raise ValueError("Hour must be between 0 and 23")
    if not (0 <= m <= 59):
        raise ValueError("Minute must be between 0 and 59")
    return f"{h:02d}:{m:02d}"


class StudySlot(BaseModel):
    """
    One daily study time slot.
    Accepts both '9:00' and '09:00' formats.

    Examples:
      Morning : { "from_time": "06:00", "to_time": "08:00" }
      Flexible: { "from_time": "7:30",  "to_time": "8:30"  }
      Short   : { "from_time": "07:00", "to_time": "07:15" }  ← 15 min is valid
      Night   : { "from_time": "22:00", "to_time": "23:00" }
    """
    from_time: str
    to_time: str

    @field_validator("from_time", "to_time", mode="before")
    @classmethod
    def normalise_time(cls, v: str) -> str:
        return _normalize_time(str(v))

    @model_validator(mode="after")
    def validate_duration(self) -> "StudySlot":
        fh, fm = map(int, self.from_time.split(":"))
        th, tm = map(int, self.to_time.split(":"))
        start = fh * 60 + fm
        end = th * 60 + tm
        if end <= start:
            end += 24 * 60  # overnight slot e.g. 23:00 → 01:00
        duration = end - start
        if duration < 10:
            raise ValueError("Study slot must be at least 10 minutes long")
        if duration > 480:
            raise ValueError("One study slot cannot exceed 8 hours")
        return self

    @property
    def duration_minutes(self) -> int:
        fh, fm = map(int, self.from_time.split(":"))
        th, tm = map(int, self.to_time.split(":"))
        start = fh * 60 + fm
        end = th * 60 + tm
        if end <= start:
            end += 24 * 60
        return end - start

    def display_label(self) -> str:
        """Returns '7:00 AM – 9:00 AM (2hr)'"""
        def fmt(t: str) -> str:
            h, m = map(int, t.split(":"))
            suffix = "AM" if h < 12 else "PM"
            h12 = h % 12 or 12
            return f"{h12}:{m:02d} {suffix}"
        mins = self.duration_minutes
        hrs, rem = divmod(mins, 60)
        dur = (f"{hrs}hr" if rem == 0 else
               f"{hrs}hr {rem}min" if hrs > 0 else
               f"{rem}min")
        return f"{fmt(self.from_time)} – {fmt(self.to_time)} ({dur})"


class OnboardingRequest(BaseModel):
    target_exam: str
    exam_date: date
    study_slots: list[StudySlot]
    preferred_lang: str = "kn"

    @field_validator("target_exam")
    @classmethod
    def validate_exam(cls, v: str) -> str:
        v = v.upper()
        if v not in VALID_EXAMS:
            raise ValueError(f"target_exam must be one of {sorted(VALID_EXAMS)}")
        return v

    @field_validator("exam_date")
    @classmethod
    def validate_exam_date(cls, v: date) -> date:
        if v <= date.today():
            raise ValueError("exam_date must be a future date")
        return v

    @field_validator("study_slots")
    @classmethod
    def validate_slots(cls, v: list) -> list:
        if not v:
            raise ValueError("At least one study slot is required")
        if len(v) > 6:
            raise ValueError("Maximum 6 study slots per day")
        return v

    @field_validator("preferred_lang")
    @classmethod
    def validate_lang(cls, v: str) -> str:
        if v not in VALID_LANGS:
            raise ValueError(f"preferred_lang must be one of {VALID_LANGS}")
        return v

    @property
    def total_daily_mins(self) -> int:
        return sum(s.duration_minutes for s in self.study_slots)


def build_display_label(row: dict) -> tuple[str, str]:
    """Build human-readable labels for an exam date option."""
    exam = row["exam_type"]
    stage = row["stage"]
    stage_kn = STAGE_LABELS_KN.get(stage, stage)
    year = row["exam_year"]
    status_en = "✓ Confirmed" if row["is_confirmed"] else "Predicted"
    status_kn = "✓ ದೃಢ" if row["is_confirmed"] else "ಅಂದಾಜು"

    if row.get("exam_date"):
        d = row["exam_date"]
        label_en = f"{exam} {stage.title()} — {d} ({status_en})"
        label_kn = f"{exam} {stage_kn} — {d} ({status_kn})"
    elif row.get("exam_month"):
        month_en = MONTH_NAMES_EN[int(row["exam_month"])]
        month_kn = MONTH_NAMES_KN[int(row["exam_month"])]
        label_en = f"{exam} {stage.title()} — {month_en} {year} ({status_en})"
        label_kn = f"{exam} {stage_kn} — {month_kn} {year} ({status_kn})"
    else:
        label_en = f"{exam} {stage.title()} — {year} ({status_en})"
        label_kn = f"{exam} {stage_kn} — {year} ({status_kn})"

    return label_en, label_kn