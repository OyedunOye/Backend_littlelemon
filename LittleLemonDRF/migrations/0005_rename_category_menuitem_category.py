# Generated by Django 4.2.9 on 2024-01-17 21:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('LittleLemonDRF', '0004_alter_menuitem_title'),
    ]

    operations = [
        migrations.RenameField(
            model_name='menuitem',
            old_name='Category',
            new_name='category',
        ),
    ]