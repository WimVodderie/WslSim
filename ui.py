import wx
import os

import wslsim

class MainWindow(wx.Frame):
    def __init__(self, parent, title):

        wx.Frame.__init__(self, parent, title=title, size=(-1,-1))

        self._engine = wslsim.Engine()


        self.control = wx.TextCtrl(self, style=wx.TE_MULTILINE)

        # statusbar in the bottom of the window
        self.CreateStatusBar()

        # setting up the menu
        filemenu= wx.Menu()
        menuAbout= filemenu.Append(wx.ID_ABOUT, "&About"," Information about this program")
        menuExit = filemenu.Append(wx.ID_EXIT,"E&xit"," Terminate the program")

        # creating the menubar
        menuBar = wx.MenuBar()
        menuBar.Append(filemenu,"&File")
        self.SetMenuBar(menuBar)

        # events
        self.Bind(wx.EVT_MENU, self.OnExit, menuExit)
        self.Bind(wx.EVT_MENU, self.OnAbout, menuAbout)

        self.sizer2 = wx.BoxSizer(wx.HORIZONTAL)

        # buttons
        playBmp = wx.Bitmap("res/play.jpg", wx.BITMAP_TYPE_ANY)
        self.playButton = wx.BitmapButton(self, id=wx.ID_ANY, bitmap=playBmp, size=(playBmp.GetWidth()+10, playBmp.GetHeight()+10))
        self.playButton.Bind(wx.EVT_BUTTON,self.OnButtonPlay)
        self._engine._playButton.SetEnableCallback(self.OnButtonPlayEnabled)
        self.sizer2.Add(self.playButton, 1, wx.EXPAND)
        pauseBmp = wx.Bitmap("res/pause.jpg", wx.BITMAP_TYPE_ANY)
        self.pauseButton = wx.BitmapButton(self, id=wx.ID_ANY, bitmap=pauseBmp, size=(pauseBmp.GetWidth()+10, pauseBmp.GetHeight()+10))
        self.pauseButton.Bind(wx.EVT_BUTTON,self.OnButtonPause)
        self._engine._pauseButton.SetEnableCallback(self.OnButtonPauseEnabled)
        self.sizer2.Add(self.pauseButton, 1, wx.EXPAND)
        stopBmp = wx.Bitmap("res/stop.jpg", wx.BITMAP_TYPE_ANY)
        self.stopButton = wx.BitmapButton(self, id=wx.ID_ANY, bitmap=stopBmp, size=(stopBmp.GetWidth()+10, stopBmp.GetHeight()+10))
        self.stopButton.Bind(wx.EVT_BUTTON,self.OnButtonStop)
        self._engine._stopButton.SetEnableCallback(self.OnButtonStopEnabled)
        self.sizer2.Add(self.stopButton, 1, wx.EXPAND)
        ejectBmp = wx.Bitmap("res/eject.jpg", wx.BITMAP_TYPE_ANY)
        self.ejectButton = wx.BitmapButton(self, id=wx.ID_ANY, bitmap=ejectBmp, size=(ejectBmp.GetWidth()+10, ejectBmp.GetHeight()+10))
        self.ejectButton.Bind(wx.EVT_BUTTON,self.OnButtonEject)
        self._engine._ejectButton.SetEnableCallback(self.OnButtonEjectEnabled)
        self.sizer2.Add(self.ejectButton, 1, wx.EXPAND)

        # Use some sizers to see layout options
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.control, 1, wx.EXPAND)
        self.sizer.Add(self.sizer2, 0, wx.EXPAND)

        #Layout sizers
        self.SetSizer(self.sizer)
        self.SetAutoLayout(1)
        self.sizer.Fit(self)
        self.Show()

    def OnAbout(self,e):
        # Create a message dialog box
        dlg = wx.MessageDialog(self, " A simple simulator for\n web-stop-location", "About WSL", wx.OK)
        dlg.ShowModal() # Shows it
        dlg.Destroy() # finally destroy it when finished.

    def OnExit(self,e):
        self.Close(True)  # Close the frame.

    def OnOpen(self,e):
        """ Open a file"""
        dlg = wx.FileDialog(self, "Choose a file", self.dirname, "", "*.*", wx.FD_OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            self.filename = dlg.GetFilename()
            self.dirname = dlg.GetDirectory()
            f = open(os.path.join(self.dirname, self.filename), 'r')
            self.control.SetValue(f.read())
            f.close()
        dlg.Destroy()

    def OnButtonPlay(self,e):
        self.control.AppendText("Play pressed\n")
        self._engine._playButton.OnPressed()

    def OnButtonPlayEnabled(self,enabled):
        if enabled==True:
            self.playButton.Enable()
        else:
            self.playButton.Disable()

    def OnButtonPause(self,e):
        self.control.AppendText("Pause pressed\n")
        self._engine._pauseButton.OnPressed()

    def OnButtonPauseEnabled(self,enabled):
        if enabled==True:
            self.pauseButton.Enable()
        else:
            self.pauseButton.Disable()


    def OnButtonStop(self,e):
        self.control.AppendText("Stop pressed\n")
        self._engine._stopButton.OnPressed()

    def OnButtonStopEnabled(self,enabled):
        if enabled==True:
            self.stopButton.Enable()
        else:
            self.stopButton.Disable()


    def OnButtonEject(self,e):
        self.control.AppendText("Eject pressed\n")
        self._engine._ejectButton.OnPressed()

    def OnButtonEjectEnabled(self,enabled):
        if enabled==True:
            self.ejectButton.Enable()
        else:
            self.ejectButton.Disable()



app = wx.App(False)
frame = MainWindow(None, "Sample editor")
app.MainLoop()