
import tkinter as tk
from tkinter import ttk
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
import winreg

################################################# VBAN FLOW ###############################################



stop_vban_event = mp.Event()





def load_variables_dgtr():
    filename = "Config.txt"
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
    vban_recv = pyVBAN.VBAN_Recv(stream1_ip_received, stream1_name_received, 6980,int(output_device) , verbose=False)
    while not stop_vban_event.is_set():
        vban_recv.runonce()
    vban_recv.quit()  

def start_vban_send():#Shared_entry_stream1_ip_send, Shared_entry_stream1_name_send, Shared_entry_stream2_ip_send, Shared_entry_stream2_name_send, Shared_selected_input_index):
    stream1_ip_send = Shared_entry_stream1_ip_send
    stream1_name_send = Shared_entry_stream1_name_send
    input_device = Shared_selected_input_index
    vban_send = pyVBAN.VBAN_Send(stream1_ip_send, 6980, stream1_name_send, 48000, int(input_device), verbose=False)
    while not stop_vban_event.is_set():
        vban_send.runonce()
    vban_send.quit() 


# def send_vban_process(vban_send, variables):
#     while not stop_vban_event.is_set():
#         vban_send.runonce()
#     vban_send.quit()

# def recv_vban_process(vban_recv, variables):
    
#     while not stop_vban_event.is_set():
#         vban_recv.runonce()
#     vban_recv.quit()

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

    recv_process = None
    send_process = None

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
        Vban_off()
        python = sys.executable
        subprocess.Popen([python] + sys.argv)
        sys.exit()
        

    def apply_settings():
        # Save the variables
        filename = "Config.txt"
        if os.path.exists(filename):
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
            file.write(f"lunch on window st-up: {autostart_var.get()}\n")
            
        print("Variables saved to", filename )
        toggle_autostart()
        messagebox.showinfo("VBAN I/O Setup", "Settings applied and saved!\n The Software will restart. ")
        restart_application()

###################################################################################################################################

    def cancel_settings():
        # Close the app and ask for confirmation to close without saving
        if messagebox.askyesno("VBAN I/O Setup", "Are you sure you want to close without saving?"):
            root.destroy()


    def load_variables():
        filename = "Config.txt"
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
    
    

    def Quit_app(icon):
        if messagebox.askyesno("VBAN I/O Setup", "Are you sure you want to close without saving?"):
            icon.stop()
            Vban_off()
            root.destroy()


    def Quit_app_button():
        if messagebox.askyesno("VBAN I/O Setup", "Are you sure you want to close without saving?"):
            Vban_off()
            root.destroy()



    def show_window(icon):
            icon.stop()
            root.after(0,root.deiconify)
            #print("debug")

        
    def withdraw_window():  
        root.withdraw()
        image = Image.open("io_icon.png")
        menu = (
        item('Quitter', Quit_app),
        item('Show' , show_window, default=True)
    )
        icon = pys.Icon("I/O VBAN ", image, "I/O VBAN", menu)
        icon.run_detached()


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
    #root.configure(bg="#373861")
    root.title("VBAN I/O Setup")
    root.protocol('WM_DELETE_WINDOW', withdraw_window)


    # Received Space
    frame_received = tk.LabelFrame(root, text="Received", padx=10, pady=10)
    frame_received.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
    #frame_received.configure(bg="#373861")


    # Stream 1 - Received
    # label_stream1_received = tk.Label(frame_received, text="Stream 1:")
    # label_stream1_received.grid(row=1, column=0, padx=5, pady=5, sticky="e")

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
    #frame_send.configure(bg="#373861")

############################################################# label and tooltip #####################################################


    class Tooltip:
        def __init__(self, widget, text):
            self.widget = widget
            self.text = text
            self.tooltip = None
            self.widget.bind("<Enter>", self.show_tooltip)
            self.widget.bind("<Leave>", self.hide_tooltip)

        def show_tooltip(self, event=None):
            if self.tooltip is not None:
                return
            x, y, _, _ = self.widget.bbox("insert")
            x += self.widget.winfo_rootx() + 25
            y += self.widget.winfo_rooty() + 20

            self.tooltip = tk.Toplevel(self.widget)
            self.tooltip.wm_overrideredirect(True)
            self.tooltip.wm_geometry(f"+{x}+{y}")
            label = tk.Label(self.tooltip, text=self.text, background="#ffffe0", relief="solid", borderwidth=1)
            label.pack(ipadx=1)

        def hide_tooltip(self, event=None):
            if self.tooltip is not None:
                self.tooltip.destroy()
                self.tooltip = None

    #Label ip and Steam Name
    label_Ip_send = tk.Label(frame_send, text="Ip Adress:")
    label_Ip_send.grid(row=0, column=1, padx=5, pady=5, sticky="sw")
    tooltip = Tooltip(label_Ip_send, "Enter here the ip address of the workstation where you want to send the audio")

    label_Name_send = tk.Label(frame_send, text="Stream Name:")
    label_Name_send.grid(row=0, column=2, padx=5, pady=5, sticky="sw")
    tooltip = Tooltip( label_Name_send, "I recommend that you enter the name of the workstation here,\n the same name should be entered in the reception area of the receiving workstation.")

    #Label ip and Steam Name
    label_Ip_received = tk.Label(frame_received, text="Ip Adress:")
    label_Ip_received.grid(row=0, column=1, padx=5, pady=5, sticky="sw")
    tooltip = Tooltip( label_Ip_received, "Enter the IP address of the workstation from which you are receiving the audio here")

    label_Name_received = tk.Label(frame_received, text="Stream Name:")
    label_Name_received.grid(row=0, column=2, padx=5, pady=5, sticky="sw")
    tooltip = Tooltip( label_Name_received, "Enter here the name of the audio stream sent from the sender's workstation")


