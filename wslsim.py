from enum import Enum
import logging

logging.basicConfig(level=logging.DEBUG, filename=f"{__file__}.log", format="%(asctime)s:%(message)s")


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


class State(Enum):
    Standby = 1
    Paused = 2
    Printing = 3


class StateManager:
    def __init__(self):
        self._current = State.Standby
        self._target = State.Standby
        self._statesCallback = None
        self._incrementLock = None
        self._decrementLock = None

    def Dump(self):
        print(f"State: Current {self._current} Target {self._target}")
        print(f"Increment: {self._incrementLock if self._incrementLock!=None else 'None'}")
        print(f"Decrement: {self._decrementLock if self._decrementLock!=None else 'None'}")

    def SetStatesCallback(self,callback):
        self._statesCallback=callback

    def SetTargetState(self,newTargetState):
        if self._target!=newTargetState:
            self._target=newTargetState
            self.CallStatesCallback()

    def CallStatesCallback(self):
        if self._statesCallback!=None:
            self._statesCallback(self._current,self._target)

    def IncrementLock(self,incrementLockState):
        self._incrementLock = incrementLockState

    def DecrementLock(self,decrementLockState):
        self._decrementLock=decrementLockState

    def Run(self):
        changed=False

        # UP - from standby to paused
        if self._target.value > State.Standby.value and self._current == State.Standby:
            if self._incrementLock==None or self._incrementLock.value > State.Standby.value:
                self._current = State.Paused
                changed=True

        # UP - from paused to printing
        if self._target.value == State.Printing.value and self._current == State.Paused:
            if self._incrementLock==None or self._incrementLock.value > State.Paused.value:
                self._current = State.Printing
                changed=True

        # DOWN - when engine is printing and target state drops we follow immediately
        if self._current.value == State.Printing.value and self._target.value < State.Printing.value:
            self._current = State.Paused

        if self._current.value == State.Paused.value and self._target.value == State.Standby.value:
            self._current = State.Standby

        if changed:
            self.CallStatesCallback()


class Engine:
    def __init__(self):
        self._stateManager = StateManager()
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
        self._stateManager.SetTargetState(State.Printing)
        self.RunEngine()

    def OnPausePressed(self):
        self._stateManager.SetTargetState(State.Paused)
        self.RunEngine()

    def OnStopPressed(self):
        self._stateManager.SetTargetState(State.Standby)
        self.RunEngine()

    def OnEjectPressed(self):
        self._stateManager.SetTargetState(State.Standby)
        self.RunEngine()

    def Dump(self):
        self._stateManager.Dump()
        self._web.Dump()

    def QueueSheets(self,count,sheetType):
        for i in range(count):
            self._queue.Push(Sheet(sheetType))

    def RunWeb(self):
        # when engine is in printing state we advance the web
        if self._stateManager._current == State.Printing:
            self._position += 1

            # transfer a sheet from the queue to the web
            self._web.Push(self._queue.Pop(), self._position)

    def UpdateButtons(self):

        if self._stateManager._target == State.Standby:
            self._playButton.Enable()
            self._pauseButton.Enable()
            self._stopButton.Disable()
            self._ejectButton.Disable()

        if self._stateManager._target == State.Paused:
            self._playButton.Enable()
            self._pauseButton.Disable()
            self._stopButton.Enable()
            self._ejectButton.Enable()

        if self._stateManager._target == State.Printing:
            self._playButton.Disable()
            self._pauseButton.Enable()
            self._stopButton.Enable()
            self._ejectButton.Disable()


    def RunEngine(self):

        # when queue is empty the engine should not pass paused
        if self._queue.IsEmpty():
            self._stateManager.IncrementLock(State.Paused)
        else:
            self._stateManager.IncrementLock(None)

        self._stateManager.Run()
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

    engine._stateManager.SetTargetState(State.Printing)

    for i in range(20):
        engine.RunEngine()
        engine.Dump()
