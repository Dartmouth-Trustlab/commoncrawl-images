'''
By Chavin (Kris) Udomwongsa - 2022

Script that downloads wet files, extracts urls from the files
then downloads the images stored at the url.

ASSUMES that within the same directory as the script, are folders
containing wet.paths files, which is downloaded from
https://commoncrawl.org/the-data/get-started/

This script deals with 4 image formats:
- jpg
- png
- gif
- bmp
- ntf

Takes in a limit at cmdline.
(so python3 download_images.py <limit>)
where limit is the number of images of each filetype 
that is desired
'''

import sys
import threading
import os
import gzip
import wget
import requests

import argparse



# wet paths stored do not contain the url prefix
PREFIX = "https://data.commoncrawl.org/"

# number of threads concurrently downloading images,
# modify if needed
NUM_OF_THREADS = 1

# get current path
path = os.path.abspath(os.getcwd())

# lock
# lock = threading.Lock()

def main():
    parser = argparse.ArgumentParser(
    description="Utility script to download images of various extensions from common crawler. Enter the extensions that you want"
    )
        
    parser.add_argument(
        "-l",
        "--limit",
        help="Number of images per file-type to download", 
        required=True,
        metavar="<limit>",
        type=int
    )

    parser.add_argument(
        "-f",
        "--formats",
        help="File extensions to download, will do all by default",
        required=False,
        default=["jpg","bmp","png","gif","nitf"],
        nargs="+"
    )
    args = parser.parse_args()

    print(args)
    print(args.limit)
    print(args.formats)

    limit = args.limit
    formats = args.formats

# check cmdline input

    # edge case for nitf, since there are so many different extensions for it
    if "nitf" in formats:
        formats.append("ntf")
        formats.append("nsf")
        formats.append("ntf.r0")
        formats.append("ntf.r1")
        formats.append("ntf.r2")
        formats.append("ntf.r3")
        formats.append("ntf.r4")
        formats.append("ntf.r5")



    if limit <= 0:
        print("ERROR: limit must be a positive integer\nUSAGE: python3 download_images.py <limit>")
        return 1
    
    # initialize dictionary to hold number of images of each filetype collected
    count = {}
    for ext in formats:
        count[ext] = 0

    print(count)

    # create target directories
    for ext in count.keys():
        if not os.path.isdir(path + "/" + ext):
            os.system("mkdir " + ext)

   
    wet_paths = []
    
    # for each file in directory
    for file in os.listdir(path):
        # if it's a directory
        if os.path.isdir(file):
            # check for wet.paths
            check_path = file + "/wet.paths"
            if os.path.isfile(check_path):
                print("Found: " + check_path)
                wet_paths.append(check_path)

    # error message if no wet.paths files are found
    if len(wet_paths) == 0:
        print("ERROR, no wet.paths found")
        print("This program expects wet.paths files in subdirectories stored in the same directory as this script")
        print("Please download wet files from https://commoncrawl.org/the-data/get-started/ extract and store them in subdirectories")
        return 1

    # we have the wet.paths file now, we can download
    # we do loop through one wet.paths file at a time, 
    # and within each wet.paths we do 10 threads to extract the images

    # while we don't have enough images of each type
    while sum(count.values())  < limit * len(count.keys()):

        # for each month of common crawl (cc) that we have
        for cc_month in wet_paths:

            # open wet.paths file
            file = open(cc_month,"r")

            # logging info
            print("\nCurrent wet.paths target: " + cc_month)
            
            # we're doing a batch of 10 threads each time
            batch_urls = [] # array to store 10 urls for each batch

            batch_count = 0 # just here for logging reasons

            # for each line in the wet_paths
            for line in file:

                batch_urls.append(PREFIX + line)

                # when we have 10 urls
                if len(batch_urls) % NUM_OF_THREADS == 0:
                    
                    threads = []    # array to store each thread

                    # for each of our 10 urls
                    for url in batch_urls:

                        # call a thread for each url
                        thread = threading.Thread(target=thread_download_images, args=(count,limit,url,formats))
                        threads.append(thread)
                        thread.start()
                    
                    # WAIT for all threads to finish
                    for thread in threads:
                        thread.join()
                    
                    # reset batch_urls when done
                    batch_urls = []

                    batch_count += 1
                    print("   Batch " + str(batch_count) + " done.")
                    
                    print("counts:")
                    for ext in count.keys():
                        print("- " + ext + " " + str(count[ext]))


                # then, check if we're done (have limit number of images for each type)
                if sum(count.values())  >= limit * len(count.keys()):
                    # if done, celebrate by exiting
                    print("Done!")
                    return 0
                    
            # after clearing our file, if there's still urls left to do:
            if len(batch_urls) > 0:
                # for each of our 10 urls
                for url in batch_urls:
                        # call a thread for each url
                        threading.Thread(target=thread_download_images, args=(count,limit,url,formats))
                # call a thread

