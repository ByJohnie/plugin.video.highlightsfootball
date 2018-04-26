# -*- coding: utf-8 -*-
#Библиотеки, които използват python и Kodi в тази приставка
import re
import sys
import os
import urllib
import urllib2
import xbmc, xbmcplugin,xbmcgui,xbmcaddon
import urlresolver
import urlparse
#Място за дефиниране на константи, които ще се използват няколкократно из отделните модули
__addon_id__= 'plugin.video.highlightsfootball'
__Addon = xbmcaddon.Addon(__addon_id__)
searchicon = xbmc.translatePath(__Addon.getAddonInfo('path') + "/resources/search.png")

MUA = 'Mozilla/5.0 (Linux; Android 5.0.2; bg-bg; SAMSUNG GT-I9195 Build/JDQ39) AppleWebKit/535.19 (KHTML, like Gecko) Version/1.0 Chrome/18.0.1025.308 Mobile Safari/535.19' #За симулиране на заявка от мобилно устройство
UA = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/58.0' #За симулиране на заявка от  компютърен браузър


#Меню с директории в приставката
def CATEGORIES():
        addDir('Search','https://highlightsfootball.com/?s=',2,searchicon)
        baseurl = 'https://highlightsfootball.com/'
        req = urllib2.Request(baseurl)
        req.add_header('User-Agent', UA)
        response = urllib2.urlopen(req)
        data = response.read()
        response.close()
        match = re.compile('category menu-item-\d+"><a href="(.+?category.+?)">(.+?)</a></li>').findall(data)
        for link, tit in match:
         addDir(tit, link, 1, 'DefaultFolder.png')


#Разлистване видеата на първата подадена страница
def INDEXPAGES(url):
        req = urllib2.Request(url)
        req.add_header('User-Agent', UA)
        response = urllib2.urlopen(req)
        #print 'request page url:' + url
        data=response.read()
        response.close()

        #Начало на обхождането
        br = 0 #Брояч на видеата в страницата - 24 за този сайт
        match = re.compile('><a href="(.+?)" rel.+?title="(.+?)".*src="(.+?)".*\n.+?datetime.+?>(.+?)<').findall(data)
        for link,zaglavie,kartinka,dobaven in match:
            desc = dobaven
            addLink(zaglavie,link,3,dobaven,kartinka)
            br = br + 1
            print 'Items counter: ' + str(br)
        if br == 15: #тогава имаме следваща страница и конструираме нейния адрес
            matchp = re.compile('<span class="current">1</span><a href="(.+?)/page/(.+?)/').findall(data)
            for baseurl,numb in matchp:
             number = 0
             page = int(number)
             currentDisplayCounter = page + int(numb)
             url = baseurl + '/page/' + str(currentDisplayCounter) + '/'
             print 'sledvasta stranica' + url
             thumbnail='DefaultFolder.png'
             addDir('Следваща страница>>'+str(currentDisplayCounter),url,1,thumbnail)


#Търсачка
def SEARCH(url):
        keyb = xbmc.Keyboard('', 'Search')
        keyb.doModal()
        searchText = ''
        if (keyb.isConfirmed()):
            searchText = urllib.quote_plus(keyb.getText())
            searchText=searchText.replace(' ','+')
            searchurl = url + searchText
            searchurl = searchurl.encode('utf-8')
            #print 'SEARCHING:' + searchurl
            req = urllib2.Request(searchurl)
            req.add_header('User-Agent', UA)
            response = urllib2.urlopen(req)
            #print 'request page url:' + url
            data=response.read()
            response.close()
            #Начало на обхождането
            br = 0 #Брояч на видеата в страницата - 24 за този сайт
            match = re.compile('<a href="(.+?)" rel.+?title="(.+?)".*src="(.+?)"').findall(data)
            for link,zaglavie,kartinka in match:
             desc = ''
             addLink(zaglavie,link,3,desc,kartinka)
             br = br + 1
             print 'Items counter: ' + str(br)
            if br >= 15: #тогава имаме следваща страница и конструираме нейния адрес
             matchp = re.compile('<span class="current">1</span><a href="(.+?)/page/(.+?)/').findall(data)
             for baseurl,numb in matchp:
              number = 0
              page = int(number)
              currentDisplayCounter = page + int(numb)
              url = baseurl + '/page/' + str(currentDisplayCounter) + '/'
              print 'sledvasta stranica' + url
              thumbnail='DefaultFolder.png'
              addDir('Следваща страница>>'+str(currentDisplayCounter),url,1,thumbnail)
        else:
             addDir('Върнете се назад в главното меню за да продължите','','',"DefaultFolderBack.png")

