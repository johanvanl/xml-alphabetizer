
import webapp2
import cgi

import xml.etree.ElementTree as ET

def sortXml(elem, reverse_sort):
    elems = list(elem)
    elems.sort(key = lambda e: (e.tag, e.text), reverse=reverse_sort)
    elem[:] = elems
    for e in elem:
        sortXml(e, reverse_sort)

def sortXmlByAttribute(elem, node, attribute, reverse_sort):
    elems = list(elem)
    begin_ind = -1
    # end is index of last node under conditions
    end_ind = -1
    for ind in xrange(len(elems)):
        if begin_ind < 0 and elems[ind].tag == node:
            begin_ind = ind
        if begin_ind >= 0 and elems[ind].tag == node:
            end_ind = ind
    sub_list = elems[begin_ind:end_ind+1]
    sub_list.sort(key = lambda e: (e.attrib[attribute], e.text), reverse=reverse_sort)
    elems[begin_ind:end_ind+1] = sub_list
    elem[:] = elems
    for e in elem:
        sortXmlByAttribute(e, node, attribute, reverse_sort)

def flatten(elem):
    if elem.text is None or elem.text.strip() == '':
        elem.text = ''
    elem.tail = ''
    for e in elem:
        flatten(e)

def prettifyElement(elem, indent='  ', level=0):
    i = "\n" + level * indent
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + indent
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            prettifyElement(elem, indent, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

class MainPage(webapp2.RequestHandler):
    def get(self):
        # Didn't want to install the templates library
        # to run locally
        self.response.write(open('index.html', 'r').read())

    def post(self):
        out = None
        try:
            root = ET.fromstring(self.request.get('ta_xml'))
            if self.request.get('rad_group_sort') == 'rad_asc':
                sortXml(root, False)
            else:
                sortXml(root, True)
            node = self.request.get('inp_node').strip()
            attr = self.request.get('inp_attribute').strip()
            if len(node) > 0 and len(attr) > 0:
                if self.request.get('rad_group_sort') == 'rad_asc':
                    sortXmlByAttribute(root, node, attr, False)
                else:
                    sortXmlByAttribute(root, node, attr, True)
            if self.request.get('rad_group_out') == 'rad_prettify':
                prettifyElement(root)
            else:
                flatten(root)
            out = ET.tostring(root).strip()
        except Exception, e:
            out = 'ERROR : ' + str(e)

        self.response.content_type = 'application/rss+xml'
        self.response.write(out)

application = webapp2.WSGIApplication([
    ('/', MainPage),
], debug=True)

def main():
    from paste import httpserver
    httpserver.serve(application, host='127.0.0.1', port='8080')

if __name__ == '__main__':
    main()
