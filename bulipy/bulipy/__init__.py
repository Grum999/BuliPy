from .bulipy import BuliPy

# And add the extension to Krita's list of extensions:
app = Krita.instance()
extension = BuliPy(parent=app)
app.addExtension(extension)