def SHOW(url):
       req = urllib2.Request(url)
       req.add_header('User-Agent', UA)
       response = urllib2.urlopen(req)
       data=response.read()
       response.close()
       match = re.compile("<iframe.+?src=.(.+?). ").findall(data)
       for link in match:
        print link       
        match2 = re.compile('<h2>(.+?)</h2>\s+<p>(.+?)<br />\s+(.*)<br />\s+.*<br />\s+(.*)<br />\s+(.*)<br />').findall(data)
        for one,two,three,four,five in match2:
         one = one.replace('&#8211;','')
         desc = one + ' ' + two + ' ' + three + ' ' + four + ' ' + five
         print desc
         if 'matchat' in link:
          addLink2(name,link,5,desc,'DefaultVideo.png')
         if 'content-ventures' in link:
          match3 = re.compile('id="item2"><a href="(.+?)"><div class="acp_title">').findall(data)
          for link2 in match3:     
            addLink2(name,link2,6,desc,'DefaultVideo.png')       
         if not 'content-ventures' or not 'matchat' in link:
          addLink2(name,link,4,desc,'DefaultVideo.png') 







#Зареждане на видео
def PLAY(url):
        li = xbmcgui.ListItem(iconImage=iconimage, thumbnailImage=iconimage, path=url)
        li.setInfo('video', { 'title': name })
        link = url
        try: stream_url = urlresolver.HostedMediaFile(link).resolve()
        except:
               deb('Link URL Was Not Resolved',link); deadNote("urlresolver.HostedMediaFile(link).resolve()","Failed to Resolve Playable URL."); return

        ##xbmc.Player().stop()
        play=xbmc.Player() ### xbmc.PLAYER_CORE_AUTO | xbmc.PLAYER_CORE_DVDPLAYER | xbmc.PLAYER_CORE_MPLAYER | xbmc.PLAYER_CORE_PAPLAYER
        try: _addon.resolve_url(url)
        except: t=''
        try: _addon.resolve_url(stream_url)
        except: t=''
        play.play(stream_url, li); xbmcplugin.setResolvedUrl(handle=int(sys.argv[1]), succeeded=True, listitem=li)
        try: _addon.resolve_url(url)
        except: t=''
        try: _addon.resolve_url(stream_url)
        except: t=''

def PLAYMC(url):
        req = urllib2.Request(url)
        req.add_header('User-Agent', UA)
        response = urllib2.urlopen(req)
        data = response.read()
        response.close()
        match = re.compile("hls: '(.+?)'").findall(data)
        for urlc in match:
          lnk = 'https:' + urlc
          li = xbmcgui.ListItem(iconImage=iconimage, thumbnailImage=iconimage, path=lnk)
          li.setInfo('video', { 'title': name })
          xbmcplugin.setResolvedUrl(handle=int(sys.argv[1]), succeeded=True, listitem=li)
          try:
           xbmc.Player().play(lnk, li)
          except:
           xbmc.executebuiltin("Notification('Грешка','Видеото липсва на сървъра!')")

