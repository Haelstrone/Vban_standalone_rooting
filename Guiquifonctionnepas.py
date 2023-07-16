import tkinter as tk
from tkinter import messagebox
import pyaudio
import os
import subprocess
import sys
import pyVBAN.pyVBAN as pyVBAN
import threading


def apply_settings():
    global vban_recv, vban_send
    # Save the variables and restart the software
    # TODO: Implement saving of variables and software restart
    filename = "save.txt"
    with open(filename, 'w') as file:
        file.write(f"Input Device: {selected_input_device.get()}\n")
        file.write(f"Output Device: {selected_output_device.get()}\n")
        file.write(f"Stream 1 - Received IP: {entry_stream1_ip_received.get()}\n")
        file.write(f"Stream 1 - Received Name: {entry_stream1_name_received.get()}\n")
        file.write(f"Stream 2 - Received IP: {entry_stream2_ip_received.get()}\n")
        file.write(f"Stream 2 - Received Name: {entry_stream2_name_received.get()}\n")
        file.write(f"Stream 1 - Send IP: {entry_stream1_ip_send.get()}\n")
        file.write(f"Stream 1 - Send Name: {entry_stream1_name_send.get()}\n")
        file.write(f"Stream 2 - Send IP: {entry_stream2_ip_send.get()}\n")
        file.write(f"Stream 2 - Send Name: {entry_stream2_name_send.get()}\n")
    print("Variables saved to", filename)

    messagebox.showinfo("VBAN I/O Setup", "Settings applied and saved!")
        # Create separate threads for VBAN send and receive
    recv_thread = threading.Thread(target=start_vban_recv)
    send_thread = threading.Thread(target=start_vban_send)
    
    # Start the threads
    recv_thread.start()
    send_thread.start()

    #root.destroy()
    
def start_vban_recv():
    stream1_ip_received = entry_stream1_ip_received.get()
    stream1_name_received = entry_stream1_name_received.get()
    vban_recv = pyVBAN.VBAN_Recv(stream1_ip_received, stream1_name_received, 6980, output_device_number, verbose=True)
    vban_recv.runforever()


def start_vban_send():
    stream1_ip_send = entry_stream1_ip_send.get()
    stream1_name_send = entry_stream1_name_send.get()
    vban_send = pyVBAN.VBAN_Send(stream1_ip_send, 6980, stream1_name_send, 48000, input_device_number, verbose=True)
    vban_send.runforever()
    

# Redémarrer le programme
    #python = sys.executable
    #subprocess.Popen([python] + sys.argv)
    #root.destroy()


def cancel_settings():
    # Close the app and ask for confirmation to close without saving
    if messagebox.askyesno("VBAN I/O Setup", "Are you sure you want to close without saving?"):
        root.destroy()

#load variable
def load_variables():
    filename = "save.txt"
    variables = {}
    try:
        with open(filename, 'r') as file:
            for line in file:
                try:
                    key, value = line.strip().split(": ")
                    variables[key] = value
                except ValueError:
                    print(f"Ligne mal formatée : {line}")
        print("Variables chargées depuis", filename)
        return variables
    except FileNotFoundError:
        print("Fichier de sauvegarde non trouvé.")
        return None








#Get device id

def get_output_device_number(output_device):
    p = pyaudio.PyAudio()

    # Obtenir le numéro du périphérique d'entrée sélectionné
    output_device_info = None
    for i in range(p.get_device_count()):
        device_info = p.get_device_info_by_index(i)
        if device_info['name'] == output_device:
            output_device_info = device_info
            break

    # Obtenir l'API hôte du périphérique d'entrée
    host_api_info = p.get_host_api_info_by_index(output_device_info['hostApi'])

    # Trouver le périphérique de sortie correspondant

    global output_device_number

    output_device_number = None
    for i in range(p.get_device_count()):
        device_info = p.get_device_info_by_index(i)
        if (
            device_info['maxOutputChannels'] > 0
            and device_info['hostApi'] == output_device_info['hostApi']
            and device_info['defaultSampleRate'] == output_device_info['defaultSampleRate']
            and device_info['hostApi'] == host_api_info['index']
        ):
            output_device_number = i
            break

    p.terminate()
    return output_device_number


def get_input_device_number(input_device):
    p = pyaudio.PyAudio()

    # Obtenir le numéro du périphérique d'entrée sélectionné
    input_device_info = None
    for i in range(p.get_device_count()):
        device_info = p.get_device_info_by_index(i)
        if device_info['name'] == input_device:
            input_device_info = device_info
            break

    # Obtenir l'API hôte du périphérique d'entrée
    host_api_info = p.get_host_api_info_by_index(input_device_info['hostApi'])

    # Trouver le périphérique de sortie correspondant

    global input_device_number

    input_device_number = None
    for i in range(p.get_device_count()):
        device_info = p.get_device_info_by_index(i)
        if (
            device_info['maxOutputChannels'] > 0
            and device_info['hostApi'] == input_device_info['hostApi']
            and device_info['defaultSampleRate'] == input_device_info['defaultSampleRate']
            and device_info['hostApi'] == host_api_info['index']
        ):
            input_device_number = i
            break

    p.terminate()
    return input_device_number


#Get I/O device
def get_audio_devices():
    p = pyaudio.PyAudio()
    devices = []
    for i in range(p.get_device_count()):
        device_info = p.get_device_info_by_index(i)
        device_name = device_info['name']
        devices.append(device_name)
    p.terminate()
    return devices

def on_device_selected(selection, is_input):
    if is_input:
        print("Input device selected:", selection)
    else:
        print("Output device selected:", selection)


input_devices = get_audio_devices()
output_devices = get_audio_devices()        

