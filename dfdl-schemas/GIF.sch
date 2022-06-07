<?xml version="1.0" encoding="UTF-8"?>
<sch:schema xmlns:sch="http://purl.oclc.org/dsdl/schematron" 
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
    
    <sch:pattern id="GIF-Rules">
        <sch:rule context="GIF">
            <sch:assert test="*[last()][self::Trailer]">
                Trailer shall be last.
            </sch:assert>
            <sch:assert test="not(Trailer[2])">
                One SOI only.
            </sch:assert>
            <sch:assert test="number(Trailer) eq 59">
                The value of Trailer must be 59.
            </sch:assert>
            <sch:assert test="*[1][self::Header]">
                Header shall be first.
            </sch:assert>
            <sch:assert test="not(Header[2])">
                One Header only.
            </sch:assert>
            <sch:assert test="not(Header/Signature[2])">
                One Header Signature only.
            </sch:assert>
            <sch:assert test="Header/Signature eq 'GIF'">
                The value of the Header Signature must be GIF.
            </sch:assert>
            <sch:assert test="not(Header/Version[2])">
                One Header Version only.
            </sch:assert>
            <sch:assert test="Header/Version = ('89a', '87a')">
                The value of the Header Version must be 89a or 87a.
            </sch:assert>
            <sch:assert test="Header/following::*[1][self::Logical_Screen_Descriptor]">
                Logical_Screen_Descriptor immediately follows Header.
            </sch:assert>
            <sch:assert test="not(Logical_Screen_Descriptor[2])">
                One Logical_Screen_Descriptor only.
            </sch:assert>
        </sch:rule>
        
        <sch:rule context="Logical_Screen_Descriptor">
            <sch:assert test="number(Canvas_Height) gt 0">
                The canvas height must be greater than zero.
            </sch:assert>
            <sch:assert test="number(Canvas_Width) gt 0">
                The canvas width must be greater than zero.
            </sch:assert>
        </sch:rule>
        
        <sch:rule context="Logical_Screen_Descriptor/Packed_Byte/Global_Color_Table_Flag[number(.) eq 0]">
            <sch:assert test="not(/GIF/Global_Color_Table)">
                The color table flag indicates that there must not be a global color table.
            </sch:assert>
        </sch:rule>
        
        <sch:rule context="Logical_Screen_Descriptor/Packed_Byte/Global_Color_Table_Flag[number(.) eq 1]">
            <sch:assert test="/GIF/Global_Color_Table">
                The color table flag indicates that there must be a global color table.
            </sch:assert>
            <sch:assert test="count(/GIF/Global_Color_Table/RGB) eq math:pow(2, ../number(Size_of_Global_Color_Table) + 1)">
                There must be <sch:value-of select="math:pow(2, ../number(Size_of_Global_Color_Table) + 1)"/> RGB values.
            </sch:assert>
        </sch:rule>
        
        <sch:rule context="Logical_Screen_Descriptor/Packed_Byte/Background_Color_Index">
            <sch:assert test="
                if (not(/GIF/Global_Color_Table[1])) then
                    number(.) eq 0
                else true()
                ">
                If there is no global color table, then the background color index should be 0.
            </sch:assert>
        </sch:rule>
        
        <sch:rule context="RGB">
            <sch:assert test="
                   ((number(Red) ge 0) and (number(Red) le 255)) and 
                   ((number(Green) ge 0) and (number(Green) le 255)) and 
                   ((number(Blue) ge 0) and (number(Blue) le 255))
                   ">
                RGB values must be between 0 and 255.
            </sch:assert>
        </sch:rule>
        
        <sch:rule context="Reserved_For_Future_Use">
            <sch:assert test="number(.) eq 0">
                The 3 bits in packed data that are reserved for future use must be zero.
            </sch:assert>
        </sch:rule>
        
        <sch:rule context="Wrapper[Image_Descriptor_Minus_First_Two_Bytes]">
            <sch:assert test="
                if (Image_Descriptor_Minus_First_Two_Bytes/Packed_Byte/number(Size_of_Color_Table) eq 0) then
                    not (Local_Color_Table/*[1]) 
                else
                    count(Local_Color_Table/RGB) eq math:pow(2, Image_Descriptor_Minus_First_Two_Bytes/Packed_Byte/number(Size_of_Color_Table) + 1) 
                ">
                The number of elements in the logical color table must accord with "size of color table".
            </sch:assert>
            <sch:assert test="Image_Descriptor_Minus_First_Two_Bytes/number(Image_Height) gt 0">
                The image height must be greater than zero.
            </sch:assert>
            <sch:assert test="Image_Descriptor_Minus_First_Two_Bytes/number(Image_Width) gt 0">
                The image width must be greater than zero.
            </sch:assert>
        </sch:rule>
        
        <sch:rule context="Byte-Sub-block">
            <sch:assert test="(string-length(Bytes) div 2) eq number(Number_of_Bytes)">
                The number of bytes in a byte sub-block must match the "number of bytes" field.
                Number_of_Bytes = <sch:value-of select="Number_of_Bytes"/>
                (string-length(Bytes) div 2) = <sch:value-of select="(string-length(Bytes) * 2)"/>
            </sch:assert>
        </sch:rule>
        
        <sch:rule context="Text-Sub-block">
            <sch:assert test="(string-length(Bytes) div 2) eq number(Number_of_Bytes)">
                The number of bytes in a byte sub-block must match the "number of bytes" field.
                Number_of_Bytes = <sch:value-of select="Number_of_Bytes"/>
                (string-length(Bytes) div 2) = <sch:value-of select="(string-length(Bytes) * 2)"/>
            </sch:assert>
        </sch:rule>
        
        <sch:rule context="/GIF/Wrapper/Plain_Text_Extension">
            <sch:assert test="/GIF/Global_Color_Table">
                The plain text extension requires a Global Color Table to be available.
            </sch:assert>
            <sch:assert test="number(Block_Size) eq 12">
                The plain text extension block size must be 12.
            </sch:assert>
            <sch:assert test="number(Text_Grid_Width) gt 0">
                The text grid width must be greater than zero.
            </sch:assert>
            <sch:assert test="number(Text_Grid_Height) gt 0">
                The text grid height must be greater than zero.
            </sch:assert>
        </sch:rule>
        
        <sch:rule context="/GIF/Wrapper/Application_Extension">
            <sch:assert test="number(Block_Size) eq 11">
                The application extension block size must be 11.
            </sch:assert>
        </sch:rule>
    </sch:pattern>
    
</sch:schema>