"""
Module with common functions used across application
"""
import pathlib
import subprocess


def clear_data():
    state_file = f'{pathlib.Path(__file__).parent}/state/current_state.json'
    state_data_folder = f'{pathlib.Path(__file__).parent}/state/data'
    subprocess.run(['rm', '-f', state_file])
    subprocess.run(f'rm -rf {state_data_folder}/*', shell=True)
