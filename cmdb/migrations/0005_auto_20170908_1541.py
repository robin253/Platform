# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-09-08 15:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cmdb', '0004_auto_20170907_1719'),
    ]

    operations = [
        migrations.AddField(
            model_name='dbmeta',
            name='db_type',
            field=models.CharField(default='oracle', help_text=b'\xe6\x95\xb0\xe6\x8d\xae\xe5\xba\x93\xe7\xb1\xbb\xe5\x9e\x8b', max_length=32, verbose_name=b'\xe6\x95\xb0\xe6\x8d\xae\xe5\xba\x93\xe7\xb1\xbb\xe5\x9e\x8b'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='dbmeta',
            name='admin_ip',
            field=models.CharField(help_text=b'\xe7\xae\xa1\xe7\x90\x86\xe7\xbd\x91IP', max_length=16, verbose_name=b'\xe7\xae\xa1\xe7\x90\x86\xe7\xbd\x91IP'),
        ),
        migrations.AlterField(
            model_name='dbmeta',
            name='db_desc',
            field=models.CharField(help_text=b'\xe6\x95\xb0\xe6\x8d\xae\xe5\xba\x93\xe5\x90\x8d', max_length=128, verbose_name=b'\xe6\x95\xb0\xe6\x8d\xae\xe5\xba\x93\xe5\x90\x8d'),
        ),
        migrations.AlterField(
            model_name='dbmeta',
            name='db_port',
            field=models.IntegerField(choices=[(b'oracle', b'ORACLE'), (b'mysql', b'MySQL'), (b'redis', b'REDIS')], help_text=b'\xe5\xae\x9e\xe4\xbe\x8b\xe7\xab\xaf\xe5\x8f\xa3', verbose_name=b'\xe7\x9b\x91\xe5\x90\xac\xe7\xab\xaf\xe5\x8f\xa3'),
        ),
        migrations.AlterField(
            model_name='dbmeta',
            name='domain_name',
            field=models.CharField(help_text=b'\xe5\x9f\x9f\xe5\x90\x8d', max_length=128, verbose_name=b'\xe5\x9f\x9f\xe5\x90\x8d'),
        ),
        migrations.AlterField(
            model_name='dbmeta',
            name='rw_flag',
            field=models.CharField(choices=[(b'w', b'\xe5\x86\x99'), (b'r', b'\xe8\xaf\xbb')], default=b'r', help_text=b'\xe8\xaf\xbb\xe5\x86\x99\xe5\xba\x93\xe6\xa0\x87\xe7\xa4\xba\xef\xbc\x8cr\xe8\xaf\xbb\xe5\xba\x93\xef\xbc\x8cw\xe5\x86\x99\xe5\xba\x93', max_length=1, verbose_name=b'\xe8\xaf\xbb\xe5\x86\x99\xe5\xba\x93'),
        ),
    ]
