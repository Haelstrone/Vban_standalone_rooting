
import tkinter as tk
from tkinter import messagebox
import pyaudio
import pyVBAN.pyVBAN as pyVBAN
import pystray as pys
from pystray import MenuItem as item, Menu as menu
from PIL import Image
import multiprocessing as mp 
from multiprocessing import Process, Value, Array
from ctypes import c_char_p as ccp
import os 
import time
import sys
import subprocess
################################################# VBAN FLOW ###############################################



stop_vban_event = mp.Event()

recv_process = None
send_process = None



def load_variables_dgtr():
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
    
Default_value = 0      

saved_variables = load_variables_dgtr()




if saved_variables:
    Shared_entry_stream1_ip_received = saved_variables.get("Stream 1 - Received IP", "")
    Shared_entry_stream1_name_received = saved_variables.get("Stream 1 - Received Name", "")
    Shared_entry_stream2_ip_received = saved_variables.get("Stream 2 - Received IP", "")
    Shared_entry_stream2_name_received = saved_variables.get("Stream 2 - Received Name", "")
    Shared_entry_stream1_ip_send = saved_variables.get("Stream 1 - Send IP", "")
    Shared_entry_stream1_name_send = saved_variables.get("Stream 1 - Send Name", "")
    Shared_entry_stream2_ip_send = saved_variables.get("Stream 2 - Send IP", "")
    Shared_entry_stream2_name_send = saved_variables.get("Stream 2 - Send Name", "")
    Shared_selected_input_index = saved_variables.get("input index", Default_value)
    Shared_selected_output_index = saved_variables.get("output index", Default_value)




def start_vban_recv():#Shared_entry_stream1_ip_received, Shared_entry_stream2_ip_received, Shared_entry_stream2_name_received, Shared_selected_output_index):
    stream1_ip_received = Shared_entry_stream1_ip_received
    stream1_name_received = Shared_entry_stream1_name_received
    output_device = Shared_selected_output_index
    vban_recv = pyVBAN.VBAN_Recv(stream1_ip_received, stream1_name_received, 48000, int(output_device), verbose=True)
    return vban_recv

def start_vban_send():#Shared_entry_stream1_ip_send, Shared_entry_stream1_name_send, Shared_entry_stream2_ip_send, Shared_entry_stream2_name_send, Shared_selected_input_index):
    stream1_ip_send = Shared_entry_stream1_ip_send
    stream1_name_send = Shared_entry_stream1_name_send
    input_device = Shared_selected_input_index
    vban_send = pyVBAN.VBAN_Send(stream1_ip_send, 6980, stream1_name_send, 48000, int(input_device), verbose=True)
    return vban_send


def send_vban_process(vban_send, variables):
    while not stop_vban_event.is_set():
        vban_send.runonce()
    vban_send.quit()

def recv_vban_process(vban_recv, variables):
    
    while not stop_vban_event.is_set():
        vban_recv.runonce()
    vban_recv.quit()

def clear_dictionary():
    saved_variables.clear()

    

def print_debug():
    stream1_ip_received = Shared_entry_stream1_ip_received
    stream1_name_received = Shared_entry_stream1_name_received
    recv_output_device = Shared_selected_output_index
    myint = saved_variables.get("input index")
    print(recv_output_device, stream1_ip_received, stream1_name_received)
    print(saved_variables)
    print(myint)