#Creating window
root = tk.Tk()
root.title("VBAN I/O Setup")

# Received Space
frame_received = tk.LabelFrame(root, text="Received", padx=10, pady=10)
frame_received.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

#Label ip and Steam Name
label_Ip_received = tk.Label(frame_received, text="Ip Adress:")
label_Ip_received.grid(row=0, column=1, padx=5, pady=5, sticky="sw")

label_Name_received = tk.Label(frame_received, text="Stream Name:")
label_Name_received.grid(row=0, column=2, padx=5, pady=5, sticky="sw")

# Stream 1 - Received
label_stream1_received = tk.Label(frame_received, text="Stream 1:")
label_stream1_received.grid(row=1, column=0, padx=5, pady=5, sticky="e")

entry_stream1_ip_received = tk.Entry(frame_received, width=15)
entry_stream1_ip_received.grid(row=1, column=1, padx=5, pady=5)

entry_stream1_name_received = tk.Entry(frame_received, width=15)
entry_stream1_name_received.grid(row=1, column=2, padx=5, pady=5)

# Stream 2 - Received
label_stream2_received = tk.Label(frame_received, text="Stream 2:")
label_stream2_received.grid(row=2, column=0, padx=5, pady=5, sticky="e")

entry_stream2_ip_received = tk.Entry(frame_received, width=15)
entry_stream2_ip_received.grid(row=2, column=1, padx=5, pady=5)

entry_stream2_name_received = tk.Entry(frame_received, width=15)
entry_stream2_name_received.grid(row=2, column=2, padx=5, pady=5)

# Send Space
frame_send = tk.LabelFrame(root, text="Send", padx=10, pady=10)
frame_send.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

#Label ip and Steam Name
label_Ip_send = tk.Label(frame_send, text="Ip Adress:")
label_Ip_send.grid(row=0, column=1, padx=5, pady=5, sticky="sw")

label_Name_send = tk.Label(frame_send, text="Stream Name:")
label_Name_send.grid(row=0, column=2, padx=5, pady=5, sticky="sw")

# Stream 1 - Send
label_stream1_send = tk.Label(frame_send, text="Stream 1:")
label_stream1_send.grid(row=1, column=0, padx=5, pady=5, sticky="e")

entry_stream1_ip_send = tk.Entry(frame_send, width=15)
entry_stream1_ip_send.grid(row=1, column=1, padx=5, pady=5)

entry_stream1_name_send = tk.Entry(frame_send, width=15)
entry_stream1_name_send.grid(row=1, column=2, padx=5, pady=5)

# Stream 2 - Send
label_stream2_send = tk.Label(frame_send, text="Stream 2:")
label_stream2_send.grid(row=2, column=0, padx=5, pady=5, sticky="e")

entry_stream2_ip_send = tk.Entry(frame_send, width=15)
entry_stream2_ip_send.grid(row=2, column=1, padx=5, pady=5)

entry_stream2_name_send = tk.Entry(frame_send, width=15)
entry_stream2_name_send.grid(row=2, column=2, padx=5, pady=5)

# device input Space
frame_input_device = tk.LabelFrame(frame_send, text="Input Device", padx=10, pady=10)
frame_input_device.grid(row=3, column=0, columnspan = 3, padx=10, pady=10, sticky="nsew")


# Input device dropdown menu

selected_input_device = tk.StringVar(root)
selected_input_device.set(input_devices[0])

dropdown_input = tk.OptionMenu(frame_input_device, selected_input_device, *input_devices, command=lambda x: on_device_selected(x, True))
dropdown_input.grid(row=3, column=2, padx=0, pady=10, sticky="w")

# device output Space
frame_output_device = tk.LabelFrame(frame_received, text="Input Device", padx=10, pady=10)
frame_output_device.grid(row=3, column=0, columnspan = 3, padx=10, pady=10, sticky="nsew")

# Output device dropdown menu

selected_output_device = tk.StringVar(root)
selected_output_device.set(output_devices[0])

dropdown_output = tk.OptionMenu(frame_output_device, selected_output_device, *output_devices, command=lambda x: on_device_selected(x, False))
dropdown_output.grid(row=3, column=2, padx=0, pady=10, sticky="w")

# Apply and Cancel Buttons
frame_buttons = tk.Frame(root, padx=10, pady=10)
frame_buttons.grid(row=3, column=1, sticky="e")

apply_button = tk.Button(frame_buttons, text="Apply", width=10, command=apply_settings)
apply_button.grid(row=0, column=0, padx=5, pady=5)

cancel_button = tk.Button(frame_buttons, text="Cancel", width=10, command=cancel_settings)
cancel_button.grid(row=0, column=1, padx=5, pady=5)


# Load saved variables
saved_variables = load_variables()
if saved_variables:
    selected_input_device.set(saved_variables.get("Input Device", input_devices[0]))
    selected_output_device.set(saved_variables.get("Output Device", output_devices[0]))
    entry_stream1_ip_received.insert(0, saved_variables.get("Stream 1 - Received IP", ""))
    entry_stream1_name_received.insert(0, saved_variables.get("Stream 1 - Received Name", ""))
    entry_stream2_ip_received.insert(0, saved_variables.get("Stream 2 - Received IP", ""))
    entry_stream2_name_received.insert(0, saved_variables.get("Stream 2 - Received Name", ""))
    entry_stream1_ip_send.insert(0, saved_variables.get("Stream 1 - Send IP", ""))
    entry_stream1_name_send.insert(0, saved_variables.get("Stream 1 - Send Name", ""))
    entry_stream2_ip_send.insert(0, saved_variables.get("Stream 2 - Send IP", ""))
    entry_stream2_name_send.insert(0, saved_variables.get("Stream 2 - Send Name", ""))






root.mainloop()
