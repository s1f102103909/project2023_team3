# Generated by Django 4.2.3 on 2024-01-10 05:48

from django.db import migrations, models
import interview.models


class Migration(migrations.Migration):

    dependencies = [
        ('interview', '0005_remove_userinformation_shushoku_maxscore_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='userinformation',
            name='result_images',
            field=models.ImageField(blank=True, null=True, upload_to=interview.models.dir_path_name_graph),
        ),
    ]