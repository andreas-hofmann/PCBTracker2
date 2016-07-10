#from dajax.core import Dajax
#
#from dajaxice.decorators import dajaxice_register
#
from PCBTracker.models import *
from PCBTracker.views import get_username
#
#from django.contrib.auth.decorators import login_required
#
#import logging
#logging.basicConfig()
#
def update_patchstatus(request, board_id, patch_id):
    dajax = Dajax()

    latest = PatchDesc.objects.filter(patchid=patch_id).latest('id')
    patch = Patch.objects.filter(id=patch_id).latest('id')

    author = get_username(request)
    if not author:
        dajax.alert('Please log in first!')
        return dajax.json()

    b = Board.objects.get(id=board_id)

    dajax.add_data({
            'board_id':   board_id,
            'patch_id':   patch_id,
            'latest_rev': latest.revision,
            'patch_name': patch.name,
            'patch_desc': latest.desc,
            'board_name': b.csnr,
            'claimed':    (b.get_location() == author),
        }, 'show_patch_popup'
    )

    return dajax.json()

def commit_patchstatus(request, status, board_id, patch_id):
    dajax = Dajax()

    author = get_username(request)
    if not author:
        dajax.alert('Please log in first!')
        return dajax.json()

    b = Board.objects.get(id=board_id)

    new_status = b.set_patchstatus(board_id, patch_id, status, author)
    dajax.script("document.location.reload(true);")

    return dajax.json()
