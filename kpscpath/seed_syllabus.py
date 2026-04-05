import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.environ["SUPABASE_URL"]
key = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
supabase = create_client(url, key)

# ─────────────────────────────────────────
# SYLLABUSES
# ─────────────────────────────────────────
syllabuses = [
    {"exam_type": "KAS_PRELIMS", "version": "2024", "name_en": "KAS Preliminary Examination", "name_kn": "ಕೆಎಎಸ್ ಪ್ರಾಥಮಿಕ ಪರೀಕ್ಷೆ",  "is_active": True},
    {"exam_type": "KAS_MAINS",   "version": "2024", "name_en": "KAS Main Examination",        "name_kn": "ಕೆಎಎಸ್ ಮುಖ್ಯ ಪರೀಕ್ಷೆ",    "is_active": True},
    {"exam_type": "FDA",         "version": "2024", "name_en": "First Division Assistant",    "name_kn": "ಪ್ರಥಮ ದರ್ಜೆ ಸಹಾಯಕ",      "is_active": True},
    {"exam_type": "SDA",         "version": "2024", "name_en": "Second Division Assistant",   "name_kn": "ದ್ವಿತೀಯ ದರ್ಜೆ ಸಹಾಯಕ",    "is_active": True},
]

print("Inserting syllabuses...")
syl_res = supabase.table("syllabuses").upsert(syllabuses, on_conflict="exam_type,version").execute()
syl_rows = syl_res.data
print(f"  ✓ {len(syl_rows)} syllabuses")

syl_map = {r["exam_type"]: r["id"] for r in syl_rows}

