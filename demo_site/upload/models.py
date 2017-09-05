# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib import admin
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver

# Create your models here.
class Photo(models.Model):
    image = models.ImageField(upload_to='photos/%Y-%m-%d')

@receiver(pre_delete, sender=Photo)
def photo_delete(sender, instance, **kwargs):
    # Pass false so FileField doesn't save the model.  print sender.image
    print instance
    instance.image.delete(False)

def user_directory_path(instance, filename):
    print "in user_directory_path: " + filename
    return filename

class File(models.Model):
    # the file will be uploaded to MEDIA_ROOT
    myfile = models.FileField(upload_to=user_directory_path)


    def save(self, *args, **kwargs):
        print "in save():"
        print "  filename: " + self.myfile.name
        count = File.objects.filter(myfile='%s' % self.myfile.name).count()
        print "  number  : %d" % count
        #count = File.objects.get(myfile='%s' % self.myfile.name).count()
        if count > 0:
            File.objects.filter(myfile='%s' % self.myfile.name).delete()
            print "Remove already existing objects from DB"

        super(File, self).save(*args, **kwargs)


@receiver(pre_delete, sender=File)
def file_delete(sender, instance, **kwargs):
    # Pass false so FileField doesn't save the model.
    print sender.myfile
    print instance
    instance.myfile.delete(False)

@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    pass

@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    pass
