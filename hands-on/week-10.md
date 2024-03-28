# Modul praktikum - Minggu 10 - Classification model

Dosen pengampu: **Henokh Lugo Hariyanto**; **Diana Nurlaily**   
Asisten mata kuliah: **Ukthi Nurul Isnaniah (16211028)**

**Tujuan**:
- Mampu memahami tahapan-tahapan penggunaan model klasifikasi yang 
  disedikan oleh _library_ `scikit-learn`. 
- Mampu menjelaskan perbedaan (kelebihan dan kekurangan) untuk tiga model
  klasifikasi yaitu k-NN, SVM, dan Decisition Tree. 

> Tips belajar bahasa pemrograman adalah mengetik ulang perintah yang kita
> temukan di buku ataupun di internet, lalu kita ubah-ubah untuk menguji 
> pemahaman kita sudah tepat atau belum. Faktor bermain-main dan eskplorasi
> sangat diperlukan untuk memahami setiap perintah bahasa pemrograman yang
> kita pelajari. Setiap potongan kode di bawah dapat dijalankan secara lokal
> menggunakan VSCode dan Jupyter Notebook, atau menggunakan Google Colab.

Dalam pertemuan ini kita akan mempelajar tiga model dasar yang digunakan untuk   
melakukan klasifikasi. Sebagai pembanding, kita akan menggunakan dataset yang   
sama untuk ketiga model yang akan kita buat. Di akhir tutorial ini diharapkan  
dapat mengerti perbedaan ketiga model tersebut melalui hasil yang diberikan.

## Masalah klasifikasi
Masalah yang kita ambil dalam tutorial ini adalah masalah klasifikasi, yaitu   
diberikan pasangan input/feature dan output/label data, kita mencari model   
yang mampu menghubungkan dua pasangan data tersebut. Agar kita dapat memahami  
penggunaan model klasifikasi ke data yang dikumpulkan dari pengukuran langsung   
di lapangan, kita akan menggunakan contoh dataset yang terkenal yaitu 
[California housing dataset](https://www.dcc.fc.up.pt/~ltorgo/Regression/cal_housing.html)

Dataset ini terdiri dari 20,640 samples dengan dimensi input/feature sebanyak 
8, dan output/label berupa bilangan riil antara 0.15 sampai 5 (dengan 
satuan $100,000). Karena problem yang akan diselesaikan adalah masalah klasifikasi
dan output/label bernilai kontinyu, maka kita perlu membagi nilai label ini
ke dalam beberapa _bins_ supaya menjadi data kategori.

Untuk itu kita perlu melakukan plot dan melihat nilai _bins_ yang cocok untuk 
data label ini

## $k$-Nearest Neighbors



## Support Vector Machine


## Decision Tree