# ─────────────────────────────────────────
# SUBJECTS
# ─────────────────────────────────────────
subjects_data = [
    # KAS PRELIMS
    {"exam_type": "KAS_PRELIMS", "name_en": "Indian History",          "name_kn": "ಭಾರತೀಯ ಇತಿಹಾಸ",         "sort_order": 1},
    {"exam_type": "KAS_PRELIMS", "name_en": "Karnataka History",       "name_kn": "ಕರ್ನಾಟಕ ಇತಿಹಾಸ",         "sort_order": 2},
    {"exam_type": "KAS_PRELIMS", "name_en": "Indian Polity",           "name_kn": "ಭಾರತೀಯ ರಾಜ್ಯಶಾಸ್ತ್ರ",     "sort_order": 3},
    {"exam_type": "KAS_PRELIMS", "name_en": "Indian Geography",        "name_kn": "ಭಾರತ ಭೂಗೋಳಶಾಸ್ತ್ರ",      "sort_order": 4},
    {"exam_type": "KAS_PRELIMS", "name_en": "Karnataka Geography",     "name_kn": "ಕರ್ನಾಟಕ ಭೂಗೋಳಶಾಸ್ತ್ರ",    "sort_order": 5},
    {"exam_type": "KAS_PRELIMS", "name_en": "Indian Economy",          "name_kn": "ಭಾರತೀಯ ಅರ್ಥಶಾಸ್ತ್ರ",      "sort_order": 6},
    {"exam_type": "KAS_PRELIMS", "name_en": "Karnataka Economy",       "name_kn": "ಕರ್ನಾಟಕ ಅರ್ಥಶಾಸ್ತ್ರ",      "sort_order": 7},
    {"exam_type": "KAS_PRELIMS", "name_en": "General Science",         "name_kn": "ಸಾಮಾನ್ಯ ವಿಜ್ಞಾನ",         "sort_order": 8},
    {"exam_type": "KAS_PRELIMS", "name_en": "Environment & Ecology",   "name_kn": "ಪರಿಸರ ಮತ್ತು ಜೀವಿಶಾಸ್ತ್ರ", "sort_order": 9},
    {"exam_type": "KAS_PRELIMS", "name_en": "Current Affairs",         "name_kn": "ಪ್ರಚಲಿತ ವಿದ್ಯಮಾನಗಳು",     "sort_order": 10},
    {"exam_type": "KAS_PRELIMS", "name_en": "Mental Ability",          "name_kn": "ಮಾನಸಿಕ ಸಾಮರ್ಥ್ಯ",         "sort_order": 11},
    {"exam_type": "KAS_PRELIMS", "name_en": "Kannada Language",        "name_kn": "ಕನ್ನಡ ಭಾಷೆ",             "sort_order": 12},

    # KAS MAINS
    {"exam_type": "KAS_MAINS", "name_en": "General Studies Paper 1",  "name_kn": "ಸಾಮಾನ್ಯ ಅಧ್ಯಯನ ಪತ್ರಿಕೆ 1", "sort_order": 1},
    {"exam_type": "KAS_MAINS", "name_en": "General Studies Paper 2",  "name_kn": "ಸಾಮಾನ್ಯ ಅಧ್ಯಯನ ಪತ್ರಿಕೆ 2", "sort_order": 2},
    {"exam_type": "KAS_MAINS", "name_en": "General Studies Paper 3",  "name_kn": "ಸಾಮಾನ್ಯ ಅಧ್ಯಯನ ಪತ್ರಿಕೆ 3", "sort_order": 3},
    {"exam_type": "KAS_MAINS", "name_en": "General Studies Paper 4",  "name_kn": "ಸಾಮಾನ್ಯ ಅಧ್ಯಯನ ಪತ್ರಿಕೆ 4", "sort_order": 4},
    {"exam_type": "KAS_MAINS", "name_en": "Essay Paper",              "name_kn": "ಪ್ರಬಂಧ ಪತ್ರಿಕೆ",          "sort_order": 5},
    {"exam_type": "KAS_MAINS", "name_en": "Kannada Compulsory",       "name_kn": "ಕನ್ನಡ ಕಡ್ಡಾಯ",            "sort_order": 6},

    # FDA
    {"exam_type": "FDA", "name_en": "General Kannada",    "name_kn": "ಸಾಮಾನ್ಯ ಕನ್ನಡ",   "sort_order": 1},
    {"exam_type": "FDA", "name_en": "General English",    "name_kn": "ಸಾಮಾನ್ಯ ಇಂಗ್ಲಿಷ್", "sort_order": 2},
    {"exam_type": "FDA", "name_en": "General Knowledge",  "name_kn": "ಸಾಮಾನ್ಯ ಜ್ಞಾನ",    "sort_order": 3},
    {"exam_type": "FDA", "name_en": "Arithmetic",         "name_kn": "ಅಂಕಗಣಿತ",          "sort_order": 4},
    {"exam_type": "FDA", "name_en": "Computer Knowledge", "name_kn": "ಕಂಪ್ಯೂಟರ್ ಜ್ಞಾನ",   "sort_order": 5},

    # SDA
    {"exam_type": "SDA", "name_en": "General Kannada",    "name_kn": "ಸಾಮಾನ್ಯ ಕನ್ನಡ",   "sort_order": 1},
    {"exam_type": "SDA", "name_en": "General Knowledge",  "name_kn": "ಸಾಮಾನ್ಯ ಜ್ಞಾನ",    "sort_order": 2},
    {"exam_type": "SDA", "name_en": "Arithmetic",         "name_kn": "ಅಂಕಗಣಿತ",          "sort_order": 3},
    {"exam_type": "SDA", "name_en": "Computer Knowledge", "name_kn": "ಕಂಪ್ಯೂಟರ್ ಜ್ಞಾನ",   "sort_order": 4},
]

print("Inserting subjects...")
subjects_to_insert = []
for s in subjects_data:
    exam_type = s.pop("exam_type")
    s["syllabus_id"] = syl_map[exam_type]
    subjects_to_insert.append(s)

sub_res = supabase.table("subjects").upsert(
    subjects_to_insert,
    on_conflict="syllabus_id,name_en"   # unique key: same subject name per syllabus
).execute()
sub_rows = sub_res.data
print(f"  ✓ {len(sub_rows)} subjects")

sub_map = {}
for r in sub_rows:
    key = (r["syllabus_id"], r["name_en"])
    sub_map[key] = r["id"]

def sid(exam_type, name_en):
    return sub_map[(syl_map[exam_type], name_en)]

