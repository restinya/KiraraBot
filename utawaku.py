from __future__ import unicode_literals
import youtube_dl
import threading
import os
import time
import requests
import pickle
import base64
import httplib2
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload
from tabulate import tabulate
from oauth2client.service_account import ServiceAccountCredentials

from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

#what do we want:
#scrape certain channels (suisui, ppt, rushia, etc) for utawaku streams
#accept input from discord servers to process in case missed/asleep/not on list

#======Global stuffs========
scopes = ['https://www.googleapis.com/auth/drive.metadata.readonly',
          'https://www.googleapis.com/auth/drive.file',
          'https://www.googleapis.com/auth/youtube.force-ssl']

url = ['https://www.googleapis.com/upload/drive/v3/files?uploadType=resumable']
id ='suichanwaaaa@karaoke-waaaaai.iam.gserviceaccount.com'
key = base64.b64decode(open("configs\private_key.json", "r").read())

# creds = Credentials.from_json_keyfile_name('client_secrets.json', scopes)
# service = build('drive', 'v2', credentials=creds)

g_login = GoogleAuth()
#g_login.creds = creds
g_login.LoadCredentialsFile('configs\mycreds.txt')

if g_login.credentials is None:
    g_login.LocalWebserverAuth()
elif g_login.access_token_expired:
    g_login.Refresh()
else:
    g_login.Authorize()

g_login.SaveCredentialsFile('configs\mycreds.txt')
drive = GoogleDrive(g_login)
folder_id = ['1eAnQD9mV0xhqaMVoeSGA06NrU1R6ik7Y']
channel_ids = ['UC5CwaMl1eIgY8h02uZw7u8A','UCl_gCybOJRIgOXw6Qb4qJzQ']

#====polling loop for youtube; update manually for now.====
def poll_loop(channel_id):
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = "configs/client_secrets.json"

    # Get credentials and create an API client
    credentials = ServiceAccountCredentials.from_json_keyfile_name(client_secrets_file, scopes)
    # flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
    #     client_secrets_file, scopes)
    # credentials = flow.run_console()
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials)

    request = youtube.search().list(
        part="snippet",
        channelId=channel_id,
        eventType="live",
        order="date",
        maxResults=25,
        type="video",
        q="歌枠 | カラオケ"
    )

    print("Checking for new VODs...")
    response = request.execute()
    #if "歌" in response['items'][0]['snippet']['title'] or "カラオケ" in response['items'][0]['snippet']['title']:
    #    return False
    if response['items']:
        return response['items'][0]['id']['videoId']
    else:
        return False

class Logger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)

#=====multithread drifting=====
# class youtubeThread(threading.Thread):
#     def __init__(self, threadID, channel):
#         threading.Thread.__init__(self)
#         self._threadID = threadID
#         self._channel = channel
    
#     def run(self):
#         print("Starting for channel " + self._channel)
#         youtube_loop(self._channel)


def my_hook(d):
    if d['status'] == 'finished':
        print(d)
        print('Done downloading, now converting.')
        return d['filename']

ydl_opts_archive = {
    'format': 'bestaudio/best[height<=480]',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'download_archive': 'configs\Downloaded.txt',
    'logger': Logger(),
    'progress_hooks': [my_hook],
    'nooverwrites': True
}

ydl_opts_on_demand = {
    'format': 'bestaudio/best[height<=480]',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'logger': Logger(),
    'progress_hooks': [my_hook],
    'nooverwrites': True
}

def dl_audio(url):
    with youtube_dl.YoutubeDL(ydl_opts_archive) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)

def dl_on_demand(url):
    with youtube_dl.YoutubeDL(ydl_opts_on_demand) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)

def get_gdrive_service():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                'client_secrets.json', scopes)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    # return Google Drive API service
    return googleapiclient.discovery.build('drive', 'v3', credentials=creds)

service = get_gdrive_service()

def make_folder():
    folder_metadata = {
        "name": "Karaoke Archive",
        "mimeType": "application/vnd.google-apps.folder"
    }
    folder = service.files().create(body=folder_metadata, fields='id').execute()
    print('Folder creation success!')
    print('Folder ID:', folder.get('id'))
    return folder.get('id')

#filename = title, source = path, folder_id given; id of karaoke archive
def up(filename, dest_folder_id=folder_id):
    service = get_gdrive_service()
    file_metadata = {
        'name': filename,
        'parents': [dest_folder_id],
        'mimeType': 'audio/mpeg'
    }
    media = MediaFileUpload(
        filename,
        mimetype='audio/mpeg'
    )
    user_permission = {
    'type': 'anyone',
    'role': 'reader',
}

    if check_file(filename) is False:
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id').execute()
        file_id = file.get('id')
        print('Uploaded!')
        print('File ID:', file_id)
        service.permissions().create(
            fileId=file_id,
            body=user_permission,
            fields='id',
        ).execute()
        return file_id
    else:
        print('File already exists as', filename)



#couldnt find one for files... check to see if folder check works for files
def check_file(filename):
    results = service.files().list(q="mimeType='audio/mpeg' and name='"+filename+"' and trashed = false", fields="nextPageToken, files(id,name)").execute()
    items = results.get('files', [])
    if items:
        return True
    else:
        return False

def youtube_loop(channel_id):
    #while True:
        newStream = poll_loop(channel_id)
        if newStream:
            return channel_id
        else:
            return False

def archive_audio(channel_id):
    while True:
        if youtube_loop(channel_id):
            new_file = dl_audio(channel_id)
            fixed_fname = new_file.split('.')[0]+'.mp3'
            file_id = up(fixed_fname)
            os.remove(fixed_fname)
            print('Uploaded file to {url}'.format(url='https://drive.google.com/open?id=' + file_id.get('id')))
        else:
            time.sleep(300 - time.time() % 300)

def download_audio(video_id):
    new_file = dl_on_demand(video_id)
    fixed_fname = new_file.split('.')[0]+'.mp3'
    return fixed_fname

# def test_archive(x):
#     new_file = dl_audio(x)
#     fixed_fname = new_file.split('.')[0]+'.mp3'
#     file_id = up(fixed_fname)
#     print(file_id)
#     os.remove(fixed_fname)
#     print('Uploaded file to {url}'.format(url='https://drive.google.com/open?id=' + file_id))

# def test_download(x):
#     new_file = dl_on_demand(video_id)
#     fixed_fname = new_file.split('.')[0]+'.mp3'
#     return fixed_fname
# test_function('https://www.youtube.com/watch?v=5yDNEmcKQFY')