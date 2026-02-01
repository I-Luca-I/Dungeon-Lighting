import FreeSimpleGUI as sg
import os

class Menu:
    def __init__(self) -> None:
        sg.theme('Green')
        self.dungeons = os.listdir(f"saves")
        for i in range(len(self.dungeons)):
            self.dungeons[i] = self.dungeons[i][len("dungeon_"):]
        self.entraces = ["wip"]
        self.saves = []
        self.default_dungeon = "Scegli un dungeon da caricare"
        self.default_save = "Scegli un save"
        self.default_entrance = "Scegli un\'entrata"

        layout = [
            [sg.Frame("",
                [
                    [sg.Push(), sg.Button(button_text="X", key="CHIUDI", size=2)],
                    [sg.Image("assets/title.png")],
                    [sg.Combo(self.dungeons, key="-DUNGEON-", default_value=self.default_dungeon, readonly=True, enable_events=True, expand_x=True)], 
                    [
                        sg.Combo(self.saves, key="-SAVE-", default_value=self.default_save, readonly=True, enable_events=True, size=(33, 100)),
                        sg.Combo(self.entraces, key="-ENTRANCE-", default_value=self.default_entrance, readonly=True, enable_events=True, size=(33, 100))
                    ],
                    [sg.Push(), sg.Button("START"), sg.Push()]
                ],
                background_color="OrangeRed3", border_width=10, pad=(0, 0)
            )]
        ]

        self.window = sg.Window("--DUNGEON LIGHTING--", layout=layout, icon="assets/icon.ico", no_titlebar=True, grab_anywhere=True)

    def run(self) -> dict:
        id = ""
        save = ""

        while True:
            event, values = self.window.read() # type: ignore

            if event == "-DUNGEON-":
                files = os.listdir(f"saves/dungeon_{values['-DUNGEON-']}")
                self.saves = []
                for f in files:
                    if f.endswith(".json"):
                        self.saves.append(f[:len("0000-00-00-00-00")])
                self.saves.sort(reverse=True)
                self.window["-SAVE-"].update(values=self.saves, value="Scegli un save", size=(33, 100)) # type: ignore

            if event in (sg.WINDOW_CLOSED, "CHIUDI"):
                load_dungeon = False
                break

            if event == "START" and values["-DUNGEON-"] != self.default_dungeon and values["-SAVE-"] != self.default_save:
                load_dungeon = True
                id = values["-DUNGEON-"]
                save = values["-SAVE-"]
                break

        self.window.close()
        return {
            "load_dungeon": load_dungeon,
            "id": id,
            "save": save
        }
