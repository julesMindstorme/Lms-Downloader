from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys  
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select,WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import selenium,sys,os,traceback,glob,shutil,csv
import multiprocessing as mp
from tkinter import *
from tkinter import simpledialog
from tkinter import filedialog
from functools import partial
from tkinter import *
from tkinter.ttk import *




from bs4 import BeautifulSoup
import time
import requests

def getParentPath():
    ParentPath = os.path.join(os.getcwd(), os.pardir)

    while '.app' in os.path.abspath(ParentPath):
        ParentPath = os.path.join(ParentPath, os.pardir)

    ParentPath = os.path.abspath(ParentPath)

    return ParentPath

def ScaleValue(x, in_min, in_max, out_min, out_max):
  return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


UrlSearched = []
def folderSearcher(browser,Folders,Files):
    global baseURL
    global UrlSearched
    NewFolders = []
    founds = []
    baseURL = 'https://www.lelycee.org'

    for _, id, url, _ in Folders:
        if not(url in UrlSearched):
            UrlSearched.append(url)

            browser.get(url)

            soup = BeautifulSoup(browser.page_source, 'html.parser')
            
            FindUrl = []
            
            for folder in soup.findAll('div', id=lambda x: x and x.startswith('fsResourcesGridFolderContainer_')):
                folder= str(folder)

                for e in folder.split('\n'):
                    if 'fsResourcesGridHeader' in e:
                        eltName = e.replace('<div class="fsResourcesGridHeader">','').replace('</div>','')
                        #print(eltName)
                        break

                for e in folder.split(' '):
                    if 'data-rcid' in e:
                        eltId = e.replace('data-rcid=','').replace('"','')
                        #print(eltId)
                        break
                url = url.split('&tab=resources&rgid=')[0]
                NewFolders.append([id,eltId,'{}&tab=resources&rgid={}'.format(url,eltId),eltName]) # ---------------------------------------------------IS THIS THE ANSWER?????-----------------------------
                #Folders.append([id,eltId,'{}&rgid={}'.format(url,eltId),eltName])

            for file in soup.findAll('div'):
                eltUrl, eltName = '',''
                if 'fsResourcesGridItemContainer fsResourcesSortableItem' in str(file):
                    for e in str(file).split(' '):
                        if 'data-resourcelink=' in e:
                            eltUrl = e.replace('data-resourcelink=','').replace('"','')
                    for e in str(file).split('\n'):
                        if '<div class="fsResourcesGridHeader">' in e:
                            eltName = e.replace('<div class="fsResourcesGridHeader">','').replace('</div>','')

                    #print(eltUrl,eltName)
                    #print('\n')
                    if [baseURL+eltUrl,eltName] not in founds:
                        
                        if 'http' in eltUrl: # handle external links:
                            founds.append([eltUrl,eltName])
                        else:
                            founds.append([baseURL+'/'+eltUrl,eltName])

            Files[id] = founds
            founds = []
    return NewFolders,Files
        
