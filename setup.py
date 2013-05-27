from distutils.core import setup
import py2exe
import glob

setup(name="dvonn",
      scripts=["dvonn.py"],
      data_files=[
          ("",["dvonn.cfg"]),
          ("",["dvonn.ico"]),
          ("",glob.glob("*.bmp")),
          ("",glob.glob("*.ttf"))]
      )
