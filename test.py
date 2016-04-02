#!/usr/bin/python

import re
import sys, getopt

def test_signature(inputfile):
    f1 = open(inputfile)
    f2 = open(inputfile)

    sign_entry = re.compile('^.* ([0-9]+)$')
    flag = 0
    line = f1.readline()
    i = 1
    j = 0

    while line:
        line = f1.readline()
        i = i + 1
        if "** SIGN entry ** :" in line: #look for signature lock
            trd = sign_entry.match(line)
            
            if trd is not None:
                f2.seek(f1.tell(), 0)
                sign_line = f2.readline()
                j = i + 1
                dbg = "Line " + str(i) + ": " + trd.group(0)
                
                while sign_line:
                    if "** SIGN exit ** :" in sign_line:
                        regex = "^.*Sign: (.+?), Thread number: " + trd.group(1) + "$" #Second file pointer looks for signature unlock on same thread
                        sign = re.search(regex, sign_line)
                        if sign is not None:
                            flag = 1 # set flag is unlock found
                            break
                        else:
                            print dbg
                            print "Line " + str(j) + ": " + sign_line
                            regex = "^.*Thread number: ([0-9]+)$"
                            print "Error: Thread %s in critical section of Thread %s" %(re.search(regex, sign_line).group(1), trd.group(1))

                    if "** SIGN entry ** :" in sign_line: #look for second signature lock within critical section
                        print dbg
                        print "Line " + str(j) + ": " + sign_line
                        regex = "^.*Thread number: ([0-9]+)$"
                        print "Error: Thread %s in critical section of Thread %s" %(re.search(regex, sign_line).group(1), trd.group(1))
                    
                    sign_line = f2.readline()
                    j = j + 1

                if flag is 0:
                    print dbg
                    print 'Error: Thread %s. no SIGN exit found !' % trd.group(1) #Print error if no unlock found
                else:
                    flag = 0
    f1.close()
    return;

def test_queue(inputfile):
    f1 = open(inputfile)
    f2 = open(inputfile)

    queue_entry = re.compile('^.* ([0-9]+)$')
    flag = 0
    line = f1.readline()

    i = 1
    j = 0

    while line:
        line = f1.readline()
        i = i + 1
        if "** QUEUE entry ** :" in line or "** QUEUE Entry" in line: #look for queue entry
            trd = queue_entry.match(line)
            
            if trd is not None:
                f2.seek(f1.tell(), 0)
                queue_line = f2.readline()
                j = i + 1
                dbg = "Line " + str(i) + ": " + trd.group(0)

                while queue_line:
                    if "** QUEUE Exit" in queue_line or "** QUEUE exit" in queue_line:
                        regex = "^.*Thread number: " + trd.group(1) + "$" #Second file pointer looks for queue unlock on same thread
                        queue = re.search(regex, queue_line)
                        if queue is not None:
                            flag = 1 # set flag is unlock found
                            break
                        else:
                            print dbg
                            print "Line " + str(j) + ": " + queue_line
                            regex = "^.*Thread number: ([0-9]+)$"
                            print "Error: Thread %s in critical section of Thread %s" %(re.search(regex, queue_line).group(1), trd.group(1))

                    if "** QUEUE entry ** :" in queue_line or "** QUEUE Entry" in queue_line: #look for second queueature lock within critical section
                        print dbg
                        print "Line " + str(j) + ": " + queue_line
                        regex = "^.*Thread number: ([0-9]+)$"
                        print "Error: Thread %s in critical section of Thread %s" %(re.search(regex, queue_line).group(1), trd.group(1))
                    
                    queue_line = f2.readline()
                    j = j + 1

                if flag is 0:
                    print dbg
                    print 'Error: Thread %s. no QUEUE exit found !' % trd.group(1) #Print error if no unlock found
                else:
                    flag = 0
    f1.close()
    return;

