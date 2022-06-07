import subprocess # for dfdl_valid
import sqlite3 
#import snowy # for snowy
import PIL
from PIL import Image # Pillow library
import os
import hashlib
import sys
import kaitaistruct

#local files
import jpeg
import png
import gif
import bmp

def main():    

    # -------------- #
    # INITIALIZATION #
    # -------------- #

    # if user inputted 1 argument
    if len(sys.argv) == 2:

        # check which filetype was specified, which then decides
        # target schema (for dfdl) and filetype variable
        if sys.argv[1] == "jpg":
            schema = "dfdl-schemas/jpeg.dfdl.xsd"
            filetype = "jpg"

        elif sys.argv[1] == "png":
            schema = "dfdl-schemas/png.dfdl.xsd"
            filetype = "png"

        elif sys.argv[1] == "gif":
            schema = "dfdl-schemas/gif.dfdl.xsd"
            filetype = "gif"

        elif sys.argv[1] == "bmp":
            schema = "dfdl-schemas/bmp.dfdl.xsd"
            filetype = "bmp"

        else:
            print("Error: invalid filetype. Format is python3 test.py [FILETYPE], where the filetypes accepted are: jpg, png, gif, and bmp")
            return 

    else:
        print("Error: invalid number of arguments. Format is python3 test.py [FILETYPE], where the filetypes accepted are: jpg, png, gif, and bmp")
        return 

    # create database and table
    database = r"results.db" # r prefix means we're passing as raw string
    connection = sqlite3.connect(database)
    c = connection.cursor() # .cursor() allows us to execute sql commands on the database

    c.execute("CREATE TABLE IF NOT EXISTS {table}(filename text,hash text PRIMARY KEY, dfdl_flag integer, dfdl_string text, kt_flag integer, kt_string text, snowy_flag integer, snowy_string text, pillow_flag integer, pillow_string text)".format(table = filetype))
    connection.commit() 
   

    # get current directory
    current_dir = os.getcwd()

    # get target directory
    #target_dir = current_dir + "/" + filetype
    target_dir = "/media/kris/2a9713f8-7d16-4fd8-a38e-d95a5eb0860a/spring-22/" + filetype
    dir = os.fsencode(target_dir)

    count = 1
    # for each file in the directory
    for file in os.listdir(dir):

        filename = os.fsdecode(file)

        try:
            print(str(count) + ": checking " + filename + "...")
        except:
            print("Skipped!")
            continue
        
        query = "SELECT * FROM " + filetype +" WHERE filename = \'"+filename.replace("'","")+"\'"
        c.execute(query)
        results = c.fetchall()
        print(results)

        if results != []:
            print("already done")
            continue
        print("not done yet")

        file_path = target_dir + "/" + filename

        # process each file
        hash,dfdl_flag,dfdl_string,kt_flag,kt_string,\
        snowy_flag,snowy_string,pillow_flag,pillow_string  = process(schema,file_path,filetype)      

        # add to sqlite column, wrapping strings in ' for sql to parse correctly
        column_to_input = "\'"+filename.replace("'","")+"\'" + "," + "\'" + hash + "\'" + "," + str(dfdl_flag) + "," + "\'"+ dfdl_string + "\'" + "," + str(kt_flag) + "," \
        + "\'" + kt_string + "\'" + "," + str(snowy_flag) + "," + "\'" + snowy_string + "\'" + "," + str(pillow_flag) + "," + "\'" + pillow_string + "\'"

        #print(column_to_input)
        print(column_to_input)

        c.execute("INSERT or REPLACE INTO {table} VALUES ({values})".format(table=filetype,values=column_to_input))
        count += 1
        connection.commit()
 
    connection.close()



