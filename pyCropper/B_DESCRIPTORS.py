from __future__ import annotations
try: from A_DEPENDENCIES import runConstants, RunMode
except: from .A_DEPENDENCIES import runConstants, RunMode

if runConstants.RUNMODE== RunMode.RUN:
	from .A_DEPENDENCIES import Number, typing, os
	from .A_DEPENDENCIES import cv2t, np
	from . import A_DEPENDENCIES

else:
	from A_DEPENDENCIES import Number, typing, os
	from A_DEPENDENCIES import cv2t, np
	import A_DEPENDENCIES

# instance: The instance of the class where the descriptor is used.
# owner: The class where the descriptor is used.
# value: The value being assigned to the attribute.

class NonUniqueDescr:
	def __init__(self, name: str = None) -> None:
		# name: The name of the attribute being managed by the descriptor.
		self.name = name

	def __get__(self, instance: A_DEPENDENCIES.CLASS, owner: typing.Type[A_DEPENDENCIES.CLASS]) -> str:
		if not self.name in instance.__dict__: instance.__dict__[self.name] = None
		return instance.__dict__[self.name]

	def __set__(self, instance: A_DEPENDENCIES.CLASS, value: int) -> None:
		instance.__dict__[self.name] = value

	def __delete__(self, instance: A_DEPENDENCIES.CLASS) -> None:
		del instance.__dict__[self.name]



class StringDescr(NonUniqueDescr):
	"""A descriptor protocol used for string assignments

	Raises:
		TypeError: raises an error if the assigned value is not an string
		ValueError: raises an error if the assigned value is string

	Returns:
		_type_: int: a string
	"""
	# instance: The instance of the class where the descriptor is used.
	# owner: The class where the descriptor is used.
	# value: The value being assigned to the attribute.

	def __set__(self, instance: A_DEPENDENCIES.CLASS, value: int) -> None:
		if not isinstance(value, str):
			raise TypeError(f"{instance}: trying to set the {self.name} to a non-string value: {type(value)}={value}.")

		instance.__dict__[self.name] = value



class CreatePathDescriptor(NonUniqueDescr):
	"""A descriptor protocol used for path properties within a e.g. Constants instance, creates non-existent paths.

	Raises:
		FileNotFoundError: raises an error if the used path does not exist

	Returns:
		_type_: A_CLASSES.Path
	"""
	# instance: The instance of the class where the descriptor is used.
	# owner: The class where the descriptor is used.
	# value: The value being assigned to the attribute.


	def __get__(self, instance: A_DEPENDENCIES.CLASS, owner: typing.Type[A_DEPENDENCIES.CLASS]) -> A_DEPENDENCIES.Path:
		if not os.path.exists(instance.__dict__[self.name]):
			#print(f"{instance.__class__.__name__}: the path {instance.__dict__[self.name]} does not exist, creating")
			os.makedirs(instance.__dict__[self.name], exist_ok=True)
		return instance.__dict__[self.name]

	def __set__(self, instance: A_DEPENDENCIES.CLASS, value: A_DEPENDENCIES.Path) -> None:
		if not os.path.exists(value):
			#print(f"{instance.__class__.__name__}: the path {value} does not exist, creating")
			os.makedirs(value, exist_ok=True)
		instance.__dict__[self.name] = value


class ValidPathDescriptor(NonUniqueDescr):
	"""A descriptor protocol used for path properties within a e.g. Constants instance, blocks using non-existent paths.

	Raises:
		FileNotFoundError: raises an error if the used path does not exist

	Returns:
		_type_: A_CLASSES.Path
	"""
	# instance: The instance of the class where the descriptor is used.
	# owner: The class where the descriptor is used.
	# value: The value being assigned to the attribute.


	def __set__(self, instance: A_DEPENDENCIES.CLASS, value: A_DEPENDENCIES.Path) -> None:
		if not os.path.exists(value):
			raise FileNotFoundError(f"{instance}: trying to set the {self.name} to a non-existent path: {value}.")
		instance.__dict__[self.name] = value




class UnsignedInteger(NonUniqueDescr):
	"""A descriptor protocol used for unsigned integer assignments

	Raises:
		TypeError: raises an error if the assigned value is not an integer
		ValueError: raises an error if the assigned value is negative

	Returns:
		_type_: int: an unsigned integer
	"""
	# instance: The instance of the class where the descriptor is used.
	# owner: The class where the descriptor is used.
	# value: The value being assigned to the attribute.


	def __set__(self, instance: A_DEPENDENCIES.CLASS, value: int) -> None:
		if not isinstance(value, int):
			raise TypeError(f"{instance}: trying to set the {self.name} to a floating point value: {value}.")

		if value < 0:
			raise ValueError(f"{instance}: trying to set the {self.name} to a negative value: {value}.")
		instance.__dict__[self.name] = value



