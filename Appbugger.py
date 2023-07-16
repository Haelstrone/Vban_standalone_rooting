import tkinter as tk
from tkinter import messagebox
import pyaudio
import pyVBAN.pyVBAN as pyVBAN
import threading
import pystray
from pystray import MenuItem as item, Menu as menu
from PIL import Image

def apply_settings():
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
                                                                     # <- ça c'est chelou aussi
    # Start the threads
    recv_thread.start()
    send_thread.start()

def on_window_close():
    # Minimize the main window
    root.iconify()
    # Hide the main window
    root.withdraw()

# Create a function to restore the main window
def show_window():
    root.deiconify()
    root.state('normal')

    

def start_vban_recv():
    stream1_ip_received = entry_stream1_ip_received.get()
    stream1_name_received = entry_stream1_name_received.get()
    output_device_number = get_output_device_number(selected_output_device.get())
    vban_recv = pyVBAN.VBAN_Recv(stream1_ip_received, 6980, stream1_name_received, 48000, output_device_number, verbose=True)
    vban_recv.runforever()

                                                                                # la aussi ya un bail chelou
def start_vban_send():
    stream1_ip_send = entry_stream1_ip_send.get()
    stream1_name_send = entry_stream1_name_send.get()
    input_device_number = get_input_device_number(selected_input_device.get())
    vban_send = pyVBAN.VBAN_Send(stream1_ip_send, 6980, stream1_name_send, 48000, input_device_number, verbose=True)
    vban_send.runforever()


def cancel_settings():
    # Close the app and ask for confirmation to close without saving
    if messagebox.askyesno("VBAN I/O Setup", "Are you sure you want to close without saving?"):
        root.destroy()


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
        return variables                                                         # A L E D
    except FileNotFoundError:
        print("Fichier de sauvegarde non trouvé.")
        return None


def get_output_device_number(output_device):
    p = pyaudio.PyAudio()
    output_device_number = None
    for i in range(p.get_device_count()):
        device_info = p.get_device_info_by_index(i)
        if device_info['name'] == output_device:
            output_device_number = i
            break
    p.terminate()
    return output_device_number


def get_input_device_number(input_device):
    p = pyaudio.PyAudio()
    input_device_number = None
    for i in range(p.get_device_count()):
        device_info = p.get_device_info_by_index(i)
        if device_info['name'] == input_device:
            input_device_number = i
            break
    p.terminate()
    return input_device_number


# Load saved variables
saved_variables = load_variables()

# Get audio devices
input_devices = pyaudio.PyAudio().get_device_info_by_index(0)["name"]
output_devices = pyaudio.PyAudio().get_device_info_by_index(0)["name"]


# Initialize output device number
output_device_number = None


#Creating window
root = tk.Tk()
root.title("VBAN I/O Setup")


#############################################################################

# Handle window close event
root.protocol("WM_DELETE_WINDOW", on_window_close)

# Load your custom icon image
icon_image = Image.open('gigarig.png')
# Create a system tray icon and menu
menu = (
    item('Show', lambda: show_window),
    item('Exit', root.quit)
)
# Create the system tray icon
tray_icon = pystray.Icon("app_name", icon_image, "App Name", menu)                 #JSPAPKCAFONKTIONNEPAAAAAAAAA




# Start the system tray icon
tray_icon.run()


##############################################################################################


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





# C t1 s o s je suis touché je tombe a terre !!!!