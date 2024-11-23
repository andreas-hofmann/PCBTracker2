from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.core.files.base import ContentFile
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from tracker.helpers import *
from tracker.models import *
from tracker.forms import *

import re


def reset_index(request):
    request.session['last_boardclass'] = None
    return HttpResponseRedirect(reverse(index))


def main(request):
    return my_render_to_response('base_skeleton.html', { }, request)


def index(request):
    last_boardclass = request.session.get('last_boardclass', None)
    if last_boardclass:
        return boards(request, last_boardclass)

    all_projects = []
    projects = Project.objects.all().order_by("name")

    for p in projects:
        project_boards = BoardClass.objects.filter(projectid=p.id)
        all_projects.append({'project': p, 'boards': project_boards})

    return my_render_to_response('tracker/index.html', {
        'all_projects' : all_projects,
    }, request)


def boards(request, class_id=''):
    boardclass = BoardClass.objects.get(id=class_id)
    boards = Board.objects.filter(classid=class_id).order_by('csnr')

    request.session['last_boardclass'] = class_id

    patchdescs = get_patchdescs(class_id)

    for p in patchdescs:
        entries = p['desc'].mantis.split()

        for split_character in [" ", ",", "\n", "\r"]:
            mantis = []
            for tmp in entries:
                mantis.extend(tmp.split(split_character))
            entries = mantis

        p['desc'].mantis = entries

    raw_table = []

    x = []
    x.append("Board-ID")
    for p in patchdescs:
        x.append(p)
    x.append("Comment")
    x.append("SW-version")
    x.append("Attachment")
    x.append("Location")
    raw_table.append(x)

    for b in boards:
        x = []

        x.append(b)

        for p in b.get_patchstatus():
            x.append(p)

        x.append(b.comment)

        if (b.swversion):
            x.append(b.swversion)
        else:
            x.append("")

        if b.attachment:
            x.append(b.attachment)
        else:
            x.append("")

        x.append(b.get_location())

        raw_table.append(x)

    table = []
    for col_counter in range(len(raw_table[0])):
        x = []
        for row in raw_table:
            x.append(row[col_counter])
        table.append(x)

    return my_render_to_response("tracker/boards.html", {
        'boardclass': boardclass,
        'boards': boards,
        'patchdescs': patchdescs,
        'board_table': table,
    }, request)


def board(request, board_id=''):
    board = Board.objects.get(id=board_id)
    events = Event.objects.filter(boardid=board_id)
    patches = Patch.objects.filter(classid=board.classid)
    boardstates = BoardStatus.objects.filter(boardid=board_id)
    locations = Location.objects.filter(boardid=board_id)

    eventform = EventForm()
    locationform = LocationForm()

    all_patches = board.get_all_patches()

    states = []
    for s in boardstates:
        s_patches = s.get_patches()
        p = []
        for cur_p in all_patches:
            if str(cur_p.id) in s_patches:
                p.append("Rev " + s_patches[str(cur_p.id)])
            else:
                p.append("-")
        states.append({'s':s, 'p':p, 'id': s.id})

    return my_render_to_response("tracker/board.html", {
        'board': board,
        'patches': patches,
        'states': states,
        'events': events,
        'eventform': eventform,
        'locationform': locationform,
        'locations': locations,
    }, request)


def patch(request, patch_id=''):
    patch = Patch.objects.get(id=patch_id)
    descs = PatchDesc.objects.filter(patchid=patch_id)
    boardclass = BoardClass.objects.get(id=patch.classid.id)

    username = get_username(request)

    return my_render_to_response("tracker/patch.html", {
        'username': username,
        'patch': patch,
        'descs': descs,
        'boardclass': boardclass
    }, request)


def do_register(request):
    username = get_username(request)
    if username:
        return HttpResponse("You are already logged in, no need for a new registration.")

    if request.method == 'POST':
        try:
            if not request.POST['password']:
                return my_render_to_response("error.html", {
                    'error': 'No password specified!',
                }, request)
        except KeyError:
            pass

        form = RegisterForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            password2 = form.cleaned_data['password2']
            email = form.cleaned_data['email']
            firstname = form.cleaned_data['firstname']
            lastname = form.cleaned_data['lastname']

            if password2 != password:
                return my_render_to_response("error.html", {
                    'error': 'Passwords don\'t match!',
                }, request)

            u = User.objects.create_user(username, email, password)
            u.firstname = firstname
            u.lastname = lastname
            try:
                u.save()
            except IntegrityError:
                return my_render_to_response("error.html", {
                    'error': 'User is already registered!',
                }, request)
            return my_render_to_response("registered.html", {
            }, request)
        return my_render_to_response("register.html", {
                'error': 'Invalid Data entered.',
                'form': form,
                'next': reverse(do_register),
            }, request)

    form = RegisterForm()

    return my_render_to_response("register.html", {
        'form': form,
        'next': reverse(do_register),
    }, request)


