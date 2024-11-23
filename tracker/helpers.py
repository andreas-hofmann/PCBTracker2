from django.shortcuts import render
from django.template import RequestContext

from tracker.models import *
from tracker.forms import *

import re

def get_username(request):
    username = None
    if request.user.is_authenticated:
        username = request.user.username
    return username

def my_render_to_response(template, data, request):
    d = {
            'searchform': SearchForm(),
            'username': get_username(request),
    }
    d.update(data)
    return render(request, template, d)

def get_patchdescs(class_id=0):
    patches = Patch.objects.filter(classid = class_id)

    patchdescs = []
    for p in patches:
        patchdesc = PatchDesc.objects.filter(patchid = p.id)
        if patchdesc:
            patchdesc = patchdesc.latest('id')
            patchdescs.append({ 'patch' : p, 'desc': patchdesc, })

    return patchdescs

def search_board(searchstring="", search_boardname=True, search_projectname=True,
                    search_serial=True, search_productnr=True, search_patch=True):
    results = {}
    results['projects'] = []
    results['boards'] = []
    results['boardclasses'] = []
    results['patches'] = []

    # Split on commas & remove extra whitespace
    strings = [ s.strip(" ") for s in searchstring.split(";") ]

    # Process search strings
    for s in strings:
        # Search Project-ID
        if search_projectname:
            projects = Project.objects.all()
            for p in projects:
                if re.search(s, p.name, re.I) or re.search(s, p.desc, re.I):
                    boardclasses = BoardClass.objects.filter(projectid=p.id)
                    for b in boardclasses:
                        result = Board.objects.filter(classid=b.id)
                        results['projects'].extend(result)

        # Search BoardClass-names + Product number
        if search_boardname or search_productnr:
            classes = BoardClass.objects.all()
            for c in classes:
                if search_boardname:
                    if re.search(s, c.name, re.I):
                        result = Board.objects.filter(classid=c.id)
                        results['boardclasses'].extend(result)
                if search_productnr:
                    if re.search(s, c.productnr, re.I):
                        result = Board.objects.filter(classid=c.id)
                        results['boardclasses'].extend(result)

        # Search Serial-Numbers
        if search_serial:
            for b in Board.objects.all():
                if re.search(s, b.serial_top, re.I):
                    results['boards'].extend([b])
                elif re.search(s, b.serial_bottom, re.I):
                    results['boards'].extend([b])

        # Search Patch-Numbers
        if search_patch:
            try:
                for b in Patch.objects.filter(id=int(s)):
                    results['patches'].extend([b])
            except:
                pass

    # Only return unique results
    for k in results.keys():
        results[k] = list(set(results[k]))

    return results