'''
Function that takes in a dictionary, a limit, and a url, and will
- download the .gz stored at the url
- extract the .wet file
- extract UNIQUE urls from the .wet file
- call wget on the urls to download images

Takes in
- dictionary: storing the count of each data type
- limit: the # of images we want for each data type
- url: urls storing .gz of .wet file

Returns
- 0 if done, nothing went wrong
- 1 if something went wrong
'''
def thread_download_images(count, limit, wet_url, formats):

    # download wet
    try:
        # wget call
        filename = wget.download(wet_url)

        wet_file_name = filename[:-3]

    except:
        print("wget failed for " + url)
        return 1
    
    try:
        # unzip the file
        gunzip(filename,wet_file_name)
        # delete original
        os.remove(filename)
    except:
        print("gunzip failed for " + filename)
        return 1

    # get urls
    wet_file = open(wet_file_name,"r")
    urls = []

    # for each line in wet file
    for line in wet_file:

        line = line.split(" ")

        # for each word in each line
        for word in line:
            
            if len(word) >= 10:
                # extract last 3 characters and first 4 characters
                suffix = word.split(".")[-1] 

                suffix2 = suffix

                if "nitf" in formats:
                    suffix2 = word[-6:]

                prefix = word[:4]
                # if it ends in the extension and starts with http, it's a link
                
                if prefix == "http" and (suffix in formats or suffix2 in formats):
                    print("found one for " + suffix)
                    # get lock and check if we have enough images
                    # lock.acquire()
                    if count[suffix] < limit:
                                            
                        # if we haven't already found this url
                        if not (word in urls):
                            urls.append(word)

                            print(word)
                            # download image
                            try:
                                # get the image
                                response = requests.get(word,timeout=2)
                                # print(response)
                                # print(path + "/" + suffix + "/" + word.split("/")[2])

                                # if the link works, write contents to file
                                if response.status_code == 200:
                                    f = open(path + "/" + suffix + "/" + word.split("/")[2] +"." + suffix, 'wb')
                                    f.write(response.content)
                                    f.close()

                                    count[suffix] += 1


                                #print("download done, moving it to " + path + "/" + suffix)
                                # os.system("mv \'" + path + filename + "\'" + " \'" + path + suffix + "/" + filename+"\'")

                            except:
                                #print("wget or move failed for " + word)
                                # lock.release()
                                continue
                            
                            
                            

                        if sum(count.values())  >= limit * len(count.keys()):
                            # if done, celebrate by exiting
                            print("Done!")
                            return 0

                    # lock.release()

                        # update count if success
                        
                        

    # once done with wet file, we cleanup
    wet_file.close()
    os.system("rm " + wet_file_name)

    return 0


'''
Function that takes in a file source path, and destination,
the source_filepath is assumed to be a path to a .gz file
The contents of the .gz is extracted and then the original
source_filepath is deleted.

Modified from https://stackoverflow.com/questions/52332897/how-to-extract-a-gz-file-in-python
'''
def gunzip(source_filepath, dest_filepath, block_size=65536):
	s_file = gzip.open(source_filepath,"rb")
	d_file = open(dest_filepath,"wb")
	while True:
		block = s_file.read(block_size)
		if not block:
			break
		else:
			d_file.write(block)
	d_file.close()
	s_file.close()



if __name__ == "__main__":
    main()

