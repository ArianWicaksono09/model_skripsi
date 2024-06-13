import mysql.connector
import json
from config.database import connect
from bs4 import BeautifulSoup
import html

def clean_html_tags(text):
    # Bersihkan HTML tags menggunakan BeautifulSoup dan html.unescape
    soup = BeautifulSoup(text, 'html.parser')
    cleaned_text = html.unescape(soup.get_text(separator=' '))
    
    # Hapus karakter ' dan "
    # cleaned_text = cleaned_text.replace("€", '').replace('“', '').replace("‘", '')
    cleaned_text = (
        cleaned_text
        .replace("\u00e2\u20ac\u201c", '')  # untuk karakter “
        .replace("\u00e2\u20ac\u2122", '')  # untuk karakter €
        .replace("\u201c", '')               # untuk karakter "
        .replace("\u201d", '')               # untuk karakter '
        .replace("\u00a0", ' ')             # untuk karakter spasi non-pecahan
        .replace("\u2013", '')
        .replace("\u00ef", 'i')
        .replace("\u2019", '')
        .replace("!", '')
        .replace("(", '')
        .replace(")", '')
        .replace("[", '')
        .replace("]", '')
        .replace(":", '')
        .replace('\"', '')
        .replace(".", '')
        .replace(",", '')
        .replace("-", '')
    )
    return cleaned_text

def load_existing_intents():
    try:
        with open('intents.json', 'r', encoding='utf-8') as file:
            existing_data = json.load(file)
            return existing_data.get("intents", [])
    except FileNotFoundError:
        return []

def save_intents_to_file(intents):
    with open('intents.json', 'w', encoding='utf-8') as file:
        json.dump({"intents": intents}, file, indent=2)

def get_data_from_database(table_name, columns):
    db = connect()
    if db:
        try:
            cursor = db.cursor()
            select_query = f"SELECT {', '.join(columns)} FROM {table_name}"
            cursor.execute(select_query)
            rows = cursor.fetchall()
            return rows
        except mysql.connector.Error as err:
            print(f"Error: {err}")
        finally:
            cursor.close()
            db.close()
    return []

def split_long_sentence(sentence, max_words_per_pattern):
    words = sentence.split()
    splitted_sentences = []
    for i in range(0, len(words), max_words_per_pattern):
        pattern = ' '.join(words[i:i + max_words_per_pattern])
        splitted_sentences.append(pattern)
    return splitted_sentences

