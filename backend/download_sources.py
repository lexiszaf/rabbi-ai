# backend/download_sources.py
import requests
import json
import os
import time

OUTPUT_DIR = "./data/texts"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# All sources organized — Sefaria API names
SOURCES = {
    "Torah": [
        "Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy"
    ],
    "Nevi'im": [
        "Joshua", "Judges", "I_Samuel", "II_Samuel", "I_Kings", "II_Kings",
        "Isaiah", "Jeremiah", "Ezekiel", "Hosea", "Joel", "Amos",
        "Obadiah", "Jonah", "Micah", "Nahum", "Habakkuk", "Zephaniah",
        "Haggai", "Zechariah", "Malachi"
    ],
    "Ketuvim": [
        "Psalms", "Proverbs", "Job", "Song_of_Songs", "Ruth",
        "Lamentations", "Ecclesiastes", "Esther", "Daniel",
        "Ezra", "Nehemiah", "I_Chronicles", "II_Chronicles"
    ],
    "Mishnah": [
        "Mishnah_Berakhot", "Mishnah_Peah", "Mishnah_Demai",
        "Mishnah_Kilayim", "Mishnah_Sheviit", "Mishnah_Terumot",
        "Mishnah_Maasrot", "Mishnah_Maaser_Sheni", "Mishnah_Challah",
        "Mishnah_Orlah", "Mishnah_Bikkurim", "Mishnah_Shabbat",
        "Mishnah_Eruvin", "Mishnah_Pesachim", "Mishnah_Shekalim",
        "Mishnah_Yoma", "Mishnah_Sukkah", "Mishnah_Beitzah",
        "Mishnah_Rosh_Hashanah", "Mishnah_Taanit", "Mishnah_Megillah",
        "Mishnah_Moed_Katan", "Mishnah_Chagigah", "Mishnah_Yevamot",
        "Mishnah_Ketubot", "Mishnah_Nedarim", "Mishnah_Nazir",
        "Mishnah_Sotah", "Mishnah_Gittin", "Mishnah_Kiddushin",
        "Mishnah_Bava_Kamma", "Mishnah_Bava_Metzia", "Mishnah_Bava_Batra",
        "Mishnah_Sanhedrin", "Mishnah_Makkot", "Mishnah_Shevuot",
        "Mishnah_Eduyot", "Mishnah_Avodah_Zarah", "Mishnah_Avot",
        "Mishnah_Horayot", "Mishnah_Zevachim", "Mishnah_Menachot",
        "Mishnah_Chullin", "Mishnah_Bekhorot", "Mishnah_Arakhin",
        "Mishnah_Temurah", "Mishnah_Keritot", "Mishnah_Meilah",
        "Mishnah_Tamid", "Mishnah_Middot", "Mishnah_Kinnim",
        "Mishnah_Kelim", "Mishnah_Oholot", "Mishnah_Negaim",
        "Mishnah_Parah", "Mishnah_Tahorot", "Mishnah_Mikvaot",
        "Mishnah_Niddah", "Mishnah_Makhshirin", "Mishnah_Zavim",
        "Mishnah_Tevul_Yom", "Mishnah_Yadayim", "Mishnah_Oktzin"
    ],
    "Talmud Bavli": [
        "Berakhot", "Shabbat", "Eruvin", "Pesachim", "Rosh_Hashanah",
        "Yoma", "Sukkah", "Beitzah", "Taanit", "Megillah", "Moed_Katan",
        "Chagigah", "Yevamot", "Ketubot", "Nedarim", "Nazir", "Sotah",
        "Gittin", "Kiddushin", "Bava_Kamma", "Bava_Metzia", "Bava_Batra",
        "Sanhedrin", "Makkot", "Shevuot", "Avodah_Zarah", "Horayot",
        "Zevachim", "Menachot", "Chullin", "Bekhorot", "Arakhin",
        "Temurah", "Keritot", "Meilah", "Niddah"
    ],
    "Halacha": [
        "Shulchan_Arukh,_Orach_Chaim",
        "Shulchan_Arukh,_Yoreh_Deah",
        "Shulchan_Arukh,_Even_HaEzer",
        "Shulchan_Arukh,_Choshen_Mishpat",
        "Mishneh_Torah,_Human_Dispositions",
        "Mishneh_Torah,_Torah_Study",
        "Mishneh_Torah,_Repentance",
        "Mishneh_Torah,_Sabbath",
        "Mishneh_Torah,_Prayer_and_the_Priestly_Blessing",
        "Mishneh_Torah,_Marriage",
        "Mishneh_Torah,_Mourning",
    ],
    "Midrash": [
        "Bereshit_Rabbah", "Shemot_Rabbah", "Vayikra_Rabbah",
        "Bamidbar_Rabbah", "Devarim_Rabbah", "Midrash_Tanchuma",
        "Pirkei_DeRabbi_Eliezer"
    ],
    "Mussar & Philosophy": [
        "Pirkei_Avot",
        "Mesillat_Yesharim",
        "Orchot_Tzaddikim",
        "Duties_of_the_Heart",
        "Kuzari",
    ],
    "Chassidut": [
        "Tanya",
    ],
    "Commentary": [
        "Rashi_on_Genesis", "Rashi_on_Exodus", "Rashi_on_Leviticus",
        "Rashi_on_Numbers", "Rashi_on_Deuteronomy",
        "Ramban_on_Genesis", "Ramban_on_Exodus", "Ramban_on_Leviticus",
        "Ramban_on_Numbers", "Ramban_on_Deuteronomy",
        "Ibn_Ezra_on_Genesis", "Ibn_Ezra_on_Exodus",
        "Sforno_on_Genesis", "Sforno_on_Exodus",
    ],
}

def download_text(name):
    filename = f"{OUTPUT_DIR}/{name.replace(',', '').replace(' ', '_')}.json"
    
    if os.path.exists(filename):
        print(f"⏭️  Skipping {name} (already downloaded)")
        return

    url = f"https://www.sefaria.org/api/texts/{name}?commentary=0&context=0&pad=0&wrapLinks=0"
    
    try:
        res = requests.get(url, timeout=30)
        if res.status_code == 200:
            data = res.json()
            if "error" in data:
                print(f"❌ {name}: {data['error']}")
                return
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False)
            print(f"✅ {name}")
        else:
            print(f"❌ {name}: HTTP {res.status_code}")
    except Exception as e:
        print(f"❌ {name}: {e}")
    
    time.sleep(0.5)  # be polite to Sefaria's servers

if __name__ == "__main__":
    total = sum(len(v) for v in SOURCES.values())
    done = 0

    for category, texts in SOURCES.items():
        print(f"\n📚 {category}")
        print("-" * 40)
        for text in texts:
            download_text(text)
            done += 1
            print(f"   Progress: {done}/{total}")
    
    print("\n🎉 All downloads complete! Now run: python ingest.py")