if __name__ == '__main__':

    def Vban_on():
        global recv_process, send_process
        if recv_process is None or not recv_process.is_alive():
            recv_process =  mp.Process(target=start_vban_recv, )#args=(Shared_entry_stream1_ip_received, Shared_entry_stream1_name_received, Shared_entry_stream2_ip_received, Shared_entry_stream2_name_received, Shared_selected_output_index)'' )
            recv_process.start()
        if send_process is None or not send_process.is_alive():
            send_process = mp.Process(target=start_vban_send, )#args=(Shared_entry_stream1_ip_send, Shared_entry_stream1_name_send, Shared_entry_stream2_ip_send, Shared_entry_stream2_name_send, Shared_selected_input_index))
            send_process.start()


    def Vban_off():
        global recv_process, send_process
        if recv_process is not None and recv_process.is_alive():
            recv_process.terminate()
            recv_process.join()
            recv_process = None
        if send_process is not None and send_process.is_alive():
            send_process.terminate()
            send_process.join()
            send_process = None
        stop_vban_event.set()

    def restart_application():
        # Terminer les processus VBAN en cours d'exécution
        Vban_off()
        root.destroy()

        python = sys.executable
        os.execl(sys.argv[0])
        

    def apply_settings():
        # Save the variables
        filename = "save.txt"
        os.remove(filename)
        with open(filename, 'w') as file:
            file.write(f"Input Device: {selected_input_device.get()}\n")
            file.write(f"Output Device: {selected_output_device.get()}\n")
            file.write(f"Stream 1 - Received IP: {entry_stream1_ip_received.get()}\n")
            file.write(f"Stream 1 - Received Name: {entry_stream1_name_received.get()}\n")
            # file.write(f"Stream 2 - Received IP: {entry_stream2_ip_received.get()}\n")
            # file.write(f"Stream 2 - Received Name: {entry_stream2_name_received.get()}\n")
            file.write(f"Stream 1 - Send IP: {entry_stream1_ip_send.get()}\n")
            file.write(f"Stream 1 - Send Name: {entry_stream1_name_send.get()}\n")
            # file.write(f"Stream 2 - Send IP: {entry_stream2_ip_send.get()}\n")
            # file.write(f"Stream 2 - Send Name: {entry_stream2_name_send.get()}\n")
            file.write(f"VBAN - Toggle On Start: {check_var.get()}\n")
            file.write(f"input index: {selected_input_index}\n")
            file.write(f"output index: {selected_output_index}\n")
        print("Variables saved to", filename )

        messagebox.showinfo("VBAN I/O Setup", "Settings applied and saved!\n The Software will restart. ")
        restart_application()

###################################################################################################################################

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
        



##################################### -TRAY ICON & FONCTION- ##########################


    def Quit_app(icon, item):
        icon.stop()
        Vban_off()
        recv_process.join()
        send_process.join()
        root.destroy()

    def Quit_app_button():
        Vban_off()
        recv_process.join()
        send_process.join()
        root.destroy()

    def show_window(icon, item):
        if not root.state():
            icon.stop()
            root.after(0,root.deiconify)

    def withdraw_window():  
        root.withdraw()
        image = Image.open("gigarig.png")
        menu = (
        item('Quitter', Quit_app),
        item('Show' , show_window, default=True)
    )
        icon = pys.Icon("name", image, "title", menu)
        icon.run()


########################################### VBAN CONTROL ###############################


    def toggle_button():
        if On_off_button["text"] == "VBAN ON":
            On_off_button["text"] = "VBAN OFF"
            On_off_button["bg"] = "red"
            #fonction Off
            print("vban off")
            Vban_off()
        else:
            On_off_button["text"] = "VBAN ON"
            On_off_button["bg"] = "green"
            # fonction ON
            print("vban on")
            Vban_on()


########################################################################################
######################################### GUI ##########################################
#########################################################################################

    #Creating window
    root = tk.Tk()
    root.title("VBAN I/O Setup")
    root.protocol('WM_DELETE_WINDOW', withdraw_window)


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

    # # Stream 2 - Received
    # label_stream2_received = tk.Label(frame_received, text="Stream 2:")
    # label_stream2_received.grid(row=2, column=0, padx=5, pady=5, sticky="e")

    # entry_stream2_ip_received = tk.Entry(frame_received, width=15)                 
    # entry_stream2_ip_received.grid(row=2, column=1, padx=5, pady=5)

    # entry_stream2_name_received = tk.Entry(frame_received, width=15)
    # entry_stream2_name_received.grid(row=2, column=2, padx=5, pady=5)

    # Send Space
    frame_send = tk.LabelFrame(root, text="Send", padx=10, pady=10)
    frame_send.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")