@login_required
def add_project(request):
    username = get_username(request)

    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name'].upper()
            desc = form.cleaned_data['desc']

            nr = re.match("^(\d+)", name)
            if nr:
                name = str(nr.group(1))
            else:
                return my_render_to_response("error.html", {
                    'error': 'Invalid nr entered!',
                }, request)

            p = Project(name=name, desc=desc)
            p.save()
            g = Group(name=name)
            g.save()
            return HttpResponseRedirect(reverse(index))
        else:
            return my_render_to_response("error.html", {
                'error': 'Invalid data entered!',
            }, request)

    form = ProjectForm()

    return my_render_to_response("tracker/new_project.html", {
        'form': form,
        'username': username,
    }, request)


@login_required
def edit_project(request, project_id):
    username = get_username(request)

    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name'].upper()
            desc = form.cleaned_data['desc']

            nr = re.match("^[Cc]?[Oo]?[Rr]?(\d+)", name)
            if nr:
                name = "COR" + str(nr.group(1))
            else:
                return my_render_to_response("error.html", {
                    'error': 'Invalid nr entered!',
                }, request)

            p = Project.objects.get(id=project_id)
            g = Group.objects.get(name=p.name)

            g.name = name
            g.save()

            p.name = name
            p.desc = desc
            p.save()

            return HttpResponseRedirect(reverse(index))
        else:
            return my_render_to_response("error.html", {
                'error': 'Invalid data entered!',
            }, request)

    project = Project.objects.filter(id=project_id)[0]
    form = ProjectForm(initial={
            'name': project.name,
            'desc': project.desc
    })

    return my_render_to_response("tracker/edit_project.html", {
        'project': project,
        'form': form,
        'username': username,
    }, request)


@login_required
def add_boardclass(request, project_id=''):
    username = get_username(request)

    if request.method == 'POST':
        form = BoardClassForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            desc = form.cleaned_data['desc']
            productnr = form.cleaned_data['productnr'].upper()
            revision = form.cleaned_data['revision']
            project = Project.objects.get(id=project_id)

            if (BoardClass.objects.filter(name=name).filter(revision=revision).filter(projectid=project)):
                return my_render_to_response("error.html", {
                    'error': 'BoardClass for project %s with name %s and revision %s already exists!' %
                             (project, name, revision),
                }, request)

            b = BoardClass(
                projectid=project,
                name=name,
                desc=desc,
                productnr=productnr, 
                revision=revision
            )
            b.save()

            return HttpResponseRedirect(reverse(index))
        else:
            return my_render_to_response("error.html", {
                'error': 'Invalid data entered!',
            }, request)

    project = Project.objects.get(id=project_id)
    form = BoardClassForm()

    return my_render_to_response("tracker/new_boardclass.html", {
        'project': project,
        'form': form,
        'username': username,
    }, request)


@login_required
def edit_boardclass(request, class_id=''):
    username = get_username(request)
    boardclass = BoardClass.objects.get(id=class_id)

    if request.method == 'POST':
        form = BoardClassForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            desc = form.cleaned_data['desc']
            productnr = form.cleaned_data['productnr'].upper()
            revision = form.cleaned_data['revision']

            b = BoardClass.objects.filter(id=class_id)[0]
            b.name = name
            b.revision = revision
            b.desc = desc
            b.productnr = productnr
            b.save()

            return HttpResponseRedirect(reverse(index))
        else:
            return my_render_to_response("error.html", {
                'error': 'Invalid data entered!',
            }, request)

    form = BoardClassForm(initial={
        'name': boardclass.name,
        'desc': boardclass.desc,
        'productnr': boardclass.productnr,
        'revision': boardclass.revision,
    })

    return my_render_to_response("tracker/edit_boardclass.html", {
        'boardclass': boardclass,
        'form': form,
        'username': username,
    }, request)


@login_required
def add_board(request, class_id):
    username = get_username(request)

    if request.method == 'POST':
        form = BoardForm(request.POST)
        if form.is_valid():
            comment = form.cleaned_data['comment']
            csnr = form.cleaned_data['csnr']
            serial_top = form.cleaned_data['serial_top']
            serial_bottom = form.cleaned_data['serial_bottom']
            swversion = form.cleaned_data['swversion']

            attachment_content = None
            attachment_name = None
            if request.FILES:
                attachment_content = ContentFile(request.FILES['attachment'].read())
                attachment_name = request.FILES['attachment'].name

            classid = BoardClass.objects.get(id=class_id)

            b = Board(
                classid=classid,
                comment=comment,
                csnr=csnr,
                serial_top=serial_top,
                serial_bottom=serial_bottom,
                revision=classid.revision,
                swversion=swversion
            )

            if attachment_name and attachment_content:
                b.attachment.save(attachment_name, attachment_content)
                print("add: attachment uploaded")

            b.save()

            l = Location(
                boardid=b,
                location=username,
            )
            l.save()

            return HttpResponseRedirect(reverse(boards, args=(classid.id,)))
        else:
            return my_render_to_response("error.html", {
                'error': 'Invalid data entered!',
            }, request)

    boardclass = BoardClass.objects.get(id=class_id)

    form = BoardForm()

    return my_render_to_response("tracker/new_board.html", {
        'boardclass': boardclass,
        'form': form,
        'username': username,
    }, request)