def GetFilesLocations(USERNAME, PASSWORD):
    chromeOptions = Options()
    #chromeOptions.headless = True
    chromeOptions.add_argument("--log-level=3")
    chromeOptions.add_argument("--no-sandbox")
    chromeOptions.add_argument("—disable-gpu")
    chromeOptions.add_argument("start-maximized")
    chromeOptions.add_argument("disable-infobars")
    chromeOptions.add_argument("--disable-extensions")

    prefs = {"profile.managed_default_content_settings.images": 2}
    chromeOptions.add_experimental_option("prefs", prefs)

    browser = webdriver.Chrome(ChromeDriverManager().install(),options=chromeOptions)

    browser.get('https://www.lelycee.org/login')

    # try to login

    browser.find_element_by_name('username').clear()
    usernameBox = browser.find_element_by_name('username')
    passwordBox = browser.find_element_by_name('password')

    usernameBox.send_keys(USERNAME)
    passwordBox.send_keys(PASSWORD)

    browser.find_element_by_name("commit").click()


    browser.get('https://www.lelycee.org/groups.cfm')


    soup = BeautifulSoup(browser.page_source, 'html.parser')


    baseURL = 'https://www.lelycee.org'

    classLinks = {}

    FoldersContent = {}

    ClassFolders = {}

    Files = {}

    Folders = []



    if len(soup.findAll(href=True)) != 0:
        for elt in soup.findAll(href=True):
            eltUrl = elt.get('href')
            if '/groups.cfm' in eltUrl and 'groupID' in eltUrl:
                classLinks[eltUrl] = []

    for ClassUrl in classLinks.keys():
        url = baseURL+ClassUrl+'&tab=resources'
        browser.get(url)

        ClassName = browser.find_element_by_xpath('//*[@id="fsGroupSpaceTitle"]').text
        soup = BeautifulSoup(browser.page_source, 'html.parser')
        
        FindUrl = []
        for folder in soup.findAll('div', id=lambda x: x and x.startswith('fsResourcesGridFolderContainer_')):
            folder= str(folder)

            for e in folder.split('\n'):
                if 'fsResourcesGridHeader' in e:
                    eltName = e.replace('<div class="fsResourcesGridHeader">','').replace('</div>','')
                    #print(eltName)
                    break


            for e in folder.split(' '):
                if 'data-rcid' in e:
                    eltId = e.replace('data-rcid="','').replace('"','')
                    #print(eltId)
                    break

                
            FindUrl.append([eltId,'{}&rgid={}'.format(url,eltId),eltName])

        ClassFolders[ClassName] = FindUrl


    for folder in ClassFolders.values():
        founds = []
        for id, url, _ in folder:
            
            browser.get(url)

            soup = BeautifulSoup(browser.page_source, 'html.parser')
            
            FindUrl = []
            
            for folder in soup.findAll('div', id=lambda x: x and x.startswith('fsResourcesGridFolderContainer_')):
                folder= str(folder)

                for e in folder.split('\n'):
                    if 'fsResourcesGridHeader' in e:
                        eltName = e.replace('<div class="fsResourcesGridHeader">','').replace('</div>','')
                        #print(eltName)
                        break

                for e in folder.split(' '):
                    if 'data-rcid' in e:
                        eltId = e.replace('data-rcid=','').replace('"','')
                        #print(eltId)
                        break
                url = url.split('&tab=resources&rgid=')[0]
                Folders.append([id,eltId,'{}&tab=resources&rgid={}'.format(url,eltId),eltName]) # ---------------------------------------------------IS THIS THE ANSWER?????-----------------------------
                #Folders.append([id,eltId,'{}&rgid={}'.format(url,eltId),eltName])

            for file in soup.findAll('div'):
                eltUrl, eltName = '',''
                if 'fsResourcesGridItemContainer fsResourcesSortableItem' in str(file):
                    for e in str(file).split(' '):
                        if 'data-resourcelink=' in e:
                            eltUrl = e.replace('data-resourcelink=','').replace('"','')
                    for e in str(file).split('\n'):
                        if '<div class="fsResourcesGridHeader">' in e:
                            eltName = e.replace('<div class="fsResourcesGridHeader">','').replace('</div>','')

                    #print(eltUrl,eltName)
                    #print('\n')
                    if [baseURL+eltUrl,eltName] not in founds:
                        
                        if 'http' in eltUrl: # handle external links:
                            founds.append([eltUrl,eltName])
                        else:
                            founds.append([baseURL+'/'+eltUrl,eltName])

            Files[id] = founds
            founds = []


    # get all of the files from the sub-sub- folders


    NewFolders = Folders
    while len(NewFolders)!=0:
        NewFolders,Files = folderSearcher(browser,NewFolders,Files)
        Folders+=NewFolders



    #remove duplicates
    for key in Files.keys():
        Keeps = []
        for item in Files[key]:
            if item not in Keeps:
                Keeps.append(item)
        Files[key] = Keeps

    browser.quit()

    return ClassFolders,Folders,Files


