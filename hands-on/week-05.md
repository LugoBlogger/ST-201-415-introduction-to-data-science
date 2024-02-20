# Modul praktikum - Minggu 05 - Data Smoothing 

Dosen pengampu: **Henokh Lugo Hariyanto**; **Diana Nurlaily**   
Asisten mata kuliah: **Ukthi Nurul Isnaniah (16211028)**

**Tujuan**:
- Mampu melakukan proses _data smoothing_ dengan bahasa pemrograman Python 
- Mampu menjelaskan pola di dalam data menggunakkan kurva _smoothing_

> Tips belajar bahasa pemrograman adalah mengetik ulang perintah yang kita
> temukan di buku ataupun di internet, lalu kita ubah-ubah untuk menguji 
> pemahaman kita sudah tepat atau belum. Faktor bermain-main dan eskplorasi
> sangat diperlukan untuk memahami setiap perintah bahasa pemrograman yang
> kita pelajari. Setiap potongan kode di bawah dapat dijalankan secara lokal
> menggunakan VSCode dan Jupyter Notebook, atau menggunakan Google Collabs.

Panduan berikut diambil dari:
- [(Albert, 2023) - A Course in Exploratory Data Analysis](https://bayesball.github.io/EDA/)
- [(Velleman and Hoaglin, 1981) - Applications, Basics, and Computing of Exploratory Data Analysis](https://ecommons.cornell.edu/bitstreams/e5688170-b7d4-4e35-9ba0-ee51b3bed1b4/download)

Teknik data smoothing, merupakan teknik yang cukup populer terutama dalam
dunia _image processing_. Dengan teknik ini kita bisa mendapatkan gambar yang
lebih _smooth_ dalam pengertian menghilangkan _noise_ akibat kerusakan pixel.

Namun dalam perkuliahan/tutorial ini kita **TIDAK** mempelajari penerapan
_data smoothing_ terhadap data gambar tetapi ke data _time series_ atau 
menggunaan istilah yang lebih tepat adalah _sequences_. Disebut _sequences_
karena kita tidak terlalu memperhatikan nilai dari variabel di sumbu-x
dengan asumsi variabel tersebut sudah diurutkan berdasarkan urutan kejadian
(_chronological order_)

Kita juga akan menggunakan data jumlah pengunjung pertandingan
_baseball_ untuk tim [Atlanta Braves](https://www.mlb.com/braves)
pada musim pertandingan di tahun 1995.

## Data Smoothing 
Ide besar _data smooting_ adalah bagaimana kita dapat mempertahankan
pola trend yang lebih bebas daripada pola trend dari garis linear.
Kita juga ingin hasil kurva smoothing yang kita peroleh tetap memberikan
pola trend yang masih tidak dipengaruhi oleh ada tidaknya _outliers_.

Kita sudah belajar pada pertemuan sebelumnya bahwa _resistant line_ cukup
baik menggambarkan trend linear dari suatu data yang memiliki hubungan
linear apabila terdapat _outliers_. Jika _resistant line_ digunakan
untuk model linear, maka _data smoothing_ yang kita pelajari saat ini
digunakan untuk model _smoothing_ yang lebih umum dari garis linear.
Bisa disebut bahwa kurva _smoothing_ yang dihasilkan adalah model 
nonlinear.

Menurut (Velleman dan Hoaglin, 1981) ada dua prosedur smoothing
yang cukup baik diterapkan untuk data-data yang berfluktuasi tinggi
yaitu _smoothing procedure_ dengan kode: 
1. **3RSSH.twice**: 
   1. **"3R"**: _repeated running median of 3_
   2. **"SS"**: _two times splitting_
   3. **"H"**: _hanning smoothing_
   4. **".twice"**: apply 3RSSH to rough (residual data)
2. **4253H.twice**. 
   1. **"42"**: _running median of 4_ + _recentering median of 2_  
   2. **"5"**: _running median of 5_
   3. **"3"**: _running median of 3_
   4. **"H"**: _hanning smoothing_
   4. **".twice"**: apply 4253H to rough (residual data)

Namun pada tutorial ini, kita cukup mempelajari 
_smoothing procedure_ yang pertama. Di akhir tutorial kalian
diharapkan dapat menghasilkan kurva _smoothing_ sebagai berikut
dan juga akan diberikan bagaimana membaca hasil kurva _smoothing_
tersebut

<img src="../img-resources/smoothing-3RSSHtwice.png" width=400>

Ada 6 tahapan yang akan buat dengan menggunakan Python untuk dapat
membuat _smoothing procedure_ **3RSSH.twice**:
1. _Running median of 3_ (dengan lebar jendela sebesar 3)
2. _End value smoothing_
3. _Repeated running median of 3_
4. _Splitting_
5. _Hanning_
6. _Reroughing_

Semua fungsi untuk melakukan _smoothing procedures_ sudah tersedia dalam 
berkas `eda/smoothing.py`.

1. Buatlah berkas _jupyter notebook_ dengan nama `smoothing-albert.ipynb`.
   Isi dengan modul Python untuk pengolahan _array_, tabel, _plotting_, dan  modul `eda/smoothing.py`berikut:
   ```py
   import numpy as np
   import pandas as pd
   import matplotlib.pyplot as plt
   import eda.smoothing as eda_smt
   ```

2. Bacalah data `./datasets/braves.attendance.txt` menggunakan Pandas
   dengan kode Python sebagai berikut:
   ```py
   df = pd.read_table("./datasets/braves.attendace.txt")
   df
   ```

3. Lakukan _plotting_ data yang sudah dipanggil tersebut menggunakan 
   Matplotlib
   ```py
   fig, ax = plt.subplots(figsize=[6, 4])

   ax.plot(df["Game"], df["Attendance"], marker='o', linestyle="None",
           markersize=4)

   ax.grid("on")
   ax.set_xlabel("Game")
   ax.set_ylabel("Attendance (x 100 people)")
   ax.set_title("Home attendance for the Atlanta Braves baseball team",
               fontsize="medium")

   plt.show(fig)
   ```

   Jika langkah-langkah di atas dijalankan dengan benar, maka akan didapatkan
   hasil sebagai berikut

   <img src="../img-resources/smoothing-data-plot.png" width=400>

## _Running median of 3_

Tahap _smoothing_ yang akan kita implementasikan ke dalam Python adalah
_running median of 3_. Teknik _smoothing_ ini mengambil secara terus menerus
tiga data berurutan dan kemudian dihitung nilai median dari tiga data tersebut.

Untuk lebih jelas dapat dilihat gambar berikut:

<img src="../img-resources/running-medians.png" width=400>

Pada contoh di atas terdapat 5 buah data yang akan kita lakukan _smoothing_
yaitu $(y_1, y_2, y_3, y_4, y_5)$. _Running median_ dihitung dengan cara
mengambil tiga data pertama $(y_1, y_2, y_3)$ lalu dihitung nilai median dari
tiga data tersebut dan didapatkan nilai _smoothing_, $z_1$. Kita lakukan
selanjutnya pada tiga data berikutnya dengan cara menggeser *window* ke kanan
sejauh satu satuan data yaitu data $(y_2, y_3, y_4)$ dan didapatkan nilai 
_smoothing_ $z_2$. Lakukan sampai *window* menyentuh ujung data terakhir ($y_5$).

Untuk contoh di atas terlihat ada titik data yang hilang pada ujung kiri dan
kanan. Untuk mengestimasi nilai _smooting_ data _endpoints_ tersebut
kita akan lanjutkan pada tahap berikutnya _end value smoothing_.

Implementasi proses _running median of 3_ ke dalam kode Python adalah 
sebagai berikut

```py
smooth3_noEnd = df["Attendance"].rolling(window=3, center=True).median()
smooth3_noEnd
```

Pada kode di atas, kita menggunakan _method_ yang disediakan oleh objek
`pandas.Series` untuk melakukan operasi _rolling_ (bahasa lain untuk _running_
dalam _running median_). Kemudian kita tambahkan opsi `center=True` untuk
membuat perhitungan akhir median menyisakan _end value_ NaN pada bagian pertama
dan terakhir. Lalu setelah kita menerapkan _method_ `.rolling()`, kita terapkan
fungsi yang akan kita gunakan selama proses _rolling_ yaitu `.median()`.

4. Tulis potongan kode di atas dalam berkas _jupyter notebook_ yang sudah
   dibuat pada tahap sebelumnya.

   Jika tahapan di atas dijalankan dengan benar makan akan ditampilkan hasil
   _running median of 3_ sebagian berikut

   <img src="../img-resources/smoothing-median3-noEnd.png" width=400>


## _End value smoothing_
Pada tahap ini kita akan mengisi ujung pertama dan terakhir dari hasil 
di tahap sebelumnya yaitu indeks 0 dan 71 pada variabel `smooth3_noEnd`.

Untuk menentukan nilai _smooth_ dari _endpoints_ tersebut, kita perlu memahami
tiga buah kasus 

<img src="../img-resources/smoothing-evs-cases.png" width=1000>

- **Case 1**. Nilai _end value_ berada diluar rentang dua kali selisih
  antara dua _smoothed data_ terdekat dari _end value_.
  Pada kasus ini, nilai _end value_ diestimasi nilai _smoothing_-nya
  sebagai batas terdekat dengan nilai _end value_. Batas ini merupakan 
  batas yang didapatkan dengan menambahkan atau mengurangi _smoothed data_
  terdekat pertama dengan dua kali nilai selisih dari dua _smoothed data_
  terdekat pertama dan kedua dari _end value_. Pada gambar di atas selisih
  dua nilai _smoothed data_ terdekat pertama dan kedua adalah $\Delta y$.
  Lalu batas atas dan bawah ditunjukkan pada interval garis vertikal
  yang memuat tulisan $2\Delta y$.

- **Case 2**. Nilai _end value_ berada didalam rentang dua kali selisih
  antara dua nilai _smoothed data_ terdekat pertama dan kedua dari _end value_.
  Pada gambar di atas terlihat titik berwarna biru berada dalam rentang
  inteval garis vertikal bertuliskan $2\Delta y$. Untuk kasus ini 
  nilai _smoothing_ untuk _end value_ adalah dirinya sendiri (tidak berubah)

- **Case 3**. Selisih antara nilai _smoothed data_ pertama dan kedua dari 
  _end value_ adalah nol. Pada kasus ini, nilai _smoothing_ untuk 
  _end value_ adalah nilai _smoothed data_ terdekat pertama.

Ketiga _cases_ di atas telah diimplentasikan ke dalam dua fungsi `get_evs()`
yang terdapat di dalam berkas `eda/smoothing.py`.

5. Kalian tidak perlu menuliskan ulang kode Pyton untuk `get_evs()`
   Cukup memanggil fungsi `apply_evs()` yang tersedia di dalam 
   modul `eda/smoothing.py`. Tuliskan kode Python berikut ke cell baru
   di dalam berkas _jupyter notebook_ yang sudah kalian buat
   ```py
   eda_smt.apply_evs(df["Attendance"].to_list(), smooth3_noEnd)
   eda_smt.apply_evs
   ```

   Jika tahap di atas dijalankan dengan benar, maka akan didapatkan
   hasil sebagai berikut untuk penerapan `apply_evs` ke variabel
   `smooth3_noEnd`. Terlihat nilai di indeks pertama dan terakhir sudah terisi
   dengan angka yang mengestimasi nilai _smoothing_ untuk _end values_.

   <img src="../img-resources/smoothing-evs-results.png" width=400>

## _Repeated running median of 3_

Dua tahap yang kita telah pelajari sebelumnya merupakan satu-kesatuan 
prosedur _smoothing_ yang disebut dengan kode **`3`** (gabungan
_running median of 3_ dan _end value smoothing_). Karena hasil yang didapatkan
setelah proses _smoothing_ ini memiliki panjang data yang sama, maka kita
bisa menerapkan prosedur _smoothing_ ini berkali-kali.
Jika kita terapkan prosedur **`3`** ini berkali-kali hingga tidak terjadi 
perubahan, maka proses yang kita lakukan dinamakan dengan kode **`3R`**.

Di dalam modul `eda/smoothing.py`, telah disediakan dua fungsi untuk melakukan
smoothing dengan kod **`3`** dan dengan kode **`3R`** yaitu
`apply_3()` dan `apply_3R()`.

6. Jalankan `apply_3()` dan `apply_3R()` dari modul `eda/smooting` terhadap
   DataFrame `df` yang telah didefinisian di tahapan sebelumnya.
   Kalian dapat mengetikan perintah berikut

   ```py
   df["Smooth3"] = eda_smt.apply_3(df["Attendance"].to_numpy())
   df["Smooth3R"] = eda_smt.apply_3R(df["Attendance"].to_numpy())[1]
   df
   ```
   
   Terdapat indeks `[1]` dalam fungsi _smoothing_ kode **`3R`**, karena
   dalam implementasi kode Python terdapat dua output yang pertama 
   (indeks `[0]`) menyatakan
   indeks saat kapan proses _smoothing_ **`3`** konvergen, output yang
   kedua (indeks `[1]`) hasil _smoothing_. Dan kita cukup menggunakan
   output yang kedua.

7. Lakukan _plotting_ untuk kolom `df["Smooth3"]` dan `df["Smooth3R"]`
   menggunakan Matplotlib. Gunakan kode Python berikut:
   
   ```py
   fig, ax = plt.subplots(figsize=[8, 4])

   ax.plot(df["Game"], df["Attendance"], marker='o', linestyle="None",
           markersize=4, zorder=2, label=None)
   ax.plot(df["Game"], df["Smooth3"], linestyle="-", linewidth=1, alpha=1,
           zorder=2, label="3")
   ax.plot(df["Game"], df["Smooth3R"], linestyle="-", linewidth=1, alpha=1,
           zorder=3, label="3R")

   ax.grid("on")
   ax.set_xlabel("Game")
   ax.set_ylabel("Attendance (x 100 people)")
   ax.set_title("Home attendance for the Atlanta Braves baseball team",
                fontsize="medium")
   ax.legend(loc="best")

   plt.show(fig)
   ```

   Jika tahapan di atas dilakukan dengan benar, maka akan didapatkan tabel 
   dan gambar sebagai berikut

   <table>
     <tr>
       <td> <img src="../img-resources/smoothing-code-3-and-3R.png" width=200>
       <td> <img src="../img-resources/smoothing-code-3-and-3R-plot.png" width=350>
   </table>

## _Spliting_
Jika kita lihat hasil tahap sebelumnya (kurva warnah hijau), kita
menemukan ada puncak-puncak datar dan lembah-lembah datar.
Pada tahap _splitting_ ini kita akan melakukan _smoothing_ dan 
hanya berfokus pada _2-high peaks_ dan _2-low valleys_.

Ilustrasi di bawah ini menunjukkan kondisi data saat terjadi 
_2-high peaks_ dan _2-low valleys_

<table>
  <tr>
    <td> <img src="../img-resources/smoothing-2-high-peaks.png" width=300>
    <td> <img src="../img-resources/smoothing-2-low-valleys.png" width=300>
</table>

<img src="../img-resources/smoothing-2-high-peaks-2-low-peaks-identification.png">

_2-high peaks_ terjadi saat ada dua puncak yang memiliki nilai yang sama namun nilai di sekeliling dua puncak tersebut lebih rendah. 
_2-low valleys_ terjadi saat ada dua lembah yang memiliki nilai yang sama namun
nilai di sekeliling dua lembah tersebut lebih tinggi.

Pada gambar _zoom in_ kurva _smoothing_ **`3R`**, terlihat ada dua buah
_2-high peaks_ dan satu buah _2-low-valleys_. Perlu diperhatikan harus
terdapat dua nilai yang sama dan dikeliling oleh dua nilai yang lebih besar
dari dua puncak yang sama itu. Jika terdapat tiga puncak atau lebih yang
bernilai sama, maka bukan disebut _2-high peaks_.

Ada tiga _subprocedure_ untuk dapat melakukan proses _splitting_, yaitu: 1) 
perlu mengidentifikasi lokasi _2-high peaks_ dan _2-low valleys_; 2) melakukan
pemisiahan _left sequence_ dan _right sequence_ berdasarkan lokasi
_2-high peaks_ dan _2-low valleys_. Untuk _left sequence_ dilakukan 
_end value smoothing_ di ujung kanan. Untuk _right sequence_ dilakukan 
_end value smoothing_ di ujung kiri. Setelah itu, kedua _sequences_ digabung.
Berikut ilustrasi untuk proses _splitting_

<img src="../img-resources/splitting.png" width=400>

Dalam tutorial ini tidak akan dijelaskan secara detail implementasi 
proses _splitting_ ke dalam kode Python, namun kalian dapat melihat 
implementasi tersebut dalam kode Python sebagai fungsi `scan_peak_or_valley()`,
`apply_evs_in_split()` dan `apply_S()` di dalam modul `eda/smoothing.py`.

8. Jalan kode berikut untuk melakukan proses _splitting_ terhadap hasil
   yang didapatkan dari langkah sebelumnya yaitu hasil dari proses _smoothing_
   dengan kode **`3R`**.

   ```py
   df["Smooth3RSS"] = eda_smt.apply_S(
    eda_smt.apply_S(
      df["Smooth3R"].to_numpy()))
   df
   ```

   Kode di atas akan menjalankan dua kali proses _splitting_.

9. Buatlah plot untuk kolom `df["Smooth3RSS"]`

## _Hanning_

## _Reroughing_


## Tugas (Exercise 03)
> Laporan harus ditulis dan dikumpulkan dalam bentuk berkas _markdown_ 
> (berekstensi `.md`). Apabila laporan memuat lebih dari satu beras, misal
> memuat gambar `.png` atau `.jpg`, maka berkas disatukan menjadi berkas 
> `.zip`. **PASTIKAN** berkas `.md` sudah dilakukan _preview_, sehingga kod
> `markdown` bisa di-_preview_ dengan benar di VSCode. Format penamaan file: 
> `NIM_NAMA.md` atau `NIM_NAMA.zip`  (boleh nama lengkap atau nama panggilan).
>
> **Contoh format laporan atau jawaban (`NIM_NAMA.md`)**
> Nama: [NAMA LENGKAP]
> NIM: [NIM]
> 1. (Jawaban nomor 1)
> 2. (Jawaban nomor 2)

1. [30 poin]
   Bacalah literatur kedua yang disebutkan di awal tutorial (Velleman and Hoaglin, 1981)
   dan jelaskan prosedur _smoothing_ dengan kode **`4253H.twice`**.

2. [70 poin] 
   Terapkan prosedur _smoothing_ di atas (**`3RSSH.twice`**)
   untuk data suhu sapi yang diukur setiap 5 menit (sumber data: [(de Alba and Zartman, 1979) page 137](https://archive.org/details/analysingtimeser0000unse)

   <img src="../img-resources/cow-temperatures-beeps-5-mins.png" width=600>
   
   [Hint] Data dibaca dari kiri ke kanan lalu dari atas ke bawah.
   Kurangi setiap nilai diatas dengan 800 untuk mendapatkan
   suhu sapi. Gunakan sumbu-x dengan periode dari 1 hingga total data.
