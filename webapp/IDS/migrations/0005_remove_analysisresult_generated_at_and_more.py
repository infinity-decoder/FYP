# Generated by Django 5.2 on 2025-05-01 04:29

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('IDS', '0004_alter_pcapfile_file'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='analysisresult',
            name='generated_at',
        ),
        migrations.RemoveField(
            model_name='pcapfile',
            name='analysis_result',
        ),
        migrations.AddField(
            model_name='pcapfile',
            name='progress_status',
            field=models.CharField(default='Waiting for processing', max_length=255),
        ),
        migrations.AlterField(
            model_name='analysisresult',
            name='malicious_ips',
            field=models.JSONField(),
        ),
        migrations.AlterField(
            model_name='analysisresult',
            name='model_details',
            field=models.JSONField(),
        ),
        migrations.AlterField(
            model_name='analysisresult',
            name='pcap_file',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='IDS.pcapfile'),
        ),
        migrations.AlterField(
            model_name='pcapfile',
            name='uploaded_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
