from __future__ import annotations
if __name__ == "__main__":
	from A_DEPENDENCIES import runConstants, RunMode
	runConstants.RUNMODE = RunMode.TEST

	from A_DEPENDENCIES import allowedFileTypes, screenX, screenY, TkinterActions, signal, signal_handler, ClickStates, itertools
	from A_DEPENDENCIES import aPoint, aCorners
	from A_DEPENDENCIES import os, cv2, typing, time, np
	from A_DEPENDENCIES import Image, ImageTk, tk

	from A_DEPENDENCIES import Path, ImageOrientation
	from A_DEPENDENCIES import aShape, cv2t
	from D_CONSTANTS import userConstants
	import B_DESCRIPTORS
	from C_CLASSES_UTILITY import Picklable
	import E_FUNCTIONS_UTILITY
	import pyCropper.F_GEOMETRY as F_GEOMETRY
	from pyCropper.F_GEOMETRY import Point, Rectangle


else:
	from .A_DEPENDENCIES import allowedFileTypes, screenX, screenY, TkinterActions, signal, signal_handler, ClickStates
	from .A_DEPENDENCIES import aPoint, aCorners, itertools
	from .A_DEPENDENCIES import os, cv2, typing, time, np
	from .A_DEPENDENCIES import Path, ImageOrientation
	from .A_DEPENDENCIES import Image, ImageTk, tk

	from .A_DEPENDENCIES import aShape, cv2t
	from .D_CONSTANTS import userConstants
	from . import B_DESCRIPTORS
	from .C_CLASSES_UTILITY import Picklable
	from . import E_FUNCTIONS_UTILITY
	from . import F_GEOMETRY
	from .F_GEOMETRY import Point, Rectangle



