from enum import Enum
import logging

logging.basicConfig(level=logging.DEBUG, filename="wslsim.log", format="%(asctime)s:%(message)s")


class State(Enum):
    Standby = 1
    Paused = 2
    Printing = 3


class SheetType(Enum):
    Blank = 1
    Job = 2
    Test = 3


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

    def Cleanup(self, position):
        """ Remove all sheets from the web that have passed the given position."""



class Engine:
    def __init__(self):
        self._currentState = State.Standby
        self._targetState = State.Standby

        self._queue = Queue()
        self._web = Web()

        self._stopLocation = 10
        self._pauseLocation = 15
        self._ejectLocation = 20

        self._position = 0

    def GotoStandby(self):
        self._targetState = State.Standby

    def GotoPaused(self):
        self._targetState = State.Paused

    def GotoPrinting(self):
        self._targetState = State.Printing

    def RunStateMachine(self):
        # UP - can always go to pausing
        if self._targetState > State.Standby and self._currentState == State.Standby:
            self._currentState = State.Pausing

        # UP - can go to printing when the queue is not empty
        if self._targetState == State.Printing and self._currentState == State.Pausing:
            if self._queue.IsEmpty() == False:
                self._currentState = State.Printing

        # DOWN - when engine is printing and target state drops we follow immediately
        if self._currentState == State.Printing and self._targetState < State.Printing:
            self._currentState = State.Pausing

        if self._currentState == State.Pausing and self._targetState == State.Standby:
            self._currentState = State.Standby

    def RunWeb(self):
        # when engine is in printing state we advance the web
        if self._currentState == State.Printing:
            self._position += 1

            # transfer a sheet from the queue to the web
            self._web.Push(self._queue.Pop(), self._position)

    def RunEngine(self):
        self.RunStateMachine()
        self.RunWeb()


class Button:
    def __init__(self):
        pass

    def OnPressed(self):
        pass

    def Enable(self):
        pass

    def Disable(self):
        pass


class UI:
    def __init__(self):
        self._playButton = Button()
        self._pauseButton = Button()
        self._stopButton = Button()
        self._ejectButton = Button()


class BusinessLogic:
    def __init__(self):
        pass

