cluttool - create and convert 3D/color LUTs
-------------------------------------------

This tool is a sort of swiss army knife for color LUTs.  Color LUTs concisely
describe linear color transformations that many video monitors and post
production software can understand.  There are a relatively small number of
color LUT file formats, such as 3D LUT (3DL) and Hald CLUT, but no one LUT
format is used by every software and firmware system.  This tool may help you
to convert between LUT formats, or generate new ones in the format that you
need.

Not all LUTs are created equal
------------------------------

This tool is not aware of the context of the color LUT.  It doesn't know what
type of source medium it was made for, nor what its goals are.  It simply
converts the color transformations verbatim.

Those film simulation HaldCLUT files aren't going to apply correctly to s-log
footage, and those video style LUT packs aren't going to apply corrrectly to
your 8-bit gamma or 14-bit RAW photos.  If you're grabbing color LUTs off the
internet, you should understand what *source* the color LUT was created for,
and what kind of transformation it does.

When in doubt, just test it.  However, some LUT packs are purchased and
non-refundable.  My hope is that this tool will help make it easier for you to
freely create your own color LUTs for your own needs.

Supported color LUT formats:
-----------------------

* Hald CLUT (.png)
* 3D LUT (.3dl)
* Cube LUT (.cube)

Similar Tools
-------------

3DLutConverter is another color LUT converter with similar goals:

https://github.com/spoilt-exile/3DLutConverter

However, it only supports 

References:
-----------

* Hald CLUT reference: http://www.quelsolaar.com/technology/clut.html
* 3D LUT (3DL) reference: http://download.autodesk.com/us/systemdocs/pdf/lustre_color_management_user_guide.pdf#page=14
* Cube LUT reference: http://wwwimages.adobe.com/www.adobe.com/content/dam/acom/en/products/speedgrade/cc/pdfs/cube-lut-specification-1.0.pdf
