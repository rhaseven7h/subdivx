#!/usr/bin/env python
#
#   This file is part of SubDivX.
#
#   SubDivX is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License.
#
#   SubDivX is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with SubDivX, if not, see <http://www.gnu.org/licenses/>.
#
#   See the LICENSE file.
#

import re
import urllib
import urllib2
import lxml.html
import os.path
import tempfile

class SubDivXClient:
  """
  Client for spanish subtitles downloading from http://www.subdivx.com/

    
  Examples:
  
  # List of dictionaries of results [ {'title': title, 'link': link, 'description': description, 'cds': cds}, ... ]
  subs = SubDivXClient.search('The Matrix').get_results()
  
  # Path to downloaded sutitles archive file, i.e. /tmp/subdivx/32425.rar
  filepath = SubDivXClient().search('The Matrix').fecth(1) 
  
  """
  
  def __init__(self):
    self.results = []
    
  def get_results(self):
    """
    Returns the results list
    [ {'title': title, 'link': link, 'description': description, 'cds': cds}, ... ]
    """
    return self.results

  def search(self, str_terms, page):
    """
    Makes a search for subtitles.
    Returns self for chaining.
    
    str_terms -- The string to search for at subdivx.com
    page -- The page number to fetch
    """
    
    # The magic url for searching
    str_url = "http://www.subdivx.com/index.php?buscar=%s&accion=5&masdesc=1&subtitulos=1&realiza_b=1" % urllib.quote(str_terms)
    
    # If not the first page, add the page parameter.
    if page > 1:
      str_url += "&pg=" +str(page)
    
    # Fetch the search results page
    doc = lxml.html.fromstring(unicode(urllib.urlopen(str_url).read(), errors='ignore')).getroottree().getroot()
    
    # Initialize the result elements, separate parallel lists of data
    titles = []
    links = []
    descriptions = []
    cds = []

    # Fetch the titles and links
    for link in doc.cssselect("a.titulo_menu_izq"):
      titles.append(link.text_content())
      links.append(link.get('href'))

    # Now the descriptions
    for desc in doc.cssselect("div#buscador_detalle_sub"):
      descriptions.append(desc.text_content())
      
    # The number of cds ...
    for dato in doc.cssselect("div#buscador_detalle_sub_datos"):
      cds.append(re.search('Cds:<\/b> ([0-9]+)', lxml.etree.tostring(dato)).group(1))
      
    # We will consolidate the above results in a list of dictionaries in the results list
    self.results = []
    for i in range(len(titles)):
      self.results.append({ 'title': titles[i], 'link': links[i], 'description': descriptions[i], 'cds': cds[i] })

    # And return self, for chaining, see SubDivXClient class doc.
    return self
    
  def fetch(self, int_num):
    """
    Fetches the selected result from results (which you fill up by calling search()),
    and returns the path to the downloaded file stored at {SYSTEM_TEMP_DIR}/subdivx/
    You MUST call search first.
    
    int_num -- The results index number, starting from 0 (zero), from results array
    """
    
    # Create a request object for the result page with the captcha form for the selected result.
    # From here we will get the 'desub' and 'u' paramaters needed to make the request for
    # the actual file.
    # Must make a req. first, because we need to add a Referer header.
    req = urllib2.Request(self.results[int_num]['link'])
    req.add_header('Referer', self.results[int_num]['link'])
    
    # Fetch the above request and parse it.
    doc = lxml.html.fromstring(unicode(urllib2.urlopen(req).read(), errors='ignore')).getroottree().getroot()
    
    # Get the 'desub' and 'u' form parameters
    desub = doc.cssselect("input[type='hidden'][name='desub']")[0].get('value')
    u = doc.cssselect("input[type='hidden'][name='u']")[0].get('value')

    # Now build a second request to fetch the actual file, as before we need a req. object
    # to add the Referer header, now the referer is the above fetched url.
    req = urllib2.Request("http://www.subdivx.com/bajar.php?captcha_user=ME2&idcaptcha=1007&desub=%s&u=%s" % (desub, u))
    req.add_header('Referer', self.results[int_num]['link'])
    
    # And open the subtitle actual file url
    subs = urllib2.urlopen(req)
    
    # Get the content-disposition header to obtain the file name
    # subdivx.com returns the subtitles as rars and zips, so we
    # need to know the name of the file.
    fn = subs.info().get('content-disposition').split(';')[1].split('=')[1]
    
    # Create the output temporary directory 'subdivx' below the system's
    # temporary directory. If it doesn't exist, create it.
    out_dir = os.path.join(tempfile.gettempdir(), 'subdivx')
    if os.path.exists(out_dir):
      if os.path.isdir(out_dir):
        pass
      else:
        raise IOError("Temp file subdivx couldn't be created or already exists as a file or with wrong permissions")
    else:
      os.makedirs(out_dir)
      
    # Now we know we have the subdirectory to hold the file, generate the file name
    # using the above temporary directory and the file name we got from the content-disposition
    # header
    out_file = os.path.join(out_dir, fn)

    # Open in binary write mode the output file, and write to it the data
    # read from the url.
    of = open(out_file, 'wb')
    of.write(subs.read())
    
    # Clean up our mess
    of.close()
    subs.close()
    
    # And return the saved subtitle file path.
    return out_file

