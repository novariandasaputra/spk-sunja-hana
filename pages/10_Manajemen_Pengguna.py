"""
pages/10_Manajemen_Pengguna.py — Halaman 11: Manajemen Pengguna
"""
import streamlit as st
import sys
import os

# Ensure root directory is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from views.manajemen_pengguna import show

if __name__ == "__main__":
    if not st.session_state.get("logged_in", False):
        st.warning("Silakan login terlebih dahulu melalui halaman utama.")
    else:
        show()
