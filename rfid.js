const fs = require('fs');
const readline = require('readline');

// Path ke device input RFID, ganti sesuai dengan perangkat Anda.
const devicePath = '/dev/input/event4';

// Buka stream ke perangkat input
const deviceStream = fs.createReadStream(devicePath);

// Pastikan stream terbuka
deviceStream.on('open', () => {
    console.log(`Device ${devicePath} opened`);
});

// Tangkap error jika perangkat tidak ditemukan
deviceStream.on('error', (err) => {
    console.error(`Error opening device ${devicePath}:`, err.message);
    process.exit(1);
});

// Membaca data input
deviceStream.on('data', (chunk) => {
    const rfidData = chunk.toString('hex'); // Konversi ke format heksadesimal
    console.log(`RFID Data: ${rfidData}`);
});