@login_required
def edit_board(request, board_id):
    username = get_username(request)

    b = Board.objects.get(id=board_id)

    if request.method == 'POST':
        form = BoardForm(request.POST)
        if form.is_valid():
            comment = form.cleaned_data['comment']
            csnr = form.cleaned_data['csnr']
            serial_top = form.cleaned_data['serial_top']
            serial_bottom = form.cleaned_data['serial_bottom']
            defect = form.cleaned_data['defect']
            swversion = form.cleaned_data['swversion']

            attachment_content = None
            attachment_name = None
            if request.FILES:
                attachment_content = ContentFile(request.FILES['attachment'].read())
                attachment_name = request.FILES['attachment'].name

            b.comment = comment
            b.csnr = csnr
            b.serial_top = serial_top
            b.serial_bottom = serial_bottom
            b.defect = defect
            b.swversion = swversion

            if attachment_name and attachment_content:
                b.attachment.save(attachment_name, attachment_content)

            b.save()

            return HttpResponseRedirect(reverse(board, args=(b.id,)))
        else:
            return my_render_to_response("error.html", {
                'error': 'Invalid data entered!',
            }, request)

    form = BoardForm(initial={
        'comment': b.comment,
        'csnr': b.csnr,
        'serial_top': b.serial_top,
        'serial_bottom': b.serial_bottom,
        'defect': b.defect,
        'swversion': b.swversion,
    })

    return my_render_to_response("tracker/edit_board.html", {
        'board': b,
        'form': form,
        'username': username,
    }, request)


@login_required
def add_patch(request, class_id=''):
    username = get_username(request)

    if request.method == 'POST':
        form = PatchForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            desc = form.cleaned_data['desc']
            why = form.cleaned_data['why']
            mandatory = form.cleaned_data['mandatory']
            mantis = form.cleaned_data['mantis']
            attachment_content = None
            attachment_name = None
            if request.FILES:
                attachment_content = ContentFile(request.FILES['attachment'].read())
                attachment_name = request.FILES['attachment'].name

            classid = BoardClass.objects.get(id=class_id)

            p = Patch(
                classid=classid,
                name=name,
            )
            p.save()

            d = PatchDesc(
                patchid=p,
                desc=desc,
                why=why,
                mandatory=mandatory,
                mantis=mantis,
                author=User.objects.get(username=username),
                revision=1
            )
            if attachment_name and attachment_content:
                d.attachment.save(attachment_name, attachment_content)
            d.save()

            return HttpResponseRedirect(reverse(boards, args=[class_id]))
        else:
            return my_render_to_response("error.html", {
                'error': 'Invalid data entered!'
            }, request)

    form = PatchForm()

    boardclass = BoardClass.objects.get(id=class_id)

    return my_render_to_response("tracker/new_patch.html", {
        'username': username,
        'form': form,
        'boardclass': boardclass,
    }, request)


@login_required
def edit_patch(request, patch_id=''):
    username = get_username(request)

    p = Patch.objects.get(id=patch_id)
    previous = PatchDesc.objects.filter(patchid=p.id).latest('id')

    if request.method == 'POST':
        form = PatchForm(request.POST, request.FILES)

        if form.is_valid():
            update_rev = False

            name = form.cleaned_data['name']
            desc = form.cleaned_data['desc']
            why = form.cleaned_data['why']
            mandatory = form.cleaned_data['mandatory']
            mantis = form.cleaned_data['mantis']
            attachment_content = None
            attachment_name = None
            if request.FILES:
                attachment_content = ContentFile(request.FILES['attachment'].read())
                attachment_name = request.FILES['attachment'].name

            if name != p.name:
                p.name = name
                p.save()

            if desc != previous.desc:
                update_rev = True
            if why != previous.why:
                update_rev = True
            if mantis != previous.mantis:
                update_rev = True
            if attachment_content:
                update_rev = True

            if not update_rev:
                previous.mandatory = mandatory
                previous.save()
                return HttpResponseRedirect(reverse(patch, args=[patch_id]))

            d = PatchDesc(
                patchid=p,
                desc=desc,
                why=why,
                mandatory=mandatory,
                mantis=mantis,
                author=User.objects.get(username=username),
            )

            if previous.revision:
                d.revision = previous.revision + 1
            else:
                d.revision = 1

            if attachment_content:
                d.attachment.save(attachment_name, attachment_content)
            else:
                d.attachment = previous.attachment

            d.save()

            return HttpResponseRedirect(reverse(patch, args=[patch_id]))
        else:
            return my_render_to_response("error.html", {
                'error': 'Invalid data entered!'
            }, request)

    d = PatchDesc.objects.filter(patchid=p).latest('id')
    form = PatchForm(initial={
        'name': p.name,
        'desc': d.desc,
        'why': d.why,
        'mandatory': d.mandatory,
        'mantis': d.mantis,
        'attachment': d.attachment,
    })

    boardclass = BoardClass.objects.get(id=p.classid.id)

    return my_render_to_response("tracker/edit_patch.html", {
        'username': username,
        'form': form,
        'boardclass': boardclass,
        'patch': p,
    }, request)