def chunks(seq, chunks):
        size = len(seq)
        start = 0
        for i in range(1, chunks + 1):
            stop = i * size // chunks
            yield seq[start:stop]
            start = stop

def Download_And_Place_AllFile(FileDownloadInstructions,USERNAME,PASSWORD,gui):

    MasterDownloads = os.path.join(os.getcwd(), 'Downlads')
    DownloadDir = os.path.join(MasterDownloads,str(mp.current_process().pid))

    if os.path.exists(DownloadDir):
        shutil.rmtree(DownloadDir)
    os.mkdir(DownloadDir)

    chromeOptions = Options()
    #chromeOptions.headless = True
    chromeOptions.add_argument("--log-level=3")
    chromeOptions.add_argument("--no-sandbox")
    chromeOptions.add_argument("—disable-gpu")
    chromeOptions.add_argument("start-maximized")
    chromeOptions.add_argument("disable-infobars")
    chromeOptions.add_argument("--disable-extensions")
    chromeOptions.add_argument("--mute-audio")

    chromeOptions.add_experimental_option('prefs', {
    "download.default_directory": DownloadDir,
    "download.prompt_for_download": False, #To auto download the file
    "download.directory_upgrade": True,
    "plugins.always_open_pdf_externally": True,
    "profile.managed_default_content_settings.images": 1
    })

    
    browser = webdriver.Chrome(ChromeDriverManager().install(),options=chromeOptions)

    browser.get('https://www.lelycee.org/login')

    # try to login

    browser.find_element_by_name('username').clear()
    usernameBox = browser.find_element_by_name('username')
    passwordBox = browser.find_element_by_name('password')

    usernameBox.send_keys(USERNAME)
    passwordBox.send_keys(PASSWORD)

    browser.find_element_by_name("commit").click()

    s = Style()
    s.theme_use("default")
    s.configure("Progressbar", thickness=50)
    progress = Progressbar(gui, orient = HORIZONTAL,length = 100, mode = 'determinate',style="TProgressbar")
    progress.pack()
    gui.update()

    
    for index in range(len(FileDownloadInstructions)):
        url,Destination,Filename = FileDownloadInstructions[index]
        progress['value'] = ScaleValue(index,0,len(FileDownloadInstructions),0,100)
        gui.update()

        try:
            Download_And_Place_File(browser,DownloadDir,url,Destination,Filename)
        except:
            print('BIG ERROR')
            browser.quit()
            
            path = os.path.join(os.getcwd(),'ERRORS.csv')
            with open(path, "a+") as file:
                file.write('\n'+Destination+',' + Filename + ',' + url +','+ 'MAJOR ERROR')

            
            browser = webdriver.Chrome(ChromeDriverManager().install(),options=chromeOptions)

            browser.get('https://www.lelycee.org/login')

            # try to login

            browser.find_element_by_name('username').clear()
            usernameBox = browser.find_element_by_name('username')
            passwordBox = browser.find_element_by_name('password')

            usernameBox.send_keys(USERNAME)
            passwordBox.send_keys(PASSWORD)

            browser.find_element_by_name("commit").click()
    progress.destroy()
    gui.update()

    browser.quit()


