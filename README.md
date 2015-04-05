# simple-gmail-receiver
Simple Gmail Client that fetches mail from inbox and downloads its attachments

#Requirements
The usage of this script requires:
  - Python 3.4
  - 2 step validation Disbaled
  - Enabled IMAP access
  - Enabled less secured access from applications

#Configuration
Keep the config file in the same folder as the script. The parameters used in the config file are:
  - Username: your Gmail user
  - Password: your Gmail passowrd
  - mailbox: The mailbox that the client will check. INBOX is the default one
  - filter: IMAP filter to apply, see RFC 3501 Section 6.4.4. ALL would fetch everything
  - rootDir: root directory where the files will be saved. Ex: C:\myMails

#Execution
You can execute the script either from command line or GUI:
  - From CLI: navigate to the folder where the script is placed and run "python gmail-client.py"
  
  - From GUI: double click on the "gmail-client.py" file. A command prompt will open and execute the script
  
