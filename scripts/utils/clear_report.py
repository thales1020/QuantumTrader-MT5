#clear all file in reports folder
import os
import shutil

reports_dir = 'reports'
if os.path.exists(reports_dir):
    shutil.rmtree(reports_dir)
os.makedirs(reports_dir, exist_ok=True)
