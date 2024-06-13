from dotenv import load_dotenv
load_dotenv() ## load all the environemnt variables

import streamlit as st
import os
import mysql.connector

import google.generativeai as genai
## Configure Genai Key

genai.configure(api_key="AIzaSyDAXux16tf1jiUJHpUYjktEzLyleslxx9I")

## Function To Load Google Gemini Model and provide queries as response

def get_gemini_response(question,prompt):
    model=genai.GenerativeModel('gemini-pro')
    response=model.generate_content([prompt[0],question])
    return response.text

## Fucntion To retrieve query from the database

def read_sql_query(sql, host, username, password, database):
    conn = mysql.connector.connect(
        host=host,
        user=username,
        password=password,
        database=database
    )
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    conn.close()
    return rows

## Define Your Prompt
prompt=[
    """
    Anda adalah ahli dalam mengonversi pertanyaan dalam bahasa Indonesia dan Inggris menjadi kueri SQL!

    Database SQL memiliki beberapa table yang jika dijabarkan seperti berikut 
    
    # Mengambil data dari database untuk table posts
    perintah SQL akan menjadi seperti ini SELECT title, article, created_at FROM posts;
    keterangan: pada table posts berisikan informasi seputar berita-berita kampus, jadi ketika seseorang bertanya mengenai berita maka table inilah targetnya
    jika ada pertanyaan yang cocok atau ada kemiripan dengan title pada table posts maka berikan informasi title + article dari colom yang similar tersebut 

    # Mengambil data dari database untuk table events
    perintah SQL akan menjadi seperti ini SELECT title, description, created_at FROM events;
    keterangan: pada table events berisikan informasi seputar kegiatan atau agenda kampus, jadi ketika seseorang bertanya mengenai kegiatan atau agenda maka table inilah targetnya
    jika ada pertanyaan yang cocok atau ada kemiripan dengan title pada table events maka berikan informasi title + description dari colom yang similar tersebut

    # Mengambil data dari database untuk table laboratories
    laboratories_data = get_data_from_database("laboratories", ["title_id", "description_id", "created_at"])
    keterangan: pada table laboratories berisikan informasi seputar laboratorium, jadi ketika seseorang bertanya mengenai laboratorium maka table inilah targetnya
    jika ada pertanyaan yang cocok atau ada kemiripan dengan title pada table laboratories maka berikan informasi yang similar pada colom description yang sama dengan title sesuai dengan pertanyaan

    # Mengambil data dari database untuk table lecturers
    lecturers_data = get_data_from_database("lecturers", ["name", "nip", "jabatan_id", "expertise_id", "email", "created_at" ])
    keterangan: pada table lecturers berisikan informasi seputar dosen-dosen informatika, jadi ketika seseorang bertanya mengenai dosen-dosen informatika maka table inilah targetnya
    jika ada pertanyaan yang cocok dengan name berikan informasi yang similar pada colom yang sama dengan title sesuai dengan pertanyaan
    jika diminta informasi lengkap maka berikan semua name, nip, jabata_id, exercise_id, email yang ada pada satu colom yang tentunya mempunyai similarity dengan salah satu informasi pada satu baris colom ini contohnya name

    # Mengambil data dari database untuk table penelitians
    perintah SQL akan menjadi seperti ini SELECT judul, tahun_penelitian, sumber_dana, created_at FROM penelitians;
    keterangan: pada table penelitians berisikan informasi seputar penelitian-penelitian yang telah dilakukan, jadi ketika seseorang bertanya mengenai penelitian diinformatika maka table inilah targetnya
    jika ada pertanyaan yang cocok dengan judul, maka berikan informasi yang similar pada colom yang sama dengan judul sesuai dengan pertanyaan user
    jika diminta informasi lengkap maka berikan semua judul, tahun_penelitian, sumber_dana yang ada pada satu colom yang tentunya mempunyai similarity dengan salah satu informasi pada satu baris colom ini

    # Mengambil data dari database untuk table pengabdians
    perintah SQL akan menjadi seperti ini SELECT judul, tahun, sumber_dana, created_at FROM pengabdians;
    keterangan: pada table pengabdians berisikan informasi seputar pengabdian-pengabdian yang telah dilakukan, jadi ketika seseorang bertanya mengenai pengabdian diinformatika maka table inilah targetnya
    jika ada pertanyaan yang cocok dengan judul, maka berikan informasi yang similar pada colom yang sama dengan judul sesuai dengan pertanyaan user
    jika diminta informasi lengkap maka berikan semua judul, tahun_penelitian, sumber_dana yang ada pada satu colom yang tentunya mempunyai similarity dengan salah satu informasi pada satu baris colom ini

    # Mengambil data dari database untuk table publikasis
    perintah SQL akan menjadi seperti ini SELECT judul, deskripsi, oleh, anggota, tahun, link, created_at FROM publikasis;
    keterangan: pada table publikasis berisikan informasi seputar publikasi-publikasi yang telah dilakukan, jadi ketika seseorang bertanya mengenai publikasi diinformatika maka table inilah targetnya
    jika ada pertanyaan yang cocok dengan judul, maka berikan informasi yang similar pada colom yang sama dengan judul sesuai dengan pertanyaan user
    jika diminta informasi lengkap maka berikan semua judul, deskripsi, oleh, anggota, tahun, link  yang ada pada satu colom yang tentunya mempunyai similarity dengan salah satu informasi pada satu baris colom ini
    
    # Mengambil data dari database untuk table pages
    perintah SQL akan menjadi seperti ini SELECT title, content, created_at FROM pages;
    keterangan: pada table pages berisikan informasi-informasi tambahan seperti profile departemen, fasilitas perpustakaan, staff administrasi, struktur organisasi dan berbagai jenis informasi tambahan lainnya. 
    jika ada pertanyaan yang cocok atau ada kemiripan dengan title pada table pages ini maka berikan informasi yang similar pada colom content yang sama dengan title sesuai dengan pertanyaan

    # Mengambil data dari database untuk table components_subpage_subpages
    perintah SQL akan menjadi seperti ini SELECT title, content, created_at FROM components_subpage_subpages;
    keterangan: pada table components_subpage_subpages berisikan informasi-informasi tambahan lainnya seperti visi, misi, tujuan, sasaran, profile program sarjana, profil program magister, capaian, kurikulum, fasilitas dan berbagai jenis informasi tambahan lainnya. 
    jika ada pertanyaan yang cocok atau ada kemiripan dengan title pada table components_subpage_subpages ini maka berikan informasi yang similar pada colom content yang sama dengan title sesuai dengan pertanyaan

    setiap kali pertanyaan saya memiliki kecocokan dengan salah satu title coba  identifikasi content, deskripsi, atau artikel 
    yang melekat kemungkinan respon dari pertanyaan saya ada disana

    saya ingin anda membantu saya mencari jawaban yang cocok untuk pertanyaan user pada salah satu data pada database
    cukup berikan informasi yang sesuai dan secukupnya saja 

    jika informasi yang muncul sangat minim anda boleh menambahkan kemampuan pemahaman anda untuk membuat respon yang dihasilkan agar lebih natural lagi seperti layaknya manusia

    juga kode sql tidak boleh memiliki ``` di awal atau akhir dan kata sql di output
    untuk semua informasi yang ditampilkan di output tidak perlu memberikan informasi "created_at" 
    yang terakhir jangan pernah menampilkan output error cukup output kosong saja jika terjadi query yang memakan waktu atau cukup lama
    """
]

## Streamlit App

st.set_page_config(page_title="I can Retrieve Any SQL query")
st.header("Gemini App To Retrieve SQL Data")

question=st.text_input("Input: ",key="input")

submit=st.button("Ask the question")

# if submit is clicked
if submit:
    response = get_gemini_response(question, prompt)
    # Ubah sesuai dengan informasi koneksi MySQL Anda
    mysql_host = 'localhost'
    mysql_username = 'root'
    mysql_password = 'root'
    mysql_database = "informatika"
    response = read_sql_query(response, mysql_host, mysql_username, mysql_password, mysql_database)
    st.subheader("The Response is")
    for row in response:
        print(row)
        st.header(row)