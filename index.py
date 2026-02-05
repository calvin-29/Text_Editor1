import wx
import os


class App(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(App, self).__init__(*args, **kwargs)

        # create panel and sizer
        self.panel = wx.Panel(self)
        self.sizer = wx.BoxSizer(wx.VERTICAL)

        # create menu bar and file menu
        self.menuBar = wx.MenuBar()
        self.fileMenu = wx.Menu()

        # create save option and main text box
        self.saveItem = self.fileMenu.Append(wx.ID_SAVE, "&Save\tCtrl+S", "Save")
        self.loadItem = self.fileMenu.Append(wx.ID_OPEN, "&Open\tCtrl+O", "Open")
        self.text = wx.TextCtrl(self.panel, style=wx.TE_MULTILINE)

        # supported file types
        self.file_types = "Text files (*.txt)|*.txt|" \
                          "Python files (*.py, *.pyc)|*.py;*.pyc|" \
                          "All Files (*.*)|*.*"

        # file that is open on this instance
        self.file_path = None

        # modify ui elements
        self.init_ui()

    def init_ui(self):
        self.SetTitle("Text Editor")
        self.SetSize(1000, 500)

        # Add items to menu bar
        self.menuBar.Append(self.fileMenu, "&File")

        # Set up layout
        self.sizer.Add(self.text, 1, wx.EXPAND | wx.ALL, 5)
        self.panel.SetSizer(self.sizer)
        self.SetMenuBar(self.menuBar)
        self.Layout()

        # Bind the event handler
        self.Bind(wx.EVT_MENU, self.on_save, self.saveItem)
        self.Bind(wx.EVT_MENU, self.on_load, self.loadItem)

    def on_save(self, event):
        """Handles the save file menu command"""
        print(event)

        def save_dialog():
            # Use a wx.FileDialog for saving the file
            with wx.FileDialog(self, "Save File", wildcard=self.file_types,
                               style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:
                if fileDialog.ShowModal() == wx.ID_OK:
                    pathname = fileDialog.GetPath()
                    try:
                        # Save the content of the text control to the chosen file
                        with open(pathname, 'w') as f:
                            f.write(self.text.GetValue())
                    except IOError:
                        wx.LogError(f"Cannot save file '{pathname}'.")

        if self.file_path:
            if os.path.exists(self.file_path):
                try:
                    # Save the content of the text control to the chosen file
                    with open(self.file_path, 'w') as file:
                        file.write(self.text.GetValue())
                except IOError:
                    wx.LogError(f"Cannot save file '{self.file_path}'.")
            else:
                wx.LogError("File does not exist")
                save_dialog()

    def on_load(self, event):
        """Handles the load file menu command"""
        if self.file_path:
            print(event)

        with wx.FileDialog(self, "Open File", wildcard=self.file_types,
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_OK:
                self.file_path = fileDialog.GetPath()
                try:
                    # open the selected file
                    with open(self.file_path, "r") as file:
                        data = file.read()
                        # input text in the text control
                        self.text.AppendText(data)
                except IOError:
                    wx.LogError(f"Cannot open file '{self.file_path}'.")


if __name__ == '__main__':
    app = wx.App(False)
    frm = App(None)
    frm.Show()
    app.MainLoop()