############################################################# Bulle d'information et Label #####################################################

    Tooltip_dict = { "Ip adresse send": "" }
    global tooltip

    tooltip = tk.Toplevel(root)
    tooltip.destroy()
    
    def show_tooltip(event):
        tooltip = tk.Toplevel(root)
        tooltip.geometry(f"+{event.x_root+10}+{event.y_root+10}")
        tooltip.wm_overrideredirect(True)  # Supprime la barre de titre et la bordure de la fenêtre
        tooltip_label = tk.Label(tooltip, text="Information supplémentaire")
        tooltip_label.pack()
        
    def hide_tooltip(event):
        tooltip.destroy()


    #Label ip and Steam Name
    label_Ip_send = tk.Label(frame_send, text="Ip Adress:")
    label_Ip_send.grid(row=0, column=1, padx=5, pady=5, sticky="sw")
    label_Ip_send.bind("<Enter>", show_tooltip)
    label_Ip_send.bind("<Leave>", hide_tooltip)

    label_Name_send = tk.Label(frame_send, text="Stream Name:")
    label_Name_send.grid(row=0, column=2, padx=5, pady=5, sticky="sw")
    label_Name_send.bind("<Enter>", show_tooltip)
    label_Name_send.bind("<Leave>", hide_tooltip)

####################################################################################################################################################


    # Stream 1 - Send
    label_stream1_send = tk.Label(frame_send, text="Stream 1:")
    label_stream1_send.grid(row=1, column=0, padx=5, pady=5, sticky="e")

    entry_stream1_ip_send = tk.Entry(frame_send, width=15)
    entry_stream1_ip_send.grid(row=1, column=1, padx=5, pady=5)

    entry_stream1_name_send = tk.Entry(frame_send, width=15)
    entry_stream1_name_send.grid(row=1, column=2, padx=5, pady=5)

    # # Stream 2 - Send
    # label_stream2_send = tk.Label(frame_send, text="Stream 2:")
    # label_stream2_send.grid(row=2, column=0, padx=5, pady=5, sticky="e")

    # entry_stream2_ip_send = tk.Entry(frame_send, width=15)
    # entry_stream2_ip_send.grid(row=2, column=1, padx=5, pady=5)

    # entry_stream2_name_send = tk.Entry(frame_send, width=15)
    # entry_stream2_name_send.grid(row=2, column=2, padx=5, pady=5)





