from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Project(models.Model):
    name = models.CharField(max_length=30, unique=True)
    desc = models.CharField(max_length=200, blank=True)

    def __unicode__(self):
        return unicode(self.name)

class BoardClass(models.Model):
    projectid = models.ForeignKey(Project)
    name = models.CharField(max_length=30)
    productnr = models.CharField(max_length=30)
    desc = models.CharField(max_length=200, blank=True)
    revision = models.CharField(max_length=30, null=True)

    class Meta:
        unique_together = ("name", "revision", "projectid")

    def __unicode__(self):
        ret = unicode(self.name)

        if (self.revision):
            ret += unicode(" (" + self.revision + ")")

        return ret

class Board(models.Model):
    classid = models.ForeignKey(BoardClass)
    csnr = models.CharField(max_length=30)
    revision = models.CharField(max_length=30, blank=True)
    comment = models.CharField(max_length=2000, blank=True)
    serial_top = models.CharField(max_length=30, blank=True)
    serial_bottom = models.CharField(max_length=30, blank=True)
    date = models.DateTimeField('Created', auto_now=True)
    defect = models.NullBooleanField('Defect', default=False, null=True)
    swversion = models.CharField(max_length=30, blank=True, null=True)
    attachment = models.FileField(upload_to="attachments/board/%Y-%m-%d-%H-%M-%S/")

    def __unicode__(self):
        return unicode(self.classid.__unicode__() + " - " + self.csnr)

    def get_location(self):
        try:
            return Location.objects.filter(boardid = self).latest('id').location
        except:
            return ''

    def get_all_patches(self):
        return Patch.objects.filter(classid = self.classid)

    def get_own_patches(self):
        bs = BoardStatus.objects.filter(boardid=self)

        if bs:
            return bs.latest('id').get_patches()

        return {}

    def get_patchstatus(self):
        own_patches = self.get_own_patches()

        result = []

        for p in self.get_all_patches():
            p_id = str(p.id)
            if p_id in own_patches:
                latest = p.get_latest_rev()
                if own_patches[p_id] == str(latest) or latest == None:
                    result.append({'b_id': self.id, 'p_id': p.id, 'status':own_patches[p_id], 'latest':True})
                else:
                    result.append({'b_id': self.id, 'p_id': p.id, 'status':own_patches[p_id], 'latest':False})
            else:
                result.append({'b_id': self.id, 'p_id': p.id, 'status':'-', 'latest':True})

        return result

    def set_patchstatus(self, board_id, patch_id, status, author):
        own_patches = self.get_own_patches()

        try:
            status = int(status)
        except ValueError:
            status = ''

        patch = str(patch_id)

        if status == '':
            if patch not in own_patches:
                return

            own_patches.pop(patch)
        else:
            if patch in own_patches:
                own_patches.pop(patch)

            own_patches[patch] = status

            all_patches = self.get_all_patches()
            latest_rev = str(all_patches.filter(id = patch_id)[0].get_latest_rev())

        new_patches = '#'
        for p in own_patches.iterkeys():
            new_patches += "%s:%s#" % (p, own_patches[p])

        location = self.get_location()

        bs = BoardStatus(
            boardid=Board.objects.get(id=board_id),
            author=User.objects.get(username=author),
            patches=new_patches,
            location=location,
        )

        bs.save()

    def is_runnable(self, board_id=0):
        patchdescs = []
        for p in Patch.objects.filter(classid = self.classid.id):
            pd = PatchDesc.objects.filter(patchid = p.id).latest('id')
            patchdescs.append(pd)

        own_patches = self.get_own_patches()

        for pd in patchdescs:
            if unicode(pd.patchid.id) not in own_patches and pd.mandatory:
                return False

        return True

class BoardStatus(models.Model):
    boardid = models.ForeignKey(Board)
    author = models.ForeignKey(User)
    patches = models.CharField(max_length=2000)
    date = models.DateTimeField('Modified', auto_now=True)
    location = models.CharField('Current Location', max_length=50)

    def __unicode__(self):
        return unicode(str(self.id) + " - changed on " + str(self.date) + ": " + self.boardid.__unicode__())

    def get_patches(self):
        patches = self.patches.strip('#').split('#')

        while '' in patches:
            patches.remove('')

        patches = list(set(patches))
        result = {}

        for p in patches:
            r = p.strip(':').split(':')
            try:
                result[r[0]] = r[1]
            except:
                result[r[0]] = '0'

        return result

class Patch(models.Model):
    classid = models.ForeignKey(BoardClass)
    name = models.CharField(max_length=30)

    def get_latest_rev(self):
        rev = PatchDesc.objects.filter(patchid=self.id).latest('id').revision
        if not rev:
            return '0'
        return rev

    def __unicode__(self):
        return unicode("#" + str(self.id) + " - " + self.name + " (" + self.classid.__unicode__() + ")")

class PatchDesc(models.Model):
    patchid = models.ForeignKey(Patch)
    author = models.ForeignKey(User)
    desc = models.CharField(max_length=2000, blank=True)
    why = models.CharField(max_length=2000, blank=True)
    mandatory = models.NullBooleanField('Mandatory', null=True)
    date = models.DateTimeField('Modified', auto_now=True)
    mantis = models.CharField(max_length=2000, blank=True)
    attachment = models.FileField(upload_to="attachments/patch/%Y-%m-%d-%H-%M-%S/")
    revision = models.IntegerField(null=True)

    def __unicode__(self):
        return unicode(str(self.id) + ": changed on " + str(self.date) + ": " + self.patchid.__unicode__())

    def is_mandatory(self):
        if self.mandatory == True:
            return True
        else:
            return None

class Event(models.Model):
    boardid = models.ForeignKey(Board)
    author = models.ForeignKey(User)
    date = models.DateTimeField('Date', auto_now=True)
    desc = models.CharField(max_length=2000)

    def __unicode__(self):
        return unicode(str(self.id) + ": changed on " + str(self.date) + ": " + self.boardid.__unicode__())

class Location(models.Model):
    boardid = models.ForeignKey(Board)
    date = models.DateTimeField('Date', auto_now=True)
    location = models.CharField(max_length=200)

    def __unicode__(self):
        return unicode(str(self.id) + ": changed on " + str(self.date) + ": " + self.boardid.__unicode__())