@login_required
def add_event(request, board_id=''):
    username = get_username(request)

    b = Board.objects.get(id=board_id)

    if request.method == 'POST':
        form = EventForm(request.POST)

        if form.is_valid():
            e = Event(
                author=User.objects.get(username=username),
                boardid=b,
                desc=form.cleaned_data['desc']
            )

            e.save()
            return HttpResponseRedirect(reverse(board, args=[b.id]))
        else:
            return my_render_to_response("error.html", {
                    'error': 'You did not enter an event-description!'
            }, request)
    else:
        return my_render_to_response("error.html", {
                'error': 'This should not have happened. What are you doing here?'
        }, request)


@login_required
def claim_board(request, board_id=''):
    username = get_username(request)

    b = Board.objects.get(id=board_id)

    cur_location = Location.objects.filter(boardid=b)

    if cur_location:
        cur_location = cur_location.latest('id').location
    else:
        cur_location = ''

    if not username == cur_location:
        location = Location(
            boardid=b,
            location=username,
        )

        location.save()

    return HttpResponseRedirect(reverse(board, args=[b.id]))


@login_required
def add_location(request, board_id=''):
    b = Board.objects.get(id=board_id)

    if request.method == 'POST':
        form = LocationForm(request.POST)

        if form.is_valid():
            location = Location(
                boardid=b,
                location=form.cleaned_data['location'],
            )

            location.save()

            return HttpResponseRedirect(reverse(board, args=[b.id]))
        else:
            return my_render_to_response("error.html", {
                    'error': 'You did not enter a location!'
            }, request)
    else:
        return my_render_to_response("error.html", {
                'error': 'This should not have happened. What are you doing here?'
        }, request)


def raw_search(request, searchstring=""):
    results = search_board(searchstring)
    return my_render_to_response("error.html", {
        'error': 'This function is not fully implemented yet. Result: %s ' % results
    }, request)


def search(request):
    if request.method == 'POST':
        form = SearchForm(request.POST)

        if form.is_valid():
            searchstring = form.cleaned_data['searchstring']
            results = search_board(searchstring,
                                   form.cleaned_data['search_boardname'],
                                   form.cleaned_data['search_projectname'],
                                   form.cleaned_data['search_serial'],
                                   form.cleaned_data['search_productnr'],
                                   form.cleaned_data['search_patchnr'])

            return my_render_to_response("tracker/searchresults.html", {
                'searchstring': searchstring,
                'results_projects': results['projects'],
                'results_boardclasses': results['boardclasses'],
                'results_boards': results['boards'],
                'results_patches': results['patches'],
            }, request)
        else:
            return my_render_to_response("tracker/search.html", {
                'form': SearchForm(),
                'next': reverse(search),
            }, request)

    return my_render_to_response("tracker/search.html", {
        'form': SearchForm(),
        'next': reverse(search),
    }, request)


def export_patches(request, status_id=''):
    try:
        status = BoardStatus.objects.filter(id=status_id)[0]
        patches = status.get_patches()
    except IndexError:
        return my_render_to_response("error.html", {
            'error': 'No patch status available for status \'%s\'' % status_id
        }, request)

    board = Board.objects.filter(id=status.boardid)[0]

    descs = []

    for p in patches.keys():
        desc = PatchDesc.objects.filter(patchid=p)

        try:
            if int(patches[p]) != 0:
                desc = PatchDesc.objects.filter(patchid=p, revision=patches[p])
            else:
                desc = PatchDesc.objects.filter(patchid=p, revision=None).order_by('id').reverse()
        except ValueError:
            print("Error in key " + p + ": " + patches[p])
            pass

        if desc:
            desc = desc[0]
            descs.append({'patch': Patch.objects.filter(id=p), 'desc':desc})

    return my_render_to_response("tracker/export_patches.html", {
        'descs': descs,
        'board': board,
    }, request)