def Download_And_Place_File(browser,DownloadDir,url,Destination,Filename):
    if 'jpeg' in url or 'jpg' in url or 'png' in url:
        #if we get a image, wreat it as a jpg even when it isnt
        browser.get(url)
        #r = requests.get(url)
        path = os.path.join(Destination,Filename.replace('/','|')+'.jpg')
        open(path, 'wb').write(browser.find_element_by_xpath('/html').screenshot_as_png)
        return
    
    if 'mp3' in url or 'mp4' in url or 'wav' in url or 'm4v' in url:
        browser.get(url)
        soup = BeautifulSoup(browser.page_source, 'html.parser')
        for video in soup.findAll('source'):
            r = requests.get(video['src'])
            path = os.path.join(Destination,Filename.replace('/','|')+'.'+url[-3:])
            open(path, 'wb').write(r.content)

        return
    if 'www.lelycee.org' in url:
        browser.get(url)
        time.sleep(1) 
        old = time.time()
        start = time.time()
        while len(os.listdir(DownloadDir)) == 0:
            time.sleep(0.1)
            if time.time()-old>7:
                old = time.time()
                browser.get(url)
                time.sleep(2)
            
            if time.time()-start>30:
                print('ERROR Occured')
                path = os.path.join(os.getcwd(),'ERRORS.csv')

                with open(path, "a+") as file:
                    file.write('\n'+Destination+',' + Filename + ',' + url)
                    
                return
            
        
        time.sleep(1)
        
        while '.crdownload' in os.listdir(DownloadDir)[0]:
            time.sleep(0.1)
        
        
        File = os.listdir(DownloadDir)[0]

        Destination = os.path.join(Destination,File)

        File = os.path.join(DownloadDir,File)

        dest = shutil.move(File, Destination)

    else:
        print('URL is external')
        path = os.path.join(Destination,Filename.replace('/','|'))
        with open(path+'.html', "w") as file:
            file.write(ExternalUrlTemplate.format(url))
        
    if len(os.listdir(DownloadDir))!=0:
        for file in os.listdir(DownloadDir):
            path = os.path.join(DownloadDir,file)
            try:
                os.remove(path)
            except:
                ...

# external url template:
ExternalUrlTemplate = '''
<!DOCTYPE html>
<html>
   <head>
      <title>HTML Meta Tag</title>
      <meta http-equiv = "refresh" content = "0; url = {0}" />
   </head>
   <body>
      <p>Redirecting to: {0}</p>
   </body>
</html>
'''

def main(ClassFolders,Folders,Files, USERNAME, PASSWORD):
    #clear ErrorsFile
    path = os.path.join(os.getcwd(),'ERRORS.csv')
    with open(path, "w") as file:
        file.write('Destination'+',' + 'Filename' + ','  + 'url')
        

    HomePath = os.path.join(getParentPath(), 'LMSFolders')
    MasterDownloads = os.path.join(os.getcwd(), 'Downlads')

    if os.path.exists(HomePath):
        #os.rmdir(HomePath)
        shutil.rmtree(HomePath)

    os.mkdir(HomePath)

    if os.path.exists(MasterDownloads):
        #os.rmdir(HomePath)
        shutil.rmtree(MasterDownloads)

    os.mkdir(MasterDownloads)



    # add stage 1 folders
    for Class, ClassData in ClassFolders.items():
        ClassPath = os.path.join(HomePath, Class.replace('/','-'))
        os.mkdir(ClassPath)
        for id, irl, name in ClassData:
            itemPath = os.path.join(ClassPath, id)
            os.mkdir(itemPath)



    # add all of the other folders
    Folder_ReNamingList = []
    AllFolders = []
    for ParentId, FolderId, url, Name in Folders:
        for i in range(10):# maximum folder depth:
            AllFolders += glob.glob(HomePath+'/*/'+'*/'*i)

        for ParentPath in AllFolders:
            if ParentId in ParentPath:
                break
            else:
                ParentPath = None
        if ParentPath!=None:
            NewFolderPath = os.path.join(ParentPath, FolderId)
            RenamedFolderPath = os.path.join(ParentPath, Name.replace('/','|'))
            os.mkdir(NewFolderPath)
            Folder_ReNamingList.append([NewFolderPath,RenamedFolderPath])


    # add all of the files:
    AllFolders = []
    for i in range(10):# maximum folder depth:
        AllFolders += glob.glob(HomePath+'/*/'+'*/'*i)

    FileDownloadInstructions = []
    for parentDirID, fileList in Files.items():
        for folderPath in AllFolders:
            if parentDirID in folderPath:
                break
            else:
                folderPath = None
        if folderPath!=None:
            for fileUrl, fileName in fileList:
                #fileUrl = fileUrl.replace('https://www.lelycee.org','https://www.lelycee.org/')
                FileDownloadInstructions.append([fileUrl,folderPath,fileName])

    # remove duplicates
    FileDownloadInstructions = list(list(element) for element in set(tuple(element) for element in FileDownloadInstructions))

    path = os.path.join(os.getcwd(),'crash.txt')
    with open(path, "w") as file:
        file.write('')

    try:
        Download_And_Place_AllFile(FileDownloadInstructions,USERNAME,PASSWORD,gui)
    except:
        e = traceback.format_exc()
        path = os.path.join(os.getcwd(),'crash.txt')
        with open(path, "w") as file:
            file.write(e)


    #Change all of the folders ID to real name in stage 2 folders:
    for OldNamePath, NewNamePath in Folder_ReNamingList:
        try:
            os.rename(OldNamePath, NewNamePath)
        except:
            print('A downloaded Folder is missing: ',OldNamePath.replace(os.getcwd(),''),'\t||\t',NewNamePath.replace(os.getcwd(),''))


    #Change all of the folders ID to real name in stage 1 folders:
    for Class, ClassData in ClassFolders.items():
        ClassPath = os.path.join(HomePath, Class.replace('/','-'))
        for id, irl, name in ClassData:
            itemPath = os.path.join(ClassPath, id)
            NewItemName = os.path.join(ClassPath, name.replace('/','|'))
            try:
                os.rename(itemPath, NewItemName)
            except:
                print('A downloaded Folder is missing: ',itemPath.replace(os.getcwd(),''),'\t||\t',NewItemName.replace(os.getcwd(),''))