def PLAYCV(url):
        req = urllib2.Request(url)
        req.add_header('User-Agent', UA)
        response = urllib2.urlopen(req)
        data=response.read()
        response.close()             
        match = re.compile('<iframe.+?src="(.+?)"').findall(data)
        for url in match:
         li = xbmcgui.ListItem(iconImage=iconimage, thumbnailImage=iconimage, path=url)
         li.setInfo('video', { 'title': name })
         link = url
         try: stream_url = urlresolver.HostedMediaFile(link).resolve()
         except:
               deb('Link URL Was Not Resolved',link); deadNote("urlresolver.HostedMediaFile(link).resolve()","Failed to Resolve Playable URL."); return

         ##xbmc.Player().stop()
         play=xbmc.Player() ### xbmc.PLAYER_CORE_AUTO | xbmc.PLAYER_CORE_DVDPLAYER | xbmc.PLAYER_CORE_MPLAYER | xbmc.PLAYER_CORE_PAPLAYER
         try: _addon.resolve_url(url)
         except: t=''
         try: _addon.resolve_url(stream_url)
         except: t=''
         play.play(stream_url, li); xbmcplugin.setResolvedUrl(handle=int(sys.argv[1]), succeeded=True, listitem=li)
         try: _addon.resolve_url(url)
         except: t=''
         try: _addon.resolve_url(stream_url)
         except: t=''

#Модул за добавяне на отделно заглавие и неговите атрибути към съдържанието на показваната в Kodi директория - НЯМА НУЖДА ДА ПРОМЕНЯТЕ НИЩО ТУК
def addLink(name,url,mode,plot,iconimage):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
        ok=True
        liz = xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
        liz.setArt({'thumb': iconimage, 'poster': iconimage, 'banner': iconimage, 'fanart': iconimage})
        liz.setInfo(type="Video", infoLabels={"Title": name, "plot": plot})
        liz.setProperty("IsPlayable" , "true")
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok

def addLink2(name,url,mode,plot,iconimage):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
        ok=True
        liz = xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
        liz.setArt({'thumb': iconimage, 'poster': iconimage, 'banner': iconimage, 'fanart': iconimage})
        liz.setInfo(type="Video", infoLabels={"Title": name, "plot": plot})
        liz.setProperty("IsPlayable" , "false")
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=False)
        return ok

#Модул за добавяне на отделна директория и нейните атрибути към съдържанието на показваната в Kodi директория - НЯМА НУЖДА ДА ПРОМЕНЯТЕ НИЩО ТУК
def addDir(name,url,mode,iconimage):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
        ok=True
        liz = xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
        liz.setArt({'thumb': iconimage, 'poster': iconimage, 'banner': iconimage, 'fanart': iconimage})
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok

def log(txt, loglevel=xbmc.LOGDEBUG):
    if (__addon__.getSetting( "logEnabled" ) == "true") or (loglevel != xbmc.LOGDEBUG):
        if isinstance (txt,str):
            txt = txt.decode("utf-8")
        message = u'%s: %s' % (__addonid__, txt)
        xbmc.log(msg=message.encode("utf-8"), level=loglevel)

#НЯМА НУЖДА ДА ПРОМЕНЯТЕ НИЩО ТУК
def get_params():
        param=[]
        paramstring=sys.argv[2]
        if len(paramstring)>=2:
                params=sys.argv[2]
                cleanedparams=params.replace('?','')
                if (params[len(params)-1]=='/'):
                        params=params[0:len(params)-2]
                pairsofparams=cleanedparams.split('&')
                param={}
                for i in range(len(pairsofparams)):
                        splitparams={}
                        splitparams=pairsofparams[i].split('=')
                        if (len(splitparams))==2:
                                param[splitparams[0]]=splitparams[1]
                                
        return param







params=get_params()
url=None
name=None
iconimage=None
mode=None

try:
        url=urllib.unquote_plus(params["url"])
except:
        pass
try:
        name=urllib.unquote_plus(params["name"])
except:
        pass
try:
        name=urllib.unquote_plus(params["iconimage"])
except:
        pass
try:
        mode=int(params["mode"])
except:
        pass


#Списък на отделните подпрограми/модули в тази приставка - трябва напълно да отговаря на кода отгоре
if mode==None or url==None or len(url)<1:
        print ""
        CATEGORIES()
    
elif mode==1:
        print ""+url
        INDEXPAGES(url)

elif mode==2:
        print ""+url
        SEARCH(url)

elif mode==3:
        print ""+url
        SHOW(url)
        
elif mode==4:
        print ""+url
        PLAY(url)

elif mode==5:
        print ""+url
        PLAYMC(url)

elif mode==6:
        print ""+url
        PLAYCV(url)

xbmcplugin.endOfDirectory(int(sys.argv[1]))
