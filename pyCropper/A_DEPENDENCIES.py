from __future__ import annotations
import os
import typing
from numbers import Number
from enum import Enum, IntEnum
import cv2
import cv2.typing as cv2t


import numpy as np
import time
import ctypes
import argparse
import pickle
from PIL import Image, ImageTk
import tkinter as tk
import signal, sys
import math
import itertools
import time

def signal_handler(sig, frame):
	print('You pressed Ctrl+C!')
	sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
aPoint		= typing.Tuple[Number, Number]
aCorners	= typing.Tuple[aPoint]
aColour		= typing.Tuple[int, int, int]
aShape		= typing.Tuple[int, int, int]

T			= typing.TypeVar("T")

allowedFileTypes: typing.Sequence[str] = [".jpg", ".jpeg", ".png", ".bmp", ".jfif"]

class Path(str, os.PathLike):
	def __new__(cls, value: str) -> typing.Self:
		if len(value) > 260: raise ValueError(f"{cls.__name__}: {value} length exceeds 260 characters")
		return super(Path, cls).__new__(cls, value)

	def __setattr__(self, name: str, value: str) -> None:
		if not isinstance(value, str): raise TypeError("Value must be a string")
		if name == 'value' and len(value) >= 260: raise IOError(f"{self.__class__.__name__}: '{value}' -> length exceeds 260 characters")
		if name == 'value' and len(value) <= 0: raise IOError(f"{self.__class__.__name__}: '{value}' -> zero-length or negative lengthpath")

		super().__setattr__(name, value)

	def __fspath__(self) -> str:
		return str(self)



VALUE = typing.TypeVar('VALUE')
CLASS = typing.TypeVar('CLASS')


CV2_ESCAPE:		int = 27
CV2_LEFT:		int = 81
CV2_UP:			int = 82
CV2_RIGHT:		int = 83
CV2_DOWN:		int = 84
CV2_KEYS:		typing.Tuple[int, ...] = (CV2_ESCAPE, CV2_LEFT, CV2_RIGHT, CV2_UP, CV2_DOWN)



class ImageType(Enum):
	JPG = "jpg"
	PNG = "png"

class ImageOrientation(Enum):
	LANDSCAPE	= "LANDSCAPE"
	PORTRAIT	= "PORTRAIT"

class RunMode(Enum):
	RUN		= "RUN"
	TEST	= "TEST"


class RunModeConstants(object):
	_instance: typing.Optional[RunModeConstants] = None

	def __new__(cls) -> RunModeConstants:
		if not cls._instance:
			nuInstance = super(RunModeConstants, cls).__new__(cls)
			cls._instance = nuInstance
		return cls._instance

	RUNMODE: RunMode = RunMode.RUN

screenX, screenY	= ctypes.windll.user32.GetSystemMetrics(0), ctypes.windll.user32.GetSystemMetrics(1)

class TkinterActions(object):
	LMB: str = "<Button-1>"
	MMB: str = "<Button-2>"
	RMB: str = "<Button-3>"
	INTERRUPT: str = "<Control-c>"
	MOUSEMOVE: str = "<Motion>"
	TAB: str = "<KeyPress-Tab>"

class ClickStates(IntEnum):
	NOTHING = 0
	FIRST = 1
	BOTH = 2

runConstants = RunModeConstants()