# ─────────────────────────────────────────
# TOPICS
# NOTE: 'difficulty', 'importance', and 'pyq_frequency' have been removed
# as those columns do not exist in the topics table schema.
# If you want them, run an ALTER TABLE migration in Supabase first:
#   ALTER TABLE topics ADD COLUMN difficulty TEXT;
#   ALTER TABLE topics ADD COLUMN importance  TEXT;
#   ALTER TABLE topics ADD COLUMN pyq_frequency INT DEFAULT 0;
# ─────────────────────────────────────────
topics_data = [

    # ── INDIAN HISTORY ──
    {"subject": ("KAS_PRELIMS", "Indian History"), "name_en": "Indus Valley Civilisation",       "name_kn": "ಸಿಂಧೂ ಕಣಿವೆ ನಾಗರಿಕತೆ",       "sort_order": 1},
    {"subject": ("KAS_PRELIMS", "Indian History"), "name_en": "Vedic Age",                       "name_kn": "ವೈದಿಕ ಯುಗ",                   "sort_order": 2},
    {"subject": ("KAS_PRELIMS", "Indian History"), "name_en": "Maurya Empire",                   "name_kn": "ಮೌರ್ಯ ಸಾಮ್ರಾಜ್ಯ",              "sort_order": 3},
    {"subject": ("KAS_PRELIMS", "Indian History"), "name_en": "Gupta Empire",                    "name_kn": "ಗುಪ್ತ ಸಾಮ್ರಾಜ್ಯ",               "sort_order": 4},
    {"subject": ("KAS_PRELIMS", "Indian History"), "name_en": "Delhi Sultanate",                 "name_kn": "ದೆಹಲಿ ಸುಲ್ತಾನ್‌ಶಾಹಿ",           "sort_order": 5},
    {"subject": ("KAS_PRELIMS", "Indian History"), "name_en": "Mughal Empire",                   "name_kn": "ಮೊಘಲ್ ಸಾಮ್ರಾಜ್ಯ",              "sort_order": 6},
    {"subject": ("KAS_PRELIMS", "Indian History"), "name_en": "Bhakti and Sufi Movement",        "name_kn": "ಭಕ್ತಿ ಮತ್ತು ಸೂಫಿ ಚಳವಳಿ",        "sort_order": 7},
    {"subject": ("KAS_PRELIMS", "Indian History"), "name_en": "British Colonial Rule",           "name_kn": "ಬ್ರಿಟಿಷ್ ವಸಾಹತುಶಾಹಿ",           "sort_order": 8},
    {"subject": ("KAS_PRELIMS", "Indian History"), "name_en": "Indian National Movement",        "name_kn": "ಭಾರತೀಯ ರಾಷ್ಟ್ರೀಯ ಚಳವಳಿ",        "sort_order": 9},
    {"subject": ("KAS_PRELIMS", "Indian History"), "name_en": "Partition and Independence",      "name_kn": "ವಿಭಜನೆ ಮತ್ತು ಸ್ವಾತಂತ್ರ್ಯ",       "sort_order": 10},

    # ── KARNATAKA HISTORY ──
    {"subject": ("KAS_PRELIMS", "Karnataka History"), "name_en": "Kadamba Dynasty",              "name_kn": "ಕದಂಬ ವಂಶ",                    "sort_order": 1},
    {"subject": ("KAS_PRELIMS", "Karnataka History"), "name_en": "Chalukyas of Badami",          "name_kn": "ಬಾದಾಮಿ ಚಾಲುಕ್ಯರು",              "sort_order": 2},
    {"subject": ("KAS_PRELIMS", "Karnataka History"), "name_en": "Rashtrakutas",                 "name_kn": "ರಾಷ್ಟ್ರಕೂಟರು",                 "sort_order": 3},
    {"subject": ("KAS_PRELIMS", "Karnataka History"), "name_en": "Hoysala Empire",               "name_kn": "ಹೊಯ್ಸಳ ಸಾಮ್ರಾಜ್ಯ",              "sort_order": 4},
    {"subject": ("KAS_PRELIMS", "Karnataka History"), "name_en": "Vijayanagara Empire",          "name_kn": "ವಿಜಯನಗರ ಸಾಮ್ರಾಜ್ಯ",             "sort_order": 5},
    {"subject": ("KAS_PRELIMS", "Karnataka History"), "name_en": "Kittur Rani Chennamma",        "name_kn": "ಕಿತ್ತೂರು ರಾಣಿ ಚೆನ್ನಮ್ಮ",          "sort_order": 6},
    {"subject": ("KAS_PRELIMS", "Karnataka History"), "name_en": "Mysore Unification",           "name_kn": "ಮೈಸೂರು ಏಕೀಕರಣ",               "sort_order": 7},
    {"subject": ("KAS_PRELIMS", "Karnataka History"), "name_en": "Karnataka Ekikarana Movement", "name_kn": "ಕರ್ನಾಟಕ ಏಕೀಕರಣ ಚಳವಳಿ",          "sort_order": 8},

    # ── INDIAN POLITY ──
    {"subject": ("KAS_PRELIMS", "Indian Polity"), "name_en": "Preamble of the Constitution",     "name_kn": "ಸಂವಿಧಾನದ ಪ್ರಸ್ತಾವನೆ",           "sort_order": 1},
    {"subject": ("KAS_PRELIMS", "Indian Polity"), "name_en": "Fundamental Rights",               "name_kn": "ಮೂಲಭೂತ ಹಕ್ಕುಗಳು",              "sort_order": 2},
    {"subject": ("KAS_PRELIMS", "Indian Polity"), "name_en": "Directive Principles",             "name_kn": "ನಿರ್ದೇಶನ ತತ್ವಗಳು",              "sort_order": 3},
    {"subject": ("KAS_PRELIMS", "Indian Polity"), "name_en": "Fundamental Duties",               "name_kn": "ಮೂಲಭೂತ ಕರ್ತವ್ಯಗಳು",             "sort_order": 4},
    {"subject": ("KAS_PRELIMS", "Indian Polity"), "name_en": "Parliament",                       "name_kn": "ಸಂಸತ್ತು",                       "sort_order": 5},
    {"subject": ("KAS_PRELIMS", "Indian Polity"), "name_en": "President and Vice President",     "name_kn": "ರಾಷ್ಟ್ರಪತಿ ಮತ್ತು ಉಪರಾಷ್ಟ್ರಪತಿ",  "sort_order": 6},
    {"subject": ("KAS_PRELIMS", "Indian Polity"), "name_en": "Supreme Court",                    "name_kn": "ಸರ್ವೋಚ್ಛ ನ್ಯಾಯಾಲಯ",             "sort_order": 7},
    {"subject": ("KAS_PRELIMS", "Indian Polity"), "name_en": "State Government",                 "name_kn": "ರಾಜ್ಯ ಸರ್ಕಾರ",                  "sort_order": 8},
    {"subject": ("KAS_PRELIMS", "Indian Polity"), "name_en": "Panchayati Raj",                   "name_kn": "ಪಂಚಾಯತ್ ರಾಜ್",                  "sort_order": 9},
    {"subject": ("KAS_PRELIMS", "Indian Polity"), "name_en": "Constitutional Amendments",        "name_kn": "ಸಾಂವಿಧಾನಿಕ ತಿದ್ದುಪಡಿಗಳು",       "sort_order": 10},
    {"subject": ("KAS_PRELIMS", "Indian Polity"), "name_en": "Emergency Provisions",             "name_kn": "ತುರ್ತು ಪರಿಸ್ಥಿತಿ ನಿಬಂಧನೆಗಳು",   "sort_order": 11},
    {"subject": ("KAS_PRELIMS", "Indian Polity"), "name_en": "Election Commission",              "name_kn": "ಚುನಾವಣಾ ಆಯೋಗ",                "sort_order": 12},

    # ── INDIAN GEOGRAPHY ──
    {"subject": ("KAS_PRELIMS", "Indian Geography"), "name_en": "Physical Features of India",   "name_kn": "ಭಾರತದ ಭೌತಿಕ ಲಕ್ಷಣಗಳು",          "sort_order": 1},
    {"subject": ("KAS_PRELIMS", "Indian Geography"), "name_en": "Rivers of India",              "name_kn": "ಭಾರತದ ನದಿಗಳು",                  "sort_order": 2},
    {"subject": ("KAS_PRELIMS", "Indian Geography"), "name_en": "Climate of India",             "name_kn": "ಭಾರತದ ಹವಾಮಾನ",                  "sort_order": 3},
    {"subject": ("KAS_PRELIMS", "Indian Geography"), "name_en": "Soils and Agriculture",        "name_kn": "ಮಣ್ಣು ಮತ್ತು ಕೃಷಿ",               "sort_order": 4},
    {"subject": ("KAS_PRELIMS", "Indian Geography"), "name_en": "Minerals and Energy",          "name_kn": "ಖನಿಜಗಳು ಮತ್ತು ಶಕ್ತಿ",            "sort_order": 5},
    {"subject": ("KAS_PRELIMS", "Indian Geography"), "name_en": "Transport and Communication",  "name_kn": "ಸಾರಿಗೆ ಮತ್ತು ಸಂವಹನ",            "sort_order": 6},

    # ── KARNATAKA GEOGRAPHY ──
    {"subject": ("KAS_PRELIMS", "Karnataka Geography"), "name_en": "Districts and Divisions",   "name_kn": "ಜಿಲ್ಲೆಗಳು ಮತ್ತು ವಿಭಾಗಗಳು",       "sort_order": 1},
    {"subject": ("KAS_PRELIMS", "Karnataka Geography"), "name_en": "Rivers of Karnataka",       "name_kn": "ಕರ್ನಾಟಕದ ನದಿಗಳು",               "sort_order": 2},
    {"subject": ("KAS_PRELIMS", "Karnataka Geography"), "name_en": "Western Ghats",             "name_kn": "ಪಶ್ಚಿಮ ಘಟ್ಟಗಳು",               "sort_order": 3},
    {"subject": ("KAS_PRELIMS", "Karnataka Geography"), "name_en": "Agriculture in Karnataka",  "name_kn": "ಕರ್ನಾಟಕದ ಕೃಷಿ",                "sort_order": 4},
    {"subject": ("KAS_PRELIMS", "Karnataka Geography"), "name_en": "Forest and Wildlife",       "name_kn": "ಅರಣ್ಯ ಮತ್ತು ವನ್ಯಜೀವಿ",           "sort_order": 5},

    # ── INDIAN ECONOMY ──
    {"subject": ("KAS_PRELIMS", "Indian Economy"), "name_en": "National Income and GDP",        "name_kn": "ರಾಷ್ಟ್ರೀಯ ಆದಾಯ ಮತ್ತು ಜಿಡಿಪಿ",    "sort_order": 1},
    {"subject": ("KAS_PRELIMS", "Indian Economy"), "name_en": "Five Year Plans",                "name_kn": "ಪಂಚವಾರ್ಷಿಕ ಯೋಜನೆಗಳು",            "sort_order": 2},
    {"subject": ("KAS_PRELIMS", "Indian Economy"), "name_en": "Banking and Finance",            "name_kn": "ಬ್ಯಾಂಕಿಂಗ್ ಮತ್ತು ಹಣಕಾಸು",        "sort_order": 3},
    {"subject": ("KAS_PRELIMS", "Indian Economy"), "name_en": "Agriculture and Rural Economy",  "name_kn": "ಕೃಷಿ ಮತ್ತು ಗ್ರಾಮೀಣ ಅರ್ಥಶಾಸ್ತ್ರ", "sort_order": 4},
    {"subject": ("KAS_PRELIMS", "Indian Economy"), "name_en": "Poverty and Unemployment",       "name_kn": "ಬಡತನ ಮತ್ತು ನಿರುದ್ಯೋಗ",           "sort_order": 5},
    {"subject": ("KAS_PRELIMS", "Indian Economy"), "name_en": "Government Schemes",             "name_kn": "ಸರ್ಕಾರಿ ಯೋಜನೆಗಳು",              "sort_order": 6},
    {"subject": ("KAS_PRELIMS", "Indian Economy"), "name_en": "Budget and Taxation",            "name_kn": "ಬಜೆಟ್ ಮತ್ತು ತೆರಿಗೆ",             "sort_order": 7},

    # ── KARNATAKA ECONOMY ──
    {"subject": ("KAS_PRELIMS", "Karnataka Economy"), "name_en": "Karnataka State Budget",      "name_kn": "ಕರ್ನಾಟಕ ರಾಜ್ಯ ಬಜೆಟ್",            "sort_order": 1},
    {"subject": ("KAS_PRELIMS", "Karnataka Economy"), "name_en": "Industries in Karnataka",     "name_kn": "ಕರ್ನಾಟಕದಲ್ಲಿ ಕೈಗಾರಿಕೆಗಳು",       "sort_order": 2},
    {"subject": ("KAS_PRELIMS", "Karnataka Economy"), "name_en": "Karnataka State Schemes",     "name_kn": "ಕರ್ನಾಟಕ ರಾಜ್ಯ ಯೋಜನೆಗಳು",          "sort_order": 3},

    # ── GENERAL SCIENCE ──
    {"subject": ("KAS_PRELIMS", "General Science"), "name_en": "Physics Basics",                "name_kn": "ಭೌತಶಾಸ್ತ್ರ ಮೂಲಗಳು",              "sort_order": 1},
    {"subject": ("KAS_PRELIMS", "General Science"), "name_en": "Chemistry Basics",              "name_kn": "ರಸಾಯನಶಾಸ್ತ್ರ ಮೂಲಗಳು",            "sort_order": 2},
    {"subject": ("KAS_PRELIMS", "General Science"), "name_en": "Biology and Human Body",        "name_kn": "ಜೀವಶಾಸ್ತ್ರ ಮತ್ತು ಮಾನವ ದೇಹ",      "sort_order": 3},
    {"subject": ("KAS_PRELIMS", "General Science"), "name_en": "Space and Technology",          "name_kn": "ಬಾಹ್ಯಾಕಾಶ ಮತ್ತು ತಂತ್ರಜ್ಞಾನ",      "sort_order": 4},
    {"subject": ("KAS_PRELIMS", "General Science"), "name_en": "Diseases and Health",           "name_kn": "ರೋಗಗಳು ಮತ್ತು ಆರೋಗ್ಯ",             "sort_order": 5},

    # ── ENVIRONMENT ──
    {"subject": ("KAS_PRELIMS", "Environment & Ecology"), "name_en": "Ecosystems",              "name_kn": "ಪರಿಸರ ವ್ಯವಸ್ಥೆಗಳು",              "sort_order": 1},
    {"subject": ("KAS_PRELIMS", "Environment & Ecology"), "name_en": "Climate Change",          "name_kn": "ಹವಾಮಾನ ಬದಲಾವಣೆ",               "sort_order": 2},
    {"subject": ("KAS_PRELIMS", "Environment & Ecology"), "name_en": "Biodiversity",            "name_kn": "ಜೀವ ವೈವಿಧ್ಯತೆ",                "sort_order": 3},
    {"subject": ("KAS_PRELIMS", "Environment & Ecology"), "name_en": "Environmental Laws",      "name_kn": "ಪರಿಸರ ಕಾಯ್ದೆಗಳು",               "sort_order": 4},
    {"subject": ("KAS_PRELIMS", "Environment & Ecology"), "name_en": "Pollution",               "name_kn": "ಮಾಲಿನ್ಯ",                      "sort_order": 5},

    # ── MENTAL ABILITY ──
    {"subject": ("KAS_PRELIMS", "Mental Ability"), "name_en": "Number Series",                  "name_kn": "ಸಂಖ್ಯಾ ಸರಣಿ",                   "sort_order": 1},
    {"subject": ("KAS_PRELIMS", "Mental Ability"), "name_en": "Logical Reasoning",              "name_kn": "ತಾರ್ಕಿಕ ಚಿಂತನೆ",                "sort_order": 2},
    {"subject": ("KAS_PRELIMS", "Mental Ability"), "name_en": "Data Interpretation",            "name_kn": "ದತ್ತಾಂಶ ವಿಶ್ಲೇಷಣೆ",              "sort_order": 3},
    {"subject": ("KAS_PRELIMS", "Mental Ability"), "name_en": "Coding Decoding",                "name_kn": "ಕೋಡಿಂಗ್ ಡಿಕೋಡಿಂಗ್",              "sort_order": 4},

    # ── KANNADA LANGUAGE ──
    {"subject": ("KAS_PRELIMS", "Kannada Language"), "name_en": "Kannada Grammar",              "name_kn": "ಕನ್ನಡ ವ್ಯಾಕರಣ",                 "sort_order": 1},
    {"subject": ("KAS_PRELIMS", "Kannada Language"), "name_en": "Kannada Literature",           "name_kn": "ಕನ್ನಡ ಸಾಹಿತ್ಯ",                 "sort_order": 2},
    {"subject": ("KAS_PRELIMS", "Kannada Language"), "name_en": "Comprehension",                "name_kn": "ಗದ್ಯಾವಬೋಧ",                    "sort_order": 3},
]

print("Inserting topics...")
topics_to_insert = []
for t in topics_data:
    subject_key = t.pop("subject")
    t["subject_id"] = sid(subject_key[0], subject_key[1])
    t["is_active"] = True
    topics_to_insert.append(t)

top_res = supabase.table("topics").upsert(
    topics_to_insert,
    on_conflict="subject_id,name_en"    # unique key: same topic name per subject
).execute()
print(f"  ✓ {len(top_res.data)} topics")

print("\n✅ Seed complete.")
print(f"   Syllabuses : {len(syl_rows)}")
print(f"   Subjects   : {len(sub_rows)}")
print(f"   Topics     : {len(top_res.data)}")