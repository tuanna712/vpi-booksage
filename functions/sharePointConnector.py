#import necessary libraries
import os
from office365.sharepoint.client_context import ClientContext
from office365.runtime.auth.client_credential import ClientCredential
from dotenv import load_dotenv
load_dotenv()

class DatabaseLink():
    def  __init__(self, username):
        self.username = username
        self.site_url = os.environ['SHAREPOINT_SITE']
        self.client_id= os.environ['SHAREPOINT_CLIENT_ID']
        self.client_secret = os.environ['SHAREPOINT_CLIENT_SECRET']
        self.ctx = ClientContext(self.site_url).with_credentials(ClientCredential(self.client_id, self.client_secret))
        self.parent_url = os.environ['SHAREPOINT_PARENT_URL']
        self.user_url = self.parent_url + self.username
        self.local_path = os.getcwd() + '/' + os.environ['LOCAL_DATABASE_PATH'] + self.username
        os.makedirs(os.path.dirname(self.local_path), exist_ok=True)

    def check_folder_existed(self, folder_url):
        child_folder = os.path.basename(folder_url)
        parent_folder = os.path.dirname(folder_url)
        try:
            self.ctx.web.get_folder_by_server_relative_url(folder_url).get().execute_query()
            print(f'Folder {folder_url} existed')
        except:
            self.ctx.web.get_folder_by_server_relative_url(parent_folder).folders.add(child_folder).execute_query()
            print(f'Folder {folder_url} created')
    
    def upload_overwrite(self):
        # Check if user folder existed in server then create if not
        self.check_folder_existed(self.user_url)
        
        # Call all folders in local path
        self.local_folders_list()
        def component_len(s):
            return len(s.split('/'))
        self.local_folders.sort(key=component_len)
        
        # Convert local path to server relative url
        self.sever_folders_list = []
        for _ in self.local_folders:
            self.sever_folders_list.append(_.replace(self.local_path, self.user_url))
            
        # Check if folder existed in server then create if not
        for folder in self.sever_folders_list:
            self.check_folder_existed(folder)
        
        #Upload all local files to sever
        self.upload_files()
        
    def check_and_create_folder(self, folder_path):
        if not os.path.exists(folder_path):
            os.makedirs(folder_path, exist_ok=True)
            print(f"Folder '{folder_path}' created successfully.")
        else:
            print(f"Folder '{folder_path}' already exists.")
            
    def download_overwrite(self):
        file_urls = self.sever_files_list()
        for f_url in file_urls:
            local_path = f_url.replace(self.user_url, self.local_path)
            self.check_and_create_folder(os.path.dirname(local_path))
            # Download all files
            with open(local_path, "wb") as f:
                file = self.ctx.web.get_file_by_server_relative_url(f_url)
                file.download(f)
                self.ctx.execute_query()
            print('Downloaded file: ', os.path.basename(local_path))
        pass
    
    def local_folders_list(self):
        self.local_folders = []
        for root, dirs, files in os.walk(self.local_path):
            for dir in dirs:
                self.local_folders.append(os.path.join(root, dir))

    def files_in_local_folder(self, folder_url):
        _files_list = []
        for root, dirs, files in os.walk(folder_url):
            for file in files:
                _files_list.append(os.path.join(root, file))
        return _files_list
    
    def sever_files_list(self):
        # Level 0: Get all folders and files in user_url
        folder_urls, file_urls = self.get_objects(self.user_url)
        # Level 1: Get all folders and files in sub-folders
        folder_urls_1 = []
        for folder1 in folder_urls:
            folder_urls_lv1, _file_urls1 = self.get_objects(folder1)
            folder_urls_1.extend(folder_urls_lv1)
            file_urls.extend(_file_urls1)
        
        # Level 2: Get all folders and files in sub-sub-folders
        folder_urls_2 = []
        for folder2 in folder_urls_1:
            folder_urls_lv2, _file_urls2 = self.get_objects(folder2)
            folder_urls_2.extend(folder_urls_lv2)
            file_urls.extend(_file_urls2)
            
        # Level 3: Get all folders and files in sub-sub-sub-folders
        folder_urls_3 = []
        for folder3 in folder_urls_2:
            folder_urls_lv3, _file_urls3 = self.get_objects(folder3)
            folder_urls_3.extend(folder_urls_lv3)
            file_urls.extend(_file_urls3)
            
        return file_urls
        
    def upload_files(self):
        _file_path = self.files_in_local_folder(self.local_path)
        _file_path = [p for p in _file_path if not p.endswith('.DS_Store')]
       
        for _path in _file_path:
            _target_site = os.path.dirname(_path.replace(self.local_path, self.user_url))
            _target_folder = self.ctx.web.get_folder_by_server_relative_url(_target_site)
            with open(_path, 'rb') as f:
                _target_folder.files.upload(file_name=os.path.basename(_path), content=f).execute_query()
            print(f'File {os.path.basename(_path)} uploaded')
    
    def get_objects(self, root_url):
        #Get Folder from server
        _source = self.ctx.web.get_folder_by_server_relative_url(root_url)
        #Get Sub-folders
        folders = _source.folders
        self.ctx.load(folders).execute_query()
        
        #Get files in the current folder
        files = _source.files
        self.ctx.load(files).execute_query()
        
        #Get URLs
        folder_urls = []; file_urls = []
        for folder in folders:
            folder_urls.append(folder.properties['ServerRelativeUrl'] + '/')
        for file in files:
            file_urls.append(file.properties['ServerRelativeUrl'])
        
        return folder_urls, file_urls

# DatabaseLink('tuanna712').download_overwrite()