class ImageWrapper(Picklable, B_DESCRIPTORS.ImageWrapperTYPECHECK):
	_pickleSuffix = ".imgW"
	image: cv2t.MatLike
 
	@property
	def shape(self) -> aShape: return self.image.shape

	@property
	def colorChannels(self) -> int: return self.shape[2]

	@property
	def x(self) -> int: return self.shape[1]

	@property
	def y(self) -> int: return self.shape[0]

	@property
	def diagonal(self) -> int: return int(round((self.x**2 + self.y**2)**0.5, 0))

	@property
	def ARfloat(self) -> float: return self.x/self.y if self.x < self.y else self.y/self.x


	@property
	def ARstr(self) -> str: return f"{self.x}:{self.y}" if self.x < self.y else f"{self.y}:{self.x}"



	@property
	def xScaleScreen(self) -> float: return self.x/screenX

	@property
	def yScaleScreen(self) -> float: return self.y/screenY

	@property
	def scaleScreenFactor(self) -> float: return 1.0 / max(self.xScaleScreen, self.yScaleScreen)

	imgOrigOrient: ImageOrientation		= B_DESCRIPTORS.ImageOrienter(name="imgOrigOrient", getFromAttr="image")

	def __init__(self, image: cv2t.MatLike, screenScale: typing.Optional[float] = 0.75):
		super().__init__()
		self._origImage = image.copy()
		self.image = image
		self.screenScale = screenScale

		self._scaleX_orig = self.x/screenX
		self._scaleY_orig = self.y/screenY

		self._origSizeX = self.x
		self._origSizeY = self.y

		self.rotationState = 0
		self.horizontalState = self._origSizeX > self._origSizeY
		self.verticalState = self._origSizeY > self._origSizeX


	@classmethod
	def readImage(cls, filePath: Path) -> ImageWrapper:
		if not os.path.exists(filePath):
			raise FileNotFoundError(f"{cls.__name__}.readImage: attempting to read an image from a non-existent address {filePath}")
		readImage: cv2t.MatLike = cv2.imread(filename=filePath)
		nuInstance = cls(readImage)
		return nuInstance

	def __array__(self, dtype=None) -> cv2t.MatLike:
		if self.image: return self.image
		else: raise ValueError(f"{self}: something is trying to access the {self}.image attribute, which is not implemented, through the __array__ method")

	def __getitem__(self, key: typing.Union[int, slice, typing.Tuple[int,...]]) -> cv2t.MatLike:
		return self.image[key]

	@property
	def shape(self) -> aShape: return self.image.shape


	def rotateClockwise(self) -> None:
		self.image = cv2.rotate(
			self.image, cv2.ROTATE_90_CLOCKWISE
		)
		self.rotationState += 1
		if self.rotationState == 4: self.rotationState = 0
		if userConstants.Debug: print(f"{self}: rotated 90degs clockwise")

	def rotateCounterClockwise(self) -> None:
		self.image = cv2.rotate(
			self.image, cv2.ROTATE_90_COUNTERCLOCKWISE
		)
		self.rotationState -= 1

		if self.rotationState == -1: self.rotationState = 3
		if userConstants.Debug: print(f"{self}: rotated 90degs counter clockwise")

	def flipHorizontal(self) -> None:
		self.image = cv2.flip(self.image, 1) if self.imgOrigOrient == ImageOrientation.LANDSCAPE else cv2.flip(self.image, 0)
		self.horizontalState = not self.horizontalState
		if userConstants.Debug: print(f"{self}: flipped along horizontal axis")

	def flipVertical(self) -> None:
		self.image = cv2.flip(self.image, 0) if self.imgOrigOrient == ImageOrientation.LANDSCAPE else cv2.flip(self.image, 1)
		self.verticalState = not self.verticalState
		if userConstants.Debug: print(f"{self}: flipped along vertical axis")

	def flipBoth(self) -> None:
		self.image = cv2.flip(self.image, -1)
		self.horizontalState	= not self.horizontalState
		self.verticalState		= not self.verticalState
		if userConstants.Debug: print(f"{self}: flipped along main diagonal")

	def transpose(self) -> None:
		prevtranspose = self.imgOrigOrient

		self.image= self.image.transpose(1,0,2)
		self.flipHorizontal()
		if userConstants.Debug: print(f"{self}: transposed image from {prevtranspose} to {self.imgOrigOrient}")

	# def reset(self) -> None:
	# 	while self.rotationState != 0:
	# 		self.rotateClockwise()

	# 	if self.verticalState is not self._origVerticalState: self.flipVertical()
	# 	if self.horizontalState is not self._origHorizontalState: self.flipHorizontal()
	# 	if userConstants.Debug: print(f"{self}: reseted image transform")


	def reset(self) -> None:
		self.transposeState		= False
		self.rotationState		= False
		self.verticalState		= False
		self.horizontalState	= False
		self.image = self._origImage
		if userConstants.Debug: print(f"{self}: reseted image transform")

	@property
	def fittedCoords(self) -> tuple[int, int]:
		newX	= self.scaleScreenFactor * self.x
		newY	= self.scaleScreenFactor * self.y
		return newX, newY

	def getScaledCoords(self, scaleFactor: float) -> typing.Tuple[int, int]:
		return tuple([int(round(scaleFactor * _, 0)) for _ in self.fittedCoords])
 
	def fitToScreen(self) -> None:
		self.image		= cv2.resize(
			src=self.image,
			dsize=self.getScaledCoords(self.screenScale),
			fx=self.screenScale,
			fy=self.screenScale,
		)

	def __str__(self) -> str:
		return f"<{self.__class__.__name__}(x={self.x}, y={self.y}, channels={self.colorChannels}) @ {hex(id(self))}>"


class ImageHandler(Picklable):
	_pickleSuffix = ".imgH"
	imagePath: Path	= B_DESCRIPTORS.ValidPathDescriptor(name="imagePath")
	image:		ImageWrapper
	preview: 	ImageWrapper

	def __init__(self, filePath: Path, screenScale: typing.Optional[float] = 0.75):
		self.screenScale = screenScale
		self.imagePath = filePath
		self.image = ImageWrapper.readImage(filePath=filePath)

		self.preview =  ImageWrapper(image=	cv2.resize(	src=self.image.image.copy(),
													dsize=self.image.getScaledCoords(scaleFactor=screenScale),
													fx=userConstants.ScreenPercentage,
													fy=userConstants.ScreenPercentage)
		)

	def transpose(self) -> None:
		self.preview.transpose()
		self.image.transpose()

	def rotateClockwise(self) -> None:
		self.preview.rotateClockwise()
		self.image.rotateClockwise()

	def rotateCounterClockwise(self) -> None:
		self.preview.rotateCounterClockwise()
		self.image.rotateCounterClockwise()

	def flipVertical(self) -> None:
		self.preview.flipVertical()
		self.image.flipVertical()

	def flipHorizontal(self) -> None:
		self.preview.flipHorizontal()
		self.image.flipHorizontal()

	def reset(self) -> None:
		self.preview.reset()
		self.image.reset()

	def fitPreview(self) -> None: self.preview.fitToScreen()

	def copyTransformStates(self) -> None:
		self.preview.verticalState = self.image.verticalState
		self.preview.horizontalState = self.image.horizontalState
		self.preview.rotationState = self.image.rotationState

	@property
	def aspectRatio(self) -> float:
		if self.image.imgOrigOrient == ImageOrientation.LANDSCAPE: returnValue= self.image.x/self.image.y
		else: returnValue= self.image.y/self.image.x
		return round(returnValue, 5)


