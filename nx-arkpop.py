import tkinter as tk
import customtkinter as ctk
import requests
import webbrowser
import os


API_URLS = {"XW10": "http://arkdedicated.com/xbox/cache/unofficialserverlist.json", "PS": "http://arkdedicated.com/ps4/cache/unofficialserverlist.json"}


MAPS = {"All Maps": "All Maps", "The Island": "TheIsland", "Scorched Earth": "ScorchedEarth_P", "Aberration": "Aberration_P", "Extinction": "Extinction",
        "Genesis": "Genesis", "Genesis Part 2": "Gen2", "Crystal Isles": "CrystalIsles", "Ragnarok": "Ragnarok", "Valguero": "Valguero_P", "Lost Island": "LostIsland",
        "Fjordur": "Fjordur", "The Center": "TheCenter", "PG Ark": "PGARK"}

class ArkPopCheckApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ARK: SE   |   Pop Check")
        self.root.geometry("400x550")
        self.root.configure(bg="#1a1a1e")
        self.root.resizable(False, False)
        self.root.iconbitmap(os.path.join(os.path.dirname(__file__), "icon.ico"))
        

        
        self.api_mode = "XW10"
        self.server_mode = "ALL"
        self.selected_map = "All Maps"
        
        self.session = requests.Session()
        self.auto_refresh_active = False 
        
        self.create_widgets()
        self.root.bind('<Return>', lambda event: self.search_server())

    def create_widgets(self):
        ctk.CTkLabel(self.root, text="ARK: SE   |   Pop Check", font=("Arial", 20), text_color="#ffffff").place(x=110, y=30)
        
        ctk.CTkLabel(self.root, text="NX", font=("Arial", 50), text_color="#ffffff").place(x=25, y=15)
        
        self.servername_entry = ctk.CTkEntry(self.root, placeholder_text="Enter Server Name", font=("Arial", 16), text_color="#ffffff", height=30, width=250, fg_color="#333333", border_width=0, corner_radius=8)
        self.servername_entry.place(x=20, y=90)
        
        ctk.CTkButton(self.root, text="「 Search 」", font=("Arial", 14), text_color="#000000", height=30, width=90, command=self.search_server, fg_color="#33ddff").place(x=280, y=90)
        
        self.mode_button = ctk.CTkButton(self.root, text="ALL", font=("Arial", 14), text_color="#000000", height=30, width=90, command=self.toggle_mode, fg_color="#FFD700")
        self.mode_button.place(x=185, y=450)
        
        self.api_button = ctk.CTkButton(self.root, text=self.api_mode, font=("Arial", 14), text_color="#000000", height=30, width=90, command=self.toggle_api, fg_color="#107c10")
        self.api_button.place(x=280, y=450)
        
        ctk.CTkButton(self.root, text=" » Join Discord « ", font=("Arial", 14), text_color="#000000", height=30, width=350, command=lambda: webbrowser.open("https://discord.gg/RtEYex2vmu"), fg_color="#5767f2").place(x=20, y=490)
        
        self.map_selector = ctk.CTkComboBox(self.root, values=list(MAPS.keys()), font=("Arial", 14), height=30, width=160, command=self.select_map, state="readonly")
        self.map_selector.place(x=20, y=450)
        self.map_selector.set("All Maps")
        
        self.output_box = ctk.CTkTextbox(self.root, font=("Arial", 12), height=250, width=350, text_color="#ffffff", fg_color="#333333", corner_radius=8, state="normal")
        self.output_box.insert("1.0", "Please enter a server name and search . . . ")
        self.output_box.configure(state="disabled")
        self.output_box.place(x=20, y=180)
        
        self.totalpop_box = ctk.CTkTextbox(self.root, font=("Arial", 15), height=20, width=350, text_color="#000000", fg_color="#FFD700", corner_radius=8, state="normal")
        self.totalpop_box.insert("1.0", "👤 —— Players Online  |  🌍 —— Servers Online")
        self.totalpop_box.configure(state="disabled")
        self.totalpop_box.place(x=20, y=135)
    
    def toggle_mode(self):
        modes = {"ALL": "PVE", "PVE": "PVP", "PVP": "ALL"}
        colors = {"ALL": "#FFD700", "PVE": "#48c75f", "PVP": "#FF6347"}
        self.server_mode = modes[self.server_mode]
        self.mode_button.configure(text=self.server_mode, fg_color=colors[self.server_mode])
    
    def toggle_api(self):
        self.api_mode = "PS" if self.api_mode == "XW10" else "XW10"
        self.api_button.configure(text=self.api_mode, fg_color="#2e6db4" if self.api_mode == "PS" else "#107c10")
    
    def select_map(self, choice):
        self.selected_map = MAPS[choice]
    
    def fetch_server_data(self):
        try:
            response = self.session.get(API_URLS[self.api_mode])
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return []
    
    def search_server(self):
        servers = self.fetch_server_data()
        search_name = self.servername_entry.get().lower()
        matching_servers = [s for s in servers if search_name in s.get("Name", "").lower() and
                            (self.server_mode == "ALL" or (self.server_mode == "PVE" and s.get("SessionIsPve", 0) == 1) or
                             (self.server_mode == "PVP" and s.get("SessionIsPve", 0) == 0)) and
                            (self.selected_map == "All Maps" or s.get("MapName", "") == self.selected_map)]
        
        matching_servers.sort(key=lambda s: s.get("NumPlayers", 0), reverse=True)
        total_players = sum(s.get("NumPlayers", 0) for s in matching_servers)
        total_servers = len(matching_servers)
        
        self.totalpop_box.configure(state="normal")
        self.totalpop_box.delete("1.0", tk.END)
        self.totalpop_box.insert("1.0", f"👤 {total_players} Players Online  |  🌍 {total_servers} Servers Online")
        self.totalpop_box.configure(state="disabled")
        
        self.output_box.configure(state="normal")
        self.output_box.delete("1.0", tk.END)
        for server in matching_servers:
            self.output_box.insert(tk.END, f"📰 Name: {server['Name']}\n🌍 Map: {server['MapName']}\n👤 Players: {server['NumPlayers']} / {server['MaxPlayers']}\n🕹️ Mode: {'PVE' if server['SessionIsPve'] else 'PVP'}\n🔒 IP: {server['IP']}:{server['Port']}\n━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
        self.output_box.configure(state="disabled")
        
        
        if not self.auto_refresh_active:
            self.auto_refresh_active = True
            self.refresh_data() 

    def refresh_data(self):
        
        self.search_server() 
        self.root.after(10000, self.refresh_data) 

if __name__ == "__main__":
    root = tk.Tk()
    app = ArkPopCheckApp(root)
    root.mainloop()