class RangedNumber(NonUniqueDescr):
	"""A descriptor protocol used for floating point values in a range

	Raises:
		TypeError: raises an error if the assigned value is not a number
		ValueError: raises an error if the assigned value is outside of the bounds

	Returns:
		_type_: int: an unsigned integer
	"""
	# instance: The instance of the class where the descriptor is used.
	# owner: The class where the descriptor is used.
	# value: The value being assigned to the attribute.

	def __init__(self, name: str = None, minimum: Number = -float("inf"), maximum: Number = float("inf")) -> None:
		# name: The name of the attribute being managed by the descriptor.
		super(RangedNumber, self).__init__(name)
		self.minimum	= minimum
		self.maximum	= maximum


	def __set__(self, instance: A_DEPENDENCIES.CLASS, value: Number) -> None:
		if not isinstance(value, Number):
			raise TypeError(f"{instance}: trying to set the {self.name} to a non-numeric value: <{value}: {type(value)}>.")

		if value < self.minimum or value > self.maximum:
			raise ValueError(f"{instance}: trying to set the {self.name} to a value ({value}) outside the bound <{self.minimum}, {self.maximum}>.")
		instance.__dict__[self.name] = value



class CheckIntMixin:
	"""A descriptor protocol used for limiting the values to integer

	Raises:
		TypeError: raises an error if the assigned value is not a integer

	Returns:
		_type_: int: an integer
	"""

	def __set__(self, instance: A_DEPENDENCIES.CLASS, value:A_DEPENDENCIES.VALUE) -> None:
		if not isinstance(value, int):
			raise TypeError(f"{self.name} must be a int, you have inpuuted {type(value)}={value}.")
		super().__set__(instance, value)

class CheckFloatMixin:
	"""A descriptor protocol used for limiting the values to floats

	Raises:
		TypeError: raises an error if the assigned value is not a float

	Returns:
		_type_: float: a float
	"""

	def __set__(self, instance: A_DEPENDENCIES.CLASS, value:A_DEPENDENCIES.VALUE) -> None:
		if not isinstance(value, float):
			raise TypeError(f"{self.name} must be a float, you have inpuuted {type(value)}={value}.")
		super().__set__(instance, value)




class WriteOnceMixin:
	"""A descriptor protocol used for set-up once values

	Raises:
		AttributeError: raises an error if trying to change the value post-initial assignment

	Returns:
		_type_: int: an unsigned integer
	"""
	def __set__(self, instance:A_DEPENDENCIES.CLASS, value:A_DEPENDENCIES.VALUE) -> None:
		if self.name in instance.__dict__:
			raise AttributeError(f"The attribute '{self.name}' is read-only after initial assignment.")
		super().__set__(instance, value)





class RangedInt(CheckIntMixin, RangedNumber): pass
class RangedFloat(CheckFloatMixin, RangedNumber): pass



class WriteOnce_UnsignedInteger(WriteOnceMixin, CheckIntMixin, UnsignedInteger): pass

class WriteOnce_RangedInt(WriteOnceMixin, RangedInt): pass

class WriteOnce_RangedFloat(WriteOnceMixin, RangedFloat): pass


class WriteOnce_CreatePath(WriteOnceMixin, CreatePathDescriptor): pass

class WriteOnce_String(WriteOnceMixin, StringDescr): pass

class ImageWrapperTYPECHECK(): pass

class ImageOrienter(NonUniqueDescr):
	def __init__(self, name=None, getFromAttr: str = None) -> None:
		super().__init__(name)
		self.getFrom = getFromAttr

	def __get__(self, instance: A_DEPENDENCIES.CLASS, owner: typing.Type[A_DEPENDENCIES.CLASS]) -> A_DEPENDENCIES.ImageOrientation:
		if not isinstance(instance, ImageWrapperTYPECHECK):
			raise TypeError(f"{instance}: you have tried to assign an invalid class {instance.__class__.__name__}, it must be a np.ndarray of shape(x,y,3) here.")


		if len(instance.image.shape) != 3: raise ValueError(f"{instance}: the image array needs to have the rank 3 tensor shape of (x,y,3|4), you have passed rank {len(instance.shape)} matrix")
		if instance.image.shape[2] not in (3,4): raise ValueError(f"{instance}: the image array needs to have the rank 3 tensor shape of (x,y,3|4), your colour array does not have the length of 3 nor 4")
		if instance.image.dtype != np.uint8: raise TypeError(f"{instance}: the image array must be of uint256 type, you have {instance.dtype}")

		if instance is None or self.getFrom is None:
			return None

		image = getattr(instance, self.getFrom, None)
		if image is None or not hasattr(image, "shape"):
			return None

		y, x = image.shape[:2]
		if x >= y:return A_DEPENDENCIES.ImageOrientation.LANDSCAPE
		else:return A_DEPENDENCIES.ImageOrientation.PORTRAIT
