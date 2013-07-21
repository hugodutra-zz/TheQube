import exporters

def GetSupportedFormats():
 formats = []
 formats.append(exporters.TextExporter)
 return formats