def SetupGui(gui):
    while True:
        USERNAME = simpledialog.askstring("Username", "Enter username:",parent=gui)
        if len(USERNAME)!=0:
            break
    while True:
        PASSWORD = simpledialog.askstring("Password", "Enter password:", show='*',parent=gui)
        if len(PASSWORD)!=0:
            break

    return USERNAME,PASSWORD




if __name__ == "__main__":
    gui = Tk()
    MessageLabel = Label(gui, text = " ")
    MessageLabel.pack()

    
    USERNAME, PASSWORD = SetupGui(gui)
    MessageLabel.config(text = 'The script will now find all of the files on the LMS. A chrome window will open, DO NOT CLOSE IT, it is normal.')
    gui.update()
    for _ in range(3):
        gui.update()

    ClassFolders,Folders,Files = GetFilesLocations(USERNAME, PASSWORD)
    MessageLabel.config(text = "The files will now be downloaded into a folder in the same path as the app")
    
    gui.update()
    for _ in range(3):
        gui.update()

    # HomePath = filedialog.askdirectory(parent=gui,
    #                              initialdir=os.getcwd(),
    #                              title="Please select a folder:")

    main(ClassFolders,Folders,Files,USERNAME, PASSWORD)

    listOfEmptyDirs = [dirpath for (dirpath, dirnames, filenames) in os.walk(os.path.join(getParentPath(), 'LMSFolders')) if len(dirnames) == 0 and len(filenames) == 0]
    if len(listOfEmptyDirs)!=0:
        MessageLabel.config(text = '--- There Are Some Empty Folders, This may indicate an issue --- ')
        
        for EmptyDirs in listOfEmptyDirs:
            text = EmptyDirs.replace(str(getParentPath()),'')
            Label(gui, text = text).pack()

        Label(gui, text = '\n--- There Are Some Empty Folders, This may indicate an issue ---').pack()
        Label(gui, text = 'There are {} empty directory'.format(len(listOfEmptyDirs)))

        Label(gui, text = '\n It is possible that some files did not download correctly, a list of non downloaded files is located in the LMSFolders')
        LMSFoldersPath = os.path.join(getParentPath(), 'LMSFolders')
        
        shutil.move(os.path.join(os.getcwd(),'ERRORS.csv'), os.path.join(LMSFoldersPath,'ERRORS.csv'))
        



        gui.mainloop()




        



