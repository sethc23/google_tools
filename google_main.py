
try:
    from ipdb import set_trace as i_trace   # i_trace()
    # ALSO:  from IPython import embed_kernel as embed; embed()
except:
    pass

class Google:

    def __init__(self,_parent=None,**kwargs):
        from os                             import environ                  as os_environ
        from sys                            import path                     as py_path
        py_path.append(                         os_environ['HOME'] + '/.scripts')
        
        # SEE file_server for latest implementation

        if _parent:            
            self._parent                    =   _parent
            if hasattr(_parent,'T'):
                self.T                      =   _parent.T
            if hasattr(_parent,'PG'):
                self.PG                     =   _parent.PG


        if not _parent or not hasattr(_parent,'T'):
            from System_Control                 import System_Lib
            self.T                          =   System_Lib().T
        else:
            self.T                          =   _parent.T
            from System_Control                 import System_Reporter
            self.Reporter                   =   System_Reporter(self)


        for k in kwargs.keys():
            if k in ['username','pw']:
                self.T.update(                  {k: kwargs[k]})

            if not hasattr(self.T,'username') or not hasattr(self.T,'pw'):
                from __settings__ import default_user,default_pw
                self.username                   =   default_user
                self.pw                         =   default_pw
            else:
                self.username                   =   self.T.username
                self.pw                         =   self.T.pw


        if self.T.config.gmail._has_key('attachments_dir'):
                attachments_path            =   self.T.config.gmail.attachments_dir.replace('~/','%s/' % self.T.os.environ['HOME'])
        else:
            attachments_path                =   self.T.os.environ['HOME'] + '/.gmail/attachments/'
        if not self.T.os.path.exists(           attachments_path):
            self.T.os.mkdir(                    attachments_path)


        self.T                              =   self.T.To_Class_Dict(  self,
                                                                dict_list=[self.T.__dict__,locals()],
                                                                update_globals=True)
        self.Google                         =   self
        self.Voice                          =   self.Voice(self)
        self.Gmail                          =   self.Gmail(self)

    def _get_input(question):
        return raw_input(question)

    class Voice:

        def __init__(self,_parent):

            self                            =   _parent.T.To_Sub_Classes(self,_parent)

            # self._parent                    =   _parent
            # self.T                          =   _parent.T

            # self.Voice                      =   self
            # from googlevoice                import Voice
            # from googlevoice.util           import input
            # self.Voice                      =   Voice()
            # self.Voice.login(                   )

        def _msg(self,phone_num,msg):
            # _out                        =   self.Voice.send_sms(phone_num, msg)
            # assert _out==None
            return

    class Gmail:

        def __init__(self,_parent,**kwargs):
            import                              gmail_client                as GC
            import                              codecs

            self                            =   _parent.T.To_Sub_Classes(self,_parent)
            if hasattr(_parent,'PG'):
                self.PG                     =   _parent.PG
            
            # self._parent                    =   _parent
            # self.T                          =   _parent.T

            all_imports                     =   locals().keys()
            excludes                        =   ['self','_parent']
            new_imports                     =   [it for it in all_imports if not excludes.count(it)]
            for k in new_imports:
                self.T.update(                  {k:locals()[k]} )
            globals().update(                   self.T.__dict__)


        def _run_cmd(cmd):
            p = self.T.sub_popen(cmd,stdout=self.T.sub_PIPE,
                                 shell=True,executable='/bin/zsh')
            (_out,_err) = p.communicate()
            assert _err is None
            return _out.rstrip('\n')

        def _make_pgsql_tbl(self):
            cmd = """
                DROP TABLE IF EXISTS gmail;
                CREATE TABLE gmail
                    (
                        orig_msg jsonb,
                        all_mail_uid bigint,
                        g_msg_id bigint,
                        msg_id text
                    );
                """
            self.T.conn.set_isolation_level(0)
            self.T.cur.execute(cmd)
        def _unix_time(self,dt):
            epoch                       =   self.T.DT.datetime.utcfromtimestamp(0)
            delta                       =   dt - epoch
            return delta.total_seconds()
        def _fetch_msg_grp(self,msgs,grp_size):
            pt                          =   0
            while pt < len(msgs):
                msg_grp                 =   msgs[pt:pt+grp_size]
                res                     =   map(lambda m: m.fetch(),msg_grp)
                yield msg_grp
                pt                     +=   grp_size
        def _get_msg_ids(self,msg):
            if msg['headers'].has_key('Message-ID'):
                return msg['headers']['Message-ID']
            else:
                K                       =   msg['headers'].keys()
                dict_for_lower          =   dict(zip([it.lower() for it in K],K))
                if dict_for_lower.has_key('message-id'):
                    return msg['headers'][dict_for_lower['message-id']]
                else:
                    return 'None'
        def _msg_to_json(self,msg):
            """Cleaning/Adjusting msg contents to fit into JSON serializable"""

            D                           =   msg.__dict__

            D['body']                   =   self.T.codecs.encode(
                                                self.T.codecs.decode(D['body'],'ascii','ignore'),
                                                'ascii','ignore')
            D['html']                   =   self.T.codecs.encode(
                                                self.T.codecs.decode(D['html'],'ascii','ignore'),
                                                'ascii','ignore')

            if D.has_key('attachments'):
                'md5sum -b /home/ub2/.gmail/attachments/%(_key)s | cut -d \  -f1'
                attachment_json         =   []
                for A in msg.attachments:

                    attach_id           =   str(self.T.get_guid().hex)
                    file_dict           =   {'name'           :   A.name,
                                             'size_in_kb'     :   A.size,
                                             'content_type'   :   A.content_type}
                    
                    if A.size > 0:
                        f_path          =   self.T.attachments_path + attach_id
                        A.save(             f_path)
                        file_dict.update(   {'md5' : run_cmd('md5sum -b %s | cut -d \  -f1' % f_path) })
                        saved_size      =   self.T.os.path.getsize(f_path)
                        assert saved_size==A.size

                    AD                  =   dict({  attach_id       : file_dict })
                    attachment_json.append( AD)

                D['attachments']        =   attachment_json
            else:
                del D['attachments']

            items_to_delete             =   ['mailbox','gmail','message']
            for it in items_to_delete:
                if D.has_key(it):
                    del D[it]
            D['sent_at']                =   D['sent_at'] if type(D['sent_at'])==int else int(self._unix_time(msg.sent_at))
            D['_labels']                =   list(D['_labels'])
            D['_flags']                 =   list(D['_flags'])

            ## Confirm all elements of msg object are expected (and will fit into JSON)
        #     for k,v in msg.iteritems():
        #         if ["<type 'str'>","<type 'int'>","<type 'list'>","<type 'dict'>","<type 'NoneType'>"].count(str(type(v)))==0:
        #             print 'unexpected data type in msg class'
        #             raise SystemError

            return self.T.json.dumps(           D, ensure_ascii=False)

        def misc_queries(self):
            a="""
                select *
                from (
                    select
                    --  trim('"' from (orig_msg::json->'uid')::text)::integer _uid,
                    --  trim('"' from (orig_msg::json->'message_id')::text)::bigint _gmail_id,
                    --  to_timestamp((orig_msg::json->'sent_at')::text::double precision) _sent,
                    --  trim('"' from (orig_msg::json->'to'::text)::text) _to,
                    --  trim('"' from (orig_msg::json->'cc'::text)::text) _cc,
                    --  trim('"' from (orig_msg::json->'fr'::text)::text) _fr,
                    --  trim('"' from (orig_msg::json->'subject')::text) _subject,
                    --  orig_msg::json->'attachments' _attachments,
                        orig_msg::json->'_labels' _labels,
                        orig_msg::json->'_flags' _flags,
                        orig_msg
                    from gmail
                ) f1
                --where _sent < date 'May 1, 2007'
                --order by _sent
                limit 5
            """

        def all_mail(self,method='full'):
            """Copy all messages to pgsql@system:gmail"""
            import json as J
            from re import sub as re_sub

            def check_setup(method='full'):

                if method=='full':
                    if not self.PG.F.tables_exists('gmail'):
                        self.PG.F.functions_create_batch_groups(sub_dir='../sql_exts',
                                                                grps=['gmail_tables'],
                                                                files=['1_gmail.sql'])

                elif method=='quick':
                    if not self.PG.F.tables_exists('gmail_chk'):
                        self.PG.F.functions_create_batch_groups(sub_dir='../sql_exts',
                                                                grps=['gmail_tables'],
                                                                files=['2_gmail_chk.sql'])

            def full_sync(msg_num,all_mail_uids,g_msg_ids,msg_ids):

                msgs_as_json            =   map(lambda m: self._msg_to_json(m),msg_grp)

                cmd                     =   unicode("",encoding='utf8',errors='ignore')
                for i in range(msg_num):
                    D                   =   {'orig_msg'     :   msgs_as_json[i],
                                             'all_mail_uid' :   all_mail_uids[i],
                                             'g_msg_id'     :   g_msg_ids[i],
                                             'msg_id'       :   msg_ids[i]}


                    upsert              =   """
                        INSERT into gmail (
                            orig_msg,
                            all_mail_uid,
                            g_msg_id,
                            msg_id
                            )
                        SELECT to_json($txt$%(orig_msg)s$txt$::text)::jsonb,%(all_mail_uid)s,%(g_msg_id)s,'%(msg_id)s'
                        FROM
                            (
                            SELECT array_agg(all_mail_uid) all_uids FROM gmail
                            ) as f1,
                            (
                            SELECT array_agg(g_msg_id) all_g_m_ids FROM gmail
                            ) as f2
                            -- msg_id ignored as sampling showed such value was not unique to each msg
                            -- (
                            -- SELECT array_agg(msg_id) all_m_ids FROM gmail
                            -- ) as f3
                        WHERE
                            (
                                not all_uids @> array['%(all_mail_uid)s'::bigint]
                            AND not all_g_m_ids @> array['%(g_msg_id)s'::bigint]
                            --AND not all_m_ids @> array['%(msg_id)s'::text]
                            )
                        OR
                            (
                               all_uids is null
                            OR all_g_m_ids is null
                            --OR all_m_ids is null
                            )
                        ;
                        """
                    _out                =   upsert % D
                    _out                =   re_sub(r'[^\x00-\x7F]+',' ', _out)
                    cmd                +=   unicode(self.T.codecs.encode(_out,'ascii','ignore'),errors='ignore')
                    # cmd                +=   unicode(upsert,errors='ignore') if type(upsert) is not unicode else upsert


                self.T.conn.set_isolation_level(0)
                self.T.cur.execute(         cmd)

            def quick_sync(msg_num,all_mail_uids,g_msg_ids,msg_ids):
                cmd                     =   unicode("",encoding='utf8',errors='ignore')
                for i in range(msg_num):
                    D                   =   {'all_mail_uid' :   all_mail_uids[i],
                                             'g_msg_id'     :   g_msg_ids[i],
                                             'msg_id'       :   msg_ids[i],
                                             'UPDATE_TABLE' :   'gmail_chk'}


                    upsert              =   """
                        INSERT into %(UPDATE_TABLE)s (
                            all_mail_uid,
                            g_msg_id,
                            msg_id
                            )
                        SELECT %(all_mail_uid)s,%(g_msg_id)s,'%(msg_id)s'
                        FROM
                            (
                            SELECT array_agg(all_mail_uid) all_uids FROM %(UPDATE_TABLE)s
                            ) as f1,
                            (
                            SELECT array_agg(g_msg_id) all_g_m_ids FROM %(UPDATE_TABLE)s
                            ) as f2
                            -- msg_id ignored as sampling showed such value was not unique to each msg
                            -- (
                            -- SELECT array_agg(msg_id) all_m_ids FROM %(UPDATE_TABLE)s
                            -- ) as f3
                        WHERE
                            (
                                not all_uids @> array['%(all_mail_uid)s'::bigint]
                            AND not all_g_m_ids @> array['%(g_msg_id)s'::bigint]
                            )
                        OR
                            (
                               all_uids is null
                            OR all_g_m_ids is null
                            );
                        """
                    _out                =   upsert % D
                    _out                =   re_sub(r'[^\x00-\x7F]+',' ', _out)
                    cmd                +=   unicode(self.T.codecs.encode(_out,'ascii','ignore'),errors='ignore')
                    # cmd                +=   unicode(upsert,errors='ignore') if type(upsert) is not unicode else upsert


                self.T.conn.set_isolation_level(0)
                self.T.cur.execute(         cmd)

            start                       =   self.T.time.time()

            g                           =   self.T.GC.login(self.T.config.gmail.username, 
                                                            self.T.config.gmail.pw)
            all_mail                    =   g.all_mail().mail()

            check_setup(                    method)

            # START PROCESSING FROM WHERE PREVIOUS PROCESSING ENDED
            df                          =   self.T.pd.DataFrame(data={'msg':all_mail})
            df['g_uid']                 =   df.msg.map(lambda m: int(m.uid))

            if method=='full':
                UPDATE_TABLE            =   'gmail'
                UPDATE_COUNT            =   25
            elif method=='quick':
                UPDATE_TABLE            =   'gmail_chk'
                UPDATE_COUNT            =   500

            qry                         =   "select all_mail_uid from %s" % UPDATE_TABLE
            pdf                         =   self.T.pd.read_sql(qry,self.T.eng)
            pg_all_mail_uids            =   pdf.all_mail_uid.tolist()

            df['skip']                  =   df.g_uid.isin(pg_all_mail_uids)

            remaining_msgs              =   df[df.skip==False].msg.tolist()

            M                           =   self._fetch_msg_grp(remaining_msgs,UPDATE_COUNT)

            while True:
                try:
                    msg_grp             =   M.next()
                except StopIteration:
                    break
                msg_num                 =   len(msg_grp)
                msgs_as_dict            =   map(lambda m: m.__dict__,msg_grp)
                all_mail_uids           =   map(lambda m: m.uid, msg_grp)
                g_msg_ids               =   map(lambda m: int(m['message_id']),msgs_as_dict)
                msg_ids                 =   map(lambda m: self._get_msg_ids(m),msgs_as_dict)

                if method=='full':
                    full_sync(msg_num,all_mail_uids,g_msg_ids,msg_ids)
                elif method=='quick':
                    quick_sync(msg_num,all_mail_uids,g_msg_ids,msg_ids)

            end                         =   self.T.time.time()
            print 'total time (seconds):',end-start

        def create_account(self,**kwargs):
            """ Keyword Args:
                    first_name,last_name,
                    user_name,password,
                    recovery_phone,recovery_email
            """

            def setup_account_info():
                # SETUP VARS WITH ACCOUNT INFO
                account_info_dict           =   {'first_name'               :   'FirstName',
                                                 'last_name'                :   'LastName',
                                                 'user_name'                :   'GmailAddress',
                                                 'password'                 :   'Passwd',
                                                 'recovery_phone'           :   'RecoveryPhoneNumber',
                                                 'recovery_email'           :   'RecoveryEmailAddress'}
                account_info_keys           =   account_info_dict.keys()
                T                           =   {}

                if hasattr(self.T,'id') and hasattr(self.T.id,'details'):
                    for k,v in self.T.id.details.__dict__.iteritems():
                        T.update(               {k.strip('_')               :   v})
                        kwargs.update(          {k.strip('_')               :   v})

                for k,v in kwargs.iteritems():
                    if account_info_keys.count(k):
                        T.update(               {account_info_dict[k]       :   v})

                # FILL IN ANY MISSING INFO

                if not T.has_key('FirstName') or not T.has_key('LastName'):
                    g                       =   self.T.randrange(0,2)
                    gender                  =   'Female' if g==0 else 'Male'
                    name                    =   self.T.Identity.F.name_female() if g==0 else self.T.Identity.F.name_male()
                    while len(name.split())!=2:
                        name                =   self.T.Identity.F.name_female() if g==0 else self.T.Identity.F.name_male()
                    first,last              =   name.split()
                    T.update(                   {'FirstName':first,'LastName':last,'gender_num':g,'gender':gender})

                if not T.has_key('GmailAddress'):
                    _user                   =   str(self.T.get_guid().hex)[:10]
                    _pw                     =   str(self.T.get_guid().hex)
                    T.update(                   {'GmailAddress':_user,'Passwd':_pw,'PasswdAgain':_pw})

                T.update(                       {'birth_month'              :   self.T.randrange(1,13),
                                                 'BirthDay'                 :   self.T.randrange(1,29),
                                                 'BirthYear'                :   self.T.randrange(1925,1990)})
                birth_month_dict            =   {10:'a',11:'b',12:'c'}
                if birth_month_dict.keys().count(T['birth_month']):
                    T['birth_month']        =   birth_month_dict[ T['birth_month'] ]

                if not T.has_key('RecoveryPhoneNumber'):
                    T.update(                   {'RecoveryPhoneNumber'      :   '6177024233'})

                if not T.has_key('RecoveryEmailAddress'):
                    T.update(                   {'RecoveryEmailAddress'     :   'a2547e2@mail.com'})

                return T

            if not hasattr(self,'T'):
                self.T.py_path.append(          self.T.os_environ['BD'] + '/real_estate/autoposter')
                from auto_poster            import Auto_Poster
                AP                          =   Auto_Poster(None,no_identity=True)
                self.T.update(                  {'Identity'             :   AP.Identity})
                self.T.update(                  AP.T.__getdict__())

            T                               =   setup_account_info()
            self.T.excluded_defaults        =   ['user-agent','no_java']
            self.T.br                       =   self.T.scraper('chrome',dict=self.T).browser
            start_page                      =   ''.join(['https://accounts.google.com/SignUp?',
                                                         'continue=https%3A%2F%2Fwww.google.com%2F%3Fgws_rd%3Dssl&hl=en'])
            self.T.br.open_page(                start_page)
            self.T.br.wait_for_page(            )

            min_wait                        =   4

            form_parts                      =   ['FirstName','LastName','GmailAddress','Passwd','PasswdAgain']
            for it in form_parts:
                self.T.br.click_element_id_and_type(it,T[it])
                self.T.delay(                   self.T.randrange(min_wait,10))


            self.T.br.window.find_element_by_xpath('//*[@id=":0"]').click()
            self.T.delay(                       self.T.randrange(min_wait+3,min_wait+9))
            self.T.br.window.find_element_by_xpath('//*[@id=":%(birth_month)s"]' % T).click()
            self.T.delay(                       self.T.randrange(min_wait,9))

            form_parts                      =   ['BirthDay','BirthYear']
            for it in form_parts:
                self.T.br.click_element_id_and_type(it,T[it])
                self.T.delay(                   self.T.randrange(min_wait,10))

            # Gender
            self.T.br.window.find_element_by_xpath('//*[@id=":d"]').click()        # Menu
            if T['gender_num']==0:
                self.T.br.window.find_element_by_xpath('//*[@id=":e"]').click()    # Female
            else:
                self.T.br.window.find_element_by_xpath('//*[@id=":f"]').click()    # Male

            # Phone // Current Email
            self.T.br.click_element_id_and_type('RecoveryPhoneNumber',T['RecoveryPhoneNumber'])
            self.T.delay(                       self.T.randrange(min_wait,10))
            self.T.br.click_element_id_and_type('RecoveryEmailAddress',T['RecoveryEmailAddress'])
            self.T.delay(                       self.T.randrange(min_wait,10))

            # CAPTCHA
            self.T.br.zoom(                     '200%')
            start_size                      =   self.T.br.window.get_window_size()
            self.T.br.window.set_window_size(   630,280)
            K                               =   self.T.br.window.find_element_by_id('recaptcha_challenge_image')
            start_location                  =   self.T.br.window.get_window_position()
            self.T.br.scroll_to_element(        "recaptcha_challenge_image")
            self.T.br.post_screenshot(          )
            self.T.br.window.set_window_size(   start_size['width'],start_size['height'])
            self.T.br.zoom(                     '100%')

            # Communicate CAPTCHA
            self.T.update(                      {'line_no'                  :   self.T.I.currentframe().f_back.f_lineno})
            self._parent.Reporter._growl(       '%(line_no)s GOOG@%(user)s<%(guid)s>: NEED CAPTCHA' % self.T,
                                                'http://sys.sanspaper.com/tmp/phantomjs.html' )

            # Receive & Enter Input
            captcha_input                   =   get_input("Captcha code?\n")
            self.T.br.click_element_id_and_type('recaptcha_response_field',captcha_input)

            # VERIFY INFORMATION
            most_vars_inputted              =   ['FirstName','LastName','GmailAddress',
                                                 'BirthDay','BirthYear','RecoveryPhoneNumber','RecoveryEmailAddress']
            for it in most_vars_inputted:
                assert self.T.br.get_element_id_val(it) == str(T[it])
            month_dict                      =   {1:'January',2:'February',3:'March',4:'April',5:'May',6:'June',
                                                 7:'July',8:'August',9:'September','a':'October','b':'November','c':'December'}
            assert self.T.br.window.find_element_by_xpath('//*[@id=":0"]').text == month_dict[ T['birth_month'] ]
            gender_dict                     =   { 0:'Female',1:'Male'}
            assert self.T.br.window.find_element_by_xpath('//*[@id=":d"]').text == gender_dict[ T['gender_num'] ]

            self.T.br.scroll_and_click_id(      "TermsOfService")
            self.T.br.scroll_and_click_id(      "submitbutton")
            self.T.br.wait_for_page(            )

            # IF ASKED TO 'Verify your account'
            if self.T.br.source().count('Verify your account'):
                assert self.T.br.get_element_id_val('signupidvinput') == str(T['RecoveryPhoneNumber'])
                self.T.br.scroll_and_click_id(  'signupidvmethod-voice')
                self.T.br.scroll_and_click_id(  'next-button')
                self.T.br.wait_for_page(        )
                if self.T.br.source().count('This phone number cannot be used for verification.'):
                    print 'Verification Error'
                    i_trace()
                    a=0
                    raise SystemExit

            # COPY USER_DATA_DIR TO IDENTITIES
            cmds                            =   ['cp -r %s %s;' % ( self.T.br.window_cfg['user-data-dir'].rstrip('/'),
                                                                    self.T.br.window_cfg['SAVE_DIR'].rstrip('/'))]
            (_out,_err)                     =   self.T.exec_cmds(cmds)
            assert not _out
            assert _err is None

            # UPDATE COOKIES
            self.T.br.update_cookies(           )

            T['guid']                       =   T['GmailAddress']
            T['email']                      =   T['GmailAddress'] + '@gmail.com'
            T['pw']                         =   T.pop('Passwd')
            details                         =   {'_name'                :   '%s %s' % (T['FirstName'],T['LastName']),}
            details.update(                     {'_recovery_phone'      :   T['RecoveryPhoneNumber'],})
            details.update(                     {'_recovery_email'      :   T['RecoveryEmailAddress'],})
            birth_month_dict                =   {10:'a',11:'b',12:'c'}
            birth_month_dict_rev            =   dict(zip(birth_month_dict.values(),birth_month_dict.keys()))
            T['birth_month']                =   T['birth_month'] if not birth_month_dict_rev.has_key(T['birth_month']) else birth_month_dict_rev[T['birth_month']]
            details.update(                     {'_birthday'            :   '%04d.%02d.%02d' % (int(T['BirthYear']),
                                                                                                int(T['birth_month']),
                                                                                                int(T['BirthDay'])),})
            details.update(                     {'_gender'              :   gender_dict[ T['gender_num'] ],})
            T['details']                    =   self.T.json.dumps(details)

            qry                             =   """ INSERT INTO identities (guid,email,pw,details)
                                                    VALUES ('%(guid)s','%(email)s','%(pw)s','%(details)s'::jsonb) """ % T
            self.T.conn.set_isolation_level(    0)
            self.T.cur.execute(                 qry)

            i_trace()

            ## CONFIGURE ACCOUNT
            # 25ebeab2ff@gmail.com
            # fcc836b996044605a0d6ef16318706aa
            #
            # rec_email:a2547e2@mail.com
            # rec_phone:(617) 702-4233
            #
            # //*[@id="close-button"] -- click
            #
            # https://mail.google.com/mail/u/1/#settings/fwdandpop -- open
            #
            # //*[@id=":45"]/input -- click
            #
            # //*[@id=":4c"] -- paste  a2547e2@mail.com
            # /html/body/div[30]/div[3]/button[1] --click