def generate_intents_from_database():
    existing_intents = load_existing_intents()  # Load existing intents once

    # Mengambil data dari database untuk table posts
    posts_data = get_data_from_database("posts", ["title", "article"])

    # Mengambil data dari database untuk table events
    events_data = get_data_from_database("events", ["title", "description"])

    # Mengambil data dari database untuk table laboratories
    laboratories_data = get_data_from_database("laboratories", ["title_id", "description_id"])

    # Mengambil data dari database untuk table lecturers
    lecturers_data = get_data_from_database("lecturers", ["name", "nip", "jabatan_id", "expertise_id", "email"])

    # Mengambil data dari database untuk table penelitians
    penelitians_data = get_data_from_database("penelitians", ["judul", "tahun_penelitian", "sumber_dana"])

    # Mengambil data dari database untuk table pengabdians
    pengabdians_data = get_data_from_database("pengabdians", ["judul", "tahun", "sumber_dana"])

    # Mengambil data dari database untuk table publikasis
    publikasis_data = get_data_from_database("publikasis", ["judul", "deskripsi", "oleh", "anggota", "tahun", "link"])

    # Mengambil data dari database untuk table pages
    pages_data = get_data_from_database("pages", ["title", "content"])

    # Mengambil data dari database untuk table components_subpage_subpages
    components_subpage_subpages_data = get_data_from_database("components_subpage_subpages", ["title", "content"])


    # Generate intents untuk posts
    for index, (title, article) in enumerate(posts_data, start=1):
        intent_tag = f"post_{index}"
        if intent_tag not in [intent.get("tag") for intent in existing_intents]:
            cleaned_title = clean_html_tags(title)

            intent = {
                "tag": intent_tag,
                "patterns": [cleaned_title],
                "responses": [f"{title} <br><br> {article}"]
            }
            existing_intents.append(intent)

    # Generate intents untuk events
    for index, (title, description) in enumerate(events_data, start=1):
        intent_tag = f"event_{index}"
        if intent_tag not in [intent.get("tag") for intent in existing_intents]:
            cleaned_title = clean_html_tags(title)

            intent = {
                "tag": intent_tag,
                "patterns": [cleaned_title],
                "responses": [f"{title} <br><br> {description}"]
            }
            existing_intents.append(intent)
    
    # Generate intents untuk laboratories
    for index, (title_id, description_id) in enumerate(laboratories_data, start=1):
        intent_tag = f"lab_{index}"
        if intent_tag not in [intent.get("tag") for intent in existing_intents]:
            cleaned_title_id = clean_html_tags(title_id)

            intent = {
                "tag": intent_tag,
                "patterns": [cleaned_title_id],
                "responses": [f"{title_id} <br><br> {description_id}"]
            }
            existing_intents.append(intent)
    
    # Generate intents untuk lecturers
    for index, (name, nip, jabatan_id, expertise_id, email) in enumerate(lecturers_data, start=1):
        intent_tag = f"lecturer_{index}"
        if intent_tag not in [intent.get("tag") for intent in existing_intents]:
            cleaned_name = clean_html_tags(name)
            
            intent = {
                "tag": intent_tag,
                "patterns": [cleaned_name],
                "responses": [f"Nama: {name} <br> Nip: {nip} <br> Jabatan: {jabatan_id} <br> Bidang Keahlian: {expertise_id} <br> Email: {email}"]
            }
            existing_intents.append(intent)

    # Generate intents untuk penelitians
    for index, (judul, tahun_penelitian, sumber_dana) in enumerate(penelitians_data, start=1):
        intent_tag = f"penelitian_{index}"
        if intent_tag not in [intent.get("tag") for intent in existing_intents]:
            cleaned_judul = clean_html_tags(judul)

            intent = {
                "tag": intent_tag,
                "patterns": [cleaned_judul],
                "responses": [f"{judul} <br><br> Tahun Penelitian: {tahun_penelitian} <br> Sumber Dana: {sumber_dana}"]
            }
            existing_intents.append(intent)
    
    # Generate intents untuk pengabdians
    for index, (judul, tahun, sumber_dana) in enumerate(pengabdians_data, start=1):
        intent_tag = f"pengabdian_{index}"
        if intent_tag not in [intent.get("tag") for intent in existing_intents]:
            cleaned_judul = clean_html_tags(judul)

            intent = {
                "tag": intent_tag,
                "patterns": [cleaned_judul],
                "responses": [f"{judul} <br><br> Tahun Penelitian: {tahun} <br> Sumber Dana: {sumber_dana}"]
            }
            existing_intents.append(intent)

    # Generate intents untuk publikasis
    for index, (judul, deskripsi, oleh, anggota, tahun, link) in enumerate(publikasis_data, start=1):
        intent_tag = f"publikasi_{index}"
        if intent_tag not in [intent.get("tag") for intent in existing_intents]:
            cleaned_judul = clean_html_tags(judul)

            intent = {
                "tag": intent_tag,
                "patterns": [cleaned_judul],
                "responses": [f"{judul} <br><br> Tahun: {tahun} <br> Deskripsi: {deskripsi} <br> Oleh: {oleh} <br> Anggota Publikasi: {anggota} <br> Link Publikasi: {link}"]
            }
            existing_intents.append(intent)

    # Generate intents untuk pages
    for index, (title, content) in enumerate(pages_data, start=1):
        intent_tag = f"page_{index}"
        if intent_tag not in [intent.get("tag") for intent in existing_intents]:
            cleaned_title = clean_html_tags(title)

            intent = {
                "tag": intent_tag,
                "patterns": [cleaned_title],
                "responses": [f"{title} <br><br> {content}"]
            }
            existing_intents.append(intent)

    # Generate intents untuk components_subpage_subpages
    for index, (title, content) in enumerate(components_subpage_subpages_data, start=1):
        intent_tag = f"subpage_{index}"
        if intent_tag not in [intent.get("tag") for intent in existing_intents]:
            cleaned_title = clean_html_tags(title)

            intent = {
                "tag": intent_tag,
                "patterns": [cleaned_title],
                "responses": [f"{title} <br><br> {content}"]
            }
            existing_intents.append(intent)


    # Simpan kembali ke file jika ada perubahan atau penambahan
    save_intents_to_file(existing_intents)

    return existing_intents

# Generate intents dari database dan simpan ke file intents.json
generated_intents = generate_intents_from_database()

# Cetak intents yang telah dibuat
for intent in generated_intents:
    print(json.dumps(intent, indent=2))