# ===================================================================== #
# dfdl_valid
#  
# returns true or false, and an error message depending on whether or 
# not parsing the image creates a valid file. If it is valid, the error
# message is an empty string
#
# takes in
#   - schema: path to the schema for daffodil to use to parse
#   - image: path to the image to process
# returns
#   - flag: true or false. true if no error
#   - string: the type of exception raised if raised
# ===================================================================== #
def dfdl_valid(schema,image):

    print(schema + "\t" + image)

    try:
        # same as bash command: $ daffodil parse -s <schema> <image> > out
        
        
        cmd = ['/home/kris/apache-daffodil-3.1.0-src/daffodil-cli/target/universal/stage/bin/daffodil','parse','-s',schema,image]
        """
        tmpout = open("tmpout", "w")
        proc = subprocess.Popen([], stdout=tmpout, stderr=tmpout)
        proc.wait()
        try:
            proc = subproces.....
            proc.communicate(time=60)
        except:
            proc.kill()
        tmpout.close()
        tmpout = open("tmpout").read()
        """

        out = subprocess.run(cmd,stdout=subprocess.PIPE)
        
        #with open("x", "wb") as out: subprocess.Popen(cmd, stdout=out)
        #os.popen("daffodil parse -s " + schema + " " + image +" > out")
    
    except Exception as err:
        print(err)
        #print("ding")


    # TODO: find a way to extract the error code for the daffodil command, it's going
    # to the terminal output correctly, but subprocess can't seem to handle it


    #
    #
    # try:
    #     test = subprocess.check_output(cmd)
    # except:
    #     print(":(")


    if out.returncode == 0: # if valid
        return True, ""
    else: # returncode == 1 means something went wrong.
        # LINE BELOW USED TO WORK
        #error = out.stderr.decode("utf-8")
 
        # print("==\n1==")
        # print(out)
        # print("==\n2==")

        # print(out.stderr)
        # print("==\n3==")

        # print(out.stdout)
        # print("==\n4==")
        error = str(out)
        # print(test)

        return False, error.replace("'","")

# ===================================================================== #
# kaitai_valid
#  
# returns true or false depending on whether or not processing the
# image raises an exception
# takes in
#   - schema: path to the schema for daffodil to use to parse
#   - image: path to the image to process
# returns
#   - flag: true or false. true if no error
#   - string: the type of exception raised if raised
# ===================================================================== #
def kaitai_valid(image,filetype):

    try:
        if filetype == "jpg":
            object = jpeg.Jpeg.from_file(image)
        elif filetype == "png":
            object = png.Png.from_file(image)
        elif filetype == "gif":
            object = gif.Gif.from_file(image)
        elif filetype == "bmp":
            object = bmp.Bmp.from_file(image)
        else:
            raise Exception("Error: kaitai_valid received invalid filetype: " + filetype) from ValueError
        
    except kaitaistruct.ValidationNotEqualError:
        return False, "ValidationNotEqualError"

    except EOFError:
        return False, "EOFError"

    # otherwise:
    except Exception as err:
        print("got unidentified error" + str(err))
        return False, err
    
    # finally:
    # #     err = Exception

    #     return False, err
    return True, ""

# ===================================================================== #
# pillow_valid
#  
# returns true or false depending on whether or not pillow's Image.open
# function identifies our image as the desired filetype
# takes in
#   - image: path to the image to process
#   - filetype: either 'JPEG', 'BMP', 'PNG', or 'GIF'
# returns
#   - flag: true or false. true if no error
#   - string: the type of exception raised if raised
# ===================================================================== #
def pillow_valid(image,filetype):
    
    try:
        image = Image.open(image)
    except PIL.UnidentifiedImageError: # if file isn't recognized
        return False,"UnidentifiedImageError"

    if filetype == "jpg":
        expected_type = "JPEG"
    elif filetype == "png":
        expected_type = "PNG"
    elif filetype == "gif":
        expected_type = "GIF"
    elif filetype == "bmp":
        expected_type = "BMP"
    else:
        raise Exception("Error: pillow_valid received invalid filetype " + filetype) from ValueError

    if image.format == expected_type:
        return True,""
    else:
        return False,"WrongImageFormat"

