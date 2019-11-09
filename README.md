# Tugas Besar 2 IF3130 - Jaringan Komputer

## Nama Kelompok

    KomiCantNetwork

## Petunjuk Penggunaan Program 

1. Jalankan "python server.py" atau "python3 server.py" 
2. Gunakan "ngrok http 12000" untuk membuat endpoint websocket menjadi public
3. Client yang akan dijalankan harus menggunakan URL websocket yang diberi oleh ngrok (misal di ngrok http://e156f178.ngrok.io, maka URL websocketnya adalah ws://e156f178.ngrok.io)
4. Ada 3 perintah yang bisa dikirimkan client:
    a. "!echo <string>" untuk mengirimkan string kembali ke client
    b."!submission" untuk mengirimkan file server.py dan README.md yang sudah di zip menjadi 1 file bernama "Jarkom2_KomiCantNetwork.zip"   
    c.Kirim lagi file yang diterima untuk mengecek md5 dari file yang terkirim apakah sama dengan md5 file pada server

## Pembagian Tugas

|Nim     |Nama                       |Pembagian kerja|Persentase|
|--------|---------------------------|---------------|----------|
|13517004|Bimo Adityarahman Wiraputra| server.py     |33.33 %   |
|13517040|Ariel Ansa Razumardi       | server.py     |33.33 %   |
|13517058|Ahmad Rizqee Nurhani       | server.py     |33.33 %   |