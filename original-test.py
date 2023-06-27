import subprocess # for dfdl_valid
import sqlite3 
import os
import hashlib
import sys
import kaitaistruct
import argparse

#local files (kaitai schemas)
import ksy_schemas.jpeg
import ksy_schemas.png
import ksy_schemas.gif
import ksy_schemas.bmp
import ksy_schemas.nitf

def main():    

    parser = argparse.ArgumentParser(
        description="Testing script to generate an sql table comparing DDL performance"
    )

    parser.add_argument(
        "-f",
        "--filetype",
        help="Filetype to process, we currently support: bmp, nitf, gif, png, jpg",
        required=True,
        metavar="<filetype>",
        type=str
    )

    parser.add_argument(
        "-i",
        "--images",
        help="path to folder containing files to test",
        required=True,
        metavar="<images>",
        type=str
    )

    parser.add_argument(
        "-d",
        "--daffodil",
        help="path to the daffodil binary",
        required=True,
        metavar="<daffodil>",
        type=str
    )

    parser.add_argument(
        "-o",
        "--output",
        help="path to output database, we do results.db by default",
        metavar="<output>",
        type=str
    )

    args = parser.parse_args()


    filetype = args.filetype
    path = args.images
    daffodil = args.daffodil
    out = args.output

    if out == None:
        out = "results.db"
    elif out[-3:] != ".db": # if it doesn't have .db extension
        out += ".db"


    # validate path
    if not os.path.exists(path):
        print("Error, path " + path + " doesn't exist")
        return -1
   
    # dfdl schema uses jpeg, but we want to stick with jpg
    dfdl_schema = "dfdl-schemas/" + filetype + ".dfdl.xsd"
    if filetype == "jpg":
        dfdl_schema = "dfdl-schemas/" + "jpeg" + ".dfdl.xsd"
    elif filetype == "jpeg":
        filetype = "jpg"

    # validate filetype inputted
    supported_types = ["bmp","nitf","gif","jpeg","png","jpg"]
    if not filetype in supported_types:
        print("Error, filetype " + filetype + " is not supported")
        return -1


       

    if not os.path.exists(dfdl_schema):
        print("Error, schema " + dfdl_schema + " cannot be found")
        print("We expect the schema to be in a directory named 'dfdl_schemas' in the same directory of this script, in the format <filetype>.dfdl.xsd (this is the naming convention on github)")
        return -1

   
    # create database and table
    database = out # r prefix means we're passing as raw string
    connection = sqlite3.connect(database)
    c = connection.cursor() # .cursor() allows us to execute sql commands on the database

    c.execute("CREATE TABLE IF NOT EXISTS {table}(filename text,hash text PRIMARY KEY, dfdl_flag integer, dfdl_string text, kt_flag integer, kt_string text)".format(table = filetype))
    connection.commit() 
   

    # get current directory
    current_dir = os.getcwd()

    # get target directory
    # target_dir = current_dir + "/" + filetype
    
    if path[-1] != '/':
        path += '/'

    target_dir = path

    #target_dir = "/media/kris/2a9713f8-7d16-4fd8-a38e-d95a5eb0860a/spring-22/" + filetype
    dir = os.fsencode(target_dir)

    count = 1
    # for each file in the directory
    for file in os.listdir(dir):

        filename = os.fsdecode(file)

        try:
            print(str(count) + ": checking " + filename + "...")
        except:
            continue
        
        query = "SELECT * FROM " + filetype +" WHERE filename = \'"+filename.replace("'","")+"\'"
        c.execute(query)
        results = c.fetchall()
        #print(results)

        if results != []:
            continue
        
        file_path = target_dir + filename

        # process each file
        hash,dfdl_flag,dfdl_string,kt_flag,kt_string  = process(dfdl_schema,file_path,filetype,daffodil)      

        try:
            # add to sqlite column, wrapping strings in ' for sql to parse correctly
            row_to_input = "\'"+filename.replace("'","")+"\'" + "," + "\'" + hash + "\'" + "," + str(dfdl_flag) + "," + "\'"+ dfdl_string + "\'" + "," + str(kt_flag) + "," \
            + "\'" + kt_string + "\'"

            #print(column_to_input)
            print(row_to_input)

            c.execute("INSERT OR REPLACE INTO {table} VALUES ({values})".format(table=filetype,values=row_to_input))
            count += 1
            connection.commit()
        except Exception as err:
            print(err)
            print("Failed for " + filename.replace("'",""))
            return

 
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
def dfdl_valid(schema,image,daffodil):

    print(schema + "\t" + image)

    try:
        # same as bash command: $ daffodil parse -s <schema> <image> > out
        
        
        cmd = ["./"+daffodil,'parse','-s',schema,image]

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

        out = subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        
        output = out.stdout.decode("utf-8")
    
        
        #with open("x", "wb") as out: subprocess.Popen(cmd, stdout=out)
        #os.popen("daffodil parse -s " + schema + " " + image +" > out")
   
    except PermissionError:
        print("Permission to daffodil binary denied! Make sure you provide the binary and not the directory, and also set the permissions of the binary")
        return False, "subprocess error, not a daffodil issue"

    except Exception as err:
        output = out.stderr.decode("utf-8")
        #return False, str(err).replace("'","")
        return False, output
        
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
        return True, output
    else:         
        output = out.stderr.decode("utf-8")
        return False, output

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
        elif filetype == "nitf":
            object = nitf.Nitf.from_file(image)
        else:
            raise Exception("Error: kaitai_valid received invalid filetype: " + filetype) from ValueError
        
    except kaitaistruct.ValidationNotEqualError:
        return False, "ValidationNotEqualError"

    except EOFError:
        return False, "EOFError"

    # otherwise:
    except Exception as err:
        print("Error" + str(err))
        return False, err
    
    # finally:
    # #     err = Exception

    #     return False, err
    return True, ""

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
def process(schema,image,filetype,daffodil):
    hash = get_hash(image)

    dfdl_flag,dfld_string = dfdl_valid(schema,image,daffodil)
    if dfdl_flag:
        dfdl_flag = 1
    else:
        dfdl_flag = 0

    kt_flag,kt_string = kaitai_valid(image,filetype)
    if kt_flag:
        kt_flag = 1
    else:
        kt_flag = 0
    
        
    return hash,dfdl_flag,str(dfld_string).replace("'",""),kt_flag,str(kt_string).replace("'","")
# sql format: NAME | HASH | DFDL FLAG | DFDL STRING | KAITAI FLAG | KAITAI STRING |  


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

if __name__ == "__main__":
    main()
