from pyCropper import FolderProcessor
from pyCropper import userConstants

if __name__ == "__main__":
	print(userConstants)
	processor = FolderProcessor(
		sourceFolder=userConstants.SourceFolder,
		targetFolder=userConstants.TargetFolder,
		screenScale=userConstants.ScreenPercentage
	)
	processor.processImages()