####################################################################################################################################################


    # Stream 1 - Send
    # label_stream1_send = tk.Label(frame_send, text="Stream 1:")
    # label_stream1_send.grid(row=1, column=0, padx=5, pady=5, sticky="e")

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

    # device output Space------------------------
    frame_output_device = tk.LabelFrame(frame_received, text="Output Device", padx=10, pady=10)
    frame_output_device.grid(row=3, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")
    #frame_output_device.configure(bg="#373861")

    # device input Space-----------------
    frame_input_device = tk.LabelFrame(frame_send, text="Input Device", padx=10, pady=10)
    frame_input_device.grid(row=3, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")
    #frame_input_device.configure(bg="#373861")


    # Input device dropdown menu-------------------------------------
    # selected_input_device = tk.StringVar(root)
    # selected_input_device.set(input_devices[0])
    # selected_input_device.trace('w', on_input_device_selected)

    # dropdown_input = tk.OptionMenu(frame_send, selected_input_device, *input_devices)
    # dropdown_input.grid(row=3, column=2, padx=0, pady=10, sticky="w")

    selected_input_device = tk.StringVar(root)
    selected_input_device.set(input_devices[0])
    selected_input_device.trace('w', on_input_device_selected)

    dropdown_input = tk.OptionMenu(frame_send, selected_input_device, *input_devices)
    dropdown_input.grid(row=3, column=2, padx=0, pady=10, sticky="w")


    # Output device dropdown menu--------------------------------------
    selected_output_device = tk.StringVar(root)
    selected_output_device.set(output_devices[0])
    selected_output_device.trace('w', on_output_device_selected)

    dropdown_output = tk.OptionMenu(frame_received, selected_output_device, *output_devices)
    dropdown_output.grid(row=3, column=2, padx=0, pady=10, sticky="w")



    # Apply Cancel and quit Buttons------------------------------------
    frame_buttons = tk.Frame(root, padx=10, pady=10)
    frame_buttons.grid(row=3, column=0, sticky="e")
    #frame_buttons.configure(bg="#373861")


    apply_button = tk.Button(frame_buttons, text="Apply", width=10, command=apply_settings)
    apply_button.grid(row=0, column=0, padx=5, pady=5)

    # cancel_button = tk.Button(frame_buttons, text="Cancel", width=10, command=cancel_settings)
    # cancel_button.grid(row=0, column=1, padx=5, pady=5)

    Quit_button = tk.Button(frame_buttons, text="Quit app", width=10, command=Quit_app_button)
    Quit_button.grid(row=0, column=2, padx=5, pady=5)

    # Debug_button = tk.Button(frame_buttons, text="Debug", width=10, command=print_debug)
    # Debug_button.grid(row=0, column=3, padx=5, pady=5)

    #Vban ON/OFF --------------
    frame_vban = tk.Frame(root, padx=10, pady=10)
    frame_vban.grid(row=2, column=0, sticky="w")
    #frame_vban.configure(bg="#373861")
    On_off_button = tk.Button(frame_vban, text="VBAN OFF", bg="RED", command=toggle_button)
    On_off_button.grid(row=3, column=0, padx=2, pady=5, sticky="we")


    #vban ON on start------------------------------

    check_var = tk.IntVar()
    check_button = tk.Checkbutton(frame_vban, text="Toggle on Start", variable=check_var)
    check_button.grid(row= 3, column=1, padx=10, pady=10)

    autostart_var = tk.IntVar()
    autostart_checkbox = tk.Checkbutton(frame_buttons, text="lunch on Windows Start-Up", variable=autostart_var)
    autostart_checkbox.grid(row= 1, column=0, columnspan=3, padx=10, pady=10)

    def toggle_autostart():
        if autostart_var.get() == 1:
            
            key = winreg.HKEY_CURRENT_USER
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            app_name = "VBANIO"  
            app_path = os.path.abspath(sys.argv[0]) 
            try:
                with winreg.OpenKey(key, key_path, 0, winreg.KEY_SET_VALUE) as reg_key:
                    winreg.SetValueEx(reg_key, app_name, 0, winreg.REG_SZ, app_path)
            except Exception as e:
                print("error", e)
        else:
            
            key = winreg.HKEY_CURRENT_USER
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            app_name = "VBANIO"  
            try:
                with winreg.OpenKey(key, key_path, 0, winreg.KEY_SET_VALUE) as reg_key:
                    winreg.DeleteValue(reg_key, app_name)
            except Exception as e:
                print("Erreur", e)


    # Load saved variables--------------------------------------------------
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
        state2 = autostart_var.set(saved_variables.get("lunch on window st-up",""))
    if check_var.get() == 1 :
        Vban_on()
        print("okayletsgoooo")


    # Autostart





#
    root.mainloop()





