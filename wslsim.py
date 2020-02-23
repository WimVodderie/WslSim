from enum import Enum
import logging

logging.basicConfig(level=logging.DEBUG, filename=f"{__file__}.log", format="%(asctime)s:%(message)s")


class State(Enum):
    Standby = 1
    Paused = 2
    Printing = 3


class SheetType(Enum):
    Blank = "-"
    Job = "J"
    Test = "T"


class Sheet:
    def __init__(self, type):
        self._type = type
        self._basePosition = 0

    def Location(position):
        return position - self._basePosition


class Queue:
    """ Keep track of the sheets that have been queued."""

    def __init__(self):
        self._log = logging.getLogger("Queue")
        self._sheets = []

    def IsEmpty(self):
        return len(self._sheets) == 0

    def Push(self,sheet):
        self._sheets.append(sheet)

    def Pop(self):
        if self.IsEmpty():
            self._log.debug("blank sheet popped")
            return Sheet(SheetType.Blank)
        else:
            self._log.debug("non-blank sheet popped")
            return self._sheets.pop(0)

    def Purge(self):
        self._sheets = []


class Web:
    def __init__(self):
        self._log = logging.getLogger("Web")
        self._sheets = []

    def Push(self, sheet, position):
        self._log.debug(f"{sheet._type} sheet popped at base position {position}")
        sheet._basePosition = position
        self._sheets.append(sheet)

    def Dump(self):
        msg=""
        for s in self._sheets:
            msg+=s._type.value
        print(msg)

    def Cleanup(self, position):
        """ Remove all sheets from the web that have passed the given position."""
        pass


class Engine:
    def __init__(self):
        self._currentState = State.Standby
        self._targetState = State.Standby

        self._queue = Queue()
        self._web = Web()

        self._stopLocation = 10
        self._pauseLocation = 15
        self._ejectLocation = 20

        self._playButton = Button()
        self._playButton.SetPressedCallback(self.OnPlayPressed)
        self._pauseButton = Button()
        self._pauseButton.SetPressedCallback(self.OnPausePressed)
        self._stopButton = Button()
        self._stopButton.SetPressedCallback(self.OnStopPressed)
        self._ejectButton = Button()
        self._ejectButton.SetPressedCallback(self.OnEjectPressed)

        self._position = 0


    def OnPlayPressed(self):
        self.GotoPrinting()
        self.RunEngine()

    def OnPausePressed(self):
        self.GotoPaused()
        self.RunEngine()

    def OnStopPressed(self):
        self.GotoStandby()
        self.RunEngine()

    def OnEjectPressed(self):
        self.GotoStandby()
        self.RunEngine()

    def Dump(self):
        print(f"State: Current {self._currentState} Target {self._targetState}")
        self._web.Dump()

    def QueueSheets(self,count,sheetType):
        for i in range(count):
            self._queue.Push(Sheet(sheetType))

    def GotoStandby(self):
        self._targetState = State.Standby

    def GotoPaused(self):
        self._targetState = State.Paused

    def GotoPrinting(self):
        self._targetState = State.Printing

    def RunStateMachine(self):
        # UP - can always go to Paused
        if self._targetState.value > State.Standby.value and self._currentState.value == State.Standby.value:
            self._currentState = State.Paused

        # UP - can go to printing when the queue is not empty
        if self._targetState.value == State.Printing.value and self._currentState.value == State.Paused.value:
            if self._queue.IsEmpty() == False:
                self._currentState = State.Printing

        # DOWN - when engine is printing and target state drops we follow immediately
        if self._currentState.value == State.Printing.value and self._targetState.value < State.Printing.value:
            self._currentState = State.Paused

        if self._currentState.value == State.Paused.value and self._targetState.value == State.Standby.value:
            self._currentState = State.Standby

    def RunWeb(self):
        # when engine is in printing state we advance the web
        if self._currentState == State.Printing:
            self._position += 1

            # transfer a sheet from the queue to the web
            self._web.Push(self._queue.Pop(), self._position)

    def UpdateButtons(self):

        if self._targetState == State.Standby:
            self._playButton.Enable()
            self._pauseButton.Enable()
            self._stopButton.Disable()
            self._ejectButton.Disable()

        if self._targetState == State.Paused:
            self._playButton.Enable()
            self._pauseButton.Disable()
            self._stopButton.Enable()
            self._ejectButton.Enable()

        if self._targetState == State.Printing:
            self._playButton.Disable()
            self._pauseButton.Enable()
            self._stopButton.Enable()
            self._ejectButton.Disable()


    def RunEngine(self):
        self.RunStateMachine()
        self.RunWeb()
        self.UpdateButtons()

class Button:
    def __init__(self):
        self._enabled=True
        self._pressedCallback=None
        self._enableCallback=None

    def SetPressedCallback(self,callback):
        self._pressedCallback=callback

    def SetEnableCallback(self,callback):
        self._enableCallback=callback

    def OnPressed(self):
        if self._pressedCallback!=None:
            self._pressedCallback()

    def IsEnabled(self):
        return self._enabled

    def _SetEnabled(self,enabled):
        self._enabled=enabled
        if self._enableCallback!=None:
            self._enableCallback(self._enabled)

    def Enable(self):
        self._SetEnabled(True)

    def Disable(self):
        self._SetEnabled(False)


if __name__=="__main__":
    engine = Engine()

    engine.QueueSheets(5,SheetType.Test)
    engine.QueueSheets(5,SheetType.Job)

    engine.GotoPrinting()

    for i in range(20):
        engine.RunEngine()
        engine.Dump()
