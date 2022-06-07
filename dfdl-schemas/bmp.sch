<?xml version="1.0" encoding="UTF-8"?>
<sch:schema xmlns:sch="http://purl.oclc.org/dsdl/schematron" 
            xmlns:xs="http://www.w3.org/2001/XMLSchema"
            xmlns:math="http://www.w3.org/2005/xpath-functions/math"
            queryBinding="xslt2">
    
    <sch:ns uri="http://www.w3.org/2005/xpath-functions/math" prefix="math"/>
    
    <!--  
        NOTICE
        This software was produced for the U. S. Government under 
        Basic Contract No. W15P7T-13-C-A802, and is subject to the
        Rights in Noncommercial Computer Software and Noncommercial
        Computer Software Documentation Clause 252.227-7014 (FEB 2012)
        
        © 2017 The MITRE Corporation.

    -->
    
    <sch:pattern id="Magic-Number">
        <sch:rule context="BMP">
            <sch:assert test="Identifier = ('BM', 'BA', 'CI', 'CP', 'IC', 'PT')">
                The Identifier must be one of these values: BM, BA, CI, CP, IC, PT.
            </sch:assert>
        </sch:rule>
    </sch:pattern>
    
    <sch:pattern id="Reserved_Fields">
        <sch:rule context="Reserved">
            <sch:assert test="xs:integer(.) eq 0">
                The Reserved field must be set to zero.
            </sch:assert>
        </sch:rule>
    </sch:pattern>
    
    <sch:pattern id="Padding_Fields">
        <sch:rule context="Padding">
            <sch:assert test="xs:integer(.) eq 0">
                The Padding field must be set to zero.
            </sch:assert>
        </sch:rule>
    </sch:pattern>
    
    <sch:pattern id="Color_Encoding">
        <sch:rule context="Color_Encoding">
            <sch:assert test="xs:integer(.) eq 0">
                The color encoding field must be set to zero.
            </sch:assert>
        </sch:rule>
    </sch:pattern>
    
    <sch:pattern id="Number_of_Color_Planes">
        <sch:rule context="Number_of_Color_Planes">
            <sch:assert test="xs:integer(.) eq 1">
                The number of color planes must be 1.
            </sch:assert>
        </sch:rule>
    </sch:pattern>
    
    <sch:pattern id="Number_of_Bits_per_Pixel">
        <sch:rule context="Number_of_Bits_per_Pixel">
            <sch:assert test="xs:integer(.) = (1, 4, 8, 16, 24, 32)">
                The number of bits per pixel must be 1, 4, 8, 16, 24, or 32.
            </sch:assert>
        </sch:rule>
        <sch:rule context="BITMAPCOREHEADER">
            <sch:assert test="not(xs:integer(Number_of_Bits_per_Pixel) = (16, 32))">
                OS/2 1.x bitmaps are uncompressed and cannot be 16 or 32 bpp.
            </sch:assert>
        </sch:rule>
        <sch:rule context="*[Number_of_Colors_in_the_Color_Palette]">
            <sch:assert test="xs:integer(Number_of_Colors_in_the_Color_Palette) le math:pow(2, Number_of_Bits_per_Pixel)">
                The number of colors in the color palette must be less than
                or equal to 2**Number_of_Bits_per_Pixel.
            </sch:assert>
        </sch:rule>
    </sch:pattern>
    
    <sch:pattern id="Compression_Method">
        <sch:rule context="Compression_Method[. eq 'RLE 8-bit/pixel']">
            <sch:assert test="xs:integer(../Number_of_Bits_per_Pixel) eq 8">
                A compression method of RLE 8-bit/pixel can be used only with 8-bit/pixel bitmaps.
            </sch:assert>
        </sch:rule>
        <sch:rule context="Compression_Method[. eq 'RLE 4-bit/pixel']">
            <sch:assert test="xs:integer(../Number_of_Bits_per_Pixel) eq 4">
                A compression method of RLE 8-bit/pixel can be used only with 4-bit/pixel bitmaps.
            </sch:assert>
        </sch:rule>
    </sch:pattern>
    
</sch:schema>