cluttool - create and convert 3D/color LUTs
-------------------------------------------

This tool is a sort of swiss army knife for color LUTs.  Color LUTs concisely
describe linear color transformations that many video monitors and post
production software can understand.  There are a relatively small number of
color LUT file formats, such as 3D LUT and Hald CLUT, but no one LUT format is
used by every software and firmware system.  This tool may help you to convert
between LUT formats, or generate new ones in the format that you need.

Not all LUTs are created equal
------------------------------

Those film simulation HaldCLUT files aren't going to apply correctly to s-log
footage, and those video style LUT packs aren't going to apply corrrectly to
your 8-bit gamma or 14-bit RAW photos.  You need to know what _source_ the
color LUT was created for in order to use it.

This tool is not aware of the context of the color LUT.  It doesn't know
whether the LUT was made for gamma, log, or linear raw images.  It simply
converts them verbatim.

Supported file formats:
-----------------------

* PNG (.png)
* 3D LUT (.3dl)

References:
-----------

* Hald CLUT reference: http://www.quelsolaar.com/technology/clut.html
* 3D LUT (3DL) reference: http://download.autodesk.com/us/systemdocs/pdf/lustre_color_management_user_guide.pdf#page=14
