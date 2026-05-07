# DISTORTIONS_SEED.md — Bilingual Seed Data

This file contains the content for the seed scripts referenced in GUIDELINES.md §4. Claude Code should translate these into Python seed scripts in `backend/app/seed/`.

---

## Cognitive Distortions (the seven)

Source: the therapist's hand-drawn list. These are fixed in v1.

### 1. Fortune Telling
- **code:** `fortune_telling`
- **name_en:** Fortune Telling
- **name_id:** Meramal Masa Depan
- **description_en:** Predicting that things will turn out badly without real evidence to support that prediction.
- **description_id:** Memprediksi bahwa hal-hal akan berakhir buruk tanpa bukti nyata yang mendukung prediksi tersebut.
- **example_en:** "I just know I'm going to fail this interview."
- **example_id:** "Aku sudah tahu kok aku bakal gagal di wawancara ini."

### 2. Personalization
- **code:** `personalization`
- **name_en:** Personalization
- **name_id:** Personalisasi
- **description_en:** Blaming yourself for events outside your control, or assuming everything is about you.
- **description_id:** Menyalahkan diri sendiri atas peristiwa di luar kendalimu, atau menganggap segala sesuatu berhubungan denganmu.
- **example_en:** "My friend seems quiet today — it must be because of something I did."
- **example_id:** "Temanku diam aja hari ini — pasti gara-gara sesuatu yang aku lakukan."

### 3. Mental Filtering
- **code:** `mental_filtering`
- **name_en:** Mental Filtering
- **name_id:** Penyaringan Mental
- **description_en:** Focusing only on the negative details of a situation while filtering out anything positive.
- **description_id:** Hanya fokus pada detail negatif dari sebuah situasi sambil menyaring keluar hal-hal yang positif.
- **example_en:** "I got nine compliments and one criticism — all I can think about is the criticism."
- **example_id:** "Aku dapat sembilan pujian dan satu kritik — yang kupikirkan cuma kritiknya."

### 4. Overgeneralization
- **code:** `overgeneralization`
- **name_en:** Overgeneralization
- **name_id:** Generalisasi Berlebihan
- **description_en:** Treating a single negative event as a never-ending pattern of defeat. Watch for "always" and "never."
- **description_id:** Memperlakukan satu peristiwa negatif sebagai pola kegagalan yang tak berujung. Waspadai kata "selalu" dan "tidak pernah."
- **example_en:** "I messed up that one task. I always mess everything up."
- **example_id:** "Aku gagal di tugas itu. Aku selalu mengacaukan semuanya."

### 5. "Should" / "Must" Statements
- **code:** `should_must`
- **name_en:** "Should" / "Must" Statements
- **name_id:** Pernyataan "Harusnya" / "Wajib"
- **description_en:** Holding yourself or others to rigid rules about how things ought to be, leading to guilt and resentment.
- **description_id:** Memegang aturan kaku tentang bagaimana segala sesuatu seharusnya, sehingga menimbulkan rasa bersalah dan kesal.
- **example_en:** "I should be over this by now. I must be productive every single day."
- **example_id:** "Harusnya aku sudah move on dari ini. Aku wajib produktif setiap hari."

### 6. Magnification / Minimization
- **code:** `magnification_minimization`
- **name_en:** Magnification / Minimization
- **name_id:** Pembesaran / Pengecilan
- **description_en:** Blowing negatives out of proportion while shrinking positives until they don't count.
- **description_id:** Membesar-besarkan hal negatif sambil mengecilkan hal positif sampai dianggap tidak berarti.
- **example_en:** "One mistake at work means I'm a failure. The promotion last month was just luck."
- **example_id:** "Satu kesalahan di kantor berarti aku gagal. Promosi bulan lalu cuma keberuntungan doang."

### 7. All-or-None Thinking
- **code:** `all_or_none`
- **name_en:** All-or-None Thinking
- **name_id:** Pemikiran Hitam-Putih
- **description_en:** Seeing situations in only two categories: perfect or terrible, success or failure, with no middle ground.
- **description_id:** Melihat situasi hanya dalam dua kategori: sempurna atau buruk, sukses atau gagal, tanpa wilayah abu-abu.
- **example_en:** "If I can't do this perfectly, there's no point in doing it at all."
- **example_id:** "Kalau aku nggak bisa ngerjain ini dengan sempurna, ya nggak usah dikerjain sekalian."

---

## Seeded Emotions

A starter set of ~12 emotions. User should be able to add custom ones in v2.

| code | name_en | name_id |
|------|---------|---------|
| `sadness` | Sadness | Kesedihan |
| `anxiety` | Anxiety | Kecemasan |
| `anger` | Anger | Kemarahan |
| `frustration` | Frustration | Frustrasi |
| `shame` | Shame | Rasa Malu |
| `guilt` | Guilt | Rasa Bersalah |
| `fear` | Fear | Ketakutan |
| `loneliness` | Loneliness | Kesepian |
| `hopelessness` | Hopelessness | Putus Asa |
| `overwhelm` | Overwhelm | Kewalahan |
| `disappointment` | Disappointment | Kekecewaan |
| `numbness` | Numbness | Mati Rasa |

---

## Reality Test Prompts (used in Step 5 of the entry flow)

These are the bilingual prompt templates pulled directly from the source diagram. Store them as constants the frontend can render with placeholders.

### Reality test
- **EN:** "I'm thinking I'm {X}. Is there proof in my life that I am {X} or feel {X}?"
- **ID:** "Aku berpikir aku {X}. Ada bukti dalam hidupku ketika aku merasa {X}?"

### Pragmatic check
- **EN:** "With this thought pattern, will it help me reach my goal (calmness)?"
- **ID:** "Dengan pola pikir ini, apakah pola pikir itu akan membantuku mencapai tujuan (tenang)?"

### Alternative action
- **EN:** "How else could I do/think to improve the situation?"
- **ID:** "Apa lagi yang bisa kulakukan/kupikirkan untuk memperbaiki situasi ini?"

### Belief tags (informational chips on Step 3)
- **EN:** automatic · irrational · unhelpful
- **ID:** otomatis · irasional · tidak membantu