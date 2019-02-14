#   1. Install the paramikio module for python.
#       pip install paramiko
#   2. Edit the SSH details below.
import paramiko
import sys
import time

## EDIT SSH DETAILS ##

SSH_USERNAME = "ethos"
SSH_PASSWORD = "live"

## EDIT FILE STORAGE DIRECTORY ##

loc = "data/"

## CODE BELOW ##

#ssh = paramiko.SSHClient()
#ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

i = 0

ssh_stdin = ssh_stdout = ssh_stderr = None

while 1:
    try:
        rig_details_File = open("rig_details.txt")
        ssh_cred_list = rig_details_File.readlines()

    except Exception as e:
        print(e)
        exit()

    else:
        while 1:
            try:
                #obtain customer name and IP Address
                creds = ssh_cred_list[i].split()

                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

                #attempt to connect to rig server and send command
                ssh.connect(creds[1], username=SSH_USERNAME, password=SSH_PASSWORD)


                #send another command and read output
                #No. of GPUs
                ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command("show stats | grep \"gpus:*\"")
                gpus = ssh_stdout.readlines()
                gpus.pop(0)
                if len(gpus) != 1:
                    gpus.pop(0)
                #print(gpus)    #debugging

                #Mining Status
                ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command("show stats | grep \"status:*\"")
                miner_status = ssh_stdout.readlines()
                miner_status.pop(0)
                if len(miner_status) != 1:
                    miner_status.pop(1)
                #print(miner_status)    #debugging

                #temp
                ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command("show stats | grep \"temp:*\"")
                temp = ssh_stdout.readlines()
                temp.pop(0)
                #print(temp)    #debugging

                #miner hashes
                ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command("show stats | grep \"hashes:*\"")
                miner_hashes = ssh_stdout.readlines()
                if len(miner_hashes) != 1:
                    miner_hashes.pop(1)
                #print(miner_hashes)    #debugging


            except paramiko.AuthenticationException:
                print("[{0}] Authentication failed, please verify your credentials.".format(creds[1]))
                ssh.close()

            except paramiko.ssh_exception.NoValidConnectionsError as e:
                print("[{0}] SSH connection failed: {1}".format(creds[1], e))
                ssh.close()

            except TimeoutError as e:
                print("[{0}] SSH connection time out error: {1}".format(creds[1], e))
                ssh.close()

            #list of credientials have finished reading
            except IndexError:
                i = 0
                time.sleep(30)

                #exit the inner WHILE loop to read file again incase of new updates
                break

            except Exception as e:
                print("Unexpected exception occured! See Exception message before for more information. \n{0}".format(e))
                ssh.close()

            else:
                #to write to data file
                try:
                    rigDataFile = open(loc + creds[0] + "_statsServer.txt", "w")

                except Exception as e:
                    print("Faile to open file: {0}".format(e))

                    ssh.close()

                    continue

                else:
                    #write to data file
                    #writing the time of ssh as converting all rigs' local time to be equal to server is not feasible
                    rigDataFile.writelines([str(int(time.time())) + "\n"])
                    rigDataFile.writelines(gpus)
                    rigDataFile.writelines(miner_status)
                    rigDataFile.writelines(temp)
                    rigDataFile.writelines(miner_hashes)

                    #pop out from RAM
                    rigDataFile.close()

                #close ssh connection
                ssh.close()

            #increment to read next credentials
            i += 1
