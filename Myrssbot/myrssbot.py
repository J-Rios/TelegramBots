# -*- coding: utf-8 -*-
'''
Script:
    myrss.py
Description:
    Telegram Bot that let you subscribe and follow customs RSS, CDF and ATOM Feeds.
Author:
    Jose Rios Rubio
Creation date:
    23/08/2017
Last modified date:
    06/10/2017
Version:
    1.5.0
'''

####################################################################################################

### Imported modules ###
import re
import logging
from os import path
from copy import copy
from time import sleep, time
from threading import Thread, Lock
from collections import OrderedDict
from feedparser import parse
from telegram import MessageEntity, ParseMode, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, RegexHandler, \
                         ConversationHandler, CallbackQueryHandler
from telegram.error import TelegramError, TimedOut

import TSjson
from constants import CONST, TEXT

####################################################################################################

# Logg stuffs
logger = logging.getLogger(__name__)
hdlr = logging.FileHandler('log.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.DEBUG)

####################################################################################################

### Globals ###
threads = []
lang = 'en'
threads_lock = Lock()
lang_lock = Lock()
tlg_send_lock = Lock()

####################################################################################################

### Class for chats FeedReader threads ###
class CchatFeed(Thread):
    '''Threaded chat feed class to manage each chat FeedReader (Feeds notification)'''

    def __init__(self, args):
        ''' Class constructor'''
        Thread.__init__(self)
        self.chat_id = args[0]
        self.lang = args[1]
        self.bot = args[2]
        self.end = False
        self.lock_end = Lock()


    def get_id(self):
        '''Get thread ID (chat ID)'''
        return self.chat_id


    def finish(self):
        '''Set to finish the thread and stop it execution (called from TLG /disable command)'''
        self.lock_end.acquire()
        self.end = True
        self.lock_end.release()


    def must_finish(self):
        '''Get the finish status of the thread'''
        self.lock_end.acquire()
        end_thread = copy(self.end)
        self.lock_end.release()
        return end_thread

    def run(self):
        '''thread method that run when the thread is launched (thread.start() is call)'''
        # Logging info
        logger.info('- [%s] enabled and running.', self.name)
        # Notify that the FeedReader is enabled
        self.tlg_send_text(TEXT[lang]['FR_ENABLED'], flood_control=False)
        # Initial values of variables
        last_entries = []
        actual_feeds = []
        # Read chat feeds from json file content and determine actual feeds
        feeds = self.read_feeds()
        actual_feeds = self.parse_feeds(feeds)
        # Send the telegram initial feeds message/s
        self.bot_send_feeds_init(actual_feeds)
        # Get all the last entries in a single list
        last_entries = self.get_entries(actual_feeds[:])
        # Get the thread end status
        end_thread = self.must_finish()
        # While not "end" the thread (finish() method call from /disable TLG command)
        while not end_thread:
            # Get the actual time (seconds since epoch)
            init_time = time()
            # Read chat feeds from json file content and determine actual feeds
            feeds = self.read_feeds()
            actual_feeds = self.parse_feeds(feeds)
            # Send the telegram feeds message/s if any change was made in the feeds entries
            change = self.bot_send_feeds_changes(actual_feeds, last_entries)
            # Update last entries
            if change:
                last_entries.clear()
                last_entries = self.get_entries(actual_feeds[:])
            # If the elapsed time in Feeds notifications is less than CONST['T_FEEDS'] minute, wait
            time_elapsed = time() - init_time
            if (time_elapsed < CONST['T_FEEDS']) and (not self.end):
                # Spread wait in 1-second sleeps for manage fast thread end (/disable cmd received)
                for _ in range(0, int(CONST['T_FEEDS'] - time_elapsed) + 1):
                    sleep(1)
                    # Get the thread end status and break if needed
                    end_thread = self.must_finish()
                    if end_thread:
                        break
            # Get the thread end status
            end_thread = self.must_finish()
        # Notify that the FeedReader is disabled
        self.tlg_send_text(TEXT[lang]['FR_DISABLED'], flood_control=False)
        # Logging info
        logger.info('- [%s] disabled and stoped.', self.name)

    ##################################################

    def read_feeds(self):
        '''Read chat feeds from json file content'''
        fjson_chat_feeds = TSjson.TSjson('{}/{}.json'.format(CONST['CHATS_DIR'], self.chat_id))
        chat_feeds = fjson_chat_feeds.read_content()
        return chat_feeds[0]['Feeds']


    def get_entries(self, feeds):
        '''Extract in a single list all entries title of feeds element'''
        all_entries = []
        for feed in feeds:
            for entry in feed['Entries']:
                all_entries.append(entry)
        return all_entries


    def parse_feeds(self, feeds):
        '''Parse all feeds and determine all feed and entries data'''
        actual_feeds = []
        # For each feed
        for feed in feeds:
            # Parse and get feed data
            feedparse = parse(feed['URL'])
            if self.valid_feed(feedparse):
                feed_to_add = {'Title': '', 'URL' : '', 'Entries' : []}
                feed_to_add['Title'] = feedparse['feed']['title']
                feed_to_add['URL'] = feedparse['feed']['link']
                # Determine number of entries to show
                entries_to_show = len(feedparse['entries'])
                # If there is any entry
                if entries_to_show:
                    # For entries to show, get entry data
                    for i in range(entries_to_show-1, -1, -1):
                        if self.valid_entry(feedparse['entries'][i]):
                            entry = {'Title': '', 'Published' : '', 'Summary' : '', 'URL' : ''}
                            entry['Title'] = feedparse['entries'][i]['title']
                            if 'published' in feedparse['entries'][i]:
                                entry['Published'] = feedparse['entries'][i]['published']
                            entry['Summary'] = feedparse['entries'][i]['summary']
                            entry['URL'] = feedparse['entries'][i]['link']
                            # Fix summary text to be allowed by telegram
                            entry['Summary'] = self.html_fix_tlg(entry['Summary'])
                            # Truncate entry summary if it is more than MAX_ENTRY_SUMMARY chars
                            if len(entry['Summary']) > CONST['MAX_ENTRY_SUMMARY']:
                                entry['Summary'] = entry['Summary'][0:CONST['MAX_ENTRY_SUMMARY']]
                                entry['Summary'] = '{}...'.format(entry['Summary'])
                            # Add feed entry data to feed variable
                            feed_to_add['Entries'].append(entry)
                # Add feed data to actual feeds variable
                actual_feeds.append(feed_to_add)
        return actual_feeds


    def bot_send_feeds_init(self, feeds):
        '''Send telegram messages with initial feeds info (all feeds last entry)'''
        # If any feed, for each feed in feeds, if any entry in feed
        if feeds:
            for feed in feeds:
                if feed['Entries']:
                    # Get the last entry and prepare the bot response message
                    last_entry = feed['Entries'][len(feed['Entries']) - 1]
                    feed_titl = '<a href="{}">{}</a>'.format(feed['URL'], feed['Title'])
                    entry_titl = '<a href="{}">{}</a>'.format(last_entry['URL'], \
                            last_entry['Title'])
                    bot_msg = '<b>Feed:</b>\n{}{}<b>Last entry:</b>\n\n{}\n{}\n\n{}'.format( \
                            feed_titl, TEXT[self.lang]['LINE'], entry_titl, \
                            last_entry['Published'], last_entry['Summary'])
                    # Send the message
                    sent = self.tlg_send_html(bot_msg, flood_control=False)
                    if not sent:
                        self.tlg_send_text(bot_msg, flood_control=False)
                else:
                    # Send a message to tell that this feed does not have any entry
                    feed_titl = '<a href="{}">{}</a>'.format(feed['URL'], feed['Title'])
                    bot_msg = '<b>Feed:</b>\n{}{}\n{}'.format(feed_titl, TEXT[self.lang]['LINE'], \
                            TEXT[self.lang]['NO_ENTRIES'])
                    sent = self.tlg_send_html(bot_msg, flood_control=False)
                    if not sent:
                        self.tlg_send_text(bot_msg, flood_control=False)


    def bot_send_feeds_changes(self, actual_feeds, last_entries):
        '''Checks and send telegram feeds message/s if any change was made in the feeds entries'''
        change = False
        for feed in actual_feeds:
            if feed['Entries']:
                for entry in feed['Entries']:
                    # If there is not an entry with that title in last_entries
                    if not self.entry_in_last(entry, last_entries):
                        # Send the telegram message/s
                        feed_titl = '<a href="{}">{}</a>'.format(feed['URL'], feed['Title'])
                        entry_titl = '<a href="{}">{}</a>'.format(entry['URL'], entry['Title'])
                        bot_msg = '{}{}{}\n{}\n\n{}'.format(feed_titl, TEXT[self.lang]['LINE'], \
                                entry_titl, entry['Published'], entry['Summary'])
                        # Debug
                        logger.info('- [%s] New entry:\n%s\n%s\n%s\n%s\n\n', self.name, \
                                entry['Title'], entry['URL'], entry['Published'], entry['Summary'])
                        print('[{}] New entry:\n{}\n{}\n{}\n{}\n'.format(self.name, \
                                entry['Title'], entry['URL'], entry['Published'], entry['Summary']))
                        # Send the message
                        sent = self.tlg_send_html(bot_msg)
                        if not sent:
                            sent = self.tlg_send_text(bot_msg)
                        if sent:
                            change = True
                    if self.end:
                        break
                if self.end:
                    break
        return change

    ##################################################

    def valid_feed(self, feed_parsed):
        '''Check if the given feed is valid (has title and link keys)'''
        valid = False
        if ('title' in feed_parsed['feed']) and ('link' in feed_parsed['feed']):
            valid = True
        return valid


    def valid_entry(self, entry):
        '''Check if the given entry is valid (has title, published, summary and link keys)'''
        valid = False
        if ('title' in entry) and ('summary' in entry) and ('link' in entry):
            valid = True
        return valid


    def entry_in_last(self, entry, last_entries):
        '''Check if an entry is in the last_entries list'''
        # For each entry in lat entries, check if there is any with the same title and url
        for l_entry in last_entries:
            if entry['Title'] == l_entry['Title']:
                if entry['URL'] == l_entry['URL']:
                    #if entry['Summary'] == l_entry['Summary']:
                    return True


    def html_fix_tlg(self, summary):
        '''Remove all anoying HTML tags from entries summary'''
        # Put the input into output
        output = summary
        # Remove every HTML tag
        for tag in CONST['HTML_ANOYING_TAGS']:
            if tag == '<br>' or tag == '<br />':
                output = output.replace(tag, '\n')
            else:
                output = output.replace(tag, '')
            # Remove every HTML more complex structures (i.e. <img> to <img(.*?)>)
            tag_struct = '{}{}{}'.format(tag[:len(tag)-1], '(.*?)', tag[len(tag)-1:])
            output = self.remove_complex_html(tag_struct, output)
        return output


    def remove_complex_html(self, pattern, html_text):
        ''' Remove complex anoying HTML structures'''
        output = html_text
        # Create the pattern element and search for it in the text
        _pattern = re.compile(pattern)
        result = _pattern.search(output)
        # If there is a search result (pattern found)
        if result:
            # Get the to-delete substring and replace it to empty in the original text
            to_del = result.group(0)
            output = output.replace(to_del, '')
            # Try to do it again (recursively, maybe there is more same structures in the text)
            output = self.remove_complex_html(pattern, output)
        # If there is no search result for that pattern, return the modify text
        return output


    def tlg_send_text(self, message, flood_control=True):
        '''Try to send a Telegram text message'''
        sent = False
        # Split the message if it is higher than the TLG message legth limit
        messages = self.split_tlg_msgs(message)
        for msg in messages:
            # Try to send the message with HTML Parsing
            tlg_send_lock.acquire()
            try:
                sent = True
                self.bot.send_message(chat_id=self.chat_id, text=msg)
            # Fail to send the telegram message. Print & write the error in Log file
            except TimedOut:
                pass
            except TelegramError as error:
                sent = False
                logger.error('- %s\n%s\n%s\n\n', error, TEXT[self.lang]['LINE'], msg)
                print('{}\n{}\n{}\n'.format(error, TEXT[self.lang]['LINE'], msg))
            finally:
                # Wait 1s and release the lock. Prevent anti-flood (max 30 msg/s in all chats)
                sleep(1)
                tlg_send_lock.release()
                # Wait 12s. Prevent anti-flood system (max 20 msg/min in same chat)
                if flood_control:
                    sleep(12)
            # If the sent fail, break
            if not sent:
                break
        return sent


    def tlg_send_html(self, message, flood_control=True):
        '''Try to send a Telegram message with HTML content'''
        sent = False
        # Split the message if it is higher than the TLG message legth limit
        messages = self.split_tlg_msgs(message)
        for msg in messages:
            # Try to send the message with HTML Parsing
            tlg_send_lock.acquire()
            try:
                sent = True
                self.bot.send_message(chat_id=self.chat_id, text=msg, parse_mode=ParseMode.HTML)
            # Fail to parse HTML and send telegram message. Print & write the error in Log file
            except TimedOut:
                pass
            except TelegramError as error:
                sent = False
                logger.error('- %s\n%s\n%s\n\n', error, TEXT[self.lang]['LINE'], msg)
                print('{}\n{}\n{}\n'.format(error, TEXT[self.lang]['LINE'], msg))
            finally:
                # Wait 1s and release the lock. Prevent anti-flood (max 30 msg/s in all chats)
                sleep(1)
                tlg_send_lock.release()
                # Wait 12s. Prevent anti-flood system (max 20 msg/min in same chat)
                if flood_control:
                    sleep(12)
            # If send fail
            if not sent:
                # Add an end tag character (>) and try to send the message again
                msg = '{}>'.format(msg)
                tlg_send_lock.acquire()
                try:
                    sent = True
                    self.bot.send_message(chat_id=self.chat_id, text=msg, parse_mode=ParseMode.HTML)
                # Fail to parse HTML and send telegram message. Print & write the error in Log file
                except TimedOut:
                    pass
                except TelegramError as error:
                    sent = False
                    logger.error('- %s\n%s\n%s\n\n', error, TEXT[self.lang]['LINE'], msg)
                    print('{}\n{}\n{}\n'.format(error, TEXT[self.lang]['LINE'], msg))
                finally:
                    # Wait 1s and release the lock. Prevent anti-flood (max 30 msg/s in all chats)
                    sleep(1)
                    tlg_send_lock.release()
                    # Wait 12s. Prevent anti-flood system (max 20 msg/min in same chat)
                    if flood_control:
                        sleep(12)
            # If the sent fail, break
            if not sent:
                break
        return sent


    def split_tlg_msgs(self, text_in):
        '''Function for split a text in fragments of telegram allowed length message'''
        text_out = []
        num_char = len(text_in)
        # Just one fragment if the length of the msg is less than max chars allowed per TLG message
        if num_char <= CONST['TLG_MSG_MAX_CHARS']:
            text_out.append(text_in)
        # Split the text in fragments if the length is higher than max chars allowed by TLG message
        else:
            # Determine the number of msgs to send and add 1 more msg if it is not an integer number
            num_msgs = num_char/float(CONST['TLG_MSG_MAX_CHARS'])
            if isinstance(num_msgs, int) != True:
                num_msgs = int(num_msgs) + 1
            fragment = 0
            # Create the output fragments list of messages
            for _ in range(0, num_msgs, 1):
                text_out.append(text_in[fragment:fragment+CONST['TLG_MSG_MAX_CHARS']])
                fragment = fragment + CONST['TLG_MSG_MAX_CHARS']
        # Return the result text/list-of-fragments
        return text_out

####################################################################################################

### Functions ###
def change_lang(lang_provided):
    '''Function for change the language'''
    global lang
    global lang_lock
    changed = False
    # Lock the lang variable and try to change it
    lang_lock.acquire()
    if lang_provided != lang:
        lang = lang_provided
        changed = True
    # Release the lang variable and return if it was changed
    lang_lock.release()
    return changed


def signup_user(update):
    '''Function for sign-up a user in the system (add to users list file)'''
    # Initial user data for users list file
    usr_data = OrderedDict([])
    # Set user data for users list json file
    usr_data['Name'] = update.message.from_user.name
    usr_data['User_id'] = update.message.from_user.id
    usr_data['Sign_date'] = (update.message.date).now().strftime('%Y-%m-%d %H:%M:%S')
    usr_data['Chats'] = [] # For future uses
    # Create TSjson object for list of users and write on them the data
    fjson_usr_list = TSjson.TSjson(CONST['USERS_LIST_FILE'])
    fjson_usr_list.write_content(usr_data)


def signdown_user(user_id):
    '''Function for sign-down a user from the system (remove from users list file)'''
    # Create TSjson object for list of users and remove the user from content
    fjson_usr_list = TSjson.TSjson(CONST['USERS_LIST_FILE'])
    fjson_usr_list.remove_by_uide(user_id, 'User_id')


def user_is_signedup(user_id):
    '''Function to check if a user is signed-up in the system (if exist in the user list file)'''
    # If users list file exists, search for the user by ID and return if the user is in the file
    signedup = False
    if path.exists(CONST['USERS_LIST_FILE']):
        fjson_usr_list = TSjson.TSjson(CONST['USERS_LIST_FILE'])
        search_result = fjson_usr_list.search_by_uide(user_id, 'User_id')
        if search_result['found']:
            signedup = True
    return signedup


def subscribed(chat_id, feed_url):
    '''Function to check if a chat is already subscribed to the provided feed'''
    # Search for the feed url in chat feeds file and return if the url is in the file
    _subscribed = False
    chat_file = '{}/{}.json'.format(CONST['CHATS_DIR'], chat_id)
    if path.exists(chat_file):
        fjson_chat_feeds = TSjson.TSjson(chat_file)
        subs_feeds = fjson_chat_feeds.read_content()
        if subs_feeds:
            subs_feeds = subs_feeds[0]
            for feed in subs_feeds['Feeds']:
                if feed_url == feed['URL']:
                    _subscribed = True
                    break
    return _subscribed


def any_subscription(chat_id):
    '''Function to know if there is any feed subscription in the chat'''
    # Read users list and determine if there any feed subscription
    any_sub = False
    chat_file = '{}/{}.json'.format(CONST['CHATS_DIR'], chat_id)
    if path.exists(chat_file):
        fjson_chat_feeds = TSjson.TSjson(chat_file)
        subs_feeds = fjson_chat_feeds.read_content()
        if subs_feeds:
            subs_feeds = subs_feeds[0]
            if subs_feeds['Feeds']:
                any_sub = True
    return any_sub


def is_not_active(chat_id):
    '''Function to know if a chat FeedReader thread is running'''
    global threads # Use global variable for active threads
    global threads_lock # Use the global lock for active threads
    thr_actives_id = [] # Initial list of active threads IDs empty
    threads_lock.acquire() # Lock the active threads variable
    for thr_feed in threads: # For each active thread
        if thr_feed.isAlive(): # Make sure that the thread is really active
            thr_actives_id.append(thr_feed.get_id()) # Get the active thread ID
        else: # The thread is dead
            threads.remove(thr_feed) # Remove the thread from active threads variable
    threads_lock.release() # Release the active threads variable lock
    if chat_id in thr_actives_id: # If the actual chat is in the active threads
        is_not_running = False # Is running
    else: # The actual chat is not in the active threads
        is_not_running = True # Not running
    return is_not_running # Return running state


def add_feed(user_id, chat_id, feed_title, feed_url):
    '''Function to add (subscribe) a new url feed to the chat feeds file'''
    # Read user chats and add the actual chat to it
    fjson_usr_list = TSjson.TSjson(CONST['USERS_LIST_FILE'])
    usr_list = fjson_usr_list.read_content()
    for usr in usr_list:
        if usr['User_id'] == user_id:
            usr_chats = usr['Chats']
            if chat_id not in usr_chats:
                usr['Chats'].append(chat_id)
                fjson_usr_list.update(usr, 'User_id')
    # Read chat feeds file and add the new feed url to it
    fjson_chat_feeds = TSjson.TSjson('{}/{}.json'.format(CONST['CHATS_DIR'], chat_id))
    subs_feeds = fjson_chat_feeds.read_content()
    # If there is any feed in the file
    if subs_feeds:
        feed = {}
        feed['Title'] = feed_title
        feed['URL'] = feed_url
        if feed not in subs_feeds:
            subs_feeds = subs_feeds[0]
            subs_feeds['Feeds'].append(feed)
            fjson_chat_feeds.update(subs_feeds, 'Chat_id')
    # If there is no feeds in the file yet
    else:
        feed = {}
        feed['Title'] = feed_title
        feed['URL'] = feed_url
        usr_feeds = OrderedDict([])
        usr_feeds['Chat_id'] = chat_id
        usr_feeds['Feeds'] = [feed]
        fjson_chat_feeds.write_content(usr_feeds)


def remove_feed(chat_id, feed_url):
    '''Function to remove (unsubscribe) a feed from the chat feeds file'''
    # Get the feed title
    feed = {}
    feedpars = parse(feed_url)
    feed['Title'] = feedpars['feed']['title']
    feed['URL'] = feed_url
    # Create TSjson object for feeds of chat file and remove the feed
    fjson_chat_feeds = TSjson.TSjson('{}/{}.json'.format(CONST['CHATS_DIR'], chat_id))
    subs_feeds = fjson_chat_feeds.read_content()
    if subs_feeds:
        subs_feeds = subs_feeds[0]
        subs_feeds['Feeds'].remove(feed)
        fjson_chat_feeds.update(subs_feeds, 'Chat_id')

####################################################################################################

### Received commands handlers ###
def cmd_start(bot, update):
    '''/start command handler'''
    chat_id = update.message.chat_id # Get the chat id
    bot.send_message(chat_id=chat_id, text=TEXT[lang]['START']) # Bot reply


def cmd_help(bot, update):
    '''/help command handler'''
    chat_id = update.message.chat_id # Get the chat id
    bot.send_message(chat_id=chat_id, text=TEXT[lang]['HELP']) # Bot reply


def cmd_commands(bot, update):
    '''/commands command handler'''
    chat_id = update.message.chat_id # Get the chat id
    bot.send_message(chat_id=chat_id, text=TEXT[lang]['COMMANDS']) # Bot reply


def cmd_language(bot, update, args):
    '''/languaje command handler'''
    chat_id = update.message.chat_id # Get the chat id
    if len(args) == 1: # If 1 argument has been provided
        if user_is_signedup(update.message.from_user.id): # If the user is signed-up
            lang_provided = args[0] # Get the language provided (argument)
            if lang_provided == 'en' or lang_provided == 'es': # If language provided is valid
                changed = change_lang(lang_provided) # Change language
                if changed: # Language changed
                    bot_msg = TEXT[lang]['LANG_CHANGE'] # Bot response
                else: # Currently that language is set
                    bot_msg = TEXT[lang]['LANG_SAME'] # Bot response
            else: # Wrong Key provided
                bot_msg = TEXT[lang]['LANG_BAD_LANG'] # Bot response
        else: # The user is not signed-up
            bot_msg = TEXT[lang]['CMD_NOT_ALLOW'] # Bot response
    else: # No argument or more than 1 argument provided
        bot_msg = TEXT[lang]['LANG_NOT_ARG'] # Bot response
    bot.send_message(chat_id=chat_id, text=bot_msg) # Bot reply


def cmd_signup(bot, update, args):
    '''/signup command handler'''
    chat_id = update.message.chat_id # Get the chat id
    if is_not_active(chat_id): # If the FeedReader thread of this chat is not running
        if len(args) == 1: # If 1 argument has been provided
            if not user_is_signedup(update.message.from_user.id): # If the user is not signed-up
                key_provided = args[0] # Get the key provided (argument)
                if key_provided == CONST['REG_KEY']: # If Key provided is the correct and actual one
                    signup_user(update) # Sign-up the user (add-to/create json file)
                    bot_msg = TEXT[lang]['SIGNUP_SUCCESS'] # Bot response
                else: # Wrong Key provided
                    bot_msg = TEXT[lang]['SIGNUP_FAIL'] # Bot response
            else: # The user is alredy signed-up
                bot_msg = TEXT[lang]['SIGNUP_EXIST_USER'] # Bot response
        else: # No argument or more than 1 argument provided
            bot_msg = TEXT[lang]['SIGNUP_NOT_ARG'] # Bot response
    else: # The FeedReader thread of this chat is running
        bot_msg = TEXT[lang]['FR_ACTIVE'] # Bot response
    bot.send_message(chat_id=chat_id, text=bot_msg) # Bot reply


def cmd_signdown(bot, update, args):
    '''/signdown command handler'''
    chat_id = update.message.chat_id # Get the chat ID
    user_id = update.message.from_user.id # Get the user ID
    if is_not_active(chat_id): # If the FeedReader thread of this chat is not running
        if user_is_signedup(user_id): # If the user is signed-up
            if len(args) == 1: # If 1 argument has been provided
                confirmation_provided = args[0] # Get the confirmation provided (argument)
                if confirmation_provided == 'iamsuretoremovemyaccount': # If arg provided is correct
                    signdown_user(user_id) # Sign-down the user
                    bot_msg = TEXT[lang]['SIGNDOWN_SUCCESS'] # Bot response
                else: # Argument confirmation provided not valid
                    bot_msg = TEXT[lang]['SIGNDOWN_CONFIRM_INVALID'] # Bot response
            else: # No argument or more than 1 argument provided
                bot_msg = TEXT[lang]['SIGNDOWN_SURE'] # Bot response
        else: # The user does not have an account yet
            bot_msg = TEXT[lang]['NO_EXIST_USER'] # Bot response
    else: # The FeedReader thread of this chat is running
        bot_msg = TEXT[lang]['FR_ACTIVE'] # Bot response
    bot.send_message(chat_id=chat_id, text=bot_msg) # Bot reply


def cmd_list(bot, update):
    '''/list command handler'''
    bot_msg = 'Actual Feeds in chat:{}'.format(TEXT[lang]['LINE'])
    chat_id = update.message.chat_id # Get the chat ID
    fjson_chat_feeds = TSjson.TSjson('{}/{}.json'.format(CONST['CHATS_DIR'], chat_id)) # Chat file
    chat_feeds = fjson_chat_feeds.read_content() # Read the content of the file
    if chat_feeds:
        chat_feeds = chat_feeds[0]
        # For each feed
        for feed in chat_feeds['Feeds']:
            feed_titl = '<a href="{}">{}</a>'.format(feed['URL'], feed['Title'])
            bot_msg = '{}{}\n\n'.format(bot_msg, feed_titl)
    bot.send_message(chat_id=chat_id, text=bot_msg, parse_mode=ParseMode.HTML)


def cmd_add(bot, update, args):
    '''/add command handler'''
    chat_id = update.message.chat_id # Get the chat ID
    if is_not_active(chat_id): # If the FeedReader thread of this chat is not running
        user_id = update.message.from_user.id # Get the user id
        chat_id = update.message.chat_id # Get the chat id
        if user_is_signedup(user_id): # If the user is sign-up
            if len(args) == 1: # If 1 argument has been provided
                feed_url = args[0] # Get the feed url provided (argument)
                if not subscribed(chat_id, feed_url): # If chat not already subscribed to that feed
                    feed = parse(feed_url) # Get the feedparse of that feed url
                    if feed['bozo'] == 0: # If valid feed
                        feed_title = feed['feed']['title'] # Get feed title
                        add_feed(user_id, chat_id, feed_title, feed_url) # Add to chat feeds file
                        bot_msg = '{}{}'.format(TEXT[lang]['ADD_FEED'], feed_url) # Bot response
                    else: # No valid feed
                        bot_msg = TEXT[lang]['ADD_NO_ENTRIES'] # Bot response
                else: # Already subscribed to that feed
                    bot_msg = TEXT[lang]['ADD_ALREADY_FEED'] # Bot response
            else: # No argument or more than 1 argument provided
                bot_msg = TEXT[lang]['ADD_NOT_ARG'] # Bot response
        else: # The user is not allowed (needs to sign-up)
            bot_msg = TEXT[lang]['CMD_NOT_ALLOW'] # Bot response
    else: # The FeedReader thread of this chat is running
        bot_msg = TEXT[lang]['FR_ACTIVE'] # Bot response
    bot.send_message(chat_id=chat_id, text=bot_msg) # Bot reply


def cmd_remove(bot, update, args):
    '''/remove command handler'''
    chat_id = update.message.chat_id # Get the chat ID
    user_id = update.message.from_user.id # Get the user ID
    if is_not_active(chat_id): # If the FeedReader thread of this chat is not running
        if user_is_signedup(user_id): # If the user is signed-up
            if len(args) == 1: # If 1 argument has been provided
                feed_url = args[0] # Get the feed url provided (argument)
                if subscribed(chat_id, feed_url): # If user is subscribed to that feed
                    remove_feed(chat_id, feed_url) # Remove from chat feeds file
                    bot_msg = TEXT[lang]['RM_FEED'] # Bot response
                else: # No subscribed to that feed
                    bot_msg = TEXT[lang]['RM_NOT_SUBS'] # Bot response
            else: # No argument or more than 1 argument provided
                bot_msg = TEXT[lang]['RM_NOT_ARG'] # Bot response
        else: # The user does not have an account yet
            bot_msg = TEXT[lang]['CMD_NOT_ALLOW'] # Bot response
    else: # The FeedReader thread of this chat is running
        bot_msg = TEXT[lang]['FR_ACTIVE'] # Bot response
    bot.send_message(chat_id=chat_id, text=bot_msg) # Bot reply


def cmd_enable(bot, update):
    '''/enable command handler'''
    global threads # Use global variable for active threads
    global threads_lock # Use the global lock for active threads
    chat_id = update.message.chat_id # Get the chat id
    user_id = update.message.from_user.id # Get the user ID
    if user_is_signedup(user_id): # If the user is signed-up
        if is_not_active(chat_id): # If the actual chat is not an active FeedReader thread
            if any_subscription(chat_id): # If there is any feed subscription
                thr_feed = CchatFeed(args=(chat_id, lang, bot)) # Launch actual chat feeds thread
                thr_feed.name = 'FeedReader {}'.format(chat_id) # Give a thread name with chat ID
                threads_lock.acquire() # Lock the active threads variable
                threads.append(thr_feed) # Add actual thread to the active threads variable
                threads_lock.release() # Release the active threads variable lock
                thr_feed.start() # Launch the thread
            else: # No feed subscription
                bot.send_message(chat_id=chat_id, text=TEXT[lang]['ENA_NOT_SUBS']) # Bot reply
        else: # Actual chat FeedReader thread currently running
            bot.send_message(chat_id=chat_id, text=TEXT[lang]['ENA_NOT_DISABLED']) # Bot reply
    else:
        bot.send_message(chat_id=chat_id, text=TEXT[lang]['CMD_NOT_ALLOW']) # Bot reply


def cmd_disable(bot, update):
    '''/disable command handler'''
    global threads # Use global variable for active threads
    global threads_lock # Use the global lock for active threads
    chat_id = update.message.chat_id # Get the chat id
    user_id = update.message.from_user.id # Get the user ID
    removed = False
    if user_is_signedup(user_id): # If the user is signed-up
        bot_msg = TEXT[lang]['DIS_NOT_ENABLED'] # Bot response
        threads_lock.acquire() # Lock the active threads variable
        for thr_feed in threads: # For each active thread
            if thr_feed.isAlive(): # Make sure that the thread is really active
                if chat_id == thr_feed.get_id(): # If the actual chat is in the active threads
                    thr_feed.finish() # Finish the thread
                    threads.remove(thr_feed) # Remove actual thread from the active threads variable
                    removed = True
        threads_lock.release() # Release the active threads variable lock
    else: # The user is not signed-up
        bot.send_message(chat_id=chat_id, text=TEXT[lang]['CMD_NOT_ALLOW']) # Bot reply
    if not removed: # If the feed was not found enabled
        bot.send_message(chat_id=chat_id, text=bot_msg) # Bot reply

####################################################################################################

### Main function ###
def main():
    ''' Main Function'''
    # Logging info
    logger.info('- Starting Bot, up and running.')
    # Create Bot event handler and get the dispatcher
    updater = Updater(CONST['TOKEN'])
    disp = updater.dispatcher
    # Set the received commands handlers into the dispatcher
    disp.add_handler(CommandHandler("start", cmd_start))
    disp.add_handler(CommandHandler("help", cmd_help))
    disp.add_handler(CommandHandler("commands", cmd_commands))
    disp.add_handler(CommandHandler("language", cmd_language, pass_args=True))
    disp.add_handler(CommandHandler("signup", cmd_signup, pass_args=True))
    disp.add_handler(CommandHandler("signdown", cmd_signdown, pass_args=True))
    disp.add_handler(CommandHandler("list", cmd_list))
    disp.add_handler(CommandHandler("add", cmd_add, pass_args=True))
    disp.add_handler(CommandHandler("remove", cmd_remove, pass_args=True))
    disp.add_handler(CommandHandler("enable", cmd_enable))
    disp.add_handler(CommandHandler("disable", cmd_disable))
    # Start the Bot polling ignoring pending messages (clean=True)
    updater.start_polling(clean=True)
    # Set the bot to idle (actual main-thread stops and wait for incoming messages for the handlers)
    updater.idle()

####################################################################################################

### Execute the main function if the file is not an imported module ###
if __name__ == '__main__':
    main()