def test_reader(inputfile):
    file_dict = {}
    f1 = open(inputfile)
    f2 = open(inputfile)

    flag = 0
    line = f1.readline()
    count = 0

    i = 1
    j = 0

    while line:
        line = f1.readline()
        i = i + 1

        if "file name:" in line: # read file name
            regex = "^file name: (.+?)$"
            file_name = re.search(regex, line)
            if file_name is not None:
                file_dict[file_name.group(1)] = 0
            else:
                print "Line " + str(i) + ": Error: Unable to read file name"

        if "** Read Entry ** - Reading file:" in line: # Outer loop looks for new file open
            reader = re.search('^.*Reading file: (.+?), Sign.*Thread number: ([0-9]+)$', line)
              
            if reader is not None:
                file = reader.group(1)
                thread_id = reader.group(2)
                f2.seek(f1.tell(), 0)
                reader_line = f2.readline()
                j = i + 1
                dbg = "Line " + str(i) + ": " + reader.group(0)

                if file_dict[file] is 0 :
                    file_dict[file] = 1
                    count = 1

                    while reader_line:
                        if "** Read exit - do_read ** - Reader pausing:" in reader_line: #first case, reader volutarily pauses
                            regex = "^.*Reader pausing: file: " + file + ", Sign.* at index: ([0-9]+)$"
                            trd = re.search(regex, reader_line)
                            if trd is not None:
                                dbg = "Line " + str(j) + ": " + trd.group(0)
                                count = count - 1
                            
                        if "** READ exit - do_read - Reader queueing:" in reader_line: #first case, reader volutarily pauses
                            regex = "^.*Reader queueing: file: " + file + ", at index: ([0-9]+).*.$"
                            trd = re.search(regex, reader_line)
                            if trd is not None:
                                dbg = "Line " + str(j) + ": " + trd.group(0)
                                count = count - 1
                            
                        if "** Read Exit ** - is yielding when done with read: file:" in reader_line: # second case, reader exits
                            regex = "^.*yielding when done with read: file: " + file + ", Sign.*$"
                            trd = re.search(regex, reader_line)
                            if trd is not None:
                                dbg = "Line " + str(j) + ": " + trd.group(0)
                                count = count - 1
                        
                        if "** Read entry - do_read ** - Reader has readlock:" in reader_line: # Third case, reader acquires readlock again
                            regex = "^.*Reader has readlock: file: " + file + ", Sign.*$"
                            trd = re.search(regex, reader_line)
                            if trd is not None:
                                if count is -1 :
                                    print dbg
                                    print "Line " + str(j) + ": " + trd.group(0)
                                    print ("Error: Reader got lock with thread %s on file %s while a writer also had the lock" %(thread_id, file))
                                    break
                                count = count + 1
                                dbg = "Line " + str(j) + ": " + trd.group(0)

                        if "** READ entry - do_read - Reader queueing done:" in reader_line: # Third case, reader acquires readlock again
                            regex = "^.*Reader queueing done: file: " + file + ", at.*$"
                            trd = re.search(regex, reader_line)
                            if trd is not None:
                                if count is -1 :
                                    print dbg
                                    print "Line " + str(j) + ": " + trd.group(0)
                                    print ("Error: Reader got lock with thread %s on file %s while a writer also had the lock" %(thread_id, file))
                                    break
                                count = count + 1
                                dbg = "Line " + str(j) + ": " + trd.group(0)

                        if "** Read Entry ** - Reading file:" in reader_line: # new reader on file
                            regex = "^.*Reading file: " + file +", Sign.*$"
                            trd = re.search(regex, reader_line)
                            if trd is not None:
                                if count is -1 :
                                    print dbg
                                    print "Line " + str(j) + ": " + trd.group(0)
                                    print ("Error: Reader got lock with thread %s on file %s while a writer also had the lock" %(thread_id, file))
                                    break
                                count = count + 1
                                dbg = "Line " + str(j) + ": " + trd.group(0)

                        if "** WRITE Entry **" in reader_line:
                            regex = "^.*Thread number: ([0-9]+); filename = (.+?), loc*.*$"
                            trd = re.search(regex, reader_line)
                            if trd is not None:
                                if trd.group(2) == file:
                                    if count is -1:
                                        print dbg
                                        print "Line " + str(j) + ": " + trd.group(0)

                                        print ("Error: Writer got lock with thread %s on file %s while another writer also had the lock" %(trd.group(1)
                                        , file))
                                        break
                                    if count is 0:
                                        count = -1
                                        dbg = "Line " + str(j) + ": " + trd.group(0)
                                    else:
                                        print dbg
                                        print "Line " + str(j) + ": " + trd.group(0)

                                        print ("Error: Writer got lock with thread %s on file %s while reader also had the lock" %(trd.group(1), file))
                                        break
