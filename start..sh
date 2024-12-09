#!/bin/bash

# Looping terus menerus untuk menjalankan script Python
while true; do
    # Menjalankan script Python
    python3 start.py

    # Jika script Python berhenti atau ada error, program akan tidur selama 1 detik sebelum mencoba lagi
    echo "Script Python berhenti. Menunggu 1 detik sebelum mencoba lagi..."
    sleep 1
done
