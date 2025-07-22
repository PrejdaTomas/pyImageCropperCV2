from __future__ import annotations
try: from A_DEPENDENCIES import runConstants, RunMode
except: from .A_DEPENDENCIES import runConstants, RunMode

if runConstants.RUNMODE== RunMode.RUN:
	from .A_DEPENDENCIES import typing, os, pickle
	from .A_DEPENDENCIES import cv2, Path
	from .A_DEPENDENCIES import ImageType, ImageOrientation, RunMode
	from . import A_DEPENDENCIES
	from . import B_DESCRIPTORS

else:
	from A_DEPENDENCIES import typing, os, pickle
	from A_DEPENDENCIES import cv2, Path
	from A_DEPENDENCIES import ImageType, ImageOrientation, RunMode
	import A_DEPENDENCIES
	import B_DESCRIPTORS

class Picklable(object):
	"""
	Picklable is a class used for mixing in creation of other classes, the subclasses are provided with the added possibility of serialization.
	Defines the loadFromFile class method and saveToFile instance methods.
	"""

	_pickleSuffix: str
	"""str: a private variable containing the suffix of the serialized object copy"""

	@classmethod
	def loadFromFile(cls, filePath: Path) -> Picklable:
		"""loadFromFile class method recreates and returns a new instance of the class from the file at filePath.

		Args:
			filePath (Path): an existing path to the file with a valid suffix

		Raises:
			FileNotFoundError: the provided address does not exists
			IOError: the provided address's suffix is not valid for this class
			TypeError: the loaded instance is not the instance of this class

		Returns:
			Picklable: a new instance of this class
		"""
		if not os.path.exists(filePath): raise FileNotFoundError(f"{cls.__name__}.loadFromFile: the provided path does not exist {filePath}")

		if not os.path.exists(filePath.endswith(cls._pickleSuffix)): raise IOError(f"{cls.__name__}.loadFromFile: the provided path's suffix is not valid for this type {filePath}: {os.path.splitext(filePath)[1]}")

		with open(file=filePath, mode="rb") as readPort:
			nuInstance: Picklable = pickle.load(filename=readPort)

		if not isinstance(nuInstance, cls): raise TypeError(f"{cls.__name__}.loadFromFile: the loaded object is not an instance of this class: {nuInstance.__class__.__name__}")

		return nuInstance

	def saveToFile(self, filePathNoSuffix: Path) -> None:
		"""saveToFile instance method stores this instance to the path provided by the programmer.

		Args:
			filePath (Path): an existing path to the file without a suffix (may be provided, but will be cropped and replaced)

		Raises:
			FileNotFoundError: any directory of the provided path directory structure does not exist
		"""
		filePath	= Path(f"{os.path.splitext(filePathNoSuffix)[0]}.{self.__class__._pickleSuffix}")
		checkPath	= os.path.dirname(filePath).split(".")

		for index, checkPathCur in enumerate(checkPath):
			checkPathCur = os.path.join(filePath[:index])
			if not os.path.exists(checkPathCur):
				raise FileNotFoundError(f"{self}: saveToFile: directory {checkPathCur} in {filePath} does not exist")

		with open(file=filePath, mode="wb") as writePort:
			pickle.dump(obj=self, file=writePort)

	#def __del__(self) -> None: print(f"{self}: removing from memory")

class Constants(object):
	_instance: typing.Optional[Constants] = None
	
	def __new__(cls, *args, **kwargs) -> Constants:
		"""Ensures the returned Constants instance is a singleton.

		Returns:
			Constants: a pointer to the new singleton Constants instance
		"""
		if cls._instance is None:
			cls._instance = super().__new__(cls)
			cls._instance.__dict__.update(kwargs)
			print(cls)
		return cls._instance

	def __str__(self) -> str:
		returnStr = f"{self.__class__.__name__} @ {hex(id(self))}\n"
		for argument,value in self.__dict__.items():
			returnStr += f"\t{argument.ljust(24, ' ')}= <{value}: {type(value)}>\n"
		return returnStr



class UserConstants(Constants):
	SourceFolder: A_DEPENDENCIES.Path	= B_DESCRIPTORS.WriteOnce_CreatePath(name="SourceFolder")
	TargetFolder: A_DEPENDENCIES.Path	= B_DESCRIPTORS.WriteOnce_CreatePath(name="TargetFolder")
	MinimumPixelsDiagonal: int			= B_DESCRIPTORS.WriteOnce_UnsignedInteger(name="MinimumPixelsDiagonal")

	WidthScale: int						= B_DESCRIPTORS.WriteOnce_UnsignedInteger(name="WidthScale")
	HeightScale: int					= B_DESCRIPTORS.WriteOnce_UnsignedInteger(name="HeightScale")
	ScreenPercentage: float				= B_DESCRIPTORS.WriteOnce_RangedFloat(name="ScreenPercentage", minimum=0.05, maximum=float("inf"))

	ImageType: str						= B_DESCRIPTORS.WriteOnce_String(name="ImageType")
	QualityJPG: int						= B_DESCRIPTORS.WriteOnce_RangedInt(name="QualityJPG", minimum=10, maximum=100)
	QualityPNG: int						= B_DESCRIPTORS.WriteOnce_RangedInt(name="QualityPNG", minimum=1, maximum=10)
	Debug: bool							= False
 
	def __init__(		self,
						SourceFolder:	typing.Optional[A_DEPENDENCIES.Path]=	os.path.dirname(os.path.dirname(__file__)), 
						TargetFolder:	typing.Optional[A_DEPENDENCIES.Path]=	os.path.join(os.path.dirname(os.path.dirname(__file__)), "CROPPED"), 
						MinimumPixelsDiagonal:	typing.Optional[int]=				360, 
						WidthScale:		typing.Optional[int]=				4, 
						HeightScale:	typing.Optional[int]=				3, 
						ScreenPercentage:	typing.Optional[float]=				0.25, 
						ImageType:		typing.Optional[str]=				"JPG", 
						QualityJPG:	typing.Optional[int]=				95, 
						QualityPNG:	typing.Optional[int]=				5,
						Debug: typing.Optional[bool]= 					False
	) -> None: pass

	def __str__(self) -> str:
		returnStr = f"{self.__class__.__name__} @ {hex(id(self))}\n"
		for argument,value in self.__dict__.items():
			returnStr += f"\t{argument.ljust(24, ' ')}= <{value}: {type(value)}>\n"
		return returnStr

class IndexedCycle(typing.Generic[A_DEPENDENCIES.T]):
	_sequence: typing.Sequence[A_DEPENDENCIES.T]
	_index: int

	def __init__(self, sequence: typing.Sequence[A_DEPENDENCIES.T]) -> None:
		self._sequence = sequence
		self._index = -1

	def __len__(self) -> int: return len(self._sequence)
 
	def __next__(self) -> A_DEPENDENCIES.T:
		self._index = (self._index + 1) % len(self._sequence)
		return self._sequence[self._index]

	def previous(self) -> A_DEPENDENCIES.T:
		self._index = (self._index - 1) % len(self._sequence)
		return self._sequence[self._index]

	def __getitem__(self, index: int) -> A_DEPENDENCIES.T:
		self._index = index
		return self._sequence[self._index]

	def __repr__(self) -> str: return f"{self._sequence}"


