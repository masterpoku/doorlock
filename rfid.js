const fs = require('fs');

// Ganti dengan path perangkat RFID Anda
const devicePath = '/dev/input/event4';

// Buka stream dari perangkat
const deviceStream = fs.createReadStream(devicePath);

deviceStream.on('open', () => {
    console.log(`Device ${devicePath} opened.`);
});

deviceStream.on('error', (err) => {
    console.error(`Error accessing device: ${err.message}`);
    process.exit(1);
});

// Membaca data
deviceStream.on('data', (chunk) => {


    const hexData = chunk.toString('hex'); // Data hexadecimal

    // Mengambil ID RFID dari data mentah (asumsikan ID panjang 10 karakter heksadesimal)
    const rfidId = extractRFID(hexData);

    // Jika ID RFID ditemukan, konversi ke angka desimal
    if (rfidId) {

        console.log(`RFID ID (Hex): ${rfidId}`);

    } else {
        console.log('ID RFID tidak ditemukan.');
    }
});

// Fungsi untuk mengekstrak ID RFID dari data heksadesimal
function extractRFID(hexString) {
    // Asumsikan ID RFID adalah bagian pertama dari data, misalnya 10 karakter pertama (5 byte)
    const rfidLength = 10; // Panjang ID RFID dalam karakter hex (5 byte = 10 karakter hex)
    return hexString.slice(0, rfidLength); // Ambil segmen pertama sebagai ID RFID
}