"""
pages/3_Data_Penjualan.py — Halaman 4: Data Penjualan Bulanan
"""
import streamlit as st
import sys
import os

# Ensure root directory is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from views.data_penjualan import show

if __name__ == "__main__":
    if not st.session_state.get("logged_in", False):
        st.warning("Silakan login terlebih dahulu melalui halaman utama.")
    else:
        show()
