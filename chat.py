import random
import json

import torch

from model import NeuralNet
from test import bag_of_words, tokenize, stem
from model_bard_ai import get_gemini_response, read_sql_query  #

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

with open('intents.json', 'r', encoding='utf-8') as json_data:
    intents = json.load(json_data)

FILE = "data.pth"
data = torch.load(FILE)

input_size = data["input_size"]
hidden_size = data["hidden_size"]
output_size = data["output_size"]
all_words = data['all_words']
tags = data['tags']
model_state = data["model_state"]

model = NeuralNet(input_size, hidden_size, output_size).to(device)
model.load_state_dict(model_state)
model.eval()

bot_name = "Arian"

def get_response(msg, lang='id'):
    prompt = [
    """
    Anda adalah ahli dalam mengonversi pertanyaan dalam bahasa Indonesia dan Inggris menjadi kueri SQL yang sesuai dengan database yang diberikan.

    Database SQL memiliki beberapa tabel yang dijelaskan berikut:

    ### Table: posts
    - Fields: title, article, created_at
    - Description: Berita kampus
    - Query: `SELECT title, article FROM posts`
    - Instruction: Jika ada pertanyaan mengarah ke berita atau ada kemiripan dengan title di tabel posts, berikan title + article.
    - **Identifikasi Kemiripan**:
        - Jika pertanyaan berisi frasa yang cocok atau mirip dengan title dalam tabel `posts`, berikan title + article yang sesuai.
        - Query: `SELECT title, article FROM posts WHERE LOWER(title) LIKE LOWER('%{frasa}%')`
        - Gunakan sanitasi input untuk menghindari masalah dengan karakter khusus dalam frasa.
        - Jika pencarian dengan frasa tidak berhasil, coba dengan pencarian berbasis kata kunci yang ada dalam title.
        - Jika terdapat beberapa hasil, berikan daftar singkat dari hasil yang paling relevan.
    - **Permintaan Berita Terbaru**:
        - Jika pertanyaan meminta berita terbaru, atau beberapa berita terbaru, berikan hasil yang diurutkan berdasarkan kolom `created_at` dari yang terbaru ke yang terlama.
        - Query: `SELECT title, article FROM posts ORDER BY created_at DESC LIMIT {jumlah}`
        - Jika jumlah berita tidak disebutkan, berikan satu berita terbaru sebagai default.
        
    ### Table: events
    - Fields: title, description, created_at
    - Description: Kegiatan kampus
    - Query: `SELECT title, description FROM events`
    - Instruction: Jika pertanyaan terkait kegiatan atau agenda, berikan title + description.
    - **Identifikasi Kegiatan**:
        - Jika pertanyaan berisi frasa yang cocok atau mirip dengan title dalam tabel `events`, berikan title + description yang sesuai.
        - Query: `SELECT title, description FROM events WHERE LOWER(title) LIKE LOWER('%{frasa}%')`
        - Gunakan sanitasi input untuk menghindari masalah dengan karakter khusus dalam frasa.
        - Jika pencarian dengan frasa tidak berhasil, coba dengan pencarian berbasis kata kunci yang ada dalam title.
        - Jika terdapat beberapa hasil, berikan daftar singkat dari hasil yang paling relevan.
    - **Permintaan Agenda Terbaru**:
        - Jika pertanyaan meminta agenda terbaru, atau beberapa agenda terbaru, berikan hasil yang diurutkan berdasarkan kolom `created_at` dari yang terbaru ke yang terlama.
        - Query: `SELECT title, description FROM events ORDER BY created_at DESC LIMIT {jumlah}`
        - Jika jumlah agenda tidak disebutkan, berikan satu agenda terbaru sebagai default.

    **Table: laboratories**
    - Fields: title_id, description_id
    - Description: Informasi laboratorium
    - Query: `SELECT title_id, description_id FROM laboratories`
    - Instruction: Jika pertanyaan terkait laboratorium, berikan title_id + description_id.

    **Table: lecturers**
    - Fields: name, nip, jabatan_id, expertise_id, email
    - Description: Dosen informatika
    - Query: `SELECT name, nip, jabatan_id, expertise_id, email FROM lecturers`
    - Instruction: Jika pertanyaan terkait dosen, ikuti langkah-langkah berikut:
        1. **Identifikasi Permintaan Detail**:
            - Jika diminta NIP: `SELECT nip FROM lecturers WHERE LOWER(name) LIKE LOWER('%{nama_dosen}%')`
            - Jika diminta nama: `SELECT name FROM lecturers WHERE LOWER(name) LIKE LOWER('%{nama_dosen}%')`
            - Jika diminta jabatan: `SELECT jabatan_id FROM lecturers WHERE LOWER(name) LIKE LOWER('%{nama_dosen}%')`
            - Jika diminta bidang keahlian: `SELECT expertise_id FROM lecturers WHERE LOWER(name) LIKE LOWER('%{nama_dosen}%')`
            - Jika diminta email: `SELECT email FROM lecturers WHERE LOWER(name) LIKE LOWER('%{nama_dosen}%')`
            - Jika diminta informasi lengkap: `SELECT name, nip, jabatan_id, expertise_id, email FROM lecturers WHERE LOWER(name) LIKE LOWER('%{nama_dosen}%')`
        2. **Fallback**:
            - Jika pencarian dengan nama tidak berhasil, coba dengan field lain seperti NIP atau email jika tersedia dalam pertanyaan.
            - Jika nama tidak lengkap atau terdapat kesalahan ketik, gunakan pencarian berbasis kemiripan string.
        3. **Handle Multiple Results**:
            - Jika hasil lebih dari satu dosen, berikan daftar singkat dari beberapa hasil yang paling relevan dengan deskripsi yang singkat.

    ### Table: penelitians
    - Fields: judul, tahun_penelitian, sumber_dana
    - Description: Penelitian informatika
    - Query: `SELECT judul, tahun_penelitian, sumber_dana FROM penelitians`
    - Instruction: Jika ada pertanyaan mengarah ke penelitian atau ada kemiripan dengan judul di tabel penelitians, berikan judul + tahun_penelitian + sumber_dana.
    - **Identifikasi Kemiripan**:
        - Jika pertanyaan berisi frasa yang cocok atau mirip dengan judul dalam tabel `penelitians`, berikan judul + tahun_penelitian + sumber_dana yang sesuai.
        - Query: `SELECT judul, tahun_penelitian, sumber_dana FROM penelitians WHERE LOWER(judul) LIKE LOWER('%{frasa}%')`
        - Gunakan sanitasi input untuk menghindari masalah dengan karakter khusus dalam frasa.
        - Jika pencarian dengan frasa tidak berhasil, coba dengan pencarian berbasis kata kunci yang ada dalam judul.
        - Jika terdapat beberapa hasil, berikan daftar singkat dari hasil yang paling relevan.
    - **Permintaan Penelitian Terbaru**:
        - Jika pertanyaan meminta penelitian terbaru, atau beberapa penelitian terbaru, berikan hasil yang diurutkan berdasarkan kolom `tahun_penelitian` dari yang terbaru ke yang terlama.
        - Query: `SELECT judul, tahun_penelitian, sumber_dana FROM penelitians ORDER BY tahun_penelitian DESC LIMIT {jumlah}`
        - Jika jumlah penelitian tidak disebutkan, berikan satu penelitian terbaru sebagai default.

    ### Table: pengabdians
    - Fields: judul, tahun, sumber_dana
    - Description: Pengabdian informatika
    - Query: `SELECT judul, tahun, sumber_dana FROM pengabdians`
    - Instruction: Jika ada pertanyaan mengarah ke pengabdian atau ada kemiripan dengan judul di tabel pengabdians, berikan judul + tahun + sumber_dana.
    - **Identifikasi Kemiripan**:
        - Jika pertanyaan berisi frasa yang cocok atau mirip dengan judul dalam tabel `pengabdians`, berikan judul + tahun + sumber_dana yang sesuai.
        - Query: `SELECT judul, tahun, sumber_dana FROM pengabdians WHERE LOWER(judul) LIKE LOWER('%{frasa}%')`
        - Gunakan sanitasi input untuk menghindari masalah dengan karakter khusus dalam frasa.
        - Jika pencarian dengan frasa tidak berhasil, coba dengan pencarian berbasis kata kunci yang ada dalam judul.
        - Jika terdapat beberapa hasil, berikan daftar singkat dari hasil yang paling relevan.
    - **Permintaan Pengabdian Terbaru**:
        - Jika pertanyaan meminta pengabdian terbaru, atau beberapa pengabdian terbaru, berikan hasil yang diurutkan berdasarkan kolom `tahun` dari yang terbaru ke yang terlama.
        - Query: `SELECT judul, tahun, sumber_dana FROM pengabdians ORDER BY tahun DESC LIMIT {jumlah}`
        - Jika jumlah pengabdian tidak disebutkan, berikan satu pengabdian terbaru sebagai default.

    ### Table: publikasis
    - Fields: judul, deskripsi, oleh, anggota, tahun, link
    - Description: Publikasi informatika
    - Query: `SELECT judul, deskripsi, oleh, anggota, tahun, link FROM publikasis`
    - Instruction: Jika ada pertanyaan mengarah ke publikasi atau ada kemiripan dengan judul di tabel publikasis, berikan judul + deskripsi + oleh + anggota + tahun + link.
    - **Identifikasi Kemiripan**:
        - Jika pertanyaan berisi frasa yang cocok atau mirip dengan judul dalam tabel `publikasis`, berikan judul + deskripsi + oleh + anggota + tahun + link yang sesuai.
        - Query: `SELECT judul, deskripsi, oleh, anggota, tahun, link FROM publikasis WHERE LOWER(judul) LIKE LOWER('%{frasa}%')`
        - Gunakan sanitasi input untuk menghindari masalah dengan karakter khusus dalam frasa.
        - Jika pencarian dengan frasa tidak berhasil, coba dengan pencarian berbasis kata kunci yang ada dalam judul.
        - Jika terdapat beberapa hasil, berikan daftar singkat dari hasil yang paling relevan.
    - **Permintaan Publikasi Terbaru**:
        - Jika pertanyaan meminta publikasi terbaru, atau beberapa publikasi terbaru, berikan hasil yang diurutkan berdasarkan kolom `tahun` dari yang terbaru ke yang terlama.
        - Query: `SELECT judul, deskripsi, oleh, anggota, tahun, link FROM publikasis ORDER BY tahun DESC LIMIT {jumlah}`
        - Jika jumlah publikasi tidak disebutkan, berikan satu publikasi terbaru sebagai default.

    ### Table: pages
    - Fields: title, content
    - Description: Informasi tambahan seperti profil departemen, fasilitas, staff administrasi, struktur organisasi, dll.
    - Query: `SELECT title, content FROM pages`
    - Instruction: Jika ada pertanyaan mengarah ke informasi tambahan atau ada kemiripan dengan title di tabel pages, berikan content yang sesuai.
    - **Identifikasi Kemiripan**:
        - Jika pertanyaan berisi frasa yang cocok atau mirip dengan title dalam tabel `pages`, berikan content yang sesuai.
        - Query: `SELECT title, content FROM pages WHERE LOWER(title) LIKE LOWER('%{frasa}%') OR LOWER(content) LIKE LOWER('%{frasa}%')`
        - Gunakan sanitasi input untuk menghindari masalah dengan karakter khusus dalam frasa.
        - Jika pencarian dengan frasa tidak berhasil, coba dengan pencarian berbasis kata kunci yang ada dalam title atau content.
        - Jika terdapat beberapa hasil, berikan daftar singkat dari hasil yang paling relevan.

    ### Table: components_subpage_subpages
    - Fields: title, content
    - Description: Informasi tambahan lainnya seperti visi, misi, tujuan, sasaran, profil program sarjana, profil program magister, capaian, kurikulum, fasilitas, dsb.
    - Query: `SELECT title, content FROM components_subpage_subpages`
    - Instruction: Jika ada pertanyaan mengarah ke informasi tambahan lainnya atau ada kemiripan dengan title di tabel components_subpage_subpages, berikan content yang sesuai.
    - **Identifikasi Kemiripan**:
        - Jika pertanyaan berisi frasa yang cocok atau mirip dengan title dalam tabel `components_subpage_subpages`, berikan content yang sesuai.
        - Query: `SELECT title, content FROM components_subpage_subpages WHERE LOWER(title) LIKE LOWER('%{frasa}%') OR LOWER(content) LIKE LOWER('%{frasa}%')`
        - Gunakan sanitasi input untuk menghindari masalah dengan karakter khusus dalam frasa.
        - Jika pencarian dengan frasa tidak berhasil, coba dengan pencarian berbasis kata kunci yang ada dalam title atau content.
        - Jika terdapat beberapa hasil, berikan daftar singkat dari hasil yang paling relevan.

    **Instruksi Umum:**
    - Analisis pertanyaan user untuk menentukan tabel dan kolom yang relevan.
    - Jika pertanyaan mendetail (seperti "berikan saya NIP dosen A"), fokus pada kolom spesifik yang diminta.
    - Formulasikan kueri SQL yang tepat dan berikan jawaban berdasarkan hasil kueri.
    - Jika informasi minimal, buat respon lebih natural dan informatif.
    - Jangan menyertakan field `created_at` di output.
    - Kueri SQL tidak boleh diawali atau diakhiri dengan ```.
    - Jika terjadi error atau query lama, kembalikan output kosong saja.

    **Logika Fallback:**
    - Jika pertanyaan tidak menghasilkan data setelah beberapa kali percobaan, gunakan pola pencarian alternatif:
        - Cari di tabel yang kemungkinan terkait berdasarkan konteks umum dari pertanyaan.
        - Gunakan deskripsi atau field yang mirip dengan pertanyaan user untuk mencocokkan hasil.

    Contoh Implementasi:
    1. Analisis pertanyaan user.
    2. Tentukan tabel dan kolom yang relevan berdasarkan deskripsi tabel.
    3. Formulasikan kueri SQL yang tepat.
    4. Berikan jawaban yang sesuai berdasarkan hasil kueri.
    5. Jika informasi minimal, buat respon lebih natural dan informatif tanpa mengada-ada.

    Fokuslah untuk selalu memberikan jawaban yang singkat, tepat, dan informatif.
    """
    ]

    sentence = tokenize(msg)
    sentence = [stem(word, lang) for word in sentence]  # Melakukan proses stemming pada setiap kata dalam kalimat
    X = bag_of_words(sentence, all_words, lang)
    X = X.reshape(1, X.shape[0])
    X = torch.from_numpy(X).to(device)

    output = model(X)
    _, predicted = torch.max(output, dim=1)

    tag = tags[predicted.item()]

    probs = torch.softmax(output, dim=1)
    prob = probs[0][predicted.item()]

    if prob.item() > 0.95:
        for intent in intents['intents']:
            if tag == intent["tag"]:
                return random.choice(intent['responses'])
    else:
        # Call function to get response from Gemini model
        response = get_gemini_response(msg, prompt)

        # Check if response is empty or null
        if not response or response.strip() == "":
            return "Maaf, saya tidak memiliki informasi yang sesuai dengan pertanyaan Anda..."

        # Define MySQL connection details
        mysql_host = 'localhost'
        mysql_username = 'root'
        mysql_password = ''
        mysql_database = "informatika"

        # Execute the SQL query and fetch results
        try:
            response_data = read_sql_query(response, mysql_host, mysql_username, mysql_password, mysql_database)
            if response_data:
                return response_data
            else:
                return "Maaf, saya tidak memiliki informasi yang sesuai dengan pertanyaan Anda..."
        except Exception as e:
            print(f"Error occurred: {e}")
            return "Tidak ditemukan data yang cocok dengan pertanyaan Anda, coba tanyakan kembali dengan pertanyaan yang lebih spesifik dan pastikan tidak terjadi kesalahan penulisan..."


if __name__ == "__main__":
    print("Let's chat! (type 'quit' to exit)")
    while True:
        # sentence = "do you use credit cards?"
        sentence = input("You: ")
        if sentence == "quit":
            break

        resp = get_response(sentence)
        print(resp)

