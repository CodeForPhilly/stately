# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-09-29 15:05
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stately', '0010_action_slug'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='action',
            unique_together=set([('slug', 'state')]),
        ),
    ]