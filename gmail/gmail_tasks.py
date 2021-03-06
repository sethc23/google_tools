from sys import argv, path
path.append('$BD/crons')
path.append('$BD/gmail')
path.append('$BD/finance')
path.append('$BD/utility')
from time import time, mktime
from datetime import datetime, tzinfo
import os
from manage_cron import updateManager
# from var_checks import internet_on  //ENDFIX

import gmail_imap

class EST(tzinfo):
    def utcoffset(self, dt):
        a = str(self)
        # print a
        # print a[a.rfind(' ')+1:]
        return  # timedelta(hours=1)


class gmail_tasks:

    def __init__(self, username, password):
        self.gmail = gmail_imap.gmail_imap(username, password)

    def close(self):
        self.gmail.logout()

    def mailboxes(self):
        gmail = self.gmail
        gmail.mailboxes.load()
        return gmail.mailboxes

    def clean_global(self, global_list, daysBack):
        gmail = self.gmail
        gmail.mailboxes.load()
        all_box = gmail.mailboxes
        dates, titles, uids = [], [], []
        global_msg = dates, titles, uids, [], []

        exclude_list = ['_MATCHED', '_SENT_MAIL', '_SENT_OTHER', '[Gmail]/Sent Mail', '[Gmail]/Trash',
                      '[Gmail]/All Mail', '_DRAFTS', 'SMS', 'Trash', 'Blocked', 'Call log']
        
        archive_list = ['LAW/PATENT', 'WEB', 'WEB/CONFIRMATIONS', 'WEB/DOMAINS',
                      'WEB/GOOGLE', 'WEB/HOSTING', 'WEB/TECHNOLOGY', '_CHATS',
                      '_INBOX_SansPaper/AIIM', '_INBOX_SansPaper/Conf_Calls']
        
        item_list = []
        for it in all_box:
            if (global_list.count(it) == 0 and exclude_list.count(it) == 0):
                item_list.append(it)

        for box in global_list:
            # box='_INBOX_UNH'
            gmail.messages.process(box, 'all')
            for msg in gmail.messages:
                msgID = msg.msgID
                msg_date = self.clean_date(msg.date)

                if (daysBack >= mktime(msg_date.timetuple()) or
                    archive_list.count(box) == 0):  # days ago is bigger or equal to msg seconds
                    date = msg_date.strftime('%d-%b-%Y')
                    field_header = 'DATE "' + msg_date.__str__() + '"' + ' SUBJECT "' + msg.Subject + '"'
                    msgID_header = 'Message-ID "' + msgID + '"'
                    uid = msg.uid
                    global_msg[0].append(msgID)
                    global_msg[1].append(field_header)
                    global_msg[2].append(msgID_header)
                    global_msg[3].append(uid)
                    global_msg[4].append(box)

        del_list = [], []

        for boxes in item_list:
            # boxes='LAW/PATENT'
            box_msgs = gmail.messages.process(boxes, 'msgID')
            if (box_msgs != '[]' and box_msgs != False):
                for item in global_msg[0]:
                    if box_msgs.count(item) != 0:
                        index_num = global_msg[0].index(item)
                        global_msg[0].pop(index_num)
                        global_msg[1].pop(index_num)
                        global_msg[2].pop(index_num)
                        del_list[0].append(global_msg[3].pop(index_num))
                        del_list[1].append(global_msg[4].pop(index_num))

        for box in global_list:
            new_del_list = []
            for i in range(0, len(del_list[1])):
                if del_list[1][i] == box:
                    new_del_list.append(del_list[0][i])
            if new_del_list != []:
                gmail.messages.delMessage(box, new_del_list)

    def check_allmail(self):
        gmail = self.gmail
        gmail.mailboxes.load()
        all_box = gmail.mailboxes
        dates, titles, uids = [], [], []
        all_msgs = dates, titles, uids, [], []
        
        check_box = '[Gmail]/All Mail'
        gmail.messages.process(check_box, 'all')
        for msg in gmail.messages:
            msgID = msg.msgID            
            all_msgs[0].append(msgID)
            all_msgs[1].append(msg.uid)
            
        all_box = all_box.pop(all_box.index(box))

        for box in all_box:
            gmail.messages.process(box, 'all')
            for msg in gmail.messages:
                msgID = msg.msgID
                if all_msgs[0].count(msgID) != 0:
                    i_num = all_msgs[0].index(msgID)
                    y = all_msgs[0].pop(i_num)
                    y = all_msgs[1].pop(i_num)

        dest_folder = '_INBOX'
        for i in range(0, len(all_msgs[0])):
            print
            # gmail.messages.copyMessage(check_box, all_msgs[1][i], desti_folder_name)
        
    def clean_sentMail(self):
        gmail = self.gmail
        # gmail.mailboxes.load()
        fromFolder = '[Gmail]/Sent Mail'
        toFolder = '_SENT_MAIL'
        gmail.messages.process(fromFolder, 'all')
        number = 10
        for msg in gmail.messages:
            msgID = msg.msgID
            field_header = 'DATE "' + msg.date + '"' + ' SUBJECT "' + msg.Subject + '"'
            # print field_header
            number = number - 1
            if number == 0:
                break
            # gmail.messages.copyMessage(fromFolder, msgID, toFolder)
            # break

    def clean_Communications(self):
        gmail = self.gmail
        gmail.mailboxes.load()
        #------
        # contact = name, number, email
        msg_name, msg_number, msg_email = [], [], []
        # contact_type = sms,call,email
        # msg_location = folder, uid
        msg_folder, msg_uid = [], []
        # msg_content = date,body
        msg_date, msg_body = [], []
        """
        comm_msgs[0]=name
        comm_msgs[1]=number
        comm_msgs[2]=email
        comm_msgs[3]=folder
        comm_msgs[4]=uid
        comm_msgs[5]=date

        uniq_msgs[0]=uniq_type
        uniq_msgs[1]=uniq_val
        """
        #------
        comm_msgs = msg_name, msg_number, msg_email, msg_folder, msg_uid, msg_date
        uniq_msgs = [], []
        log_sources = ['SMS', 'Call log']
        stop = False
        for it in log_sources:
            if stop == True:
                break
            gmail.messages.process(it, 'all')
            msg_folder = it
            for msg in gmail.messages:
                msg_uid = msg.uid
                msg_name = msg.From[:msg.From.find('<') - 1]
                msg_source = msg.From[msg.From.find('<') + 1:msg.From.find('>')]
                if msg_source[0].isdigit():
                    msg_number = msg_source[:msg_source.find('@')]
                    msg_email = ''
                else:
                    msg_number = ''
                    msg_email = msg_source
                
                msg_date = self.clean_date(msg.date)
                msg_date = msg_date.strftime('%Y.%m.%d_%H:%M')
                
                
                comm_msgs[0].append(msg_name)
                comm_msgs[1].append(msg_number)
                comm_msgs[2].append(msg_email)

                if (msg_name.find('seth.t.chase') == -1 and msg_email.find('seth.t.chase') == -1):
                    if (msg_name != 'Me' and msg_email != 'Me'):
                        if uniq_msgs[1].count(msg_name) == 0:
                            uniq_msgs[0].append('name')
                            uniq_msgs[1].append(msg_name)
                        elif uniq_msgs[1].count(msg_number) == 0:
                            uniq_msgs[0].append('number')
                            uniq_msgs[1].append(msg_number)
                        elif uniq_msgs[1].count(msg_email) == 0:
                            uniq_msgs[0].append('email')
                            uniq_msgs[1].append(msg_email)

                comm_msgs[3].append(msg_folder)
                comm_msgs[4].append(msg_uid)
                comm_msgs[5].append(msg_date)
                if len(comm_msgs[0]) == 1000:
                    stop = True
                    break

        poplist = []
        for i in range(0, len(uniq_msgs[1])):
            if len(uniq_msgs[1][i]) < 3:
                poplist.append(i)
        poplist.reverse()
        for it in poplist:
            x = uniq_msgs[0].pop(it)
            x = uniq_msgs[1].pop(it)

        # print len(comm_msgs[0])
        # return uniq_msgs
        # '''
        exclude_list = ['_MATCHED', 'Blocked', 'Call log', 'INBOX', 'SMS', '_DRAFTS', 'BANK', 'COMMUNICATIONS', '[Gmail]/All Mail']
        archive_list = ['LAW/PATENT', 'WEB', 'WEB/CONFIRMATIONS', 'WEB/DOMAINS',
                      'WEB/GOOGLE', 'WEB/HOSTING', 'WEB/TECHNOLOGY',
                      '_INBOX_SansPaper/AIIM', '_INBOX_SansPaper/Conf_Calls']

        gmail.mailboxes.load()
        all_box = gmail.mailboxes        
        item_list = []
        for it in all_box:
            if (archive_list.count(it) == 0 and exclude_list.count(it) == 0):
                if item_list.count(it) == 0:
                    item_list.append(it)

        stop = False
        for box in item_list:
            if stop == True:
                break
            gmail.messages.process(box, 'all')
            # gmail.messages.searchBox(box,'HEADER',uniq_msgs[1])
            # print len(gmail.messages)

            for msg in gmail.messages:
                skip = False
                
                var = msg.From
                if str(var) != "None":
                    msg_name = var[:var.find('<') - 1].strip('"')
                    msg_source = var[var.find('<') + 1:var.find('>')]
                    if uniq_msgs[1].count(msg_name) != 0:
                        comm_msgs[0].append(msg_name)
                        skip = True
                    elif uniq_msgs[1].count(msg_source) != 0:
                        comm_msgs[2].append(msg_source)
                        skip = True

                var = msg.To
                if skip == False:
                    if str(var) != "None":
                        msg_name = var[:var.find('<') - 1].strip('"')
                        msg_source = var[var.find('<') + 1:var.find('>')]
                        if uniq_msgs[1].count(msg_name) != 0:
                            comm_msgs[0].append(msg_name)
                        elif uniq_msgs[1].count(msg_source) != 0:
                            comm_msgs[2].append(msg_source)

                if len(comm_msgs[0]) < len(comm_msgs[2]):
                    comm_msgs[0].append('')
                    skip = True
                elif len(comm_msgs[0]) > len(comm_msgs[2]):
                    comm_msgs[2].append('')
                    skip = True             

                if skip == True:
                    comm_msgs[1].append('')
                    comm_msgs[3].append(box)
                    comm_msgs[4].append(msg.uid)
                    comm_msgs[5].append(msg.date)
                else:
                    pass
                if len(comm_msgs[0]) == 2000:
                    stop = True
                    break
        # print '--'      
        # print len(comm_msgs[0])
       # print '-----------'
        comm_list = [], [], [], [], [], []
        for i in range(0, len(uniq_msgs[0])):
            index_nums = []
            uniq_var = uniq_msgs[1][i]
            for j in range(0, len(comm_msgs[0])):
                comm_var = ''
                for k in range(0, len(comm_msgs)):
                    try:
                        comm_var = comm_var + comm_msgs[k][j] + ' '
                    except:
                        # print len(comm_msgs[0])
                        # print len(comm_msgs[1])
                        # print len(comm_msgs[2])
                        # print len(comm_msgs[3])
                        # print len(comm_msgs[4])
                        # print len(comm_msgs[5])
                        error

                if comm_var.find(uniq_var) != -1:
                    index_nums.append(j)
            index_nums.reverse()
            for j in range(0, len(index_nums)):
                for k in range(0, len(comm_msgs)):
                    comm_list[k].append(comm_msgs[k].pop(index_nums[j]))

            break
        # print len(comm_msgs[0]),len(comm_list[0])
        # print len(comm_msgs),len(comm_list)

    def clean_date(self, msg_date): 
        try:
            msg_date = msg_date.lower()
            weekdays = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
            for it in weekdays:
                msg_date = msg_date.replace(it, '')
            msg_date = msg_date.replace(',', '')
            if (msg_date.find('+') != -1 or msg_date.find('-') != -1):
                if msg_date[msg_date.find('+') + 4].isdigit():
                    msg_date = msg_date[:msg_date.find('+') - 1]
                if msg_date[msg_date.find('-') + 4].isdigit():
                    msg_date = msg_date[:msg_date.find('-') - 1]              
            msg_date = msg_date.strip()

            if len(msg_date.split()[2]) == 2:
                months = ['jan', 'feb', 'mar', 'apr', 'may', 'jun',
                    'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
                for it in months:
                    if msg_date.find(it) != -1:
                        a = msg_date[msg_date.find(it) + len(it):msg_date.find(':') - 3]
                        a = a.strip().replace(' ', '')
                        if len(a) == 2:
                            msg_date = msg_date[:msg_date.find(it) + len(it) + 1] + '20' + msg_date[msg_date.find(it) + len(it) + 1:]
                                
            if msg_date.count(':') == 2:
                msgDate = datetime.strptime(msg_date[:msg_date.rfind(":") + 3], '%d %b %Y %H:%M:%S')
            elif msg_date.count(':') == 1:
                msgDate = datetime.strptime(msg_date[:msg_date.rfind(":") + 3], '%d %b %Y %H:%M')

            return msgDate

        except:  
            # print 'date error (in clean_communications)'
            # print msg_date
            return

    def get_attachments(self, source, destination, overright=False):
        x = self.gmail.messages.process(source, 'all')
        msgUIDs, dates, senders = [], [], []
        for it in x:
            msgUIDs.append(it.uid)
            dates.append(it.date)
            senders.append(it.From)
        msgVars = msgUIDs, dates, senders
        self.gmail.messages.getAttachments(source, destination, msgVars)
        return 'complete'
    
    def get_attachments_info(self, source):
        x = self.gmail.messages.process(source, 'all_attachments')
        print 'total attachments:', len(x), '\n'
        for it in x:
            print it.date + '\t' + it.From + '\t' + it.attachments


if __name__ == '__main__':
    try:
        username = argv[1]
        password = argv[2]
        cmd = []
        for i in range(3, len(argv)): cmd.append(argv[i])
        if len(cmd) != 0: command = cmd[0]
        else: command = ''
        # print username, password
        stop = False
    except:
        print 'argument error (or testing)'
        username, password, command = '', '', ''
        stop = True
    # print str(time.localtime()[3])+':'+str(time.localtime()[4])
    # if internet_on() == False: stop=True  //ENDFIX


    # -- TEST
    # '''
    tasks = gmail_tasks(username,password)
    daysBack=int(time())-3*(24*60*60) #3 days -- in
    global_list=['_INBOX','_INBOX_UNH']
    tasks.clean_global(global_list, daysBack)
    x=tasks.clean_Communications()
    tasks.clean_sentMail()
    tasks.close()
    # '''
    # -- /TEST

    if command == 'getAttachments':
        tasks = gmail_tasks(username, password)
        source = 'attachments'
        # source='attachments_backup'
        print 'from:', source
        # destination='/Users/admin/'+cmd[1]
        destination = '/Users/admin/Desktop/scans'
        if os.path.exists(destination): pass
        else: os.system('mkdir "' + destination + '"')
        print 'to:  ', destination
        y = tasks.get_attachments
        x = tasks.get_attachments(source, destination)
        tasks.close()
        stop = True

    if command == 'getAttachmentsInfo':
        tasks = gmail_tasks(username, password)
        source = 'attachments'
        # source='attachments_backup'
        print '\n', 'label:', source, '\n'
        y = tasks.get_attachments
        x = tasks.get_attachments_info(source)
        tasks.close()
        stop = True
        
    if stop == False:
        daysBack = int(time()) - 3 * (24 * 60 * 60)  # 3 days -- in 
        global_list = ['_INBOX', '_INBOX_UNH']
        tasks = gmail_tasks(username, password)
        tasks.clean_global(global_list, daysBack)
        tasks.close()

        updateManager('gmail_tasks.py')
    
    # print str(time.localtime()[3])+':'+str(time.localtime()[4])



