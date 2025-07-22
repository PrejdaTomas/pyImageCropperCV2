from __future__ import annotations
try: from A_DEPENDENCIES import runConstants, RunMode
except: from .A_DEPENDENCIES import runConstants, RunMode

if runConstants.RUNMODE== RunMode.TEST:
	from A_DEPENDENCIES import Number, typing, cv2t
	from A_DEPENDENCIES import aPoint, aColour, aCorners, ImageOrientation, math, np
	from B_DESCRIPTORS import RangedFloat, UnsignedInteger
	from D_CONSTANTS import userConstants
	import E_FUNCTIONS_UTILITY

else:
	from .A_DEPENDENCIES import Number, typing, cv2t
	from .A_DEPENDENCIES import aPoint, aColour, aCorners, ImageOrientation, math, np
	from .B_DESCRIPTORS import RangedFloat, UnsignedInteger
	from .D_CONSTANTS import userConstants
	from . import E_FUNCTIONS_UTILITY


getWidth:								typing.Callable[[Number, Number], float]	= lambda height, AR:	float(abs(height / AR)) if AR != 0 else 0.
getHeight:								typing.Callable[[Number, Number], float]	= lambda width, AR:		float(abs(width * AR)) if AR != 0 else 0.
getSign:								typing.Callable[[Number], int]				= lambda value: 1 if (value >= 0) else -1
realWidthLargerThanCalculatedWidth:		typing.Callable[[Number, Number], bool]		= lambda real, calculated: abs(real) > abs(calculated)
realHeightLargerThanCalculatedHeight:		typing.Callable[[Number, Number], bool]		= lambda real, calculated: realWidthLargerThanCalculatedWidth(real, calculated)

def getRatio(x0: int, y0: int, x1: int, y1: int) -> typing.Tuple[int,int]:
	width	= x1 - x0
	height	= y1 - y0
	gcd = math.gcd(width, height)
	if gcd == 0: return width,height
	width	= width // gcd
	height	= height // gcd
	return width, height

def getWidthHeightFromAR(width: Number, height: Number, aspectRatio: Number) -> typing.Tuple[float, float]:

	if realWidthLargerThanCalculatedWidth(	real=		width,
											calculated=	getWidth(height, aspectRatio)):
		width	= getSign(width)  * getWidth(height, aspectRatio )

	elif realHeightLargerThanCalculatedHeight(real = height, calculated = getHeight(width, aspectRatio)):
		height	= getSign(height) * getHeight(width, aspectRatio)
	return width, height


class Point(object):
	# __slots__ = ["x_rel", "y_rel"]
	x_rel: float = RangedFloat(name="x_rel", minimum=0.0, maximum=1.0)
	y_rel: float = RangedFloat(name="y_rel", minimum=0.0, maximum=1.0)

	def __init__(self, xRel: float, yRel: float) -> None:
		self.x_rel = xRel
		self.y_rel = yRel


	@classmethod
	def fromAbsCoords(cls, x_abs: int, y_abs: int, img: cv2t.MatLike) -> Point:
		xRel = x_abs/img.shape[1] if img.shape[1] > img.shape[0] else y_abs/img.shape[0]
		yRel = y_abs/img.shape[0] if img.shape[1] > img.shape[0] else x_abs/img.shape[1]
		# print("F_GEOMETRY.py: fromAbsCoords", xRel, yRel)
		return cls(xRel, yRel)

	@property
	def tupleForm(self) -> aPoint: return self.x_rel, self.y_rel

	def toAbsCoords(self, image: cv2t.MatLike) -> aPoint:
		# shape = ImageOrientation.LANDSCAPE if image.shape[1] > image.shape[0] else ImageOrientation.PORTRAIT
		# xNew = int(round(self.x_rel*image.shape[1], 0)) if shape == ImageOrientation.LANDSCAPE else int(round(self.x_rel*image.shape[0], 0))
		# yNew = int(round(self.y_rel*image.shape[0], 0)) if shape == ImageOrientation.LANDSCAPE else int(round(self.y_rel*image.shape[1], 0))

		xNew = int(round(self.x_rel*image.shape[1], 0))
		yNew = int(round(self.y_rel*image.shape[0], 0))
		return xNew, yNew

	def scale(self, scale: float) -> Point: return Point(self.x_rel/scale, self.y_rel/scale)

	def unscale(self, scale: float) -> Point: return Point(self.x_rel*scale, self.y_rel*scale)

	def moveByAspectRatio(self, start: Point, aspectRatio: float) -> Point:
		dx		= (self.x_rel - start.x_rel)
		dy		= (self.y_rel - start.y_rel)
	
		width, height = getWidthHeightFromAR(width=dx, height=dy, aspectRatio=aspectRatio)

		nuXrel= start.x_rel + width
		nuYrel= start.y_rel + height

		return Point(xRel= nuXrel, yRel= nuYrel)

	def __repr__(self) -> str: return f"({self.x_rel:.4F}:{self.y_rel:.4F})"
	def __str__(self) -> str: return f"<{self.__class__.__name__} ({self.x_rel:.4F}:{self.y_rel:.4F}) @ {hex(id(self))}>"

