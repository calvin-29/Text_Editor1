import wx
import os


class App(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(App, self).__init__(*args, **kwargs)

        # create panel and sizer
        self.panel = wx.Panel(self)
        self.sizer = wx.BoxSizer(wx.VERTICAL)

        # create menu bar and menus
        self.menuBar = wx.MenuBar()
        self.fileMenu = wx.Menu()
        self.editMenu = wx.Menu()

        # create options for file menu
        self.newCommand = self.fileMenu.Append(wx.ID_NEW, "&New\tCtrl+N", "New")
        self.newWindowCommand = self.fileMenu.Append(-1, "&New Window\tCtrl+Shift+N", "New Window")
        self.saveItem = self.fileMenu.Append(wx.ID_SAVE, "&Save\tCtrl+S", "Save")
        self.loadItem = self.fileMenu.Append(wx.ID_OPEN, "&Open\tCtrl+O", "Open")
        self.saveAsItem = self.fileMenu.Append(wx.ID_SAVEAS, "&Save As\tCtrl+Shift+S", "Save As")
        self.fileMenu.AppendSeparator()
        self.exitCommand = self.fileMenu.Append(-1, "&Exit", "Exit")

        # create options for edit menu
        self.undoCommand = self.editMenu.Append(wx.ID_UNDO, "Undo\tCtrl+Z")
        self.editMenu.AppendSeparator()
        self.cutCommand = self.editMenu.Append(wx.ID_CUT, "Cut\tCtrl+X")
        self.copyCommand = self.editMenu.Append(wx.ID_COPY, "Copy\tCtrl+C")
        self.pasteCommand = self.editMenu.Append(wx.ID_PASTE, "Paste\tCtrl+V")
        self.deleteCommand = self.editMenu.Append(wx.ID_DELETE, "Delete\tDel")

        # The text box
        self.text = wx.TextCtrl(self.panel, style=wx.TE_MULTILINE | wx.TE_RICH2)

        # supported file types
        self.file_types = "Text files (*.txt)|*.txt|" \
                          "Python files (*.py, *.pyc)|*.py;*.pyc|" \
                          "All Files (*.*)|*.*"

        # file that is open on this instance
        self.file_path = None

        # modify ui elements
        self.init_ui()

    def init_ui(self):
        self.SetTitle("*Untitled - Text Editor")
        self.SetSize(1000, 500)

        # Set font of text box
        self.text.SetFont(wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                          wx.FONTWEIGHT_NORMAL, False, "Consolas"))

        # Add items to menu bar
        self.menuBar.Append(self.fileMenu, "&File")
        self.menuBar.Append(self.editMenu, "&Edit")

        # Set up layout
        self.sizer.Add(self.text, 1, wx.EXPAND | wx.ALL, 5)
        self.panel.SetSizer(self.sizer)
        self.SetMenuBar(self.menuBar)
        self.Layout()

        # Bind the event handler
        func_widget = {
            self.on_new: self.newCommand,
            self.on_new_window: self.newWindowCommand,
            self.on_save: self.saveItem,
            self.on_load: self.loadItem,
            self.save_dialog: self.saveAsItem,
            lambda e: self.Destroy(): self.exitCommand,
            lambda e: self.text.Undo(): self.undoCommand,
            lambda e: self.text.Cut(): self.cutCommand,
            lambda e: self.text.Copy(): self.copyCommand,
            lambda e: self.text.Paste(): self.pasteCommand,
            self.delete: self.deleteCommand
        }
        for i, j in func_widget.items():
            self.Bind(wx.EVT_MENU, i, j)

        # Add "*" to title if file is altered
        self.Bind(wx.EVT_TEXT, lambda e: self.SetTitle(
            self.GetTitle() if self.GetTitle().startswith("*") else "*"+self.GetTitle()
        ), self.text)

    def save_dialog(self, event):
        with wx.FileDialog(self, "Save As", wildcard=self.file_types,
                           style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_OK:
                self.file_path = fileDialog.GetPath()
                try:
                    # Save the content of the text control to the chosen file
                    with open(self.file_path, 'w') as f:
                        f.write(self.text.GetValue())
                        self.SetTitle(os.path.basename(self.file_path))
                    # remove the * in the title if any
                    self.SetTitle(
                        self.GetTitle()[1:] if self.GetTitle().startswith("*") else self.GetTitle()
                    )
                except IOError:
                    wx.LogError(f"Cannot save file '{self.file_path}'.")

    def on_save(self, event):
        """Handles the save file menu command"""
        if self.file_path and os.path.exists(self.file_path):
            try:
                # Save the content of the text control to the chosen file
                with open(self.file_path, 'w') as file:
                    file.write(self.text.GetValue())
                # remove the * in the title if any
                self.SetTitle(
                    self.GetTitle()[1:] if self.GetTitle().startswith("*") else self.GetTitle()
                )
            except IOError:
                wx.LogError(f"Cannot save file '{self.file_path}'.")
        else:
            self.save_dialog(event)

    def on_load(self, event):
        """Handles the load file menu command"""
        with wx.FileDialog(self, "Open File", wildcard=self.file_types,
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_OK:
                self.file_path = fileDialog.GetPath()
                try:
                    # open the selected file
                    with open(self.file_path, "r") as file:
                        data = file.read()
                        # input text in the text control after clearing it
                        self.text.Clear()
                        self.text.WriteText(data)
                        # change title
                        self.SetTitle(f"{os.path.basename(self.file_path)} - Notepad")
                except IOError:
                    wx.LogError(f"Cannot open file '{self.file_path}'.")
                except UnicodeDecodeError:
                    wx.LogError(f"Cannot open file '{self.file_path}'")

    def on_new(self, event):
        if self._check_save():
            self.text.Clear()
            self.SetTitle("*Untitled - Text Editor")
            self.file_path = None
        else:
            wx.LogWarning("You have not saved your document")

    @staticmethod
    def on_new_window(event):
        new_app = App(None)
        new_app.Show()

    def _check_save(self):
        # check if the value in the text control is the same as the content of file(if it is saved)
        if self.file_path and os.path.exists(self.file_path):
            with open(self.file_path, "r") as f:
                return f.read() == self.text.GetValue()
        else:
            return False

    def delete(self, event):
        start_pos, end_pos = self.text.GetSelection()
        if start_pos != end_pos:
            self.text.Remove(start_pos, end_pos)


if __name__ == '__main__':
    app = wx.App(False)
    frm = App(None)
    frm.Show()
    app.MainLoop()