# ===================================================================== #
# snowy_valid
#  
# returns true or false and a string depending on whether or not loading 
# the image raises an exception
# takes in
#   - image: path to the image to process
# returns
#   - flag: true or false. true if no error
#   - string: the type of exception raised if raised
# ===================================================================== #
def snowy_valid(image):

    return True,""

    try:
        out = snowy.load(image)

    # if it doesn't have a valid file extension (jpg,png, or exr)
    except AssertionError: 
        return False,"AssertionError"

    # if it's an invalid file, e.g. a textfile with a .jpg extension will raise this exception
    except ValueError: 
        return False,"ValueError"

    # otherwise:
    except Exception as err:
        return False, err

    return True,""

# ===================================================================== #
# get_hash
#  
# returns the hash of a given file, this subroutine was taken from
# https://www.quickprogrammingtips.com/python/how-to-calculate-sha256-hash-of-a-file-in-python.html
# takes in
#   - image: path to the image
# returns
#   - sha256 of file
# ===================================================================== #
def get_hash(image):
    
    sha256_hash = hashlib.sha256()
    #print("opening "+image)
    file = open(image,"rb")
    # Read and update hash string value in blocks of 4K
    for byte_block in iter(lambda: file.read(4096),b""):
        sha256_hash.update(byte_block)

    return sha256_hash.hexdigest()

# ===================================================================== #
# process
#  
# returns the columns to input into sql
#   - hash: unique sha256 hash of image
#   - *_flag: either a 1 or 0
#   - *_string: error message, only exists if flag is 0
# takes in
#   - schema: path to schema for dfdl
#   - image: path to the image
#   - filetype: filetype being checked
# ===================================================================== #
def process(schema,image,filetype):
    hash = get_hash(image)

    dfdl_flag,dfld_string = dfdl_valid(schema,image)
    if dfdl_flag:
        dfdl_flag = 1
    else:
        dfdl_flag = 0

    kt_flag,kt_string = kaitai_valid(image,filetype)
    if kt_flag:
        kt_flag = 1
    else:
        kt_flag = 0
    
    pillow_flag,pillow_string = pillow_valid(image,filetype)
    if pillow_flag:
        pillow_flag = 1
    else:
        pillow_flag = 0
    
    snowy_flag,snowy_string = snowy_valid(image)
    if snowy_flag:
        snowy_flag = 1
    else:
        snowy_flag = 0
    
    #print(hash,"|",dfdl_flag,"|",dfld_string,"|",kt_flag,"|",kt_string,"|",snowy_flag,"|",snowy_string,"|",pillow_flag,"|",pillow_string)
    return hash,dfdl_flag,str(dfld_string).replace("'",""),kt_flag,str(kt_string).replace("'",""),snowy_flag,str(snowy_string).replace("'",""),pillow_flag,str(pillow_string).replace("'","")
# sql format: NAME | HASH | DFDL FLAG | DFDL STRING | KAITAI FLAG | KAITAI STRING |  
# SNOWY FLAG | SNOWY STRING | PILLOW FLAG | PILLOW STRING


def test():

    # -------------- #
    #     TESTING    #
    # -------------- #

    # this is testing for the jpg format, so we're using the jpg dfdl format.

    schema = "dfdl-schemas/jpeg.dfdl.xsd" # schema for dfdl
    png_image = "png/3080frog.png"        # a valid png file
    jpg_image = "jpg/cat.181.jpg"         # a valid jpg file
    bad = "old/jpeg"                      # python file with no extension
    
    print(dfdl_valid(schema,jpg_image))     #true
    print(dfdl_valid(schema,png_image))     #false
    print(dfdl_valid(schema,bad))           #false

    print(kaitai_valid(jpg_image))          #true
    print(kaitai_valid(png_image))          #false
    print(kaitai_valid(bad))                #false

    print(pillow_valid(jpg_image,"JPEG"))   #true
    print(pillow_valid(png_image,"JPEG"))   #false
    print(pillow_valid(bad,"JPEG"))         #false

    print(snowy_valid(jpg_image))           #true
    print(snowy_valid(png_image))           #true - passes extension check that snowy.load() does
    print(snowy_valid(bad))                 #false

if __name__ == "__main__":
    main()
