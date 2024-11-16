import requests

valid_rfid = ['0178526309']  # Daftar RFID yang valid

def fetch_data(url, data, should_read_input):
    try:
        # Mengirimkan request GET ke API
        response = requests.get(url, params=data)
        
        # Jika status kode 200, berarti data berhasil dikirim
        if response.status_code == 200:
            print(f"Data berhasil dikirim: {data}")
            # Lakukan sesuatu dengan response jika perlu, misalnya membuka pintu
        else:
            print(f"Error: Koneksi gagal dengan status kode {response.status_code}")
            
            # Validasi RFID jika status kode bukan 200
            if data['rfid'] in valid_rfid:
                print(f"RFID {data['rfid']} valid, namun koneksi ke API gagal.")
            else:
                print(f"RFID {data['rfid']} tidak valid.")

    except requests.RequestException as e:
        print(f"Terjadi kesalahan saat mengirim request: {e}")