############################################## Device select ########################################################################

    def on_input_device_selected(*args):
        global selected_input_index, selected_input_device
        selected_input_index = get_device_number(selected_input_device.get())
        print(selected_input_index)

    def on_output_device_selected(*args):
        global selected_output_index, selected_output_device
        selected_output_index = get_device_number(selected_output_device.get())
        print(selected_output_index)

    def get_device_number(device_name):
        p = pyaudio.PyAudio()
        device_number = None
        for i in range(p.get_device_count()):
            device_info = p.get_device_info_by_index(i)
            if device_info['name'] == device_name:
                device_number = i
                break
        p.terminate()
        return device_number

    p = pyaudio.PyAudio()
    input_devices = [p.get_device_info_by_index(i)["name"] for i in range(p.get_device_count())]
    output_devices = [p.get_device_info_by_index(i)["name"] for i in range(p.get_device_count())]
    p.terminate()

    # device output Space
    frame_output_device = tk.LabelFrame(frame_received, text="Output Device", padx=10, pady=10)
    frame_output_device.grid(row=3, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

    # device input Space
    frame_input_device = tk.LabelFrame(frame_send, text="Input Device", padx=10, pady=10)
    frame_input_device.grid(row=3, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

    # Input device dropdown menu
    selected_input_device = tk.StringVar(root)
    selected_input_device.set(input_devices[0])
    selected_input_device.trace('w', on_input_device_selected)

    dropdown_input = tk.OptionMenu(frame_send, selected_input_device, *input_devices)
    dropdown_input.grid(row=3, column=2, padx=0, pady=10, sticky="w")

    # Output device dropdown menu
    selected_output_device = tk.StringVar(root)
    selected_output_device.set(output_devices[0])
    selected_output_device.trace('w', on_output_device_selected)

    dropdown_output = tk.OptionMenu(frame_received, selected_output_device, *output_devices)
    dropdown_output.grid(row=3, column=2, padx=0, pady=10, sticky="w")

#############################################################################################################################################

    # Apply Cancel and quit Buttons
    frame_buttons = tk.Frame(root, padx=10, pady=10)
    frame_buttons.grid(row=3, column=0, sticky="e")

    apply_button = tk.Button(frame_buttons, text="Apply", width=10, command=apply_settings)
    apply_button.grid(row=0, column=0, padx=5, pady=5)

    cancel_button = tk.Button(frame_buttons, text="Cancel", width=10, command=cancel_settings)
    cancel_button.grid(row=0, column=1, padx=5, pady=5)

    Quit_button = tk.Button(frame_buttons, text="Quit app", width=10, command=Quit_app_button)
    Quit_button.grid(row=0, column=2, padx=5, pady=5)

    Debug_button = tk.Button(frame_buttons, text="Debug", width=10, command=print_debug)
    Debug_button.grid(row=0, column=3, padx=5, pady=5)

    #Vban ON/OFF 
    frame_vban = tk.Frame(root, padx=10, pady=10)
    frame_vban.grid(row=2, column=0, sticky="w")
    On_off_button = tk.Button(frame_vban, text="VBAN OFF", bg="RED", command=toggle_button)
    On_off_button.grid(row=3, column=0, padx=2, pady=5, sticky="we")


    #vban ON on start

    check_var = tk.IntVar()
    check_button = tk.Checkbutton(frame_vban, text="Toggle on Start", variable=check_var)
    check_button.grid(row= 3, column=1, padx=10, pady=10)



    # Load saved variables
    saved_variables = load_variables()
    if saved_variables:
        selected_input_device.set(saved_variables.get("Input Device", input_devices[0]))
        selected_output_device.set(saved_variables.get("Output Device", output_devices[0]))
        entry_stream1_ip_received.insert(0, saved_variables.get("Stream 1 - Received IP", ""))
        entry_stream1_name_received.insert(0, saved_variables.get("Stream 1 - Received Name", ""))
        # entry_stream2_ip_received.insert(0, saved_variables.get("Stream 2 - Received IP", ""))
        # entry_stream2_name_received.insert(0, saved_variables.get("Stream 2 - Received Name", ""))
        entry_stream1_ip_send.insert(0, saved_variables.get("Stream 1 - Send IP", ""))
        entry_stream1_name_send.insert(0, saved_variables.get("Stream 1 - Send Name", ""))
        # entry_stream2_ip_send.insert(0, saved_variables.get("Stream 2 - Send IP", ""))
        # entry_stream2_name_send.insert(0, saved_variables.get("Stream 2 - Send Name", ""))
        state = check_var.set(saved_variables.get("VBAN - Toggle On Start", ""))




########################## Vban go on start##############################

        if check_var.get() == 1 :
            Vban_on()
            print("okayletsgoooo")

#########################################################################



    # Shared_selected_input_index = Value('i', selected_input_index.get() )
    # Shared_selected_output_index = Value('i', selected_output_index.get())
    # Shared_entry_stream1_ip_received = Value('s', entry_stream1_ip_received.get())
    # Shared_entry_stream1_name_received = Value('s', entry_stream1_name_received.get())
    # Shared_entry_stream2_ip_received = Value('s', entry_stream2_ip_received.get() )
    # Shared_entry_stream2_name_received= Value('s', entry_stream2_name_received.get())
    # Shared_entry_stream1_ip_send = Value('s', entry_stream1_ip_send.get())
    # Shared_entry_stream1_name_send = Value('s', entry_stream1_name_send.get())
    # Shared_entry_stream2_ip_send = Value('s', entry_stream2_ip_send.get())
    # Shared_entry_stream2_name_send = Value('s', entry_stream2_name_send.get())

#
    root.mainloop()