# put logging for writer as well

                        if "** WRITE Exit **" in reader_line:
                            regex = "^.*Thread number: ([0-9]+); filename = (.+?), loc.*$"
                            trd = re.search(regex, reader_line)
                            if trd is not None:
                                if trd.group(2) == file:
                                    if count is -1:
                                        count = 0
                                        dbg = "Line " + str(j) + ": " + trd.group(0)
                                    else:
                                        print "Error: Somethings not right!!"
                                        break
                        reader_line = f2.readline() #inner loop scans if integrity of critical section is maintained
                        j = j + 1

                else:
                    flag = 0
                    while reader_line:
                        if "** Read exit - do_read ** - Reader pausing:" in reader_line: #first case, reader volutarily pauses
                            regex = "^.*Reader pausing: file: " + file + ", Sign.*Thread number: " + thread_id + ", at index: ([0-9]+)$"
                            trd = re.search(regex, reader_line)
                            if trd is not None:
                                if flag is 0:
                                    dbg = "Line " + str(j) + ": " + trd.group(0)
                                    flag = 1 # flip flag as reader is now expected to acquire readlock next
                                else:
                                    print dbg
                                    print "Line " + str(j) + ": " + trd.group(0)
                                    print("Error: Thread %s on file %s lock unexpected behaviour" %(thread_id, file))
                                    break
                            
                        if "** Read Exit ** - is yielding when done with read: file:" in reader_line: # second case, reader exits
                            regex = "^.*yielding when done with read: file: " + file + ", Sign.*Thread number: " + thread_id + "$"
                            trd = re.search(regex, reader_line)
                            if trd is not None:
                                if flag is not 0: # Unexpected reader exit
                                    print dbg
                                    print "Line " + str(j) + ": " + trd.group(0)
                                    print("Error: Thread %s on file %s lock unexpected behaviour" %(thread_id, file))
                                else:
                                    dbg = "Line " + str(j) + ": " + trd.group(0)
                                break
                        
                        if "** Read entry - do_read ** - Reader has readlock:" in reader_line: # Third case, reader acquires readlock again
                            regex = "^.*Reader has readlock: file: " + file + ", Sign.*Thread number: " + thread_id + ", at index: ([0-9]+)$"
                            trd = re.search(regex, reader_line)
                            if trd is not None:
                                if flag is 1:
                                    dbg = "Line " + str(j) + ": " + trd.group(0)
                                    flag = 0 # flip flag as reader is now expected to either relase lock or exit
                                else:
                                    print dbg
                                    print "Line " + str(j) + ": " + trd.group(0)
                                    print("Error: Thread %s on file %s lock unexpected behaviour" %(thread_id, file))
                                    break
                        reader_line = f2.readline() #inner loop scans if integrity of critical section is maintained
                        j = j + 1
    f1.close()
    return;

def main(argv):
    inputfile = ''
    outputfile = ''
    try:
        opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
    except getopt.GetoptError:
        print 'test.py -i <inputfile>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'test.py -i <inputfile>'
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
    print 'Input file is ', inputfile

    test_signature(inputfile)
    test_queue(inputfile)
    test_reader(inputfile)

if __name__ == "__main__":
    main(sys.argv[1:])