class Rectangle(object):
	# __slots__ = ["point1", "point2", "colour", "thickness"]
	point1: Point
	point2: Point

	colour: aColour
	thickness: int = UnsignedInteger(name="thickness")

	def __init__(self, pt1: Point, pt2: Point, colour: aColour = (0, 0, 0), thickness: int = 2) -> None:
		self.point1 = pt1
		self.point2 = pt2
		self.colour = colour
		self.thickness = thickness

	def toAbsCoords(self, img: cv2t.MatLike) -> aCorners:
		pt1 = self.point1.toAbsCoords(img)
		pt2 = self.point2.toAbsCoords(img)
		return (pt1, pt2)

	def getDiagonal(self, img: cv2t.MatLike) -> int:
		pt1, pt2 = self.toAbsCoords(img)
		diagonal = sum([(pt1[i] - pt2[i])**2 for i in range(len(pt1))])**0.5
		return int(round(diagonal, 0))

	def largeEnough(self, img: cv2t.MatLike) -> bool:
		return self.getDiagonal(img) >= userConstants.MinimumPixelsDiagonal

	@property
	def width(self) -> float: return self.point2.x_rel - self.point1.x_rel

	@property
	def height(self) -> float: return self.point2.y_rel - self.point1.y_rel

	@property
	def tupleForm(self) -> typing.Tuple[Point, Point]: return (self.point1, self.point2)
 
	def __repr__(self) -> str: return f"[{self.point1}:{self.point2}]"
	def __str__(self) -> str: return f"<{self.__class__.__name__} [{self.point1}:{self.point2}] @ {hex(id(self))}>"
 
 
def applyMask(disp: cv2t.MatLike, corners: Rectangle, alpha=0.6) -> cv2t.MatLike:
	# Create dark overlay
	overlay	= disp.copy()
	mask	= np.zeros_like(disp, dtype=np.uint8)
	x1,y1 = corners.point1.toAbsCoords(disp)
	x2,y2 = corners.point2.toAbsCoords(disp)
	mask[:]	= (0, 0, 0)

	# Cut out the selected rectangle
	mask[y1:y2, x1:x2] = disp[y1:y2, x1:x2]

	# Blend the overlay with the mask
	blended = E_FUNCTIONS_UTILITY.createMask(overlay=overlay, alpha=alpha, mask=mask, gamma=0.0)

	return blended

def greenInfo(imageOrientation: ImageOrientation, disp: cv2t.MatLike, corners: Rectangle) -> None:
	pt0, pt1	= corners.tupleForm
	center		= Point(xRel= (pt0.x_rel + pt1.x_rel)/2, yRel= (pt0.y_rel + pt1.y_rel)/2)

	abs_pt0	= pt0.toAbsCoords(disp)
	abs_pt1	= pt1.toAbsCoords(disp)
	abs_c	= center.toAbsCoords(disp)

	width, height = getRatio(
		math.ceil(100*corners.point1.x_rel),
		math.ceil(100*corners.point1.y_rel),
		math.ceil(100*corners.point2.x_rel),
		math.ceil(100*corners.point2.y_rel)
	)

	E_FUNCTIONS_UTILITY.greenRectangle(imageOrientation, disp, abs_pt0, abs_pt1)
	E_FUNCTIONS_UTILITY.greenText(imageOrientation, disp, abs_pt0, f"D{pt0}")
	E_FUNCTIONS_UTILITY.greenText(imageOrientation, disp, abs_c, f"{width}:{height}")
	E_FUNCTIONS_UTILITY.greenText(imageOrientation, disp, abs_pt1, f"D{pt1}")

def redWarning(imageOrientation: ImageOrientation, disp: cv2t.MatLike, corners: Rectangle) -> None:
	pt0, pt1	= corners.tupleForm
	center		= Point(xRel= (pt0.x_rel + pt1.x_rel)/2, yRel= (pt0.y_rel + pt1.y_rel)/2)

	abs_pt0	= pt0.toAbsCoords(disp)
	abs_pt1	= pt1.toAbsCoords(disp)
 
	abs_c	= center.toAbsCoords(disp)

	width, height=getRatio(*abs_pt0, *abs_pt1)
	width, height = getRatio(
		math.ceil(100*corners.point1.x_rel),
		math.ceil(100*corners.point1.y_rel),
		math.ceil(100*corners.point2.x_rel),
		math.ceil(100*corners.point2.y_rel)
	)

	E_FUNCTIONS_UTILITY.redRectangle(imageOrientation, disp, abs_pt0, abs_pt1)
	E_FUNCTIONS_UTILITY.redText(imageOrientation, disp, abs_pt0, f"D{pt0}")
	E_FUNCTIONS_UTILITY.redText(imageOrientation, disp, abs_c, f"{width}:{height}")
	E_FUNCTIONS_UTILITY.redText(imageOrientation, disp, abs_pt1, f"D{pt1}")
 

def drawArrow(disp: cv2t.MatLike, corners: Rectangle, colour: aColour, thickness: int) -> None:
	pt0, pt1	= corners.tupleForm
	abs_pt0	= pt0.toAbsCoords(disp)
	abs_pt1	= pt1.toAbsCoords(disp)
	E_FUNCTIONS_UTILITY.arrow( disp, abs_pt0, abs_pt1, colour, thickness)


def clamp(value: float, min_val: float = 0.0, max_val: float = 1.0) -> float: return max(min_val, min(value, max_val))

def clampPoint(p: Point) -> Point:
	return Point(
		xRel=clamp(p.x_rel),
		yRel=clamp(p.y_rel)
	)