class Displayer(Picklable):
	mousePos: Point  = None
	corner_1: typing.Union[Point, None]  = None
	corner_2: typing.Union[Point, None]  = None

	croppingAllowed: bool = None
	clickState: ClickStates = ClickStates.NOTHING

	@property
	def rectangle(self) -> typing.Optional[Rectangle]:
		if (self.corner_1 and self.corner_2): return Rectangle(pt1=self.corner_1, pt2=self.corner_2)
		return None
	
	def __init__(	self,
					handler: ImageHandler,
					screenName: typing.Optional[str] = "Cropper.py",
					screenScale: typing.Optional[float] = 0.75,
					frameRate: typing.Optional[int] = 30
		) -> None:
		super().__init__()
		self.handler			= handler
		self.screenName			= screenName
		self.croppingAllowed	= False

		AR = max(userConstants.WidthScale, userConstants.HeightScale), min(userConstants.WidthScale, userConstants.HeightScale)
		self.targetAR			= AR if self.handler.image.imgOrigOrient == ImageOrientation.LANDSCAPE else AR[::-1]

		self.clickState			= ClickStates.NOTHING
		self.screenScale		= screenScale

		self.processed			= False
		self.frameRate			= frameRate
		self.frameFreq			= 1./self.frameRate

	def mainLoop(self, targetPath: Path) -> None:
		self.initRender()
		cornersPreview = None
		firstIterToRefresh = True

		while not (cv2.getWindowProperty(self.screenName, cv2.WND_PROP_VISIBLE) < 1):
			time.sleep(self.frameFreq)
			self.handler.preview.image = self.handler.image.image.copy()
			self.handler.copyTransformStates()

			if firstIterToRefresh:
				self.handler.screenScale			= userConstants.ScreenPercentage
				self.handler.image.screenScale		= self.handler.screenScale
				self.handler.preview.screenScale	= self.handler.screenScale
				firstIterToRefresh = not firstIterToRefresh

			try:
				self.handler.fitPreview()
				if self.croppingAllowed and not self.rectangle:
					AR = 		(self.targetAR[1]/self.targetAR[0]) #\

					adjusted_end		= self.mousePos.moveByAspectRatio(start=self.corner_1, aspectRatio=AR)#, screenScaleFactor=self.handler.screenScale),
					cornersPreview		= Rectangle(pt1=self.corner_1, pt2=adjusted_end)



				else: cornersPreview = self.rectangle

				if cornersPreview:
					if not self.rectangle:
						drawR = Rectangle(self.mousePos, cornersPreview.point2)
						F_GEOMETRY.drawArrow(disp=self.handler.preview.image, corners=drawR, colour=(0,0,0,), thickness=4)

					if cornersPreview.largeEnough(self.handler.preview.image): 
						F_GEOMETRY.greenInfo(	imageOrientation=self.handler.preview.imgOrigOrient,
											disp=self.handler.preview.image,
											corners=cornersPreview)
						

					else:
						F_GEOMETRY.redWarning(	imageOrientation=self.handler.preview.imgOrigOrient,
											disp=self.handler.preview.image,
											corners=cornersPreview)

				cv2.imshow(winname=self.screenName, mat=self.handler.preview.image)
				key = cv2.waitKey(1) & 0xFF

				#region keypresses
				if key == 9:
					if userConstants.Debug: print(f"\tINVERTING SELLECTION")
					self.targetAR = tuple(self.targetAR[::-1])

				elif key in E_FUNCTIONS_UTILITY.ords('t'):
					if userConstants.Debug: print(f"\tTRANSPOSING IMAGE")

					self.handler.transpose()
					AR = max(userConstants.HeightScale, userConstants.WidthScale), min(userConstants.HeightScale, userConstants.WidthScale)
					self.targetAR = AR if self.handler.preview.imgOrigOrient == ImageOrientation.LANDSCAPE else AR[::-1]

				elif key in E_FUNCTIONS_UTILITY.ords('q'):
					if userConstants.Debug: print(f"\tRotation SELECTION COUNTER-CLOCKWISE")
					self.handler.rotateCounterClockwise()

				elif key in E_FUNCTIONS_UTILITY.ords('e'):
					if userConstants.Debug: print(f"\tRotation SELECTION CLOCKWISE")
					self.handler.rotateClockwise()

				elif key in E_FUNCTIONS_UTILITY.ords('a'):
					if userConstants.Debug: print(f"\tFLIPPING SELECTION HORIZONTALLY")
					self.handler.flipHorizontal()

				elif key in E_FUNCTIONS_UTILITY.ords('d'):
					if userConstants.Debug: print(f"\tFLIPPING SELECTION VERTICALLY")
					self.handler.flipVertical()

				elif key in E_FUNCTIONS_UTILITY.ords('r'):
					if userConstants.Debug: print(f"\tResetting SELECTION")
					self.handler.reset()
	 
				elif key in E_FUNCTIONS_UTILITY.ords(' '):
					if userConstants.Debug: print(f"\tSTORING SELECTION")
					self.storeImage(filePath=targetPath)
					break

				elif key  == 27:
					if userConstants.Debug: print(f"\tTERMINATING PROGRAM")
					exit(1)
				#endregion keypresses
			except KeyboardInterrupt:
				if userConstants.Debug: print("Interupting via ctrl-c")
				if userConstants.Debug: print("*"*40)
				exit()
		else:
			if userConstants.Debug: print("Interupting via window shutdown")
			if userConstants.Debug: print("*"*4)
			exit(1)

	def initRender(self) -> None:
		cv2.namedWindow(winname=self.screenName)#, flags=cv2.WND_PROP_FULLSCREEN)
		cv2.moveWindow(winname=self.screenName, x=0, y=0)
		cv2.setMouseCallback(self.screenName, self.__class__.clickAndCrop, param=self)

	def clickAndCrop(event: int, x: int, y: int, flags: int, param: Displayer) -> None:
		self: Displayer	= param
		self.mousePos	= Point.fromAbsCoords(x,y, self.handler.preview.image)
		unscaledPoint = self.mousePos		#.unscale(self.handler.aspectRatio/self.screenScale)

		if event == cv2.EVENT_LBUTTONDOWN:
			if self.clickState == ClickStates.NOTHING:
				self.corner_1			= self.mousePos

				self.croppingAllowed	= True
				self.clickState			= ClickStates.FIRST
				if userConstants.Debug: print(f"\tclick 1 @ rPos: {self.corner_1}, {self.handler.preview.imgOrigOrient}")

			elif self.clickState == ClickStates.FIRST:
				self.croppingAllowed	= False
				AR = self.targetAR[1]/self.targetAR[0]
				self.corner_2			= F_GEOMETRY.clampPoint(unscaledPoint.moveByAspectRatio(	start=self.corner_1, aspectRatio=AR))
				self.clickState = ClickStates.BOTH
				if userConstants.Debug: print(f"\tclick 2 @ rPos: {self.rectangle}, {self.handler.preview.imgOrigOrient}")

			else:
				if userConstants.Debug: print("No more clicking", self.handler.preview.shape)

		elif event == cv2.EVENT_MBUTTONDOWN:
			if userConstants.Debug: print("Resetting the point array")
			self.clickState			= ClickStates.NOTHING
			self.croppingAllowed	= False
			self.corner_1			= None
			self.corner_2			= None

		# elif event == cv2.EVENT_MOUSEMOVE and self.croppingAllowed:
		# 	self.mousePos = unscaledPoint

	def storeImage(self, filePath: Path) -> None:
		# print(f"Cropping: starting @ {self.rectangle.getDiagonal(self.handler.image)}, preview = {self.handler.preview.diagonal}|{self.handler.preview.ARfloat}, image={self.handler.image.diagonal}|{self.handler.image.ARfloat}")
		if not self.rectangle:
			cv2.imwrite(filename=filePath, img=self.handler.image.image)
			return

		x0, y0, x1, y1 = itertools.chain(*self.rectangle.toAbsCoords(img=self.handler.image.image))
		
		self.handler.image.image	= self.handler.image.image[y0:y1, x0:x1] 
		self.handler.preview.image	= self.handler.preview.image[y0:y1, x0:x1] 
		# print(f"Cropping: scaling  @ {self.rectangle.getDiagonal(self.handler.image)}, preview = {self.handler.preview.diagonal}|{self.handler.preview.ARfloat}, image={self.handler.image.diagonal}|{self.handler.image.ARfloat}")
		self.processed = True
		cv2.imwrite(filename=filePath, img=self.handler.image.image)





