import wx
import wx.stc
import os
import time

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
        self.formatMenu = wx.Menu()

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
        self.editMenu.AppendSeparator()
        self.findCommand = self.editMenu.Append(wx.ID_FIND, "FInd\tCtrl+F")
        self.editMenu.AppendSeparator()
        self.selectAllCommand = self.editMenu.Append(wx.ID_SELECTALL, "&Select All\tCtrl+A")
        self.time_dateCommand = self.editMenu.Append(-1, "&Time\\Date\tF5")

        # create options for format menu
        self.word_wrap = self.formatMenu.Append(-1, "&Word Wrap")
        self.font = self.formatMenu.Append(-1, "&Font..")

        # The text box and its font
        self.text = wx.stc.StyledTextCtrl(self.panel)
        self.current_font = wx.Font(12, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL,
                                    wx.FONTWEIGHT_NORMAL, faceName="Consolas")

        # supported file types
        self.file_types = "Text files (*.txt)|*.txt|" \
                          "Python files (*.py, *.pyc)|*.py;*.pyc|" \
                          "All Files (*.*)|*.*"

        # file that is open on this instance
        self.file_path = None

        # modify ui elements
        self.init_ui()

        # Create StatusBar and text
        self.statusBar = self.CreateStatusBar()
        self.statusBar.SetFieldsCount(3)
        self.statusBar.SetStatusWidths([-6, -2, -2])
        self.SetStatusText("", 0)
        self.SetStatusText("Ln 1, Col 1", 1)
        self.SetStatusText("100%", 2)

        # find dialog data
        self.find_data = None
        self.find_dlg = None

    def init_ui(self):
        self.SetTitle("*Untitled - Text Editor")
        self.SetSize(1000, 500)

        # Set font of text box
        self.text.StyleSetFont(wx.stc.STC_STYLE_DEFAULT, self.current_font)
        self.text.StyleClearAll()

        # Add items to menu bar
        self.menuBar.Append(self.fileMenu, "&File")
        self.menuBar.Append(self.editMenu, "&Edit")
        self.menuBar.Append(self.formatMenu, "&Format")

        # Set up layout
        self.sizer.Add(self.text, 1, wx.EXPAND | wx.ALL)
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
            self.delete: self.deleteCommand,
            self.findText: self.findCommand,
            lambda e: self.text.SelectAll(): self.selectAllCommand,
            lambda e: self.text.AppendText(
                f"{time.localtime().tm_hour - 12 if time.localtime().tm_hour > 12 else time.localtime().tm_hour}"
                f":{time.localtime().tm_min} "
                f"{'pm' if time.localtime().tm_hour > 12 else 'am'} "
                f"{time.localtime().tm_mday}/{time.localtime().tm_mon:02}/{time.localtime().tm_year:02}"
            ): self.time_dateCommand,
            self.wrap: self.word_wrap,
            self.set_font: self.font
        }
        for i, j in func_widget.items():
            self.Bind(wx.EVT_MENU, i, j)

        # Add "*" to title if file is altered
        self.Bind(wx.stc.EVT_STC_MODIFIED, self.change, self.text)

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
                        # input text in the text control after reading it
                        self.text.SetText(data)
                        # change title
                        self.SetTitle(f"{os.path.basename(self.file_path)} - Notepad")
                except IOError:
                    wx.LogError(f"Cannot open file '{self.file_path}'.")
                except UnicodeDecodeError:
                    wx.LogError(f"Cannot open file '{self.file_path}'")

    def on_new(self, event):
        if self._check_save():
            self.text.ClearAll()
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

    def wrap(self, event):
        mode = self.text.GetWrapMode()

        if mode == wx.stc.STC_WRAP_NONE:
            self.text.SetWrapMode(wx.stc.STC_WRAP_WORD)
        elif mode == wx.stc.STC_WRAP_WORD:
            self.text.SetWrapMode(wx.stc.STC_WRAP_NONE)
        else:
            self.text.SetWrapMode(wx.stc.STC_WRAP_NONE)

    def set_font(self, event):
        dialog = wx.FontDialog(self)
        if dialog.ShowModal() == wx.ID_OK:
            data = dialog.GetFontData()
            font = data.GetChosenFont()

            if font.IsOk():
                self.current_font = font
                self.text.StyleSetFont(wx.stc.STC_STYLE_DEFAULT, font)
                self.text.StyleClearAll()
    
    def change(self, event):
        self.SetTitle(
            self.GetTitle() if self.GetTitle().startswith("*") else "*" + self.GetTitle()
        )
        pos = self.text.GetCurrentPos()
        self.SetStatusText(f"Ln {self.text.LineFromPosition(pos)+1} Col {self.text.GetColumn(pos)+1}", 1)

    def findText(self, event):
        if not self.find_data:
            self.find_data = wx.FindReplaceData()
            self.find_data.SetFlags(wx.FR_DOWN)  # Default to searching down

        self.find_dlg = wx.FindReplaceDialog(self.text, self.find_data,
                                             "Find", wx.FR_NOMATCHCASE)
        self.find_dlg.Bind(wx.EVT_FIND, self.on_find)
        self.find_dlg.Bind(wx.EVT_FIND_NEXT, self.on_find)
        self.find_dlg.Bind(wx.EVT_FIND_CLOSE, self.on_find_close)
        self.find_dlg.Show()

    def on_find(self, event):
        search_string = event.GetFindString()
        if not search_string:
            return

        # convert to STC flags
        find_flags = self.find_data.GetFlags()
        stc_flags = 0
        if not (find_flags & wx.FR_MATCHCASE):
            stc_flags |= wx.stc.STC_FIND_MATCHCASE
        if find_flags & wx.FR_WHOLEWORD:
            stc_flags |= wx.stc.STC_FIND_WHOLEWORD

        search_down = event.GetFlags() & wx.FR_DOWN
        if search_down:
            self.text.SearchAnchor()
            found_pos = self.text.SearchNext(stc_flags, search_string)
        else:
            current_pos = self.text.GetCurrentPos()
            self.text.SetSelection(current_pos, current_pos)
            self.text.SearchAnchor()
            found_pos = self.text.SearchPrev(stc_flags, search_string)

        # If nothing is found, show a message.
        if found_pos == -1:
            wx.MessageBox(f'Could not find "{search_string}"', 'Find',
                          wx.OK | wx.ICON_INFORMATION, self)

    def on_find_close(self, event):
        """Destroy the dialog when it's closed."""
        if self.find_dlg:
            self.find_dlg.Destroy()
            self.find_dlg = None

if __name__ == '__main__':
    app = wx.App(False)
    frm = App(None)
    frm.Show()
    app.MainLoop()