class FolderProcessor(Picklable):
	sourceFolder: Path = B_DESCRIPTORS.ValidPathDescriptor(name="sourceFolder")
	targetFolder: Path = B_DESCRIPTORS.CreatePathDescriptor(name="targetFolder")

	_processed: typing.List[Path] = []

	@property
	def sources(self) -> typing.List[Path]: return [Path(os.path.join(self.sourceFolder, imagePath)) for imagePath in os.listdir(self.sourceFolder) if E_FUNCTIONS_UTILITY.getFileSuffix(imagePath).lower() in allowedFileTypes]

	@property
	def processed(self)  -> typing.List[Path]: return self._processed

	def __init__(self, sourceFolder: typing.Optional[str], targetFolder: typing.Optional[Path], screenScale: typing.Optional[float]) -> None:
		self.sourceFolder = sourceFolder if sourceFolder else Path(os.path.join(os.getcwd()))
		if targetFolder:
			if len(os.path.dirname(targetFolder)) == 0:
				self.targetFolder = Path(os.path.join(self.sourceFolder, targetFolder))
			else:
				self.targetFolder = targetFolder
		else: self.targetFolder =  Path(os.path.join(self.sourceFolder, "CROPPED"))
		self.screenScale = screenScale

	def processImages(self) -> None:
		strOut = "*"*50 + "\n"
		strOut +=  f"{self}.processImages: initiated\n"
		strOut +=  f"\tLoading the folder: {self.sourceFolder}\n"

		handler = ImageHandler(filePath=self.sources[0], screenScale=self.screenScale)
		displayer = Displayer(handler=handler, screenName="pyCropper", screenScale=self.screenScale)


		getChars: typing.Callable[[int], int]= lambda index: int(index/len(self.sources)*100)
		print(f"[{getChars(0)*'-'}{(100-getChars(0))*' '}]")
		for index,image in enumerate(self.sources):
			print(self.targetFolder)
			strOut +=  f"\t\tProcessing {image}\n"
			targetPath = Path(os.path.join(self.targetFolder, os.path.basename(image)))
			displayer = Displayer(handler = ImageHandler(image, screenScale=self.screenScale), screenName="pyCropper", screenScale=self.screenScale)
			displayer.initRender()
			displayer.mainLoop(targetPath= targetPath)
			strOut +=  f"\t\tSaving to {os.path.join(self.targetFolder, os.path.basename(image))}\n\n"
			print(f"[{getChars(index+1)*'-'}{(100-getChars(index+1))*' '}], {userConstants.WidthScale}:{userConstants.HeightScale}")

		strOut +=  f"\tFinished processing images in: {self.sourceFolder}\n"
		strOut +=  f"{self}.processImages: Finished!\n"
		strOut +=  "*"*50 + "\n"
		if userConstants.Debug: print(strOut)

if __name__ == "__main__":
	print("\nTesting the FolderProcessor class")
	processor		= FolderProcessor(sourceFolder=userConstants.SourceFolder, targetFolder=userConstants.TargetFolder, screenScale=userConstants.ScreenPercentage)
	processor.processImages()
	print("Done!\n")
